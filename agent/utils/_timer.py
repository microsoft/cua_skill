import time

class Timer:
    """
    A context manager class for timing the duration of a block of code.

    Attributes:
        title (str): A descriptive label for the timed code block.
        auto_display (bool): Whether to automatically print the timing result upon exiting the block.
        duration (float): Time in seconds that the block took to execute.
        message (str): Formatted timing message.

    Example Usage:
        >>> with Timer():
        ...     sum(range(10_000_000))
        ⏱ [Code Block] took 0.323456 seconds.

        >>> with Timer(title="Data Load", auto_display=False) as t:
        ...     time.sleep(1.5)
        >>> print(t.message)
        ⏱ [Data Load] took 1.500123 seconds.
    """

    def __init__(self, title: str = "Code Block", auto_display: bool = True):
        """
        Initializes the Timer context manager.

        Args:
            title (str): A label to identify the timed block. Defaults to "Code Block".
            auto_display (bool): Whether to automatically print the result when done. Defaults to True.
        """
        self.auto_display = auto_display  # Controls whether the timer result is printed
        self.duration = None              # Duration (in seconds) the block took to run
        self.title = title                # Label/title of the code block
        self.message = "No Info"          # Message to store formatted output

    def __enter__(self):
        """
        Starts the timer when entering the context.
        
        Returns:
            self: So that duration and message can be accessed outside the block.
        """
        self.start = time.perf_counter()  # Use high-resolution timer
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stops the timer and optionally prints the result when exiting the context.

        Args:
            exc_type: The type of exception (if any).
            exc_value: The exception instance (if any).
            traceback: The traceback object (if any).
        """
        self.end = time.perf_counter()  # Record end time
        self.duration = self.end - self.start  # Calculate elapsed time

        # Create the formatted output message
        self.message = f"⏱ [{self.title}] took {self.duration:.6f} seconds."

        # Display the message if enabled
        if self.auto_display:
            print(self.message)
