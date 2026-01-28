#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"  

# Path to the trigger file and .env file
TRIGGER_FILE="${ROOT_DIR}/WindowsAgentArena/src/win-arena-container/client/mm_agents/rag_cua/new_token_request.txt"
ENV_FILE="${ROOT_DIR}/WindowsAgentArena/src/win-arena-container/client/mm_agents/rag_cua/.env"

echo "Starting token refresh monitor. Checking every second..."
echo "Press Ctrl+C to stop."

# Continuous loop
while true; do
    # Check if trigger file exists
    if [ -f "$TRIGGER_FILE" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Trigger file found. Refreshing Azure AD token..."
        
        # Get new token
        NEW_TOKEN=$(az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken --output tsv)
        
        # Check if token was retrieved successfully
        if [ -z "$NEW_TOKEN" ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error: Failed to retrieve token"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Token retrieved successfully"
            
            # Update the .env file
            # Read the current UITARS_V1_BEARER_KEY line
            UITARS_LINE=$(grep "UITARS_V1_BEARER_KEY=" "$ENV_FILE")
            
            # Create new .env content
            echo "$UITARS_LINE" > "$ENV_FILE"
            echo "AZURE_AD_TOKEN=\"$NEW_TOKEN\"" >> "$ENV_FILE"
            
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Updated .env file with new token"
            
            # Delete the trigger file
            rm -f "$TRIGGER_FILE"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Deleted trigger file"
            
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Token refresh completed successfully"
        fi
    fi
    
    # Wait 1 second before checking again
    sleep 1
done