import subprocess
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.npm_command = 'npm'
    
    def run_test(self, test_command: str) -> tuple[bool, str]:
        """
        Execute a Jest test command and return the results
        
        Args:
            test_command: The test command to execute
            
        Returns:
            tuple: (success: bool, output: str)
        """
        try:
            # Prepare the command
            command = f"{self.npm_command} test -- {test_command}"
            
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
