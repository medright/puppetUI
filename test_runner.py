import subprocess
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.npm_command = 'npm'
    
    def run_test(self, test_pattern: str) -> tuple[bool, str]:
        """
        Execute a Jest test command and return the results
        
        Args:
            test_pattern: The test pattern (file path or test name pattern)
            
        Returns:
            tuple: (success: bool, output: str)
        """
        try:
            # Check if the pattern is a file path or a test pattern
            is_file = Path(test_pattern).exists()
            
            # Prepare the command
            if is_file:
                command = f"{self.npm_command} test {test_pattern}"
            else:
                # Remove the leading "-t '" and trailing "'" for proper command formatting
                pattern = test_pattern[4:-1] if test_pattern.startswith("-t '") else test_pattern
                command = f"{self.npm_command} test -- -t \"{pattern}\""
            
            # Execute the command and capture output
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Get output and error streams
            output, error = process.communicate()
            
            # Combine output and error for complete logs
            full_output = output + error
            
            # Check if the test passed
            success = process.returncode == 0
            
            return success, full_output
            
        except Exception as e:
            return False, f"Error executing test: {str(e)}"
