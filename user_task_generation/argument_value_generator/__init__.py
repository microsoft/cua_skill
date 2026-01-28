from .generate_common_argument import *
from .generate_string import *
from .generate_browser_query import *
from .generate_location import *
from .generate_datetime_range_iso import *
from .generate_setting_value import *
from .generate_file_drive_search_query import *
from .generate_snip_file import *
from .generate_email import *
from .generate_product_name import *
from .generate_media_args import *
from .generate_notepad_args import *
from .generate_list import *


ARGUMENT_GENERATORS = {
    "select_from_options": select_from_options,
    "select_file_path_in_directory": select_file_path_in_directory,
    "generate_random_number": generate_random_number,
    "generate_string": generate_string,
    "generate_location": generate_location,
    "generate_browser_query": generate_browser_query,
    "generate_datetime_range_iso": generate_datetime_range_iso,
    "generate_setting_value": generate_setting_value,
    "generate_file_drive_search_query": generate_file_drive_search_query,
    "generate_snip_file": generate_snip_file,
    "generate_email": generate_email,
    "generate_product_name": generate_product_name,
    "generate_media_file_path": generate_media_file_path,
    "generate_subtitle_filename": generate_subtitle_filename,
    "generate_stream_url": generate_stream_url,
    "generate_timestamp": generate_timestamp,
    "generate_filename": generate_filename,
    "generate_text_content": generate_text_content,
    "generate_list_items": generate_list_items,
    "generate_url": generate_url,
    "generate_file_path": generate_file_path,
    "generate_list": generate_list,
    "generate_a1_cell": generate_a1_cell,
    "generate_a1_range": generate_a1_range
}