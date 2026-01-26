
from openai import omit, AuthenticationError
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pathlib import Path
import os
import base64
import time
from transformers import AutoModelForImageTextToText, AutoProcessor



def model_loader(config):
    if config.planner.model_class == "gpt":
        return GPT(config)
    if config.planner.model_class == "qwen":
        return Qwen(config)
    raise NotImplementedError("the selected model class is not implemented")


class GPT:
    def __init__(self, config):
        self.config = config
        self.deployment = self.config.planner.expertises.gpt.deployment
        if "gpt-5" in self.deployment:
            self.reasoning_effort = self.deployment.split("-")[-1]
            self.deployment = self.deployment.strip("-" + self.reasoning_effort)
            assert self.reasoning_effort in [
                "minimal",
                "low",
                "medium",
                "high",
            ], "reasoning_effort must be one of [minimal"
            ", low, medium, high] for gpt-5 models"
        else:
            self.reasoning_effort = omit
        self.setup_client()

        self.boolean_response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "boolean_answer",
            "schema": {
                "type": "object",
                "properties": {
                    "answer": {"type": "boolean"}
                },
                "required": ["answer"],
                "additionalProperties": False
            }
        }
    }

    def setup_client(self):
        load_dotenv(override=True)
        self.endpoint = self.config.planner.expertises.gpt.endpoint
        self.api_version = self.config.planner.expertises.gpt.api_version
        self.azure_ad_token = os.getenv("AZURE_AD_TOKEN")

        if self.azure_ad_token is None or self.azure_ad_token == "":
            credential = DefaultAzureCredential()
            token_scope = self.config.planner.expertises.gpt.token_scope
            token_provider = get_bearer_token_provider(credential, token_scope)
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_version=self.api_version,
                azure_deployment=self.deployment,
                azure_ad_token_provider=token_provider,
            )
        else:
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                azure_ad_token=self.azure_ad_token,
                api_version=self.api_version,
            )

    def handel_image_input(self, image):
        if isinstance(image, str) and os.path.isfile(image):
            with open(image, "rb") as img_file:
                b64_image = base64.b64encode(img_file.read()).decode("utf-8")
        else:
            if isinstance(image, bytes):
                b64_image = base64.b64encode(image).decode("utf-8")
            else:
                b64_image = image
        return b64_image

    def create_text_image_message(self, text, image):
        # image can be a single image or a list of images
        content = [{"type": "text", "text": text}]
        if isinstance(image, list):
            for img in image:
                b64_image = self.handel_image_input(img)
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    }
                )
        else:
            b64_image = self.handel_image_input(image)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                }
            )

        template = {
            "role": "user",
            "content": content
        }
        return template

    def send_token_refresh_request(self):
        file_path = Path(__file__).parent / "new_token_request.txt"
        data = 1
        with open(file_path, "w") as f:
            f.write(str(data))
        time.sleep(10)
        print("refreshing token, waiting for 10 seconds...")
            
    def create_text_message(self, text):
        return {"role": "user", "content": text}
    
    def _get_completion(self, messages, isboolean):
        if self.deployment == "gpt-5":
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_completion_tokens=4096,
                reasoning_effort=self.reasoning_effort,
                response_format=self.boolean_response_format if isboolean else omit,
            )
        else:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_completion_tokens=4096,
                temperature=0.7,
                top_p=0.95,
                response_format=self.boolean_response_format if isboolean else omit,
            )
        return response.choices[0].message.content

    def get_completion(self, messages, isboolean=False):
        try:
            return self._get_completion(messages, isboolean)
        except AuthenticationError:
            self.send_token_refresh_request()
            self.setup_client()
            return self._get_completion(messages, isboolean)

    def get_completion_with_kwargs(self, messages, **kwargs):
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content


class Qwen:

    def __init__(self, config):
        self.config = config
        self.model_path = self.config.planner.expertises.qwen.model_path
        self.processor = AutoProcessor.from_pretrained(self.model_path)
        self.model = AutoModelForImageTextToText.from_pretrained(self.model_path, device_map="auto", torch_dtype="auto")


    def create_text_image_message(self, text, image):
        if isinstance(image, str) and os.path.isfile(image):
            with open(image, "rb") as img_file:
                b64_image = base64.b64encode(img_file.read()).decode("utf-8")
        else:
            if isinstance(image, bytes):
                b64_image = base64.b64encode(image).decode("utf-8")
            else:
                b64_image = image
        template = {
            "role": "user",
            "content": [
                {"type": "text", "text": text},
                {
                    "type": "image",
                    "image": f"data:image/jpeg;base64,{b64_image}"}
                
            ],
        }
        return template
    
    def create_text_message(self, text):
        return {"role": "user", "content": {"type": "text", "text": text}}

    def get_completion(self, messages):
        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt"
        )
        inputs = inputs.to(self.model.device)

        # Inference: Generation of the output
        generated_ids = self.model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        return output_text[0]
    

if __name__ == "__main__":
    image_path = "/home/yinhengli/projects/cua_knowledge_graph/WindowsAgentArena/img/local_prepare_screen_setup.png"
    text = "Describe the image in detail."
    from box import Box
    gpt_config = {
        "planner": {
            "model_class": "gpt",
            "expertises": {
                "deployment": "gpt-4o",
                "azure_endpoint": True,
                "api_version": "2025-01-01-preview",
                "endpoint": "https://asgoai-eastus2.openai.azure.com"
            }
        }
    }
    qwen_config = {
        "planner": {
            "model_class": "qwen",
            "model_path": "Qwen/Qwen3-VL-32B-Instruct"
        }
    }
    # gpt_model = model_loader(Box(gpt_config))
    # gpt_message = gpt_model.create_text_image_message(text, image_path)
    # gpt_response = gpt_model.get_completion([gpt_message])
    qwen_model = model_loader(Box(qwen_config))
    qwen_message = qwen_model.create_text_image_message(text, image_path)
    qwen_response = qwen_model.get_completion([qwen_message])
    # print("GPT Response: ", gpt_response)
    print("Qwen Response: ", qwen_response)