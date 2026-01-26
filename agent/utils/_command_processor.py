import subprocess  # Used to run external shell commands

class CommandProcessor:
    """
    A utility class for running Windows shell commands and returning
    their result as a tuple of (error_code, error_message).
    """

    @staticmethod
    def run_shell_command(command: str) -> tuple[int, str]:
        """
        Executes a shell command.

        Parameters:
            command (str): The shell command to execute (e.g., "start calc").

        Returns:
            tuple[int, str]: A tuple containing:
                - error code (0 if successful, non-zero otherwise)
                - error message (empty string if no error)
        """
        try:
            # Run the command using the Windows shell
            result = subprocess.run(
                command,
                shell=True,               # Allows use of shell features like "start"
                check=True,               # Raises CalledProcessError on non-zero exit
                stdout=subprocess.PIPE,   # Capture standard output
                stderr=subprocess.PIPE,   # Capture standard error
                text=True,                # Return stdout/stderr as strings instead of bytes
                timeout=30                # Timeout after 30 seconds                
            )
            return (0, "")  # Command succeeded
        except subprocess.CalledProcessError as e:
            # Command failed: return the error code and the stderr output (or fallback message)
            return (e.returncode, e.stderr.strip() or "Shell returned an error.")
        except Exception as e:
            # Some other unexpected error occurred: return generic -1 and exception message
            return (-1, str(e).strip())
