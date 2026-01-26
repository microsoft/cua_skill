from io import BytesIO
import os
import base64
import sys
import logging  # Add this import

# Suppress debug logs from OpenAI and HTTP libraries
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("azure").setLevel(logging.WARNING)
from pathlib import Path

from .utils import Misc, SessionLogger, LogMessage, Status
from .retrieval import ActionRetriever

from .action.base_action import COMMON_EXECUTABLE_ACTIONS, _OP_REGISTRY
from .llms import model_loader
from PIL import Image






class Planner:
    def __init__(self, config):
        self.project_path = Path(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.llm = model_loader(config)
        self.config = config
        self.get_base_actions()

    def set_instruction(self, task):
        self.task = task
        self.action_history = []
        self.memory = []

    # def get_planner_prompt(self):
    #     prompt = """You are a computer use agent. Your goal is to help the user complete their task.

    #     ## Task Information
    #     **Task Description:** {TASK_DESCRIPTION}
    #     **Actions Taken:** {STEPS_TAKEN}
    #     **Current Observation:** {OBSERVATION}

    #     ## Instructions
    #     Based on the task description, actions already taken, and the current screen, determine the most appropriate next action to complete the task. Summarize this action with a brief, intention-focused title.
        
    #     If multiple steps are required to complete the action, provide only the next immediate action based on the current screen. The output title must be short and concise. If all steps are completed, respond with "DONE" for thoughts, action, and title.

    #     ## Output Format
    #     Provide your response in the following JSON format:
    #     {
    #     "Thoughts": "<Your reasoning for the next action>",
    #     "Action": "<The specific action to take>",
    #     "Title": "<A concise title describing the action's intention>"
    #     }
    #     """
    #     prompt = prompt.replace("{TASK_DESCRIPTION}", self.task)
    #     prompt = prompt.replace(
    #         "{STEPS_TAKEN}",
    #         "\n".join([f"- {step}" for step in self.memory]) if self.memory else "None",
    #     )

    #     return prompt

    def get_query_prompt(self):
        prompt = """You are a computer use agent assistant. Your goal is to generate search queries to retrieve the most appropriate next action from a pre-recorded action library to help the user complete their task.

        ## Task Information
        **Task Description:** {TASK_DESCRIPTION}
        **Steps Taken:** {STEPS_TAKEN}
        **Current Observation:** [Current screen is provided]

        ## Instructions
        Analyze the task, previous steps, and current screen to generate 3-5 diverse search queries that would help retrieve the next appropriate action from the action library.

        Consider:
        - Various levels of specificity or granularities (e.g., "click submit button" vs "submit form")
        - Alternative approaches to achieve the next step
        - Common UI interaction patterns
        - Use natural language queries, do not use infer action names from the actions taken.
        - Given the task description and steps taken and the current screen, evaluate if the task is already completed. If the task is COMPLETED, simply respond with {"Query": "DONE"}.
        

        ## Output Format
        Return your response as valid JSON:
        {
        "Query1": "<Simple description for the next action>",
        "Query2": "<Alternative phrasing of the next action>",
        "Query3": "<Alternative phrasing for the next action at a different granularity>",
        }
        """
        prompt = prompt.replace("{TASK_DESCRIPTION}", self.task)
        prompt = prompt.replace(
            "{STEPS_TAKEN}",
            "\n".join([f"- {step}" for step in self.memory]) if self.memory else "None",
        )

        return prompt

    def get_action_config_prompt(self, action, step_description):
        action_name = action.type
        arguments = action.arguments
        arg_prompts = []
        template_prompts = []
        for arg_name in arguments:
            action_arg = getattr(action, arg_name)
            description = action_arg.description
            arg_prompt = f"{arg_name}: {description}"
            template_prompt = f'"{arg_name}": "<value>"'
            template_prompts.append(template_prompt)
            arg_prompts.append(arg_prompt)
        arg_prompt_str = "\n".join(arg_prompts)
        template_prompt_str = ",\n    ".join(template_prompts)

        prompt = """You are a computer use agent. Your goal is to help the user complete their task by configuring and executing pre-recorded actions.

        ## Current Context
        - **Main Task:** {TASK_DESCRIPTION}
        - **Previous Steps:** {STEPS_TAKEN}
        - **Current Screen:** [User's current screen is provided]
        - **Current Action Description:** {STEP_DESCRIPTION}

        ## Action to Configure
        **Action Name:** {ACTION_NAME}

        ## Required Parameters
        Please provide values for the following parameters for this action based on the current screen and step requirements:

        {ARG_PROMPTS}

        ## Instructions
        1. Analyze the current screen, task requirements and current action description
        2. Determine appropriate values for each parameter
        3. The parameter name must match exactly as provided

        ## Output Format
        Return your response as valid JSON with parameter names as keys:
        {{
        {TEMPLATE_PROMPTS}
        }}
        """
        prompt = prompt.replace("{TASK_DESCRIPTION}", self.task)
        prompt = prompt.replace(
            "{STEPS_TAKEN}",
            "\n".join([f"- {step}" for step in self.memory]) if self.memory else "None",
        )
        prompt = prompt.replace("{STEP_DESCRIPTION}", step_description)
        prompt = prompt.replace("{ACTION_NAME}", action_name)
        prompt = prompt.replace("{ARG_PROMPTS}", arg_prompt_str)
        prompt = prompt.replace("{TEMPLATE_PROMPTS}", template_prompt_str)
        return prompt

    def get_base_actions(self):
        action_str_ls = []
        action_ls = []
        for action_name in COMMON_EXECUTABLE_ACTIONS:
            action = _OP_REGISTRY.get(action_name)
            action_name = action.type
            arguments = list(action().arguments.keys())
            if hasattr(action, "descriptions") and action.descriptions:
                action_descriptions = action.descriptions[0]
                action_str = f"- {action_name}({', '.join(arguments)}): this is the action that {action_descriptions}"
            else:
                action_str = f"- {action_name}({', '.join(arguments)})"
            action_str_ls.append(action_str)
            action_ls.append(action)
        self.base_action_str_full = "\n".join(action_str_ls)
        self.base_action_ls = action_ls

    def get_action_selection_prompt(self, candidate_actions, query):
        action_str_ls = []
        for action in candidate_actions:
            action_name = action.type
            arguments = list(action().arguments.keys())
            if hasattr(action, "descriptions") and action.descriptions:
                action_descriptions = action.descriptions[0]
                action_str = f"- {action_name}({', '.join(arguments)}): this is the action that {action_descriptions}"
            else:
                action_str = f"- {action_name}({', '.join(arguments)})"
            action_str_ls.append(action_str)
        action_str_full = "\n".join(action_str_ls)
        prompt = """You are a computer use agent. Your goal is to help the user complete their task by selecting the most appropriate action from the available options.

        ## Current Context
        - **Main Objective:** {TASK_DESCRIPTION}
        - **Progress So Far:** {STEPS_TAKEN}
        - **Proposed Next Step:** {NEXT_STEP_DESCRIPTION}
        - **Current Screen:** [User's current screen is provided]

        
        ## Primary Actions
        {ACTION_LIST}

        
        ## Additional Base Actions
        {ADDITIONAL_ACTIONS}

        
        ## Instructions
        1. Analyze the current screen, previous steps taken, and task requirements
        2. Review the list of actions available. There can be some actions that provide more end-to-end progress toward completing the task. In this case, we should reconsider the proposed next step and select the action that best aligns with completing the overall task.
        3. If none of the action from primary actions can help with the task. Please consider the Additional Base Actions. However, using the Additional Base Actions should be a last resort.


        ## Output Format
        Return your response as valid JSON:
        {{
            "selected_action": "<action_name>",
            "action_goal": "<brief description of what this action is doing>",
            "action_category_index": "<index of the action category>, 0 is for Primary Action, 1 is for Additional Base Action",
            "action_index": "<index of the selected action in the corresponding action list, start from 0>"
        }}
        """

        prompt = prompt.replace("{TASK_DESCRIPTION}", self.task)
        prompt = prompt.replace("{NEXT_STEP_DESCRIPTION}", query)
        prompt = prompt.replace("{ACTION_LIST}", action_str_full)
        prompt = prompt.replace(
            "{STEPS_TAKEN}",
            (
                "\n".join(
                    [f"Step {idx}: {step}" for idx, step in enumerate(self.memory)]
                )
                if self.memory
                else "None"
            ),
        )
        prompt = prompt.replace("{ADDITIONAL_ACTIONS}", self.base_action_str_full)
        return prompt


    def get_action_selection_prompt_base_action_only(self, query):

        prompt = """You are a computer use agent. Your goal is to help the user complete their task by selecting the most appropriate action from the available options.

        ## Current Context
        - **Main Objective:** {TASK_DESCRIPTION}
        - **Progress So Far:** {STEPS_TAKEN}
        - **Proposed Next Step:** {NEXT_STEP_DESCRIPTION}
        - **Current Screen:** [User's current screen is provided]

        ## Base Actions
        {ADDITIONAL_ACTIONS}
        
        ## Instructions
        1. Analyze the current screen, previous steps taken, and task requirements
        2. Review the list of actions available. There can be some actions that provide more end-to-end progress toward completing the task. In this case, we should reconsider the proposed next step and select the action that best aligns with completing the overall task.


        ## Output Format
        Return your response as valid JSON:
        {{
            "selected_action": "<action_name>",
            "action_goal": "<brief description of what this action is doing>",
            "action_index": "<index of the selected action in the corresponding action list, start from 0, max index is {COMMON_EXECUTABLE_ACTIONS_LEN}>"
        }}
        """

        prompt = prompt.replace("{TASK_DESCRIPTION}", self.task)
        prompt = prompt.replace("{NEXT_STEP_DESCRIPTION}", query)
        prompt = prompt.replace("{COMMON_EXECUTABLE_ACTIONS_LEN}", str(len(COMMON_EXECUTABLE_ACTIONS) - 1))
        prompt = prompt.replace(
            "{STEPS_TAKEN}",
            (
                "\n".join(
                    [f"Step {idx}: {step}" for idx, step in enumerate(self.memory)]
                )
                if self.memory
                else "None"
            ),
        )
        prompt = prompt.replace("{ADDITIONAL_ACTIONS}", self.base_action_str_full)
        return prompt



    def get_memory_prompt(self, action):
        prompt = """You are a computer use agent tasked with documenting the result of an executed action.

        ## Action Information
        **Action Executed:** {ACTION}
        
        ## Current Screen
        The attached screenshot shows the state after the action was executed.
        
        ## Instructions
        Analyze the screenshot to determine the outcome of the action and create a concise memory entry:
        
        1. **Identify the outcome:** Determine whether the action succeeded or failed based on the visual evidence
        2. **Document the result:**
           - If successful: "Executed [action description] and the action is successful as [observed outcome]"
           - If failed: "Attempted [action description] expecting [intended outcome] but this action failed as [actual outcome/error]"
           - If uncertain: "Executed [action description]"

        ## Output Format
        Provide a single, clear sentence describing the action and its result. Output the sentence directly without any additional formatting or JSON structure.
        """
        prompt = prompt.replace("{ACTION}", action)
        return prompt
    
    def get_screen_understanding_prompt(self):
        prompt = """You are a computer-use agent analyzing the current screen.
        ## Main Task
        **Description:** {TASK_DESCRIPTION}

        ## Action Information
        **Previous Steps:** {STEPS_TAKEN}

        ## Current Screen
        A screenshot of the current screen is attached.

        ## Instructions
        Your next goal is to extract useful information from the screen that will help advance the main task. Consider previous steps and the overall objective. Analyze the screenshot carefully and identify any relevant details that support task completion.

        ## Output Format
        Return only the information you find relevant to the task. Do not include extra formatting or JSON.
        """
        prompt = prompt.replace("{TASK_DESCRIPTION}", self.task)
        prompt = prompt.replace(
            "{STEPS_TAKEN}",
            "\n".join([f"- {step}" for step in self.memory]) if self.memory else "None",
        )
        return prompt
    
    def get_feasibility_prompt(self):
        prompt = """You are a computer-use agent responsible for validating task feasibility.

        ## Task Information
        **Objective:** {TASK_DESCRIPTION}
        **Current Context:** A screenshot of the current screen is provided. A total of 5 images are provided. The first image shows the full screen view, while the next four images are zoomed-in sections of the screen.

        ## Instructions
        Evaluate whether the task can be completed given the current screen state.

        Consider the task **infeasible** if:
        1. **Mismatch with Screen:** The current screen does not match the task instruction. For example, the task mentions a file or an application is currently opened or running but the screenshot shows otherwise.
        2. **Technical Impossibility:** The required functionality or feature is not supported by the current system or application.
        Consider the task is still **feasible** if:
        The current screen does not contradict the task instruction, more steps may required to check the feasibility. For example, search for the file to see if it exists.
        
        ## Output Format
        - If the task is feasible, respond "True"
        - If the task is infeasible, respond "False"
        Then output your reasoning steps make it within one sentence.
        """
        prompt = prompt.replace("{TASK_DESCRIPTION}", self.task)
        return prompt
    
    def get_initial_state_observation_prompt(self):
        prompt = """You are a computer-use agent tasked with analyzing the initial screen state before starting task execution.

        ## Main Task
        **Description:** {TASK_DESCRIPTION}

        ## Current Screen
        A total of 5 images are provided. The first image shows the full screen view, while the next four images are zoomed-in sections of the screen.

        ## Instructions
        Examine the current screen and provide insights on:

        1. **Task-Relevant Elements:** Identify any UI elements, text, or visual indicators related to the main task. Focus on the text elements that may provide context or clues.
        2. **Readiness Assessment:** Determine if the environment is properly set up to begin the task
        - Are required applications open and accessible?
        - Are there any blockers or unexpected conditions present?


        ## Output Format
        Provide a concise summary (at most 2 sentences) describing:
        - What you observe on the screen
        - The current system readiness for the task,  
        - If not ready, any immediate actions needed before proceeding with the main task
        Return the summary directly without additional formatting.
        """
        prompt = prompt.replace("{TASK_DESCRIPTION}", self.task)
        return prompt

    def get_initial_state_observation_images(self, screenshot):
        if isinstance(screenshot, (bytes, bytearray)):
            screenshot = Image.open(BytesIO(screenshot)).convert("RGB")
        width, height = screenshot.size
        half_width = width // 2
        half_height = height // 2

        patches = [
            (0, 0, half_width, half_height),  # Top-left
            (half_width, 0, width, half_height),  # Top-right
            (0, half_height, half_width, height),  # Bottom-left
            (half_width, half_height, width, height)  # Bottom-right
        ]
        res = [screenshot] + [screenshot.crop(coords) for coords in patches]
        buf = BytesIO()
        base64_images = []
        for img in res:
            img.save(buf, format="PNG") 
            img_bytes = buf.getvalue()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            base64_images.append(img_b64)
        return base64_images

    # def get_code_solution_prompt(self, file_path):
    #     prompt = """You are a computer-use agent tasked with generating Python code to complete the user's task.

    #     ## Main Task
    #     **Description:** {TASK_DESCRIPTION}

    #     ## Current Screen
    #     A screenshot of the current screen is attached.

    #     ## Instructions
    #     Generate Python code to complete the task based on the current screen state.

    #     ### Requirements:
    #     1. Use pywin32 library for Windows automation
    #     2. Do not attempt to attach the window or application that is currently open, use the file path {FILE_PATH} to locate the file to edit
    #     3. the current application object visible on screen is used as a reference to understand the file structure and content.
    #     4. Include all necessary error handling for robust execution
    #     5. Ensure the code is complete and executable without modifications

    #     ### Important Notes:
    #     - The relevant application is already open and visible on screen
    #     - Extract all necessary information (window titles, control names, etc.) from the screenshot
    #     - Do not use placeholders or incomplete code segments
    #     - The code should be self-contained and ready to run

    #     ## Output Format
    #     Return only the Python code wrapped in ```python ... ``` blocks.
    #     Do not include explanations, comments outside the code block, or multiple code blocks.
    #     The code must be complete and directly executable.
    #     """
    #     prompt = prompt.replace("{TASK_DESCRIPTION}", self.task)
    #     prompt = prompt.replace("{FILE_PATH}", file_path)
    #     return prompt

    
    def get_code_solution_prompt(self, file_path):
        prompt = """You are a computer-use agent tasked with generating Python code to complete the user's task.

        ## Main Task
        **Description:** {TASK_DESCRIPTION}

        ## Current Screen
        A screenshot of the current screen is attached.

        ## Instructions
        Generate Python code to complete the task based on the current screen state.

        ### Requirements:
        1. Use pywin32 library for Windows automation
        2. Work with the existing application window shown on screen - do NOT create new instances
        3. Fetch and interact with the current application object visible on screen
        4. Include all necessary error handling for robust execution, make sure to print out all exceptions or errors
        5. Ensure the code is complete and executable without modifications
        6. Ensure to save the file after making changes

        ### Important Notes:
        - The relevant application is already open and visible on screen
        - Extract all necessary information (window titles, control names, etc.) from the screenshot
        - Do not use placeholders or incomplete code segments
        - The code should be self-contained and ready to run

        ## Output Format
        Return only the Python code wrapped in ```python ... ``` blocks.
        Do not include explanations, comments outside the code block, or multiple code blocks.
        The code must be complete and directly executable.
        """
        prompt = prompt.replace("{TASK_DESCRIPTION}", self.task)
        return prompt
    
class RAGPlanner(Planner):
    def __init__(self, config, logger=None):
        super().__init__(config)
        if logger is None:
            self.logger = SessionLogger(config=self.config.logger)
        else:
            self.logger = logger
        
        if "0percent" in self.config.rag.rel_action_sample_path:
            self.rag = None
        else:
            self.rag = ActionRetriever(
            index_dir=self.project_path / self.config.rag.rel_index_dir,
            model_name=self.config.rag.model_name,
            semantic_weight=self.config.rag.semantic_weight,
            logger=self.logger,
            overwrite=False,
            sample_action_path=self.config.rag.rel_action_sample_path
        )


    def force_reset_logger(self, logger):
        self.logger = logger
        if self.rag is not None:
            self.rag.force_reset_logger(logger)
        else:
            self.logger.info(
                LogMessage(
                    type="RAGPlanner.force_reset_logger",
                    message=f"self.config.rag.rel_action_sample_path={self.config.rag.rel_action_sample_path} contains '0percent', no skills are used, RAG is disabled.",
                )
            )

    def get_code_solution(self, screenshot, file_path):
        prompt = self.get_code_solution_prompt(file_path)
        messages = self.llm.create_text_image_message(text=prompt, image=screenshot)
        response = self.llm.get_completion([messages])
        self.logger.info(
            LogMessage(
                type="RAGPlanner.get_code_solution",
                message=f"code_solution_response={response}",
            )
        )
        if response.startswith("```python"):
            code_start = response.find("```python") + len("```python")
            code_end = response.rfind("```")
            code = response[code_start:code_end].strip()
        elif response.startswith("```"):
            code_start = response.find("```") + len("```")
            code_end = response.rfind("```")
            code = response[code_start:code_end].strip()
        else:
            code = response.strip()
        self.logger.info(
            LogMessage(
                type="RAGPlanner.get_code_solution",
                message=f"extracted_code_solution={code}",
            )
        )
        return code

    def get_next_step_queries(self, screenshot):
        max_retries = 3
        prompt = self.get_query_prompt()
        messages = self.llm.create_text_image_message(text=prompt, image=screenshot)
        for attempt in range(max_retries):
            queries = self.llm.get_completion([messages])
            try:
                if "DONE" in str(queries):
                    self.logger.info(
                        LogMessage(
                            type="RAGPlanner.get_next_step_queries",
                            message="TASK COMPLETED",
                        )
                    )
                    return None
                queries = self.parse_query_generation(queries)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(
                        LogMessage(
                            type="RAGPlanner.get_next_step_queries",
                            message=f"Failed to parse query generation (attempt {attempt + 1}/{max_retries}): {e}",
                        )
                    )
                    continue
                else:
                    self.logger.error(
                        LogMessage(
                            type="RAGPlanner.get_next_step_queries",
                            message=f"Failed to parse query generation after {max_retries} attempts: {e}",
                        )
                    )
                    raise
        return queries


    def parse_action_config(self, response):
        self.logger.info(
            LogMessage(
                type="RAGPlanner.parse_action_config",
                message=f"llm_action_config_response={response}",
            )
        )
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        response = response.replace("true", "True").replace("false", "False")
        response = response.strip()
        out_dict = eval(response)
        out_dict = {k: str(v) for k, v in out_dict.items()}
        self.logger.info(
            LogMessage(
                type="RAGPlanner.parse_action_config",
                message=f"parsed_action_config={out_dict}",
            )
        )
        return out_dict

    def parse_query_generation(self, response):
        self.logger.info(
            LogMessage(
                type="RAGPlanner.parse_query_generation",
                message=f"llm_query_generation_response={response}",
            )
        )
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        response = response.replace("true", "True").replace("false", "False")
        response = response.strip()
        out_dict = eval(response)
        query_list = list(out_dict.values())
        self.logger.info(
            LogMessage(
                type="RAGPlanner.parse_query_generation",
                message=f"parsed_query_generation={query_list}",
            )
        )
        return query_list

    def parse_action_selection(self, response):
        self.logger.info(
            LogMessage(
                type="RAGPlanner.parse_action_selection",
                message=f"llm_action_selection_response={response}",
            )
        )
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        response = response.replace("true", "True").replace("false", "False")
        response = response.strip()
        out_dict = eval(response)
        action_idx = int(out_dict["action_index"])
        if self.rag:
            action_cat_idx = int(out_dict["action_category_index"])
        else:
            action_cat_idx = 1  # from Additional Base Actions
        action_description = out_dict["action_goal"]
        self.logger.info(
            LogMessage(
                type="RAGPlanner.parse_action_selection",
                message=f"parsed_action_selection={out_dict}, selected_index={action_idx}, selected_category_index={action_cat_idx}",
            )
        )

        return action_idx, action_cat_idx, action_description

    def select_next_step(self, candidate_actions, screenshot, query):
        if len(candidate_actions) == 0:
            prompt = self.get_action_selection_prompt_base_action_only(query)
        else:
            prompt = self.get_action_selection_prompt(candidate_actions, query)
        messages = self.llm.create_text_image_message(text=prompt, image=screenshot)
        max_retries = 3
        for attempt in range(max_retries):
            response = self.llm.get_completion([messages])
            try:
                selected_idx, action_cat_idx, action_description = (
                    self.parse_action_selection(response)
                )
                if action_cat_idx:  # from Additional Base Actions
                    action = self.base_action_ls[selected_idx]
                else:
                    action = candidate_actions[selected_idx]

                return action, action_description, action_cat_idx
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(
                        LogMessage(
                            type="RAGPlanner.select_next_step",
                            message=f"Failed to parse action selection (attempt {attempt + 1}/{max_retries}): {e}",
                        )
                    )
                    continue
                else:
                    self.logger.error(
                        LogMessage(
                            type="RAGPlanner.select_next_step",
                            message=f"Failed to parse action selection after {max_retries} attempts: {e}",
                        )
                    )
                    raise

    # def retrieve_next_step(self, screenshot):

    #     query = self.get_next_step_description(screenshot)
    #     candidate_actions = self.rag.retrieve_actions(query, top_k=10)
    #     action = self.select_next_step(candidate_actions, screenshot, query)
    #     self.logger.info(f"RAGPlanner.retrieve_next_step: next_step={action}")
    #     return action

    def build_memory(self, screenshot):
        if self.action_history:
            last_action = self.action_history[-1]
            prompt = self.get_memory_prompt(last_action)
            messages = self.llm.create_text_image_message(text=prompt, image=screenshot)
            response = self.llm.get_completion([messages])
            self.logger.info(
                LogMessage(
                    type="RAGPlanner.build_memory",
                    message=f"memory_entry={response}",
                )
            )
            self.memory.append(response)
        else:
            prompt = self.get_initial_state_observation_prompt()
            images = self.get_initial_state_observation_images(screenshot)
            messages = self.llm.create_text_image_message(text=prompt, image=images)
            response = self.llm.get_completion([messages])
            self.logger.info(
                LogMessage(
                    type="RAGPlanner.build_memory",
                    message=f"initial_observation_memory_entry={response}",
                )
            )
            self.memory.append(response)

    def predict_task_feasibility(self, screenshot):
        prompt = self.get_feasibility_prompt()
        images = self.get_initial_state_observation_images(screenshot)

        messages = self.llm.create_text_image_message(text=prompt, image=images)
        response = self.llm.get_completion([messages])
        self.logger.info(
            LogMessage(
                type="RAGPlanner.predict_task_feasibility",
                message=f"feasibility_response={response}",
            )
        )
        if "true" in response.lower():
            return True
        return False

    def retrieve_next_step(self, screenshot):
        self.build_memory(screenshot)
        queries = self.get_next_step_queries(screenshot)
        if queries is None:
            return None, None, None
        candidate_actions_set = set()
        if self.rag is None:
            candidate_actions = []
        else:
            for query in queries:
                candidate_actions = self.rag.retrieve_actions(query, top_k=4)
                candidate_actions_set.update(candidate_actions)
                candidate_actions = list(candidate_actions_set)
        queries_str = "; ".join(queries)
        action, step_description, is_base_action = self.select_next_step(
            candidate_actions, screenshot, queries_str
        )
        self.action_history.append(step_description)
        return action, step_description, is_base_action

    def execute_screen_understanding(self, screenshot):
        prompt = self.get_screen_understanding_prompt()
        messages = self.llm.create_text_image_message(text=prompt, image=screenshot)
        response = self.llm.get_completion([messages])
        self.logger.info(
            LogMessage(
                type="RAGPlanner.execute_screen_understanding",
                message=f"screen_understanding_output={response}",
            )
        )
        screen_info = f"Screen Understanding is executed. Here is the extracted information from the screen: {response}"
        self.memory.append(screen_info)


    def config_next_step(self, action_class, screenshot, step_description):
        # the input action is a class, need to instantiate with the configured arguments
        uninit_action = action_class()
        if uninit_action.type == "screen_understanding":
            self.execute_screen_understanding(screenshot)
            return uninit_action
        action_arguments = uninit_action.arguments
        if not action_arguments:
            return uninit_action
        else:
            param_count = 0  # if all parameters are frozen, skip configuration
            for arg_name in action_arguments:
                action_arg = getattr(uninit_action, arg_name)
                param_count += 1 - action_arg._frozen
            if param_count == 0:
                return uninit_action

        prompt = self.get_action_config_prompt(uninit_action, step_description)
        messages = self.llm.create_text_image_message(text=prompt, image=screenshot)
        max_retries = 3
        for attempt in range(max_retries):
            response = self.llm.get_completion([messages])
            action_config = self.parse_action_config(response)
            invalid_keys = [
                k for k in action_config.keys() if not hasattr(uninit_action, k)
            ]
            if not invalid_keys:
                out_action = action_class(**action_config)
            else:
                if attempt < max_retries - 1:
                    self.logger.warning(
                        LogMessage(
                            type="RAGPlanner.config_next_step",
                            message=f"Invalid attributes {invalid_keys} for action {uninit_action.type}. Retrying... (attempt {attempt + 1}/{max_retries})",
                        )
                    )
                else:
                    raise ValueError(
                        f"Invalid attributes {invalid_keys} for action {uninit_action.type} after {max_retries} attempts."
                    )

        self.logger.info(
            LogMessage(
                type="RAGPlanner.config_next_step",
                message=f"configured_action={out_action}",
            )
        )

        return out_action


if __name__ == "__main__":  # python -m agent.planner

    from agent.utils._misc import Misc

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

    # Easy to paste Windows paths - just replace the path string
    # image_path = r"C:\Users\yinhengli\Desktop\projects\cua_knowledge_graph\test\logs\2025-10-13_13-19-08\000001-before_after_observation_action_system.png"
    image_path = (
        r"C:\Users\yinhengli\Pictures\Screenshots\Screenshot 2025-10-22 230905.png"
    )
    config_path = (
        r"C:\Users\yinhengli\Desktop\projects\cua_knowledge_graph\agent\config_rag.json"
    )

    # Convert to Path objects
    image_path = str(Path(image_path))
    config_path = str(Path(config_path))
    config = Misc.file_to_namespace(config_path)
    task = "calcuate 123 + 311 in calculator and get the result"
    planner = RAGPlanner(config)
    planner.set_instruction(task)
    action, step_description, is_base_action = planner.retrieve_next_step(image_path)  # Convert to string
    print(action, step_description, is_base_action)
