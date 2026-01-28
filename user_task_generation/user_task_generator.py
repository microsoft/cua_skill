import os
import json
import random
import argparse
from typing import Any, Dict
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent))
from argument_value_generator import *
import time
import hashlib
from tqdm import tqdm
import logging
import traceback

# ${{arg}}  -> {arg} (so we can use one formatter)
_DOLLAR_PLACEHOLDER = re.compile(r"\$\{\{(\w+)\}\}")
# {arg} placeholders for safe manual substitution
_BRACE_PLACEHOLDER  = re.compile(r"\{(\w+)\}")


LLM = None  # Placeholder for LLM instance if needed
processor = None

def _initialize_llm():
    global LLM
    global processor

    from transformers import (
        Qwen2_5_VLForConditionalGeneration,
        AutoProcessor,
    )
    import torch

    LLM = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2.5-VL-7B-Instruct", 
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
        device_map="cuda:0",
    )

    global processor
    processor = AutoProcessor.from_pretrained(
        "Qwen/Qwen2.5-VL-7B-Instruct", 
        size={'shortest_edge': 3136, 'longest_edge': 1003520}
    )

def rephrase_instruction_by_local_llm(
    instruction: str
):
    global LLM
    global processor
    
    from qwen_vl_utils import process_vision_info

    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": "Please rephrase the following instruction to make it more natural and user-friendly. Make the instruction to be concise and remove unnecessary details. Typically, the instruction to launch application could be skipped. Output only the rephrased instruction without any additional explanations."},
            {"type": "text", "text": instruction}
        ]}
    ]
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to("cuda:0")

    start_time = time.time()
    # Inference: Generation of the output
    generated_ids = LLM.generate(**inputs, max_new_tokens=512)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    refined_instruction = output_text[0].strip()
    return refined_instruction


def _normalize_template_placeholders(tmpl: str) -> str:
    """Convert ${{arg}} to {arg} so we can safely fill values."""
    return _DOLLAR_PLACEHOLDER.sub(lambda m: "{" + m.group(1) + "}", tmpl)


def _safe_format(tmpl: str, args: Dict[str, Any]) -> str:
    """
    Fill {arg} with values from args; if a key is missing, keep the placeholder.
    Avoids KeyError and keeps instructions readable.
    """
    def repl(m: re.Match) -> str:
        k = m.group(1)
        return str(args[k]) if k in args and args[k] is not None else m.group(0)
    return _BRACE_PLACEHOLDER.sub(repl, tmpl)


def _sample_prob(prob_range: list) -> float:
    """
    Interprets probability range inputs:
      - [] or None  -> 0.0
      - [p]         -> clamp(p, 0..1)
      - [a, b]      -> uniform(clamp(a), clamp(b)) with order-agnostic handling
      - longer lists -> use first two elements
    """
    if not prob_range:
        return 0.0
    if len(prob_range) == 1:
        p = float(prob_range[0])
        return max(0.0, min(1.0, p))
    # take first two values
    a, b = float(prob_range[0]), float(prob_range[1])
    low_prob, high_prob = sorted([max(0.0, min(1.0, a)), max(0.0, min(1.0, b))])
    if low_prob == high_prob:
        return low_prob
    return random.uniform(low_prob, high_prob)

def _is_launch_application_step(step: Dict[str, Any]) -> bool:
    return step.get("primitive_operation").endswith("Launch")

def generate_user_task_id(
    domain: str | None = None,
    composition_id: str | None = None,
    instruction: str | None = None,
    counter: int | None = None,
    timestamp: Optional[float] = None,
) -> str:
    """
    Example outputs:
      powerpoint_insert-image_000123_4f9a2c91_a1b2c3d4
      powerpoint_insert-image_4f9a2c91_f3e9a1b2
      powerpoint_noinstr_a1b2c3d4
    """
    parts = [domain]

    if composition_id:
        parts.append(composition_id)

    if counter is not None:
        parts.append(f"{counter:06d}")
    
    ts = str(int(timestamp or time.time()))  # default to current epoch seconds
    raw_hash_str = f"{domain}|{composition_id}|{counter}|{instruction}|{ts}"
    h = hashlib.sha1(raw_hash_str.encode("utf-8")).hexdigest()
    parts.append(h[:16])  # take first 16 chars of sha1 digest
    return "_".join(parts)


def generate_step_instruction(
    arguments,
    instruction_pool,
    instruction, 
):
    if not instruction_pool:
        # Fallback if no templates exist
        return " ".join(f"{k}={v}" for k, v in arguments.items()) or "Do the step."

    if instruction is None:
        arg_keys = set(arguments.keys())
        # Set of argument keys that have non-None values
        non_none_arg_keys = {k for k, v in arguments.items() if v is not None}
        # Matches {var} or {{var}}
        ptn = r"\{{1,2}\s*(\w+)\s*\}{1,2}" 
        # 1. Relevance: Check if every argument exists in the template
        if arg_keys:
            candidates = [t for t in instruction_pool if all(
                var in arg_keys
                for var in re.findall(ptn, t)
            )]
        else:
            candidates = instruction_pool.copy()
        # 2. Safety: Ensure ALL variables in the template exist in our provided args
        # E.g., should not use "Add a new slide with layout as {slide_layout}" if we don't have "slide_layout" arg or arguments["slide_layout"] is None
        candidates = [t for t in candidates if all(
            var in arg_keys and arguments[var] is not None
            for var in re.findall(ptn, t)
        )]
        # print(arg_keys)
        # print(json.dumps(candidates, indent=2))
        if not candidates:
            candidates = instruction_pool

        # 3. Prioritize templates that use MORE of our non-None arguments
        # This ensures that if textbox_position is provided, we prefer templates with {textbox_position}
        # over templates that say "(at any place)"
        def count_used_args(template):
            template_vars = set(re.findall(ptn, template))
            return len(template_vars & non_none_arg_keys)
        
        max_coverage = max(count_used_args(t) for t in candidates)
        best_candidates = [t for t in candidates if count_used_args(t) == max_coverage]
        
        chosen_instruction = random.choice(best_candidates)
    else:
        chosen_instruction = instruction

    # Normalize ${{arg}} -> {arg} and fill safely
    chosen_norm = _normalize_template_placeholders(chosen_instruction)
    formatted_instruction = _safe_format(chosen_norm, arguments)

    return formatted_instruction


# Helper function to parse strings like "${1.rows} + 1" (used in argument dependency)
def resolve_expression(expression_str, context_mappings):
    """
    Parses a string containing references like ${mapping_id.key}.
    Replaces them with values from context_mappings.
    If the result is a math expression, evaluates it.
    """
    # 1. Regex to find patterns like ${1.text} or ${1.rows}
    pattern = r"\$\{(\w+)\.(\w+)\}"
    
    def replace_match(match):
        map_id = match.group(1)
        map_key = match.group(2)
        
        if map_id not in context_mappings:
            raise ValueError(f"Mapping ID '{map_id}' not found in context.")
        if map_key not in context_mappings[map_id]:
            raise ValueError(f"Key '{map_key}' not found in mapping ID '{map_id}'.")
        
        val = context_mappings[map_id][map_key]
        return str(val)

    # 2. Replace all references with actual values
    # e.g., "${1.rows} + 1" -> "5 + 1"
    resolved_str = re.sub(pattern, replace_match, str(expression_str))

    # 3. Try to evaluate as math (integers/floats)
    # If it's just text (e.g. "Hello World"), eval might fail or is unnecessary.
    try:
        # distinct check: if the string is just a number or math expr
        # We use python's eval() here. In production, use a safer math parser.
        result = eval(resolved_str)
        return result
    except (SyntaxError, NameError, TypeError):
        # If eval fails, it's likely just a plain string (e.g. "Title Text")
        return resolved_str



def generate_user_task(
    primitive_operations: Dict[str, Any], 
    composition: Dict[str, Any], 
    domain: str = None,
    llm_rephrase: bool = False,
    instruction_dropoff_prob_range: list = None,
    llm_rephrase_prob_range: list = None,
    launch_app_instruction_dropoff_prob_range: list = None
) -> Dict[str, Any]:
    # Robust defaults
    instruction_dropoff_prob_range = instruction_dropoff_prob_range or [0.0]
    llm_rephrase_prob_range = llm_rephrase_prob_range or [0.0]
    launch_app_instruction_dropoff_prob_range = launch_app_instruction_dropoff_prob_range or [0.5]

    # Sample the per-task probabilities
    instruction_dropoff = _sample_prob(instruction_dropoff_prob_range)
    llm_rephrase_prob = _sample_prob(llm_rephrase_prob_range)
    launch_app_instruction_dropoff = _sample_prob(launch_app_instruction_dropoff_prob_range)

    user_task = {
        'id': None,
        'instruction': None,
        'domain': domain if domain is not None else 'unknown',
        "steps": [],
        "composition": composition.get("id", None)
    }
    
    # Build steps
    steps = []
    value_mappings = {}
    for step in composition.get('steps', []):
        primitive_operation_name = step.get('primitive_operation')
        
        # 1. Extract control keys and existing arguments
        arguments = {}
        mapping_id = None
        step_argument_mappings = {}   # Direct dependencies: "text": "${1.text}"
        step_value_func_mapping = {}  # Generator parameter overrides: "row_index.max_value": "${1.rows} + 1"

        for k, v in step.items():
            if k == "primitive_operation":
                continue
            elif k == "mapping_id":
                mapping_id = v
                continue
            elif k == "argument_mappings":
                step_argument_mappings = v
                continue
            elif k == "value_func_mapping":
                step_value_func_mapping = v
                continue
            arguments[k] = v

        primitive_spec = primitive_operations.get(primitive_operation_name, {})
        all_spec_arguments = {arg['name']: arg for arg in primitive_spec.get('arguments', []) if 'name' in arg}
        
        for arg_name, arg_spec in all_spec_arguments.items():
            # --- Case 1: Direct Mapping (Dependency) ---
            # If the argument is defined in "argument_mappings", resolve it and skip generation.
            if arg_name in step_argument_mappings:
                expr = step_argument_mappings[arg_name]
                arguments[arg_name] = resolve_expression(expr, value_mappings)
                continue

            # --- Case 2: Already Provided ---
            # If the argument is explicit in the JSON step, use it.
            if arg_name in arguments:
                continue

            # --- Case 3: Optional Check ---
            optional = arg_spec.get("optional", False)
            # If optional and not required by a mapping, random chance to skip
            if optional:
                if random.random() < 0.5:
                    continue
            
            # --- Case 4: Generation with Value Function ---
            value_func_spec = arg_spec.get("value_func", None)
            if value_func_spec:
                value_func_name = value_func_spec.get("name", None)
                # Make a copy of default arguments to avoid mutating the spec
                value_func_arguments = value_func_spec.get("arguments", {}).copy()

                # Apply value_func_mapping overrides here
                # Check if there are dynamic overrides for this argument's generator parameters
                # Key format expected: "arg_name.param_name" -> e.g., "row_index.max_value"
                for mapping_key, mapping_expr in step_value_func_mapping.items():
                    if "." in mapping_key:
                        target_arg_name, target_param_name = mapping_key.split('.', 1)
                        
                        if target_arg_name == arg_name:
                            # Resolve the expression (e.g., "${1.rows} + 1" -> 6)
                            resolved_param_value = resolve_expression(mapping_expr, value_mappings)
                            # Override the generator's parameter
                            value_func_arguments[target_param_name] = resolved_param_value

                argument_value_generator = ARGUMENT_GENERATORS.get(value_func_name, None)
                if argument_value_generator is None:
                    print(f"Warning: No argument generator found for {value_func_name}")
                    continue

                # Generate the final value
                arguments[arg_name] = argument_value_generator(**value_func_arguments)

        # 3. Store result in context for future steps
        if mapping_id is not None:
            value_mappings[mapping_id] = arguments

        step_instruction = generate_step_instruction(
            arguments = arguments,
            instruction_pool = primitive_spec.get("instructions", []),
            instruction = None
        )
        steps.append(
            {
                "primitive_operation": primitive_operation_name,
                "instruction": step_instruction,
                "arguments": arguments
            }
        )

    # instruction: prefer explicit composition instruction, else synthesize
    instruction = composition.get('instruction')
    if not instruction:
        # Accumulate step instructions with probabilistic drop-off
        accumulated_instructions = []
        for step in steps:
            if instruction_dropoff > 0.0 and random.random() < instruction_dropoff:
                continue
            if _is_launch_application_step(step):
                if random.random() < launch_app_instruction_dropoff:
                    continue
            accumulated_instructions.append(step["instruction"])
        instruction = " ".join(accumulated_instructions).strip()

    # If all step instructions are dropped, fall back to joining all step instructions
    if not instruction:                
        instruction = " ".join([step["instruction"] for step in steps]).strip()

    task_id = generate_user_task_id(
        domain=domain,
        composition_id=composition.get("id"),
        instruction=instruction,
        # counter=<optional int if you track sequence>
    )

    # Optional LLM rephrase (based on sampled probability)
    if llm_rephrase_prob > 0.0 and random.random() < llm_rephrase_prob:
        if LLM is None:
            _initialize_llm()
        instruction = rephrase_instruction_by_local_llm(instruction)

    user_task = {
        'id': task_id,
        'instruction': instruction,
        'domain': domain,
        'steps': steps
    }
    return user_task


def generate_user_tasks(
    primitive_operation_path: str, 
    composition_path: str, app_name: str, 
    output_path: str = None, 
    seed: int = None, 
    num_tasks: int = None, 
    instruction_dropoff_prob_range: list = [0.0],
    llm_rephrase_prob_range: list = [0.0],
    launch_app_instruction_dropoff_prob_range: list = [0.5]
) -> None:
    """Generate user tasks from a composition file.

    - If num_tasks is None, generate one task per composition entry (preserve order).
    - If num_tasks is provided and <= number of compositions, randomly sample that many
      compositions without replacement.
    - If num_tasks is greater than number of compositions, sample with replacement
      until the requested count is reached.
    """
    if seed is not None:
        random.seed(seed)

    with open(primitive_operation_path, 'r', encoding='utf-8') as f:
        primitive_operations = json.load(f)

    with open(composition_path, 'r', encoding='utf-8') as f:
        compositions = json.load(f)
        compositions = list(compositions.items())

    num_compositions = len(compositions)

    generated_tasks = {}

    target_num_tasks = num_tasks if num_tasks is not None else num_compositions
    
    # Build a queue to ensure coverage: each template used at least once before random sampling
    # If target_num_tasks >= num_compositions, shuffle all compositions first (coverage pass),
    # then fill remaining slots with random sampling (with replacement).
    composition_queue = []
    if target_num_tasks >= num_compositions:
        # Coverage pass: shuffle all compositions to ensure each is used at least once
        coverage_list = list(compositions)
        random.shuffle(coverage_list)
        composition_queue.extend(coverage_list)
    
    # progress bar
    pbar = tqdm(total=target_num_tasks, desc="Generating user tasks", unit="task") if tqdm else None
    attempts = 0
    coverage_achieved = set()  # Track which composition IDs have been successfully used

    while len(generated_tasks) < target_num_tasks:
        attempts += 1
        
        # Pick from queue (coverage pass) or random sample (after coverage is done)
        if composition_queue:
            composition_id, composition = composition_queue.pop(0)
        else:
            composition_id, composition = random.choice(compositions)

        # (optional) quiet noisy prints when tqdm is present
        if not pbar:
            print(composition_id, composition)

        user_task = generate_user_task(
            primitive_operations=primitive_operations,
            composition=composition,
            domain=app_name,
            instruction_dropoff_prob_range=instruction_dropoff_prob_range,
            llm_rephrase_prob_range=llm_rephrase_prob_range,
            launch_app_instruction_dropoff_prob_range=launch_app_instruction_dropoff_prob_range
        )

        if user_task['id'] in generated_tasks:
            # Duplicate task ID - if this was from coverage pass, re-queue for another attempt
            if composition_id not in coverage_achieved and target_num_tasks >= num_compositions:
                composition_queue.append((composition_id, composition))
            # show a tiny hint about duplicates without breaking the bar
            if pbar:
                pbar.set_postfix_str(f"attempts={attempts}, dups")
            continue

        generated_tasks[user_task['id']] = user_task
        coverage_achieved.add(composition_id)
        if pbar:
            pbar.update(1)
            pbar.set_postfix_str(f"attempts={attempts}, coverage={len(coverage_achieved)}/{num_compositions}")

    if pbar:
        pbar.close()

    # default output path
    if not output_path:
        out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test', 'user_tasks')
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, f"{app_name}_tasks.json")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(generated_tasks, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(generated_tasks)} tasks to {output_path}")

def batch_processing():
    parser = argparse.ArgumentParser(description='Generate user tasks from primitive-operation compositions')
    parser.add_argument('--config', default=R"./generator_config.json", help='Path to generator config JSON')
    args = parser.parse_args()
    config_path = args.config

    with open(config_path, 'r', encoding='utf-8') as f:
        generator_config = json.load(f)

    basic_config = generator_config.get("basic_config")
    app_names = generator_config.get("app_names")

    primitive_operation_folder = basic_config.get("primitive_operation_folder")
    composition_folder = basic_config.get("composition_folder")
    output_folder = basic_config.get("output_folder")
    output_file = basic_config.get("output_file")
    seed = basic_config.get("seed")
    num_tasks = basic_config.get("num_tasks")
    instruction_dropoff_prob_range = basic_config.get("instruction_dropoff_prob_range")
    llm_rephrase_prob_range = basic_config.get("llm_rephrase_prob_range")
    launch_app_instruction_dropoff_prob_range = basic_config.get("launch_app_instruction_dropoff_prob_range")

    # log file
    log_dir = os.path.join(os.path.dirname(config_path), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"batch_processing_{int(time.time())}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # Also print to console
        ]
    )
    logger = logging.getLogger(__name__)

    successful_apps = []
    failed_apps = []

    for app_name in app_names:
        try:
            primitive_operation_path = os.path.join(primitive_operation_folder, f"{app_name}_primitive_operation.json")
            composition_path = os.path.join(composition_folder, f"{app_name}_primitive_operation_composition.json")

            if output_file is None:
                output_path = os.path.join(output_folder, f"{app_name}_tasks.json")
            else:
                output_path = os.path.join(output_folder, output_file)
            
            generate_user_tasks(
                primitive_operation_path=primitive_operation_path,
                composition_path=composition_path,
                app_name=app_name,
                output_path=output_path,
                seed=seed,
                num_tasks=num_tasks,
                instruction_dropoff_prob_range=instruction_dropoff_prob_range,
                llm_rephrase_prob_range=llm_rephrase_prob_range,
                launch_app_instruction_dropoff_prob_range=launch_app_instruction_dropoff_prob_range
            )
            print(f"Generated {num_tasks} tasks for {app_name}")
            successful_apps.append(app_name)
        except Exception as e:
            error_msg = f"Failed to generate tasks for {app_name}: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            failed_apps.append(app_name)
            print(f"ERROR: Failed to generate tasks for {app_name}. Error logged to {log_file}")
            continue

    summary_msg = f"\n{'='*60}\n"
    summary_msg += f"Batch processing completed.\n"
    summary_msg += f"Successful: {len(successful_apps)} app(s) - {successful_apps}\n"
    if failed_apps:
        summary_msg += f"Failed: {len(failed_apps)} app(s) - {failed_apps}\n"
    summary_msg += f"{'='*60}\n"
    
    logger.info(summary_msg)
    print(summary_msg, end='')
    if failed_apps:
        print(f"Error details logged to: {log_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate user tasks from primitive-operation compositions')
    parser.add_argument('--primitive-operation', default=R"./asset/primitive_operation/bingsearch_primitive_operation.json", help='Path to primitive operation JSON')
    parser.add_argument('--composition', default=R"./asset/primitive_operation_composition/bingsearch_primitive_operation_composition.json", help='Path to composition JSON')
    parser.add_argument('--app-name', default="bingsearch", help='Application/domain name (e.g., calculator)')
    parser.add_argument('--out-dir', default=R"./asset/user_task", help='Output JSON path (default: test/user_tasks/{app}_tasks.json)')
    parser.add_argument('--out-file', default=None, help='Output JSON file (default: test/user_tasks/{app}_tasks.json)')
    parser.add_argument('--seed', type=int, help='Optional random seed for reproducibility')
    parser.add_argument('--num-tasks', default=10000, type=int, help='Number of tasks to generate (sampling/repeating compositions as needed)')
    parser.add_argument('--instruction-dropoff-prob-range', type=json.loads, default='[0.0]', help='A range of probabilities for dropping step instructions to increase diversity. If [p] with p > 0, then use that probability. If [a, b] with a < b, then randomly choose a value in that range for each task.')
    parser.add_argument('--llm-rephrase-prob-range', type=json.loads, default='[0.0]', help='Probability of rephrasing the final instruction using LLM. If [0.0], then no rephrasing. If [p] with p > 0, then use that probability. If [a, b] with a < b, then randomly choose a value in that range for each task.')
    parser.add_argument('--launch-app-instruction-dropoff-prob-range', type=json.loads, default='[0.5]', help='Probability of dropping the "launch application" step if it exists (default: 0.5)')
    args = parser.parse_args()

    if args.out_file is None:
        output_path = os.path.join(args.out_dir, f"{args.app_name}_tasks.json")
    else:
        output_path = os.path.join(args.out_dir, args.out_file)
    os.makedirs(args.out_dir, exist_ok=True)

    generate_user_tasks(
        primitive_operation_path=args.primitive_operation, 
        composition_path=args.composition, 
        app_name=args.app_name, 
        output_path=output_path, 
        seed=args.seed, 
        num_tasks=args.num_tasks, 
        instruction_dropoff_prob_range=args.instruction_dropoff_prob_range, 
        llm_rephrase_prob_range=args.llm_rephrase_prob_range,
        launch_app_instruction_dropoff_prob_range=args.launch_app_instruction_dropoff_prob_range
    )


if __name__ == '__main__':
    main()
    # batch_processing()