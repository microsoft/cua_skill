import random
import os
import string
import re
from pathlib import Path
from typing import List, Optional

def generate_via_gpt(prompt: str, **kwargs) -> str:
    # Simulate GPT response for demonstration purposes
    raise NotImplementedError("This function should call the GPT API to generate text.")


def generate_random_number(
    min_value=-10000, 
    max_value=10000, 
    return_float_prob: float = 0.5,
    **kwargs
) -> float or int:
    """
    Randomly generate an integer or float number within the specified range.
    Args:
        min_value (int): Minimum value of the range (inclusive).
        max_value (int): Maximum value of the range (inclusive).
        return_float_prob (float): Probability of returning a float number. Value between 0 and 1.
    """
    if min_value > max_value:
        raise ValueError("min_value should be less than max_value.")

    return_float = False
    if random.random() < return_float_prob:
        return_float = True
    if return_float:
        return round(random.uniform(min_value, max_value), 2)
    else:
        return random.randint(min_value, max_value)


def select_from_options(
    options: list,
    quantity=1,
    **kwargs
) -> list or str:
    if quantity > len(options):
        raise ValueError("Quantity exceeds the number of available options.")
    return random.sample(options, quantity) if quantity > 1 else random.choice(options)


def select_file_path_in_directory(
    directory: str,
    file_extensions: Optional[List[str]] = None,
    quantity: int = 1,
    **kwargs
) -> List[str]:
    """
    Select one or more random files from a directory, filtered by extensions.

    Args:
        directory: Path to the directory.
        file_extensions: List of extensions to filter (e.g., [".txt", ".json"]). 
                         If None, all files are considered.
        quantity: Number of files to select.

    Returns:
        List of absolute file paths.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"The directory {directory} does not exist.")

    files = os.listdir(directory)

    # Normalize extensions if provided
    if file_extensions:
        file_extensions = [ext.lower() for ext in file_extensions]
        files = [f for f in files if any(f.lower().endswith(ext) for ext in file_extensions)]

    if not files:
        raise ValueError(
            f"No files found in {directory} "
            f"{'with extensions ' + str(file_extensions) if file_extensions else ''}."
        )

    if quantity > len(files):
        raise ValueError("Quantity exceeds the number of available files.")

    selected_files = random.sample(files, quantity) if quantity > 1 else [random.choice(files)]
    if len(selected_files) == 1:
        # Return POSIX-style (Linux) path string
        return Path(os.path.join(directory, selected_files[0])).as_posix()
    else:
        # Return list of POSIX-style (Linux) path strings
        return [Path(os.path.join(directory, f)).as_posix() for f in selected_files]


def generate_timestamp(
    max_hours: int = 2,
    max_minutes: int = 59,
    max_seconds: int = 59,
    format: str = "hh:mm:ss",
    **kwargs
) -> str:
    """
    Generate a timestamp for media seeking.
    
    Args:
        max_hours: Maximum hours value
        max_minutes: Maximum minutes value
        max_seconds: Maximum seconds value
        format: Output format for timestamp
        **kwargs: Additional parameters
    
    Returns:
        A formatted timestamp string
    """
    
    # Generate random time components
    hours = random.randint(0, max_hours)
    minutes = random.randint(0, max_minutes)
    seconds = random.randint(0, max_seconds)
    
    # Format based on requested format
    if format == "hh:mm:ss":
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    elif format == "mm:ss":
        total_minutes = hours * 60 + minutes
        return f"{total_minutes:02d}:{seconds:02d}"
    elif format == "seconds":
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return str(total_seconds)
    else:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def generate_a1_cell(
    min_col: str = "A",
    max_col: str = "Z",
    min_row: int = 1,
    max_row: int = 100,
    **kwargs
) -> str:
    """
    Generate a random Excel cell reference in A1 notation (e.g., "B5", "AA10").
    
    Args:
        min_col: Minimum column letter (e.g., "A")
        max_col: Maximum column letter (e.g., "Z", "AA", "AZ")
        min_row: Minimum row number (inclusive)
        max_row: Maximum row number (inclusive)
        **kwargs: Additional parameters
    
    Returns:
        A cell reference string like "B5" or "AA10"
    """
    def col_to_num(col: str) -> int:
        """Convert column letter(s) to number (A=1, Z=26, AA=27, etc.)"""
        num = 0
        for char in col.upper():
            num = num * 26 + (ord(char) - ord('A') + 1)
        return num
    
    def num_to_col(num: int) -> str:
        """Convert number to column letter(s) (1=A, 26=Z, 27=AA, etc.)"""
        col = ""
        while num > 0:
            num -= 1
            col = chr(ord('A') + num % 26) + col
            num //= 26
        return col
    
    # Convert column letters to numbers
    min_col_num = col_to_num(min_col)
    max_col_num = col_to_num(max_col)
    
    # Generate random column and row
    col_num = random.randint(min_col_num, max_col_num)
    row_num = random.randint(min_row, max_row)
    
    # Convert back to A1 notation
    col = num_to_col(col_num)
    return f"{col}{row_num}"


def generate_a1_range(
    min_col: str = "A",
    max_col: str = "Z",
    min_row: int = 1,
    max_row: int = 100,
    prefer_rectangular: bool = True,
    **kwargs
) -> str:
    """
    Generate a random Excel range in A1 notation (e.g., "A1:C10", "B5:B20").
    
    Args:
        min_col: Minimum column letter (e.g., "A")
        max_col: Maximum column letter (e.g., "Z")
        min_row: Minimum row number (inclusive)
        max_row: Maximum row number (inclusive)
        prefer_rectangular: If True, generates rectangular ranges (both columns and rows differ).
                           If False, can generate single-column or single-row ranges.
        **kwargs: Additional parameters
    
    Returns:
        A range reference string like "A1:C10" or "B5:B20"
    """
    def col_to_num(col: str) -> int:
        """Convert column letter(s) to number (A=1, Z=26, AA=27, etc.)"""
        num = 0
        for char in col.upper():
            num = num * 26 + (ord(char) - ord('A') + 1)
        return num
    
    def num_to_col(num: int) -> str:
        """Convert number to column letter(s) (1=A, 26=Z, 27=AA, etc.)"""
        col = ""
        while num > 0:
            num -= 1
            col = chr(ord('A') + num % 26) + col
            num //= 26
        return col
    
    # Convert column letters to numbers
    min_col_num = col_to_num(min_col)
    max_col_num = col_to_num(max_col)
    
    # Generate two random cells
    start_col_num = random.randint(min_col_num, max_col_num)
    end_col_num = random.randint(min_col_num, max_col_num)
    start_row = random.randint(min_row, max_row)
    end_row = random.randint(min_row, max_row)
    
    # Ensure start is before end
    if start_col_num > end_col_num:
        start_col_num, end_col_num = end_col_num, start_col_num
    if start_row > end_row:
        start_row, end_row = end_row, start_row
    
    # If prefer_rectangular, ensure we have a multi-cell range
    if prefer_rectangular:
        # Make sure it's not a single cell
        if start_col_num == end_col_num and start_row == end_row:
            # Expand the range
            if end_col_num < max_col_num:
                end_col_num += 1
            elif start_col_num > min_col_num:
                start_col_num -= 1
            
            if end_row < max_row:
                end_row += 1
            elif start_row > min_row:
                start_row -= 1
    
    # Convert to A1 notation
    start_col = num_to_col(start_col_num)
    end_col = num_to_col(end_col_num)
    
    return f"{start_col}{start_row}:{end_col}{end_row}"
