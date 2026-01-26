from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import requests
from .utils import pil_to_base64, LogMessage
from typing import List
from types import SimpleNamespace
import os
import re

class MixtureGrounding:
    def __init__(self, 
        config: SimpleNamespace = None,
        logger = None
        ):
        self.config = config
        self.logger = logger

    def force_reset_logger(self, logger):
        self.logger = logger


    def phi_v_grounding(self,
        action_description: str = None,
        screenshot = None,
        azure_endpoint: bool = True,
        azure_url: str = None
        ) -> List:
        refined_coordinates = None

        messages = [('action_description', ('action_description.txt', action_description, 'text/plain'))]
        screenshot = Image.open(BytesIO(screenshot)).convert("RGB")
        curr_screenshot_base64 = pil_to_base64(screenshot)
        messages.append(('screenshot', ('screenshot.png', curr_screenshot_base64, 'image/png')))

        if azure_endpoint:
            headers = {}
            # Load environment variables from .env file
            load_dotenv()
            if os.getenv("PHI_V_GROUNDING_BEARER_KEY") is not None:
                key = os.getenv("PHI_V_GROUNDING_BEARER_KEY")
                headers = {"Authorization": f"Bearer {key}"}

            self.logger.info(LogMessage(
                message=f"Sending request to Phi-V-Grounding Azure endpoint: {azure_url}"
            ))
            response = requests.post(azure_url, files=messages, headers=headers)

            refined_coordinates = response.json()["coordinates"][0]
            self.logger.info(LogMessage(
                message=f"Refined coordinate: {refined_coordinates}"
            ))
        return refined_coordinates

    def uitars_v1_grounding(self,
        action_description: str = None,
        screenshot = None,
        azure_endpoint: bool = True,
        endpoint_url: str = None,
        bearer_key_env_var: str = None
        ) -> List:
        refined_coordinates = None
        user_prompt = """You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task. \n\n## Output Format\n\nAction: ...\n\n\n## Action Space\nclick(start_box='<|box_start|>(x1,y1)<|box_end|>')\n\n## User Instruction\n{instruction}"""
        user_prompt = user_prompt.format(instruction=action_description)
        screenshot = Image.open(BytesIO(screenshot)).convert("RGB")
        curr_screenshot_base64 = pil_to_base64(screenshot)

        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": user_prompt}]
            },
            {
                "role": "user",
                "content": [{"type": "image", "image": curr_screenshot_base64}]
            }
        ]


        self.logger.info(LogMessage(
            type="mixture_grounding_prompt",
            message=f"User prompt for UITARS-V1-Grounding: {user_prompt}"
        ))

        if azure_endpoint:
            headers = {}
            # Load environment variables from .env file
            load_dotenv()
            key = None
            if os.getenv(bearer_key_env_var) is not None:
                key = os.getenv(bearer_key_env_var)
            headers = {"Authorization": f"Bearer {key}"}
            if key is None:
                raise ValueError(f"Bearer key not found in environment variable '{bearer_key_env_var}'. Need to set it before running the test.")
            self.logger.info(LogMessage(
                type="mixture_grounding_sending_request",
                message=f"Sending request to UITARS-V1-Grounding Azure endpoint: {endpoint_url}"
            ))
            response = requests.post(
                endpoint_url, 
                json=messages, 
                headers=headers
            )
        else:
            self.logger.info(LogMessage(
                type="mixture_grounding_sending_request",
                message=f"Sending request to UITARS-V1-Grounding local endpoint: {endpoint_url}"
            ))
            response = requests.post(
                endpoint_url, 
                json=messages, 
            )

        refined_action_str = response.json()["response"][0]
        match = re.search(r"start_box='\((\d+),(\d+)\)'", refined_action_str)

        refined_coordinates = [0, 0]
        if match:
            x, y = int(match.group(1)), int(match.group(2))

            refined_coordinates[0] = int(x) / 1000 * screenshot.width
            refined_coordinates[1] = int(y) / 1000 * screenshot.height

        self.logger.info(LogMessage(
            type="mixture_grounding_refined_coordinate",
            message=f"Refined coordinate: {refined_coordinates}"
        ))

        return refined_coordinates

    def predict(self,
        action_description: str = None,
        observation = None
        ) -> List:
        refined_coordinates = None
        for expert in self.config.expertises:
            if expert.model == "uitars_v1_grounding" and expert.weight > 0:
                refined_coordinates = self.uitars_v1_grounding(
                    action_description=action_description,
                    screenshot=observation["screenshot"],
                    azure_endpoint=expert.azure_endpoint,
                    endpoint_url=expert.endpoint_url,
                    bearer_key_env_var=expert.bearer_key_env_var
                )
                self.logger.info(LogMessage(
                    message=f"Refined coordinates from UITARS-V1-Grounding: {refined_coordinates}"
                ))
        return refined_coordinates


