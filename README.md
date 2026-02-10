# CUA Skill — Computer Use Agent with Skills

**CUA Skill** is a skill-based autonomous GUI agent framework for Windows desktop applications. Instead of generating every low-level action from scratch, CUA Skill retrieves and executes pre-recorded action sequences (skills) from an indexed library, enabling reliable and efficient task completion across 17+ Windows applications.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Supported Applications](#supported-applications)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Agent Modes](#agent-modes)
  - [Replay Agent](#replay-agent)
  - [RAG Agent](#rag-agent)
- [User Task Generation](#user-task-generation)
- [Evaluation (Windows Agent Arena)](#evaluation-windows-agent-arena)
- [Project Structure](#project-structure)
- [License](#license)

---

## Overview

CUA Skill provides two agent modes for automating desktop tasks:

| Mode | Description |
|------|-------------|
| **Replay Agent** | Executes pre-defined task graphs step-by-step with vision-based grounding |
| **RAG Agent** | Uses an LLM planner with Retrieval-Augmented Generation (RAG) to dynamically retrieve, select, and configure skills at runtime |

The core insight is that many desktop tasks share common action patterns (e.g., opening apps, clicking menus, typing text). By indexing these patterns as reusable skills, the agent can accomplish complex tasks through composition rather than trial-and-error.

---

## Architecture

```
┌───────────────────────────────────────────────────────┐
│                      CUA Skill Agent                  │
├──────────────┬───────────────┬────────────────────────┤
│   Planner    │   Retriever   │   Mixture Grounding    │
│  (LLM-based) │  (BM25 +      │  (UI-TARS / UIA Tree)  │
│              │   Semantic)   │                        │
├──────────────┴───────────────┴────────────────────────┤
│                    Action System                      │
│  ┌────────────┐  ┌────────────────┐  ┌─────────────┐  │
│  │ Base       │  │ Common         │  │ App-Specific│  │
│  │ Actions    │  │ Actions        │  │ Skills      │  │
│  └────────────┘  └────────────────┘  └─────────────┘  │
├───────────────────────────────────────────────────────┤
│                Desktop Environment                    │
│          (Screenshots, A11y Tree, pyautogui)          │
└───────────────────────────────────────────────────────┘
```

### Key Components

- **Planner** — LLM-driven (GPT or Qwen) component that generates search queries, selects the best action from retrieved candidates, configures action parameters, and maintains an action memory.
- **Retriever** — Hybrid search engine combining BM25+ keyword ranking and semantic embeddings for skill retrieval from the indexed library.
- **Mixture Grounding** — Refines click coordinates using vision grounding models (UI-TARS v1 endpoint) in a mixture-of-experts pattern.
- **Action System** — 20+ base actions (click, type, scroll, hotkey, etc.) with a registry pattern, plus composable action graphs (DAGs) for multi-step skills.
- **Desktop Environment** — Wraps `pyautogui` and `pywinauto` for screenshots, accessibility tree extraction, and action execution.

---

## Supported Applications

| Application | Skill Module |
|-------------|-------------|
| Windows Start / Search / Run | `common_action.py` |
| Bing Search | `bing_search_action.py` |
| Google Chrome | `chrome_actions.py` |
| Microsoft Edge | `microsoft_edge_action.py` |
| Microsoft Excel | `excel_action.py` |
| Microsoft Word | `word_action.py` |
| Microsoft PowerPoint | `powerpoint_action.py` |
| Notepad | `notepad_action.py` |
| Paint | `paint_action.py` |
| Calculator | `calculator_action.py` |
| Clock | `clock_action.py` |
| File Explorer | `file_explorer_action.py` |
| VLC Media Player | `vlc_action.py` |
| VS Code | `vs_code_action.py` |
| Amazon | `amazon_action.py` |
| YouTube | `youtube_action.py` |
| Windows Settings | `windows_settings_action.py` |

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Windows OS** (agent interacts with the Windows desktop)
- Azure OpenAI access (for LLM planner and grounding models)
- (Optional) Local Qwen model for offline planner

### Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd cua_skill
   ```

2. Install dependencies:
   ```bash
   pip install -r agent/requirements.txt
   ```

3. For Windows Agent Arena evaluation, install additional dependencies:
   ```bash
   pip install -r agent/requirements_waa.txt
   ```

### Configuration

1. Create a `.env` file in the `agent/` directory:
   ```
   UITARS_V1_BEARER_KEY="your_uitars_key"
   AZURE_AD_TOKEN=""
   ```

2. Configure the agent via JSON config files:
   - **`agent/config.json`** — Replay agent settings (environment, grounding, logging)
   - **`agent/config_rag.json`** — RAG agent settings (planner model, retrieval parameters, RAG index paths)

Key configuration options:

| Setting | File | Description |
|---------|------|-------------|
| `mixture_grounding.expertises` | `config.json` | Vision grounding model endpoints and weights |
| `planner.model_class` | `config_rag.json` | LLM planner backend: `"gpt"` or `"qwen"` |
| `rag.semantic_weight` | `config_rag.json` | Blending weight for hybrid search (default: 0.7) |
| `max_steps` | Both | Maximum actions per task (default: 50) |
| `max_wall_time` | Both | Timeout in seconds (default: 300) |

---

## Agent Modes

### Replay Agent

The **Replay Agent** (`CUAKnowledgeGraphAgent`) executes pre-defined task graphs:

1. Loads a task definition (JSON) as a directed graph of actions
2. Pops steps one-by-one in topological order
3. For each step, applies mixture grounding to refine coordinates
4. Executes the action via the desktop environment

```python
from agent import CUAKnowledgeGraphAgent

agent = CUAKnowledgeGraphAgent(config="agent/config.json")
agent.proceed(instruction="Open Notepad and type Hello", example=task_json)
```

### RAG Agent

The **RAG Agent** (`CUARAGAgent`) dynamically plans and executes tasks:

1. **Feasibility check** — LLM evaluates if the task is achievable from the current screen
2. **Loop** until completion or timeout:
   - Capture screenshot observation
   - **Generate search queries** from task description + action history + screenshot
   - **Retrieve skills** via hybrid BM25 + semantic search over the indexed skill library
   - **Select** the best action from retrieved candidates (with base action fallbacks)
   - **Configure** action parameters using the LLM + current screenshot
   - **Ground** coordinates via the mixture grounding model (UI-TARS)
   - **Execute** the action
   - **Update memory** — LLM summarizes the outcome for future context

```python
from agent import CUARAGAgent

agent = CUARAGAgent(config="agent/config_rag.json")
agent.proceed(instruction="Search for 'weather today' on Bing")
```

---

## User Task Generation

The `user_task_generation/` module provides a pipeline for synthesizing diverse user tasks from **primitive operations** and **compositions**:

1. **Define primitive operations** per application (e.g., `BingSearchLaunch`, `InsertImage`) with argument generators
2. **Create compositions** combining primitives into multi-step user tasks
3. **Generate** tasks with automatic argument filling, instruction drop-off for diversity, and LLM-based rephrasing

```bash
python user_task_generation/user_task_generator.py \
  --primitive-operation ./asset/primitive_operation/bingsearch_primitive_operation.json \
  --composition ./asset/primitive_operation_composition/bingsearch_primitive_operation_composition.json \
  --app-name bingsearch \
  --out-dir ./asset/user_task \
  --num-tasks 10000
```

See [user_task_generation/README.md](user_task_generation/README.md) for full documentation.

---

## Evaluation (Windows Agent Arena)

CUA Skill can be evaluated in the [Windows Agent Arena](https://github.com/microsoft/WindowsAgentArena) environment:

1. Set up the Windows Agent Arena Docker image (see [evaluation/WindowsAgentArena/README.md](evaluation/WindowsAgentArena/README.md))
2. Place test JSON files in `evaluation/WindowsAgentArena/test_jsons/`
3. Run evaluation:
   ```bash
   cd evaluation/WindowsAgentArena
   sudo bash ./run_cua_rag.sh <test_json_filename> [options]
   ```

Available options:
- `--use_gold_image` — Use the clean backup storage image
- `--clean_mode` — Reset environment between test cases (recommended)
- `--reset_image` — Regenerate storage from setup ISO

---

## Project Structure

```
cua_skill/
├── agent/                        # Core agent framework
│   ├── agent.py                  # Replay agent (CUAKnowledgeGraphAgent)
│   ├── agent_rag.py              # RAG agent (CUARAGAgent)
│   ├── agent_waa.py              # WAA adapter for replay agent
│   ├── agent_rag_waa.py          # WAA adapter for RAG agent
│   ├── planner.py                # LLM-based planning (query gen, action selection, config)
│   ├── retrieval.py              # Hybrid BM25 + semantic retrieval engine
│   ├── mixture_grounding.py      # Vision-based coordinate grounding (UI-TARS)
│   ├── llms.py                   # LLM clients (Azure OpenAI GPT, local Qwen)
│   ├── desktop_env.py            # Desktop environment wrapper
│   ├── replay_task.py            # Task graph parser and executor
│   ├── config.json               # Replay agent configuration
│   ├── config_rag.json           # RAG agent configuration
│   ├── action/                   # Action system
│   │   ├── base_action.py        # Base actions with registry pattern
│   │   ├── compose_action.py     # Composable action DAGs
│   │   ├── <app>_action.py       # Application-specific skill modules
│   │   └── argument.py           # Action argument definitions
│   └── utils/                    # Utilities (logging, UIA, config, etc.)
├── user_task_generation/         # Task synthesis pipeline
│   ├── user_task_generator.py    # Main generator script
│   ├── argument_value_generator/ # Realistic argument value generators
│   └── README.md                 # Task generation documentation
├── evaluation/                   # Evaluation tooling
│   └── WindowsAgentArena/        # WAA integration and analysis notebooks
├── docs/                         # Project documentation website
├── LICENSE                       # MIT License
└── README.md                     # This file
```

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

Copyright (c) 2026 Microsoft Corporation.