# Running CUA-RAG in Windows Agent Arena

## Prerequisites
- Ensure `cua_skill` is already set up on your system

## Setup Instructions

### 1. Prepare WindowsAgentArena
1. Pull the latest WindowsAgentArena code in the WAA submodule
2. Follow the instructions in `WindowsAgentArena/internal/LOCALDEV.md` to:
    - Prepare and build the Docker image
    - Create the `winarena` conda environment
3. After building the image, create a clean backup copy:
    ```bash
    cp -rf cua_skill/WindowsAgentArena/src/win-arena-container/vm/storage \
             cua_skill/WindowsAgentArena/src/win-arena-container/vm/storage_gold
    ```
If you have a downloaded storage image, you can also name it `storage_gold` and place it in the same directory to use.

### 2. Configure CUA-RAG
Switch to the `rag` branch in `cua_skill` for the latest features

### 3. Set Up Environment Variables
Create a `.env` file in the `./agent` directory with the following content:
```
UITARS_V1_BEARER_KEY="your_uitars_key"
AZURE_AD_TOKEN=""
```
*Note: Leave AZURE_AD_TOKEN empty initially*

### 4. Configure Azure Authentication
1. Create a screen session named "token":
    ```bash
    screen -S token
    ```
2. Login to Azure:
    ```bash
    az login --scope https://cognitiveservices.azure.com/.default --use-device-code
    ```
3. Navigate to the evaluation directory and run the token refresh script:
    ```bash
    cd cua_skill/evaluation/WindowsAgentArena
    ./refresh_token.sh
    ```
4. Keep this screen session running in the background

### 5. File Synchronization
Changes in `cua_skill/agent/` are automatically synced to:
`cua_skill/WindowsAgentArena/src/win-arena-container/client/mm_agents/rag_cua`

**File mappings:**
- `requirements_waa.txt` → `requirements.txt`
- `agent_rag_waa.py` → `agent_waa.py`

## Model Configuration

Configure model settings in `agent/config_rag.json`:

| Setting | Description |
|---------|-------------|
| `planner.model_class` | Select planner model: `"gpt"` or `"qwen"` |
| `rag.rel_action_sample_path` | Set action sampling percentage (e.g., `"mm_agents/rag_cua/sample_actions/0percent.json"`). Leave empty (`""`) to allow all actions. options can be found in cua_skill/agent/sample_actions |

## Running Tests

### Test Configuration
- Place test JSON files in `cua_skill/evaluation/WindowsAgentArena/test_jsons`
- Run tests using the `run_cua_rag.sh` script

### Command Syntax
```bash
sudo bash ./run_cua_rag.sh <test_json_filename> [options]
```

### Available Options
- `--use_gold_image`: Use the clean backup copy of the storage image
- `--clean_mode`: Reset environment between each test case (recommended)
- `--reset_image`: Remove current storage and regenerate from `setup.iso` by running:
  ```bash
  sudo "./run-local.sh" --prepare-image true
  ```

### Examples
```bash
# Run with clean environment for each test case (recommended)
sudo bash ./run_cua_rag.sh "test_one.json" --use_gold_image --clean_mode
```

**Tips:**
- You can select different tasks within `test_one.json`
- If using a downloaded storage image, rename it to `storage_gold` and use `--use_gold_image`
- Using `--clean_mode` is recommended to avoid display errors and ensure test isolation
