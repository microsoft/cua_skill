#!/bin/bash  
  
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)" 
# Initialize variables  
TEST_JSON=""  
USE_GOLD_IMAGE=""  
RESET_IMAGE=""
CLEAN_MODE=""
cd "${ROOT_DIR}/WindowsAgentArena/scripts" 
  
# Parse command-line arguments  
while [[ $# -gt 0 ]]; do  
  case $1 in  
  --use_gold_image)  
  USE_GOLD_IMAGE="true"  
  shift  
  ;;  
  --reset_image)  
  RESET_IMAGE="true"  
  shift  
  ;;  
  --clean_mode)  
  CLEAN_MODE="true"  
  shift  
  ;;  
  *)  
  TEST_JSON="$1"  
  shift  
  ;;  
  esac  
done  
echo "TEST_JSON: ${TEST_JSON}"  
echo "USE_GOLD_IMAGE: ${USE_GOLD_IMAGE}"
echo "RESET_IMAGE: ${RESET_IMAGE}"
echo "CLEAN_MODE: ${CLEAN_MODE}"
sudo chmod -R 777 "${ROOT_DIR}/WindowsAgentArena"  
if [[ "${USE_GOLD_IMAGE}" == "true" ]]; then
  echo "Using Gold image to replace current image..."  
  sudo rm -rf "${ROOT_DIR}/WindowsAgentArena/src/win-arena-container/vm/storage"  
  sudo cp -r "${ROOT_DIR}/WindowsAgentArena/src/win-arena-container/vm/storage_gold" "${ROOT_DIR}/WindowsAgentArena/src/win-arena-container/vm/storage"
fi

if [[ "${RESET_IMAGE}" == "true" ]]; then
  echo "Resetting image use setup.iso"
  sudo rm -rf "${ROOT_DIR}/WindowsAgentArena/src/win-arena-container/vm/storage"  
  sudo "./run-local.sh" --prepare-image true
fi

  
# Sync the agent implementation into the rag_cua client folder.  
set -euo pipefail  
SOURCE_DIR="${ROOT_DIR}/agent"  
TARGET_DIR="${ROOT_DIR}/WindowsAgentArena/src/win-arena-container/client/mm_agents/rag_cua"  
mkdir -p "${TARGET_DIR}"  
  
# Remove existing target contents before copying.  
rm -rf "${TARGET_DIR:?}"/*  
  
# Copy everything from the agent source directory.  
cp -a "${SOURCE_DIR}/." "${TARGET_DIR}/"  
  
# Replace the default agent wrapper with the RAG-specific one.  
mv -f "${TARGET_DIR}/agent_rag_waa.py" "${TARGET_DIR}/agent_waa.py"  
mv -f "${TARGET_DIR}/requirements_waa.txt" "${TARGET_DIR}/requirements.txt"  
  
# Echo completion message  
echo "Synchronized RAG CUA agent implementation to WindowsAgentArena client folder."  
# Run the script with the provided JSON name  
cp -f "${SCRIPT_DIR}/test_jsons/${TEST_JSON}" "${ROOT_DIR}/WindowsAgentArena/src/win-arena-container/client/evaluation_examples_windows/${TEST_JSON}"

# Set env-mode based on clean_mode flag
ENV_MODE_ARG=""
if [[ "${CLEAN_MODE}" == "true" ]]; then
  ENV_MODE_ARG="--env-mode clean_env"
fi

sudo  "./run-local.sh" --mode dev --agent rag_cua --json-name "evaluation_examples_windows/${TEST_JSON}" --skip-build false --gpu-enabled true ${ENV_MODE_ARG}