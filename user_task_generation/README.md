
# User Task Generation Pipeline (v2)

This README explains how to generate **user tasks** for each application using the `primitive_operation` and `primitive_operation_composition` pipeline with enhanced control over instruction diversity and rephrasing.

---

## 1. Prepare the Primitive Operation File

Each application requires a **primitive operation JSON** file describing its low-level actions.  
This file defines:

- **Primitive operations** (e.g., `BingSearchLaunch`, `InsertImage`, etc.)  
- **Arguments** for each operation.  
- **Instruction templates** for human-readable instructions.  
- **Argument generators** to produce realistic values automatically.

### Argument Generators

The pipeline maps each argument to a generator function that yields realistic values.  
Common generators are implemented in `argument_value_generator.py`, including:

- `generate_random_number`  
- `select_from_options`  
- `select_file_path_in_directory`  
- `generate_string`  

If your application requires custom logic, implement a new generator and register it in `ARGUMENT_GENERATORS`.

📄 Example: [`bingsearch_primitive_operation.json`](./asset/primitive_operation/bingsearch_primitive_operation.json)

---

## 2. Create Primitive Operation Compositions

A **composition** combines primitive operations into a higher-level **user task**.

### Required Fields
- **`id`** – unique identifier for the composition.  
- **`steps`** – ordered list of primitive operations (each may include argument overrides).  

### Argument Value Behavior
- Missing arguments are automatically filled by default argument generators.  
- If a step specifies argument values, those override the generated ones.

### Instruction Behavior
- If a composition has **no explicit instruction**, the script automatically composes one from step-level instructions.  
- If an **instruction** is provided in the composition, it is directly used for the user task.

📄 Example: [`bingsearch_primitive_operation_composition.json`](./asset/primitive_operation_composition/bingsearch_primitive_operation_composition.json)

---

## 3. Generate User Tasks

Run the generator to produce user tasks from the compositions.

```bash
python user_task_generation/user_task_generator.py   --primitive-operation ./asset/primitive_operation/bingsearch_primitive_operation.json   --composition ./asset/primitive_operation_composition/bingsearch_primitive_operation_composition.json   --app-name bingsearch   --out-dir ./asset/user_task   --num-tasks 10000   --instruction-dropoff-prob-range '[0.1,0.2]'   --llm-rephrase-prob-range '[0.9]'   --launch-app-instruction-dropoff-prob '[0.6]'
```

### Key Arguments

| Argument | Description |
|-----------|--------------|
| `--primitive-operation` | Path to primitive operation JSON. |
| `--composition` | Path to composition JSON. |
| `--app-name` | Application/domain name (used in task IDs). |
| `--out-dir` | Output directory for generated tasks. |
| `--out-file` | Optional custom output file name. |
| `--seed` | Random seed for reproducibility. |
| `--num-tasks` | Number of tasks to generate. |
| `--instruction-dropoff-prob-range` | Probability range for dropping some step instructions. |
| `--llm-rephrase-prob-range` | Probability range for rephrasing final instruction with LLM. |
| `--launch-app-instruction-dropoff-prob` | Probability of skipping “Launch Application” instructions (default 0.5). |

---

## 4. Instruction and Rephrasing Logic

### Step Instruction Drop-Off
During synthesis, each step instruction can be dropped with a probability sampled from the provided range.

- Example:  
  - `[0.2]` → always drop 20% of steps.  
  - `[0.1, 0.5]` → randomly pick a drop probability between 0.1–0.5 for each task.

### Launch Step Drop-Off
If a step’s primitive operation ends with `"Launch"`, it has an additional drop probability defined by:
```bash
--launch-app-instruction-dropoff-prob '[0.5]'
```
This avoids redundant phrases like *“Launch Bing Search.”*

### LLM-Based Rephrasing
Optionally, the script uses **Qwen2.5-VL-7B-Instruct** to rephrase the final instruction into a more natural, concise user command.  
Triggered when a random value < `--llm-rephrase-prob-range`.

Example:
```bash
--llm-rephrase-prob-range '[0.1, 0.3]'
```
This gives a 10–30% chance of rephrasing each task instruction.

📘 *The model runs locally on CUDA:0 (bf16 with FlashAttention2). If you only need text processing, a lightweight model or stub can be substituted.*

---

## 5. Progress Monitoring

The script reports generation progress using `tqdm`:
```
Generating user tasks: 73%|███████▎ | 7300/10000 [00:42<00:15, 180.2 task/s] attempts=7450
```

---

## 6. Output Format

The generated file contains all tasks keyed by unique IDs:

```json
{
  "bingsearch_basic_000001_4f9a2c91a1b2c3d4": {
    "id": "bingsearch_basic_000001_4f9a2c91a1b2c3d4",
    "instruction": "Search for AI trends and open the first result.",
    "domain": "bingsearch",
    "steps": [
      {
        "primitive_operation": "BingSearchLaunch",
        "instruction": "Open Bing Search.",
        "arguments": {}
      },
      {
        "primitive_operation": "BingSearchQuery",
        "instruction": "Search for AI trends.",
        "arguments": {"query": "AI trends"}
      },
      {
        "primitive_operation": "BingResultClick",
        "instruction": "Open the first result.",
        "arguments": {"rank": 1}
      }
    ]
  }
}
```

---

## 7. Probability Range Examples

| Use Case | Example Flag | Effect |
|-----------|---------------|--------|
| Drop some step texts | `--instruction-dropoff-prob-range '[0.2,0.6]'` | Removes 20–60% of step instructions |
| Occasional rephrasing | `--llm-rephrase-prob-range '[0.0,0.3]'` | 0–30% tasks get LLM-rephrased |
| Drop “Launch” step | `--launch-app-instruction-dropoff-prob '[0.75]'` | 75% chance to skip “Launch App” step |

---

## 8. Troubleshooting

| Issue | Resolution |
|--------|-------------|
| `qwen_vl_utils not found` | Create a stub file: <br>```python<br>def process_vision_info(messages): return [], []``` |
| Model download too large | Temporarily set `--llm-rephrase-prob-range '[0.0]'` to disable LLM usage. |
| Argument generation missing | Verify that all generator functions are registered in `ARGUMENT_GENERATORS`. |
| GPU OOM during LLM inference | Reduce model precision or limit rephrase probability. |

---

## 9. Output Location

By default, the generated file is saved to:
```
./asset/user_task/{app_name}_tasks.json
```

You can override it with:
```bash
--out-file custom_tasks.json
```

---
