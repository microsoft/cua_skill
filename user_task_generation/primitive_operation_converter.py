import json
import os
import logging
from argument_value_generator import ARGUMENT_GENERATORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def convert_template_to_generator(template_file, output_file):
    """
    Convert primitive_operation_template to primitive_operation_with_argument_generator format.
    """
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            output = json.load(f)
        if all(arg in output for arg in ["value_func", "name", "description", "optional"]):
            logger.info(f"Output file {output_file} is existing and already in good format, skipping conversion")
            return

    with open(template_file, 'r', encoding='utf-8') as f:
        template = json.load(f)
    
    converted = {}
    
    for op_name, op_spec in template.items():
        converted_op = {
            "instructions": op_spec.get("task_description_variants", []),
            "arguments": []
        }
        
        for arg in op_spec.get("arguments", []):
            converted_arg = {
                "name": arg["name"],
                "description": arg["description"],
                "optional": False  # [Question]: How do I know if an argument is optional or not? [Answer]: If the argument is not mentioned in the task description, then it is optional.
            }
            
            # Map argument to appropriate generator based on name and description
            value_func = map_argument_to_generator(arg)
            if value_func:
                converted_arg["value_func"] = value_func
            
            converted_op["arguments"].append(converted_arg)
        
        converted[op_name] = converted_op
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)
    
    return converted

def map_argument_to_generator(arg):
    """
    Map an argument from template to appropriate value_func configuration.
    """
    name = arg.get("name", "").lower()
    description = arg.get("description", "").lower()
    dtype = arg.get("dtype", "")
    
    # Query arguments
    if "query" in name or "search" in description:
        if "image" in description:
            return {
                "name": "generate_browser_query",  # [Question]: bingsearch file uses "generate_bing_query" but we only have the function "generate_browser_query"
                "arguments": {
                    "mode": "images",
                    "language": "English",
                    "allow_operators": True,
                    "min_terms": 2,
                    "max_terms": 7
                }
            }
        elif "video" in description:
            return {
                "name": "generate_browser_query",
                "arguments": {
                    "mode": "videos",
                    "language": "English",
                    "allow_operators": True, # [Question]: what is this for?
                    "min_terms": 2,
                    "max_terms": 7
                }
            }
        elif "news" in description:
            return {
                "name": "generate_browser_query",
                "arguments": {
                    "mode": "news",
                    "language": "English",
                    "allow_operators": True,
                    "min_terms": 2,
                    "max_terms": 7
                }
            }
        elif "file" in description or "onedrive" in description:
            return {
                "name": "generate_file_drive_search_query",
                "arguments": {
                    "use_filters_prob": 0.3,
                    "min_terms": 1,
                    "max_terms": 5
                }
            }
        else:
            return {
                "name": "generate_browser_query",
                "arguments": {
                    "mode": "web",
                    "language": "English",
                    "allow_operators": True,
                    "min_terms": 2,
                    "max_terms": 7
                }
            }
    
    # Location arguments
    if "location" in name or "location" in description:
        return {
            "name": "generate_location",
            "arguments": {}
        }
    
    # Product arguments
    if "product" in name:
        return {
            "name": "generate_product_name",
            "arguments": {
                "complexity": "moderate",
                "include_brand": False,
                "include_modifier": True
            }
        }
    
    # Index/number arguments
    if "index" in name or dtype == "int":
        return {
            "name": "generate_random_number",
            "arguments": {
                "min_value": 1,
                "max_value": 10,
                "return_float_prob": 0
            }
        }
    
    # URL arguments
    if "url" in name:
        return {
            "name": "generate_string",
            "arguments": {
                "max_length": 120,
                "min_length": 12,
                "pattern": "https?://[a-zA-Z0-9._%+-/=?&#]+"
            }
        }
    
    # Text/string arguments
    if dtype == "str":
        if "number" in name:
            return {
                "name": "generate_random_number",
                "arguments": {
                    "min_value": -99999,
                    "max_value": 99999,
                    "return_float_prob": 0.5
                }
            }
        else:
            return {
                "name": "generate_string",
                "arguments": {
                    "max_length": 140,
                    "min_length": 10,
                    "pattern": "[A-Za-z0-9 ,.'!?\\-]+"
                }
            }

    # Email arguments
    if "email" in name:
        return {
            "name": "generate_email",
            "arguments": {
                "max_length": 40,
                "min_length": 6
          }
        }
    
    # datetime arguments
    if "datetime" in name:
        return {
            "name": "generate_datetime_range_iso",
            "arguments": {
                "return_field": "start",
                "min_minutes_from_now": 30,
                "max_minutes_from_now": 10080 # 1 week
            }
        }
    
    # # common arguments
    # if "common" in name:
    #     return {
    #         "name": "generate_common_argument",
    #         "arguments": {}
    #     }

    # media arguments
    if "media" in name:
        return {
            "name": "generate_media_args",
            "arguments": {}
        }

    # notepad arguments
    if "notepad" in name:
        return {
            "name": "generate_notepad_args",
            "arguments": {}
        }

    # setting arguments
    if "setting" in name and "value" in name:
        return {
            "name": "generate_setting_value",
            "arguments": {
            "setting_name_arg": "setting_name",
            "rules": {
              "Display brightness": {
                "type": "number",
                "min": 0,
                "max": 100,
                "step": 5,
                "suffix": "%"
              },
              "Volume": {
                "type": "number",
                "min": 0,
                "max": 100,
                "step": 5,
                "suffix": "%"
              },
              "Scale": {
                "type": "options",
                "options": [
                  "100%",
                  "125%",
                  "150%",
                  "175%",
                  "200%"
                ]
              },
              "Text size": {
                "type": "options",
                "options": [
                  "100%",
                  "110%",
                  "125%",
                  "150%"
                ]
              },
              "Refresh rate": {
                "type": "options",
                "options": [
                  "60 Hz",
                  "75 Hz",
                  "120 Hz",
                  "144 Hz"
                ]
              },
              "Power mode": {
                "type": "options",
                "options": [
                  "Best power efficiency",
                  "Balanced",
                  "Best performance"
                ]
              },
              "Screen timeout": {
                "type": "options",
                "options": [
                  "5 minute",
                  "10 minutes",
                  "15 minutes",
                  "20 minutes",
                  "25 minutes",
                  "30 minutes",
                  "Never"
                ]
              },
              "Output device": {
                "type": "options",
                "options": [
                  "Speakers (Realtek® Audio)",
                  "Headphones (Bluetooth)",
                  "HDMI (Monitor)"
                ]
              },
              "Input device": {
                "type": "options",
                "options": [
                  "Microphone Array",
                  "USB Microphone",
                  "Line In"
                ]
              },
              "Mouse pointer size": {
                "type": "number",
                "min": 1,
                "max": 15,
                "step": 1
              },
              "__default__": {
                "type": "options",
                "options": [
                  "Apply",
                  "On",
                  "Off"
                ]
              }
            }
          }
        }

    # snipping tool arguments
    if "snipping" in name:
        return {
            "name": "generate_snip_file", # [Question]: in "snipping_tool_primitive_operation.json", the function is "generate_snip_filename"
            "arguments": {}
        }

    return None


def find_missing_operations(primitive_operation_template_folder: str, primitive_operation_with_argument_generator_folder: str):
    """
    Find missing files in the primitive_operation_with_argument_generator_folder compared to the primitive_operation_template_folder.
    """
    missing_files = []
    for file in os.listdir(primitive_operation_template_folder):
        if file.endswith("_primitive_operation.json"):
            if file not in os.listdir(primitive_operation_with_argument_generator_folder):
                missing_files.append(file)
    return missing_files

def main():
    primitive_operation_template_folder = R"./asset/primitive_operation_template"
    primitive_operation_with_argument_generator_folder = R"./asset/primitive_operation_with_argument_generator"
    
    missing_files = find_missing_operations(primitive_operation_template_folder, primitive_operation_with_argument_generator_folder)
    logger.info(f"Files to convert: {missing_files}")
    logger.info(f"Total files to convert: {len(missing_files)}")

    for idx, file in enumerate(missing_files, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing file {idx}/{len(missing_files)}: {file}")
        logger.info(f"{'='*60}")
        try:
            convert_template_to_generator(
                os.path.join(primitive_operation_template_folder, file), 
                os.path.join(primitive_operation_with_argument_generator_folder, file)
            )
            logger.info(f"✓ Successfully converted {file}")
        except Exception as e:
            logger.error(f"✗ Failed to convert {file}: {type(e).__name__}: {str(e)}")
            logger.exception("Full traceback:")
            raise  # Re-raise to stop execution on error

if __name__ == "__main__":
    main()