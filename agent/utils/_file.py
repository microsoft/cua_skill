import os
import shutil
from typing import List, Optional


class File:
    @staticmethod
    def read_file(path: str, encoding: str = "utf-8") -> Optional[str]:
        """Reads the entire contents of a file as a string."""
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except FileNotFoundError:
            return None

    @staticmethod
    def write_file(path: str, content: str, encoding: str = "utf-8", overwrite: bool = True) -> bool:
        """Writes a string to a file. Overwrites by default."""
        mode = 'w' if overwrite else 'x'
        try:
            with open(path, mode, encoding=encoding) as f:
                f.write(content)
            return True
        except FileExistsError:
            return False

    @staticmethod
    def exists(path: str) -> bool:
        """Checks whether the file exists."""
        return os.path.exists(path)

    @staticmethod
    def delete(path: str) -> bool:
        """Deletes the file if it exists."""
        if File.exists(path):
            os.remove(path)
            return True
        return False

    @staticmethod
    def copy(src: str, dest: str, overwrite: bool = True) -> bool:
        """Copies a file from src to dest. Overwrites if allowed."""
        if not File.exists(src):
            return False
        if not overwrite and File.exists(dest):
            return False
        shutil.copy2(src, dest)
        return True

    @staticmethod
    def move(src: str, dest: str, overwrite: bool = True) -> bool:
        """Moves a file from src to dest."""
        if not File.exists(src):
            return False
        if not overwrite and File.exists(dest):
            return False
        shutil.move(src, dest)
        return True

    @staticmethod
    def list_files(directory: str, extension_filter: Optional[str] = None) -> List[str]:
        """Lists all files in a directory. Can filter by file extension."""
        if not os.path.isdir(directory):
            return []
        files = [
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
        if extension_filter:
            files = [f for f in files if f.endswith(extension_filter)]
        return files

    @staticmethod
    def append_to_file(path: str, content: str, encoding: str = "utf-8") -> bool:
        """Appends a string to the end of a file."""
        try:
            with open(path, 'a', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception:
            return False

    @staticmethod
    def get_file_size(path: str) -> Optional[int]:
        """Returns the size of the file in bytes."""
        if not File.exists(path):
            return None
        return os.path.getsize(path)

    @staticmethod
    def get_modified_time(path: str) -> Optional[float]:
        """Returns the last modified time of the file as a Unix timestamp."""
        if not File.exists(path):
            return None
        return os.path.getmtime(path)
