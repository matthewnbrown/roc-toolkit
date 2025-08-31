import time
import traceback
from datetime import datetime, timedelta
from typing import Optional, Callable
import os


class ExceptionHandler:
    """
    Handles unhandled exceptions with configurable timeout and retry behavior.
    """
    
    def __init__(self, log_file_path: str = None):
        if log_file_path is None:
            current_day_timestamp = datetime.now().strftime("%Y-%m-%d")
            log_file_path = f"logs/exceptions_{current_day_timestamp}.log"
        self.log_file_path = log_file_path
        self.error_count = 0
        self.last_error_time = datetime.now() - timedelta(minutes=5)
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure the log directory exists."""
        log_dir = os.path.dirname(self.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def log_exception(self, exception: Exception, error_count: int, 
                     time_since_last_error: timedelta) -> None:
        """
        Log exception details to file.
        
        Args:
            exception: The exception that occurred
            error_count: Current error count
            time_since_last_error: Time since the last error
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"""
{'='*80}
EXCEPTION LOG ENTRY - {timestamp}
{'='*80}
Error Count: {error_count}
Time Since Last Error: {time_since_last_error}
Exception Type: {type(exception).__name__}
Exception Message: {str(exception)}
Traceback:
{traceback.format_exc()}
{'='*80}
"""
        
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Failed to write to exception log: {e}")
    
    def handle_exception(self, exception: Exception, 
                        enable_timeout: bool = True,
                        timeout_minutes: int = 30,
                        on_timeout_complete: Optional[Callable] = None) -> bool:
        """
        Handle an unhandled exception with configurable timeout behavior.
        
        Args:
            exception: The exception that occurred
            enable_timeout: Whether to enable timeout and retry
            timeout_minutes: Number of minutes to wait before retrying
            on_timeout_complete: Optional callback function to call after timeout
            
        Returns:
            bool: True if the program should continue running, False if it should exit
        """
        self.error_count += 1
        time_since_last_error = datetime.now() - self.last_error_time
        self.last_error_time = datetime.now()
        
        # Log the exception
        self.log_exception(exception, self.error_count, time_since_last_error)
        
        # Print user-friendly error message
        print(f"\n{'='*60}")
        print(f"UNHANDLED EXCEPTION #{self.error_count}")
        print(f"Exception: {type(exception).__name__}: {exception}")
        print(f"Time since last error: {time_since_last_error}")
        print(f"Exception logged to: {self.log_file_path}")
        print(f"{'='*60}")
        
        if enable_timeout:
            print(f"\nException timeout is ENABLED")
            print(f"Waiting {timeout_minutes} minutes before retrying...")
            print("Press Ctrl+C to exit immediately")
            
            try:
                time.sleep(timeout_minutes * 60)
                print("\nTimeout completed. Restarting...")
                
                # Call optional callback function
                if on_timeout_complete:
                    on_timeout_complete()
                    
                return True  # Continue running
                
            except KeyboardInterrupt:
                print("\nInterrupted by user. Exiting...")
                return False  # Exit program
        else:
            print(f"\nException timeout is DISABLED")
            print("Using default error handling...")
            return True  # Continue with default handling
    
    def get_error_stats(self) -> dict:
        """Get current error statistics."""
        return {
            'error_count': self.error_count,
            'last_error_time': self.last_error_time,
            'time_since_last_error': datetime.now() - self.last_error_time
        }
