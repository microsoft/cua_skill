"""
Task Schema Transformer for Windows Agent Arena

This module transforms task schemas from input format to WAA (Windows Agent Arena) format,
with support for parallel processing and AI-generated content.
"""

import json
import math
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from openai import AzureOpenAI
from tqdm import tqdm


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class AzureOpenAIConfig:
    """Configuration for Azure OpenAI client."""
    api_key: str = ""
    api_version: str = "2025-01-01-preview"
    azure_endpoint: str = "https://your-azure-openai-endpoint/"
    model: str = "gpt-4o"
    temperature: float = 0.7


@dataclass
class ProcessingConfig:
    """Configuration for parallel processing."""
    chunk_size: int = 1000
    max_workers: int = 5


# ============================================================================
# Constants
# ============================================================================

class PrimitiveOperation(str, Enum):
    """Supported primitive operations."""
    NOTEPAD_OPEN_FILE = "NotepadOpenFile"
    VLC_OPEN_MEDIA_FILE = "VLCOpenMediaFile"
    VLC_ENQUEUE_MEDIA_FILE = "VLCEnqueueMediaFile"
    POWERPOINT_OPEN_FILE = "PowerPointOpenFile"
    POWERPOINT_INSERT_IMAGE = "PowerPointInsertImage"
    WORD_OPEN_FILE = "WordOpenFile"
    WORD_INSERT_IMAGE = "WordInsertImage"


class PreConfigType(str, Enum):
    """Pre-configuration types."""
    CREATE_FILE = "create_file"
    UPLOAD_FILE = "upload_file"
    SLEEP = "sleep"


# File extensions supported for AI content generation
SUPPORTED_EXTENSIONS = [
    '.txt', '.md', '.json', '.xml', '.html', '.csv', '.yaml', '.yml',
    '.ini', '.log', '.srt', '.py', '.js', '.ts', '.java', '.c', '.cpp', '.rst'
]

# Default paths
DEFAULT_VIDEO_PATH = "C:/Users/Docker/Videos/"
DEFAULT_DATA_PATH = "data/others/"


# ============================================================================
# AI Content Generator
# ============================================================================

class AIContentGenerator:
    """Handles AI-powered content generation using Azure OpenAI."""
    
    def __init__(self, config: AzureOpenAIConfig):
        """Initialize the AI content generator with Azure OpenAI client."""
        self.config = config
        self.client = AzureOpenAI(
            api_key=config.api_key,
            api_version=config.api_version,
            azure_endpoint=config.azure_endpoint
        )
    
    def generate_file_content(self, instruction: str, file_ext: str) -> str:
        """
        Generate file content based on instruction and file type.
        
        Args:
            instruction: Task description/instruction
            file_ext: File extension (e.g., '.txt', '.json')
            
        Returns:
            Generated file content as string
        """
        prompt = self._create_prompt(instruction, file_ext)
        
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a file content generator. Output only the file content without any explanation."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.temperature
        )
        
        return response.choices[0].message.content.strip()
    
    @staticmethod
    def _create_prompt(instruction: str, file_ext: str) -> str:
        """Create the prompt for AI content generation."""
        return f"""You must output only raw content suitable for direct writing to a text file. No explanations, wrappers, or code fences.

Task description: {instruction}
File extension: {file_ext}

Rules:
1. Generate text content only. Supported extensions like:
   {' '.join(SUPPORTED_EXTENSIONS)}
2. Content must relate to the task description and avoid sensitive or proprietary data.
3. JSON: single valid object. XML/HTML: single root element. CSV: include header if appropriate.
4. Do not include explanations, extra notes, quotes, enclosing markers, code block fences, or placeholder text.
5. Keep size reasonable: max 300 lines or 10KB.
6. Do not generate binary, Base64, hex, or disguised media content.

Output only the file content itself."""


# ============================================================================
# Pre-Configuration Builders
# ============================================================================

class PreConfigBuilder:
    """Builds pre-configuration entries for different operations."""
    
    @staticmethod
    def create_file_config(path: str, content: str) -> Dict:
        """Create a file creation pre-config entry."""
        return {
            "type": PreConfigType.CREATE_FILE.value,
            "parameters": {
                "path": path,
                "content": content
            }
        }
    
    @staticmethod
    def upload_file_config(local_path: str, remote_path: str) -> Dict:
        """Create a file upload pre-config entry."""
        return {
            "type": PreConfigType.UPLOAD_FILE.value,
            "parameters": {
                "files": [{
                    "local_path": local_path,
                    "path": remote_path
                }]
            }
        }
    
    @staticmethod
    def sleep_config(seconds: int = 2) -> Dict:
        """Create a sleep pre-config entry."""
        return {
            "type": PreConfigType.SLEEP.value,
            "parameters": {
                "seconds": seconds
            }
        }
    
    @staticmethod
    def append_to_upload_config(upload_config: Dict, local_path: str, remote_path: str) -> None:
        """Append a file to an existing upload_file config."""
        upload_config["parameters"]["files"].append({
            "local_path": local_path,
            "path": remote_path
        })


# ============================================================================
# Operation Handlers
# ============================================================================

class OperationHandler:
    """Base class for handling primitive operations."""
    
    def __init__(self, ai_generator: Optional[AIContentGenerator] = None):
        """Initialize operation handler."""
        self.ai_generator = ai_generator
        self.pre_config_builder = PreConfigBuilder()
    
    def can_handle(self, operation: str) -> bool:
        """Check if this handler can process the given operation."""
        raise NotImplementedError
    
    def handle(self, step: Dict, task_instruction: str, pre_config: List[Dict]) -> None:
        """Handle the operation and update pre_config."""
        raise NotImplementedError


class NotepadOpenFileHandler(OperationHandler):
    """Handler for NotepadOpenFile operation."""
    
    def can_handle(self, operation: str) -> bool:
        return operation == PrimitiveOperation.NOTEPAD_OPEN_FILE.value
    
    def handle(self, step: Dict, task_instruction: str, pre_config: List[Dict]) -> None:
        """Generate file content and create pre-config for opening notepad file."""
        args = step.get("arguments", {})
        path = args.get("path") or args.get("file_path")
        file_name = args.get("file_name")
        
        if not path or not file_name:
            return
        
        file_ext = Path(path).suffix
        full_path = os.path.join(path, file_name).replace("/", "\\")
        
        # Generate content using AI
        content = self.ai_generator.generate_file_content(task_instruction, file_ext)
        
        # Add create_file and sleep configs
        pre_config.append(self.pre_config_builder.create_file_config(full_path, content))
        pre_config.append(self.pre_config_builder.sleep_config())


class VLCOpenMediaFileHandler(OperationHandler):
    """Handler for VLCOpenMediaFile operation."""
    
    def can_handle(self, operation: str) -> bool:
        return operation == PrimitiveOperation.VLC_OPEN_MEDIA_FILE.value
    
    def handle(self, step: Dict, task_instruction: str, pre_config: List[Dict]) -> None:
        """Create pre-config for opening VLC media file."""
        args = step.get("arguments", {})
        file_path = args.get("file_path")
        
        if not file_path:
            return
        
        file_name = os.path.basename(file_path)
        local_path = f"{DEFAULT_DATA_PATH}{file_name}"
        remote_path = f"{DEFAULT_VIDEO_PATH}{file_name}"
        
        # Add upload_file and sleep configs
        pre_config.append(self.pre_config_builder.upload_file_config(local_path, remote_path))
        pre_config.append(self.pre_config_builder.sleep_config())


class VLCEnqueueMediaFileHandler(OperationHandler):
    """Handler for VLCEnqueueMediaFile operation."""
    
    def can_handle(self, operation: str) -> bool:
        return operation == PrimitiveOperation.VLC_ENQUEUE_MEDIA_FILE.value
    
    def handle(self, step: Dict, task_instruction: str, pre_config: List[Dict]) -> None:
        """Create or append to upload_file config for enqueuing VLC media file."""
        args = step.get("arguments", {})
        file_path = args.get("file_path")
        file_name = args.get("file_name")
        
        if not file_path or not file_name:
            return
        
        # Construct full path
        full_path = file_path if file_path.endswith(file_name) else f"{file_path}\\{file_name}"
        base_file_name = os.path.basename(full_path)
        
        local_path = f"{DEFAULT_DATA_PATH}{base_file_name}"
        remote_path = f"{DEFAULT_VIDEO_PATH}{base_file_name}"
        
        # Try to find existing upload_file config
        upload_config = self._find_upload_config(pre_config)
        
        if upload_config:
            # Append to existing upload config
            self.pre_config_builder.append_to_upload_config(upload_config, local_path, remote_path)
        else:
            # Create new upload config
            pre_config.append(self.pre_config_builder.upload_file_config(local_path, remote_path))
            pre_config.append(self.pre_config_builder.sleep_config())
    
    @staticmethod
    def _find_upload_config(pre_config: List[Dict]) -> Optional[Dict]:
        """Find existing upload_file config in pre_config list."""
        for config in pre_config:
            if config.get("type") == PreConfigType.UPLOAD_FILE.value:
                return config
        return None


class OpenFileHandler(OperationHandler):
    """Handler for OpenFile operation."""
    
    def can_handle(self, operation: str) -> bool:
        return operation == PrimitiveOperation.POWERPOINT_OPEN_FILE.value or operation == PrimitiveOperation.WORD_OPEN_FILE.value
    
    def handle(self, step: Dict, task_instruction: str, pre_config: List[Dict]) -> None:
        """Create pre-config for uploading PowerPoint file."""
        args = step.get("arguments", {})
        file_path = args.get("filename")
        
        if not file_path:
            return
        
        file_name = os.path.basename(file_path)
        local_path = f"data/data_generation/{file_path.split('asset/')[-1]}"
        remote_path = f"C:/Users/Docker/Documents/{file_name}"
        
        # Add upload_file and sleep configs
        pre_config.append(self.pre_config_builder.upload_file_config(local_path, remote_path))
        pre_config.append(self.pre_config_builder.sleep_config())

        return {
            "argument": "filename",
            "old_value": file_path,
            "new_value": remote_path
        }


class InsertImageHandler(OperationHandler):
    """Handler for InsertImage operation."""
    
    def can_handle(self, operation: str) -> bool:
        return operation == PrimitiveOperation.POWERPOINT_INSERT_IMAGE.value or operation == PrimitiveOperation.WORD_INSERT_IMAGE.value
    
    def handle(self, step: Dict, task_instruction: str, pre_config: List[Dict]) -> None:
        """Create pre-config for uploading image file to insert into PowerPoint."""
        args = step.get("arguments", {})
        image_path = args.get("image_path")
        
        if not image_path:
            return
        
        file_name = os.path.basename(image_path)
        local_path = f"data/data_generation/{image_path.split('asset/')[-1]}"
        remote_path = f"C:/Users/Docker/Documents/{file_name}"
        
        # Add upload_file and sleep configs
        pre_config.append(self.pre_config_builder.upload_file_config(local_path, remote_path))
        pre_config.append(self.pre_config_builder.sleep_config())

        return {
            "argument": "image_path",
            "old_value": image_path,
            "new_value": remote_path
        }


# ============================================================================
# Task Transformer
# ============================================================================

class TaskTransformer:
    """Transforms tasks from input format to WAA format."""
    
    def __init__(self, ai_generator: Optional[AIContentGenerator] = None):
        """Initialize task transformer with operation handlers."""
        self.ai_generator = ai_generator
        self.handlers: List[OperationHandler] = [
            NotepadOpenFileHandler(ai_generator),
            VLCOpenMediaFileHandler(ai_generator),
            VLCEnqueueMediaFileHandler(ai_generator),
            OpenFileHandler(ai_generator),
            InsertImageHandler(ai_generator)
        ]
    
    def transform_task(self, task_id: str, task_data: Dict, domain: str) -> Dict:
        """
        Transform a single task to WAA format.
        
        Args:
            task_id: Task identifier
            task_data: Task data dictionary
            domain: Domain name
            
        Returns:
            Transformed task dictionary
        """
        # Build pre-configuration
        pre_config = self._build_pre_config(task_data)

        task = {
            "id": task_data["id"],
            "instruction": task_data["instruction"],
            "domain": task_data["domain"],
            "steps": task_data["steps"]
        }
        
        if pre_config:
            task["pre_config"] = pre_config
        
        return task
    
    def _build_pre_config(self, task_data: Dict) -> List[Dict]:
        """Build pre-configuration list from task steps."""
        pre_config = []
        
        for i, step in enumerate(task_data.get("steps", [])):
            operation = step.get("primitive_operation")
            
            # Find appropriate handler
            for handler in self.handlers:
                if handler.can_handle(operation):
                    result = handler.handle(step, task_data["instruction"], pre_config)

                    if result and operation in [
                        PrimitiveOperation.POWERPOINT_OPEN_FILE.value, 
                        PrimitiveOperation.POWERPOINT_INSERT_IMAGE.value, 
                        PrimitiveOperation.WORD_OPEN_FILE.value, 
                        PrimitiveOperation.WORD_INSERT_IMAGE.value
                    ]:
                        task_data["instruction"] = task_data["instruction"].replace(
                            result["old_value"], result["new_value"]
                        )
                        task_data["steps"][i]["instruction"] = task_data["steps"][i]["instruction"].replace(
                            result["old_value"], result["new_value"]
                        )
                        task_data["steps"][i]["arguments"][result["argument"]] = result["new_value"]

                    break
        
        return pre_config


# ============================================================================
# Schema Processor
# ============================================================================

class SchemaProcessor:
    """Processes and transforms task schemas."""
    
    def __init__(self, transformer: TaskTransformer, processing_config: ProcessingConfig):
        """Initialize schema processor."""
        self.transformer = transformer
        self.processing_config = processing_config
    
    def process_single_file(
        self,
        input_schema: Dict,
        domain: str,
        related_apps: List[str],
        output_path: str
    ) -> Dict:
        """
        Process input schema into a single output file.
        
        Args:
            input_schema: Input schema dictionary or list
            domain: Domain name
            related_apps: List of related applications
            output_path: Output file path
            
        Returns:
            Transformed schema dictionary
        """
        task_items = self._prepare_task_items(input_schema)
        
        output = {
            "domain": domain,
            "related_apps": related_apps,
            "tasks": []
        }
        
        for task_id, task_data in task_items:
            task = self.transformer.transform_task(task_id, task_data, domain)
            output["tasks"].append(task)
        
        self._save_json(output, output_path)
        return output
    
    def process_parallel(
        self,
        input_schema: Dict,
        domain: str,
        related_apps: List[str],
        output_base_path: str
    ) -> List[str]:
        """
        Process input schema with parallel processing and chunking.
        
        Args:
            input_schema: Input schema dictionary or list
            domain: Domain name
            related_apps: List of related applications
            output_base_path: Base path for output files
            
        Returns:
            List of output file paths
        """
        task_items = self._prepare_task_items(input_schema)
        total_tasks = len(task_items)
        
        # Calculate chunks
        num_chunks = math.ceil(total_tasks / self.processing_config.chunk_size)
        chunks = self._create_chunks(task_items, num_chunks)
        
        print(f"Processing {total_tasks} tasks in {num_chunks} chunk(s) "
              f"with {self.processing_config.max_workers} workers...")
        
        # Process chunks in parallel
        output_files = self._process_chunks_parallel(
            chunks, domain, related_apps, output_base_path, num_chunks
        )
        
        return sorted(output_files)
    
    def _prepare_task_items(self, input_schema) -> List[Tuple[str, Dict]]:
        """Convert input schema to list of (task_id, task_data) tuples."""
        if isinstance(input_schema, dict):
            return list(input_schema.items())
        elif isinstance(input_schema, list):
            return [(task["id"], task) for task in input_schema]
        else:
            raise ValueError("Input schema must be a dictionary or list")
    
    def _create_chunks(
        self,
        task_items: List[Tuple[str, Dict]],
        num_chunks: int
    ) -> List[Tuple[List[Tuple[str, Dict]], int]]:
        """Split task items into chunks."""
        chunk_size = self.processing_config.chunk_size
        chunks = []
        
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min(start_idx + chunk_size, len(task_items))
            chunk_data = task_items[start_idx:end_idx]
            chunks.append((chunk_data, i))
        
        return chunks
    
    def _process_chunks_parallel(
        self,
        chunks: List[Tuple[List[Tuple[str, Dict]], int]],
        domain: str,
        related_apps: List[str],
        output_base_path: str,
        total_chunks: int
    ) -> List[str]:
        """Process chunks in parallel using ThreadPoolExecutor."""
        output_files = []
        
        with ThreadPoolExecutor(max_workers=self.processing_config.max_workers) as executor:
            # Submit all chunk processing tasks
            future_to_chunk = {
                executor.submit(
                    self._process_chunk,
                    chunk_data,
                    chunk_idx,
                    domain,
                    related_apps,
                    output_base_path,
                    total_chunks
                ): chunk_idx
                for chunk_data, chunk_idx in chunks
            }
            
            # Process results with progress bar
            with tqdm(total=total_chunks, desc="Processing chunks") as pbar:
                for future in as_completed(future_to_chunk):
                    chunk_idx = future_to_chunk[future]
                    try:
                        output_file = future.result()
                        output_files.append(output_file)
                        pbar.update(1)
                        print(f"✓ Chunk {chunk_idx + 1}/{total_chunks} saved to {output_file}")
                    except Exception as e:
                        print(f"✗ Error processing chunk {chunk_idx + 1}: {e}")
                        pbar.update(1)
        
        return output_files
    
    def _process_chunk(
        self,
        chunk_data: List[Tuple[str, Dict]],
        chunk_index: int,
        domain: str,
        related_apps: List[str],
        output_base_path: str,
        total_chunks: int
    ) -> str:
        """Process a single chunk and save to file."""
        output = {
            "domain": domain,
            "related_apps": related_apps,
            "tasks": []
        }
        
        # Transform each task in the chunk
        for task_id, task_data in chunk_data:
            task = self.transformer.transform_task(task_id, task_data, domain)
            output["tasks"].append(task)
        
        # Generate output filename
        output_file = self._generate_output_filename(
            output_base_path, chunk_index, total_chunks
        )
        
        # Save to file
        self._save_json(output, output_file)
        
        return output_file
    
    @staticmethod
    def _generate_output_filename(base_path: str, chunk_index: int, total_chunks: int) -> str:
        """Generate output filename with chunk suffix if needed."""
        if total_chunks > 1:
            return base_path.replace(".json", f"_part{chunk_index + 1:03d}.json")
        return base_path
    
    @staticmethod
    def _save_json(data: Dict, file_path: str) -> None:
        """Save data to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the script."""
    # Configure paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.abspath(os.path.join(script_dir, "..", "asset"))
    input_file = os.path.join(asset_dir, "user_task", "excel_tasks.json")
    output_file = os.path.join(asset_dir, "user_task", "excel_tasks_waa.json")

    # Load input data
    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    # Initialize components
    ai_config = AzureOpenAIConfig()
    ai_generator = AIContentGenerator(ai_config)
    transformer = TaskTransformer(ai_generator)
    
    processing_config = ProcessingConfig(chunk_size=1000, max_workers=5)
    processor = SchemaProcessor(transformer, processing_config)
    
    # Determine processing strategy based on data size
    num_tasks = len(input_data)
    print(f"Found {num_tasks} tasks in input file")
    
    if num_tasks > processing_config.chunk_size:
        # Use parallel processing for large datasets
        output_files = processor.process_parallel(
            input_data,
            domain="excel",
            related_apps=["Excel"],
            output_base_path=output_file
        )
        print(f"\nTransformation complete! Generated {len(output_files)} output files:")
        for file in output_files:
            print(f"  - {file}")
    else:
        # Use single-file processing for smaller datasets
        processor.process_single_file(
            input_data,
            domain="excel",
            related_apps=["Excel"],
            output_path=output_file
        )
        print(f"Transformed data saved to {output_file}")


if __name__ == "__main__":
    main()