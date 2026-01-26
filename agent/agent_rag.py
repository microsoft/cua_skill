import os
from typing import List, Dict
from types import SimpleNamespace
from .utils import Misc, SessionLogger, LogMessage, Status
from .action import BaseAction
import time
from .mixture_grounding import MixtureGrounding
import warnings
from .planner import RAGPlanner

warnings.filterwarnings("ignore")


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_rag.json")


class CUARAGAgent:
    def __init__(self, config=CONFIG_PATH, logger=None):
        self.project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = Misc.file_to_namespace(config)
        self.name = self.config.name
        
        self.mixture_grounding = MixtureGrounding(
            config=self.config.mixture_grounding
        )
        self.planner = RAGPlanner(self.config)
        self.logger = logger

    def set_logger_dir(self, explicit_log_dir):
        self.logger = SessionLogger(
            config=self.config.logger,
            remote_logger=None,
            explicit_log_dir=explicit_log_dir,
        )
        self.mixture_grounding.force_reset_logger(self.logger)
        self.planner.force_reset_logger(self.logger)

    def proceed(self, instruction, example, explicit_log_dir, env=None, cancel_event=None, **kwargs):
        # Set up the environment

        self.set_logger_dir(explicit_log_dir)
        
        if env is None:
            from .desktop_env import DesktopEnv

            self.env = DesktopEnv(
                name=self.config.env.name,
                platform=self.config.env.platform,
                url=self.config.env.url,
                screen_height=self.config.env.screen_height,
                screen_width=self.config.env.screen_width,
                observation_type=self.config.env.observation_type,
                observe_screenshot_in_bytes=self.config.env.observe_screenshot_in_bytes,
                logger=self.logger,
            )
        else:
            self.env = env

        self.reset()
        self.planner.set_instruction(instruction)
        self.logger.info(
            LogMessage(
                type="agent_start",
                message=f"Starting Agent: {self.name}",
                metadata={
                    "instruction": instruction,
                    "log_source_dir": str(self.logger.session_dir),
                },
            )
        )
        time.sleep(10)
        self.logger.info(
            LogMessage(
                type="wait for environment ready",
                message=f"Wait 10s to make sure the environment is completely ready...",
            )
        )
        observation = self.env.get_observation()
        self.logger.info(
            LogMessage(
                    type="initial_screen",
                    message=f"",
                    metadata={
                        "initial_screen": observation,
                    },
                )
            )
        # screenshot = observation["screenshot"]
        # file_path = example["config"][0]["parameters"]["files"][0]["path"]
        # exec_action = self.planner.get_code_solution(screenshot, file_path)
        # # self.env.reset()
        # self.env.step(exec_action)
        # time.sleep(60)
        # return 



        attempt_start_time = time.time()
        task_status = Status.IN_PROGRESS
        first_loop_flag = True
        while True:
            if self.termination(task_status, cancel_event, attempt_start_time):
                return task_status
            observation = self.env.get_observation()
            screenshot = observation["screenshot"]
            if first_loop_flag:
                feasibility = self.planner.predict_task_feasibility(screenshot)
                if not feasibility:
                    self.logger.info(
                        LogMessage(
                            type="agent_termination",
                            message=f"Task is predicted to be infeasible. Terminating the agent.",
                        )
                    )
                    task_status = Status.CALL_USER
                    return task_status
                first_loop_flag = False
            current_operation_class, step_description, is_base_action = (
                self.planner.retrieve_next_step(screenshot)
            )

            if current_operation_class is None:
                break

            if is_base_action:
                action = self.planner.config_next_step(
                    current_operation_class, screenshot, step_description
                )

                if (
                    hasattr(current_operation_class(), "require_grounding")
                    and current_operation_class().require_grounding
                ):
                    self.logger.info(
                        LogMessage(
                            type="mixture_grounding",
                            message=f"{self.name} [yellow]refining coordinates[/yellow] for action: {action.type}",
                        )
                    )

                    observation = self.env.get_observation()
                    action.call_grounding_model(
                                grounding_expertise=self.mixture_grounding,
                                observation=observation
                            )
                self.execute(actions=[action])
                time.sleep(self.config.step_interval_time)
                continue

            else:
                current_operation = self.planner.config_next_step(
                    current_operation_class, screenshot, step_description
                )
                current_operation.configure_from_env(env=self.env)

                self.logger.info(
                    LogMessage(
                        type="agent_operation_start",
                        message=f"Starting Operation",
                    )
                )

                while True:
                    action = current_operation.step(edge_name_pref="hotkey")

                    if (
                        hasattr(action, "require_grounding")
                        and action.require_grounding
                    ):
                        self.logger.info(
                            LogMessage(
                                type="mixture_grounding",
                                message=f"{self.name} [yellow]refining coordinates[/yellow] for action: {action.type}",
                            )
                        )

                        observation = self.env.get_observation()
                        action.call_grounding_model(
                                grounding_expertise=self.mixture_grounding,
                                observation=observation
                            )

                    self.execute(actions=[action])
                    time.sleep(self.config.step_interval_time)

                    if action is None:
                        break

        # self.logger.convert()


    def termination(
        self, task_status: Status, cancel_event, attempt_start_time
    ) -> bool:
        if cancel_event is not None and cancel_event.is_set():
            task_status = Status.CANCELED
        if time.time() - attempt_start_time > self.config.max_wall_time:
            task_status = Status.TIMEOUT

        if task_status in [
            Status.SUCCESS,
            Status.FAILURE,
            Status.CANCELED,
            Status.TIMEOUT,
            Status.CALL_USER,
        ]:
            self.logger.info(
                LogMessage(type="agent_termination", message=f"Status: {task_status}")
            )
            return True
        return False

    def execute(self, actions: List[BaseAction] = None) -> Status:
        task_status = Status.IN_PROGRESS
        for action in actions:
            if action is None:
                continue
            if action.type == "dummy":
                continue

            if action.type == "finish":
                self.logger.info(
                    LogMessage(
                        type="task_end_status",
                        message=f"{self.name} [green]finish[/green] the task.",
                    )
                )
                task_status = Status.SUCCESS
                return task_status
            elif action.type == "fail":
                self.logger.info(
                    LogMessage(
                        type="task_end_status",
                        message=f"{self.name} [red]fail[/red] the task.",
                    )
                )
                task_status = Status.FAILURE
                return task_status
            elif action.type == "call_user":
                self.logger.info(
                    LogMessage(
                        type="task_end_status",
                        message=f"{self.name} [blue]call_user[/blue] the task.",
                    )
                )
                task_status = Status.CALL_USER
                return task_status
            elif action.type == "error_env":
                self.logger.info(
                    LogMessage(
                        type="task_end_status",
                        message=f"{self.name} [red]error_env[/red] during the task.",
                    )
                )
                task_status = Status.ENV_ERROR
                return task_status

            before_observation = self.env.get_observation()

            executable_action_code = action.get_gui_code()

            # optional - getting debug image
            # warpped_text = Misc.wrap_text_lines(executable_action, 40)
            # debug_before_image = Misc.get_commands_debug_image(before_observation["screenshot"], commands_debug_info=[], text=warpped_text)

            # actual action execution
            self.env.step(executable_action_code)

            after_observation = self.env.get_observation()

            self.logger.info(
                LogMessage(
                    type=str(action.type),
                    message=f"Before/After action observation and {action} executed",
                    metadata={
                        "before_observation": before_observation,
                        # "before_observation_debug": debug_before_image,
                        "after_observation": after_observation,
                        "action": str(action),
                        "executable_action": executable_action_code,
                    },
                )
            )
        return task_status

    def reset(self, wait_time: int = 1):
        if self.logger:
            self.logger.info(
            LogMessage(
                type="agent_reset",
                message=f"Performing Agent Reset",
            )
        )
        else:
            print("Performing Agent Reset")
        time.sleep(wait_time)
