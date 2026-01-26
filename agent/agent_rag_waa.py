from mm_agents.agent_base import BaseAgent
from agent_settings import AgentSettings
from args_config import ArgsConfig
from .agent_rag import CUARAGAgent
import shutil
import os

class Agent_WAA(BaseAgent):
    def __init__(self, name: str, args: ArgsConfig):
        super().__init__(name, args)
        args.max_steps = 100
        args.observation_type = "screenshot"
        args.screen_width = 1920
        args.screen_height = 1080

        if args.agent_settings is not None and len(args.agent_settings) > 0:
            for key, value in args.agent_settings.items():
                os.environ[key] = str(value)
        self.agent = CUARAGAgent()

    def reset(self):
        """Reset the agent's state."""
        # Add logic to reset the agent's state if necessary
        self.agent.reset()

    def agent_type(self) -> str:
        """Return the type of the agent."""
        return "run" # or "prediction" based on your requirement

    def run(self, env, example, max_steps, instruction, example_result_dir, observation, **kwargs):
        """Predict the next action based on the instruction and observation."""
        print(f"Running agent {self.name} with instruction: {instruction}")
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "config_rag.json"),
            example_result_dir
        )
        self.agent.proceed(
            instruction=instruction,
            example=example,
            env=env,
            explicit_log_dir=example_result_dir
        )

    def requires_recorder(self) -> bool:
        """Determine if the agent requires a recorder. Subclasses can override this."""
        # The recorder may need to store some screenshot to the place when agent running.
        return False
