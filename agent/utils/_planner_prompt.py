import json
from typing import List


def generate_commander_prompt(
    intent: str,
    description: str,  # Screenshot description
    recent_actions_task_taken: str,  # Task + actions under it from previous plan
    current_task: str  # First task in next plan
) -> str:
    prompt = f"""
You are a short-term planner. Your task is to assist an agent by analyzing its short-term memory and determining the most appropriate **next actions**.

You are provided with a Windows environment screenshot and the following short-term memory:

- **Current Context**: Inferred from the user's intent and the screenshot description.
- **Recent Actions Taken**: The most recent task and all actions under this task that have been already taken".
- **Current Task**: This is the next task the agent must complete, and your goal is to generate a list of actions to accomplish it.

Then, based on the short-term memory and current screenshot, generate the most logical **Next Best Action** the agent should take.

Note: You should only choose actions from the following list to describe what needs to be done next:
[CLICK, TYPE, SCROLL, DRAG, WAIT, MOVE, SCREENSHOT, MOVE_ABS, SINGLE_CLICK, DOUBLE_CLICK, RIGHT_CLICK, COPY_TEXT, PASTE, OPEN_PROGRAM, SWITCH_WINDOW, PRESS_KEY]

---

**Intent**: {intent}  
**Screenshot Description**: {description}

**Recent Actions and Task Taken**:  
{recent_actions_task_taken or 'No recent actions found.'}

**Current Task**:  
{current_task or 'No task available.'}

---

Respond in this format:

Current Context: [Brief reasoning based on intent and interface state]  
Current Task: {current_task}  
Next Action(s): [Your recommended next step(s)]
"""
    return prompt.strip()


def generate_marshal_prompt(
    intent: str,
    description: str,
    previous_plan: str
) -> str:

    if not previous_plan:
        prompt = f"""
    You are a long-term planner. Your task is to assist an agent by analyzing its long-term memory and generating both a high-level plan and a contextual description based on a screenshot of a Windows environment.

    You are provided with:
    - **Intent**: A short summary of the user's goal, based on the current state of the screenshot.
    - **Prior Knowledge (Screenshot Description)**: A detailed description of the screenshot, including visible applications, layout, interface elements (e.g., buttons, forms, menus), and active/inactive windows or tabs.

    ---

    Your task:
    - **Next Plan**: Create a new, high-level plan with clearly defined, actionable steps that help the agent achieve its goal.

    If the screenshot description is missing, infer the context using common UI patterns and visual cues. You may assume the presence of typical elements such as modal dialogs, browser windows, desktop apps, or navigation components.

    **Intent**: {intent}

    Respond in the following format:

    ---

    Next Plan:
    - Task 1: [First step toward achieving the goal]
    - Task 2: ...
    - Task 3: ...

    Prior Knowledge (Screenshot Description): <A detailed description of the screenshot>
    ---
    """
    else:
        prompt = f"""
    You are an intelligent long-term planner. Your task is to assist an agent by analyzing its long-term memory and the current screenshot context, and then generating a refined plan.

    You are provided with:
    - **Intent**: {intent}
    - **Previous Plan**: {previous_plan}
    - **Prior Knowledge (Screenshot Description)**: {description if description else '[Missing] Please infer based on common UI patterns and state transitions.'}
    ---

    Your task:
    - **Updated Plan**: Since a previous plan exists, review and refine it. Identify tasks that may need correction or adjustment based on progress, visual state, or missed steps. Include reasoning when recommending changes or improvements.

    Respond in the following format:

    ---

    Updated Plan:
    - Task 1:
    - Action 1: ...
    - Action 2: ... (consider modifying if [reason])
    - Task 2:
    - Action 1: ... (this may be redundant due to [reason])
    - Task 3:
    - Action 1: ...
    where for each task actions must be from the following list:
    [CLICK,TYPE,SCROLL,DRAG,WAIT,MOVE,SCREENSHOT,MOVE_ABS,SINGLE_CLICK,DOUBLE_CLICK,RIGHT_CLICK,COPY_TEXT,PASTE,OPEN_PROGRAM,SWITCH_WINDOW,PRESS_KEY]

    Prior Knowledge (Screenshot Description): <A detailed description of the screenshot>
    ---
    """
    return prompt


def extract_tasks(plan_list):
    """Extract only the 'task' fields from a plan list."""
    return [step['task'] for step in plan_list]

def extract_recent_actions_and_task(previous_plan):
    """Extract the task and all actions from the latest task in the previous plan."""
    if previous_plan:
        latest_task = previous_plan[-1]  # Get the latest task (last item in list)
        task_name = latest_task['task']
        actions = "\n".join([f"Action {i+1}: {action}" for i, action in enumerate(latest_task['actions'])])
        return f"Task: {task_name}\n{actions}"
    return ""

def extract_latest_action(previous_plan):
    """Extract the latest action taken from the last task in the previous plan."""
    if previous_plan:
        latest_task = previous_plan[-1]  # Get the latest task (last item in list)
        return latest_task['actions'][-1] if latest_task['actions'] else ""
    return ""

def read_json_and_generate_prompt(file_path: str, role: str) -> str:
    with open(file_path, 'r') as f:
        data = json.load(f)

    llm_response = data.get("LLMResponse", {})
    role = role.lower()

    intent = llm_response.get("intent", "")
    description = llm_response.get("description", "")

    if role == "marshal":
        previous_plan = llm_response.get("previous_plan", [])
        previous_plan_str = json.dumps(previous_plan, indent=2)  # Full structure (tasks + actions)
        return generate_marshal_prompt(intent, description, previous_plan_str)

    elif role == "commander":
        previous_plan = llm_response.get("previous_plan", [])
        #latest_action = extract_latest_action(previous_plan)  # Latest action from previous plan
        recent_actions_task_taken = extract_recent_actions_and_task(previous_plan)  # Actions + task from the latest task in previous plan
        next_plan = llm_response.get("next_plan", [])
        current_task = next_plan[0]['task'] if next_plan else ""  # First task in the next_plan

        return generate_commander_prompt(intent, description,recent_actions_task_taken, current_task)

    else:
        raise ValueError(f"Unknown role '{role}'. Expected 'marshal' or 'commander'.")

def main():

    action_done = True #TODO: this should come from verifier
    
    
    # Determine the role based on the action_done flag
    if action_done:
        role = "commander"
    else:
        role = "marshal"
    json_file_path="./full_3dee74b0-bf8b-4844-afc8-072d71459cd9_20250319010103_160.json"
    
    # Call the function with the appropriate role
    prompt = read_json_and_generate_prompt(json_file_path, role)

    if action_done:
        print("Short-Term Plan Prompt:\n")
    else:
        print("Long-Term Plan Prompt:\n")

    print(prompt)


if __name__ == "__main__":
    main()

