import os
from typing import List, Dict
from types import SimpleNamespace
from .utils import (
    Misc,
    SessionLogger,
    LogMessage,
    Status
)
from .action import BaseAction
from .replay_task import ReplayTask
import sys
import time
from .mixture_grounding import MixtureGrounding
import warnings
warnings.filterwarnings("ignore")


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

class CUAKnowledgeGraphAgent:
    def __init__(self, config=CONFIG_PATH, logger=None, explicit_log_dir:str = None):
        self.config = Misc.file_to_namespace(config)
        self.name = self.config.name
        self.logger = SessionLogger(config=self.config.logger, remote_logger=logger, explicit_log_dir=explicit_log_dir)

        self.mixture_grounding = MixtureGrounding(
            config=self.config.mixture_grounding,
            logger=self.logger
        )

    def proceed(
        self, 
        instruction: str, 
        env = None, 
        example = None,
        cancel_event = None,
        **kwargs):

        # Set up the environment
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
                logger=self.logger
            )
        else:
            self.env = env

        replay_task = ReplayTask.from_json(example)
        self.reset()
        self.logger.info(LogMessage(
            type="agent_start",
            message=f"Starting Agent: {self.name}\nTask id: {replay_task.id}\nTask Domain: {replay_task.domain}\nTask Description: {replay_task.instruction}",
            metadata={
                "id": replay_task.id + "",
                "task_domain": replay_task.domain,
                "task_type": "unknown",
                "instruction": instruction,
                "log_source_dir": str(self.logger.session_dir)
            }
        ))

        attempt_start_time = time.time()
        task_status = Status.IN_PROGRESS

        try:
            while True:
                if self.termination(task_status, cancel_event, attempt_start_time):
                    return task_status

                curr_operation = replay_task.next_step()

                if curr_operation is None:
                    break
                curr_operation.configure_from_env(env=self.env)

                self.logger.info(LogMessage(
                    type="agent_operation_start",
                    message=f"Starting Operation: {curr_operation}",
                ))

                while True:
                    action = curr_operation.step()

                    if hasattr(action, 'require_grounding') and action.require_grounding and hasattr(action, 'call_grounding_model'):
                        self.logger.info(
                            LogMessage(
                                type="mixture_grounding",
                                message=f"{self.name} [yellow]refining coordinates[/yellow] for action: {action.type}", 
                            )
                        )

                        observation = self.env.get_observation()
                        # Temporarily disable this option because WAA does not currently support
                        # observation = self.env.get_observation(calibrate_env_before_observe=True)
                        for attempt in range(self.config.max_grounding_attempts):
                            try: 
                                action.call_grounding_model(
                                    grounding_expertise=self.mixture_grounding,
                                    observation=observation
                                )
                                break  # success, exit loop
                            except Exception as e:
                                if attempt < self.config.max_grounding_attempts - 1:
                                    # Optional: log and retry
                                    self.logger.info(
                                        LogMessage(
                                            type="mixture_grounding_failure",
                                            message=f"Grounding attempt {attempt+1}/{self.config.max_grounding_attempts} failed for action: {action.type}. Retrying...", 
                                        )
                                    )
                                else:
                                    # Last attempt – re-raise or handle as needed
                                    self.logger.info(
                                        LogMessage(
                                            type="mixture_grounding_failure",
                                            message=f"Grounding attempt {attempt+1}/{self.config.max_grounding_attempts} failed for action: {action.type}. No more retries left.", 
                                        )
                                    )
                                    raise e

                    self.execute(actions=[action])

                    if action is None:
                        break
        finally:
            self.logger.convert()

    def termination(self, task_status: Status, cancel_event, attempt_start_time) -> bool:
        if cancel_event is not None and cancel_event.is_set():
            task_status = Status.CANCELED
        if time.time() - attempt_start_time > self.config.max_wall_time:
            task_status = Status.TIMEOUT

        if task_status in [Status.SUCCESS, Status.FAILURE, Status.CANCELED, Status.TIMEOUT, Status.CALL_USER]:
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
                        type = "task_end_status",
                        message=f"{self.name} [green]finish[/green] the task.", 
                    )
                )
                task_status = Status.SUCCESS
                return task_status
            elif action.type == "fail":
                self.logger.info(
                    LogMessage(
                        type = "task_end_status",
                        message=f"{self.name} [red]fail[/red] the task.", 
                    )
                )
                task_status = Status.FAILURE
                return task_status
            elif action.type == "call_user":
                self.logger.info(
                    LogMessage(
                        type = "task_end_status",
                        message=f"{self.name} [blue]call_user[/blue] the task.", 
                    )
                )
                task_status = Status.CALL_USER
                return task_status
            elif action.type == "error_env":
                self.logger.info(
                    LogMessage(
                        type = "task_end_status",
                        message=f"{self.name} [red]error_env[/red] during the task.", 
                    )
                )
                task_status = Status.ENV_ERROR
                return task_status

            before_observation = self.env.get_observation()

            executable_action = action.get_gui_code()

            # optional - getting debug image
            warpped_text = Misc.wrap_text_lines(executable_action, 40)
            debug_before_image = Misc.get_commands_debug_image(before_observation["screenshot"], commands_debug_info=[], text=warpped_text)

            # actual action execution
            self.env.step(executable_action)

            # Wait for a short interval before the next action
            time.sleep(self.config.step_interval_time)
            
            after_observation = self.env.get_observation()

            self.logger.info(LogMessage(
                type = "before_after_observation_action",
                message = f"Before/After action observation and {action} executed",
                metadata={
                    "before_observation": before_observation,
                    "before_observation_debug": debug_before_image,
                    "after_observation": after_observation,
                    "action": str(action),
                    "executable_action": executable_action
                }
            ))
        return task_status

    def reset(self, wait_time:int = 1):
        self.logger.info(LogMessage(
            type="agent_reset",
            message=f"Performing Agent Reset",
        ))
        time.sleep(wait_time)