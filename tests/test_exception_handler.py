import unittest
import tempfile
import os
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from rocalert.services.exception_handler import ExceptionHandler


class TestExceptionHandler(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary log file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test_exceptions.log")
        self.handler = ExceptionHandler(log_file_path=self.log_file)
    
    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test that ExceptionHandler initializes correctly."""
        self.assertEqual(self.handler.error_count, 0)
        self.assertIsInstance(self.handler.last_error_time, datetime)
        self.assertEqual(self.handler.log_file_path, self.log_file)
    
    def test_log_directory_creation(self):
        """Test that log directory is created if it doesn't exist."""
        # Create handler with non-existent directory
        test_dir = os.path.join(self.temp_dir, "nonexistent")
        test_log_file = os.path.join(test_dir, "exceptions.log")
        
        handler = ExceptionHandler(log_file_path=test_log_file)
        
        # Check that directory was created
        self.assertTrue(os.path.exists(test_dir))
        
        # Clean up
        os.rmdir(test_dir)
    
    def test_log_exception(self):
        """Test that exceptions are logged correctly."""
        test_exception = ValueError("Test exception message")
        
        # Log an exception
        self.handler.log_exception(
            exception=test_exception,
            error_count=1,
            time_since_last_error=timedelta(minutes=5)
        )
        
        # Check that log file was created and contains the exception
        self.assertTrue(os.path.exists(self.log_file))
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.assertIn("Test exception message", log_content)
        self.assertIn("ValueError", log_content)
        self.assertIn("Error Count: 1", log_content)
    
    def test_handle_exception_with_timeout_enabled(self):
        """Test exception handling with timeout enabled."""
        test_exception = RuntimeError("Test runtime error")
        
        # Mock time.sleep to avoid actual waiting
        with patch('time.sleep') as mock_sleep:
            result = self.handler.handle_exception(
                exception=test_exception,
                enable_timeout=True,
                timeout_minutes=30
            )
        
        # Check that sleep was called with correct duration
        mock_sleep.assert_called_once_with(30 * 60)
        
        # Check that error count was incremented
        self.assertEqual(self.handler.error_count, 1)
        
        # Should return True to continue running
        self.assertTrue(result)
    
    def test_handle_exception_with_timeout_disabled(self):
        """Test exception handling with timeout disabled."""
        test_exception = RuntimeError("Test runtime error")
        
        result = self.handler.handle_exception(
            exception=test_exception,
            enable_timeout=False,
            timeout_minutes=30
        )
        
        # Check that error count was incremented
        self.assertEqual(self.handler.error_count, 1)
        
        # Should return True to continue running
        self.assertTrue(result)
    
    def test_handle_exception_keyboard_interrupt(self):
        """Test that KeyboardInterrupt during timeout returns False."""
        test_exception = RuntimeError("Test runtime error")
        
        # Mock time.sleep to raise KeyboardInterrupt
        with patch('time.sleep', side_effect=KeyboardInterrupt):
            result = self.handler.handle_exception(
                exception=test_exception,
                enable_timeout=True,
                timeout_minutes=30
            )
        
        # Should return False to exit program
        self.assertFalse(result)
    
    def test_handle_exception_with_callback(self):
        """Test exception handling with callback function."""
        test_exception = RuntimeError("Test runtime error")
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        # Mock time.sleep to avoid actual waiting
        with patch('time.sleep'):
            result = self.handler.handle_exception(
                exception=test_exception,
                enable_timeout=True,
                timeout_minutes=30,
                on_timeout_complete=test_callback
            )
        
        # Check that callback was called
        self.assertTrue(callback_called)
        self.assertTrue(result)
    
    def test_get_error_stats(self):
        """Test getting error statistics."""
        # Log an exception first
        test_exception = ValueError("Test exception")
        self.handler.log_exception(
            exception=test_exception,
            error_count=1,
            time_since_last_error=timedelta(minutes=5)
        )
        
        stats = self.handler.get_error_stats()
        
        self.assertIn('error_count', stats)
        self.assertIn('last_error_time', stats)
        self.assertIn('time_since_last_error', stats)
        
        self.assertEqual(stats['error_count'], 0)  # log_exception doesn't increment count
        self.assertIsInstance(stats['last_error_time'], datetime)
        self.assertIsInstance(stats['time_since_last_error'], timedelta)
    
    def test_multiple_exceptions(self):
        """Test handling multiple exceptions."""
        test_exception1 = ValueError("First exception")
        test_exception2 = RuntimeError("Second exception")
        
        # Mock time.sleep to avoid actual waiting
        with patch('time.sleep'):
            # Handle first exception
            result1 = self.handler.handle_exception(
                exception=test_exception1,
                enable_timeout=True,
                timeout_minutes=30
            )
            
            # Handle second exception
            result2 = self.handler.handle_exception(
                exception=test_exception2,
                enable_timeout=True,
                timeout_minutes=30
            )
        
        # Check that error count was incremented twice
        self.assertEqual(self.handler.error_count, 2)
        self.assertTrue(result1)
        self.assertTrue(result2)


if __name__ == '__main__':
    unittest.main()
