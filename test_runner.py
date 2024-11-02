import subprocess
from pathlib import Path
import re
import streamlit as st
import json
import shutil

class TestRunner:
    def __init__(self, project_dir: str = None):
        self.npm_command = 'npm'
        self.project_dir = self._validate_project_dir(project_dir or str(Path.cwd()))
        self._ensure_configs()
    
    def _validate_project_dir(self, directory: str) -> str:
        """Validate the project directory exists and contains package.json"""
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise ValueError(f"Project directory does not exist: {directory}")
            
        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
            
        package_json = dir_path / 'package.json'
        if not package_json.exists():
            raise ValueError(f"No package.json found in directory: {directory}")
            
        return str(dir_path)

    def _ensure_configs(self):
        """Ensure both Jest and Jest Puppeteer configs exist"""
        # Jest Puppeteer config
        puppeteer_config = """
module.exports = {
  launch: {
    headless: 'new',
    args: ['--no-sandbox']
  },
  server: {
    command: 'npm start',
    port: 3000,
    launchTimeout: 10000,
    debug: true,
  },
}
"""
        # Jest config
        jest_config = """
module.exports = {
  preset: 'jest-puppeteer',
  testEnvironment: 'node',
  setupFilesAfterEnv: ['expect-puppeteer'],
  testMatch: [
    '**/__tests__/**/*.test.js',
    '**/?(*.)+(spec|test).js'
  ],
  testTimeout: 30000,
  verbose: true
}
"""
        
        # Write Jest Puppeteer config
        puppeteer_config_path = Path(self.project_dir) / 'jest-puppeteer.config.js'
        if not puppeteer_config_path.exists():
            with open(puppeteer_config_path, 'w') as f:
                f.write(puppeteer_config.strip())
            st.success("Created jest-puppeteer.config.js")

        # Write Jest config
        jest_config_path = Path(self.project_dir) / 'jest.config.js'
        if not jest_config_path.exists():
            with open(jest_config_path, 'w') as f:
                f.write(jest_config.strip())
            st.success("Created jest.config.js")

    def run_test(self, test_pattern: str) -> tuple[bool, str]:
        """Execute a Jest test command and return the results"""
        try:
            # Get the test file path
            test_path = None
            if test_pattern.endswith('.test.js'):
                # If it's a direct file path
                test_path = Path(test_pattern)
            else:
                # If it's a test name pattern, find the containing file
                for root, _, files in Path(self.project_dir).glob('**/*.test.js'):
                    for file in files:
                        full_path = root / file
                        if test_pattern in full_path.read_text():
                            test_path = full_path
                            break
                    if test_path:
                        break

            if not test_path:
                return False, f"Could not locate test file for pattern: {test_pattern}"

            # Ensure we're using absolute paths
            test_path = test_path.resolve()
            
            # Build the command
            if test_pattern.startswith("-t '"):
                # For test name patterns
                test_name = test_pattern[4:-1]  # Remove "-t '" prefix and trailing "'"
                cmd = f"{self.npm_command} test -- -t \"{test_name}\""
            else:
                # For file paths, use relative path from project directory
                relative_path = test_path.relative_to(Path(self.project_dir))
                cmd = f"{self.npm_command} test {relative_path}"
            
            # Log execution details
            st.write(f"🔧 Executing command: `{cmd}`")
            st.write(f"📂 Working directory: {self.project_dir}")
            
            # Execute the command from the project directory
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.project_dir)
            )
            
            try:
                output, error = process.communicate(timeout=300)
                
                if output:
                    st.write("📤 Raw output:")
                    st.code(output, language="bash")
                if error:
                    st.write("⚠️ Error output:")
                    st.code(error, language="bash")
                
                full_output = f"Command: {cmd}\nWorking Directory: {self.project_dir}\n\n"
                if output:
                    full_output += f"Output:\n{output}\n"
                if error:
                    full_output += f"Errors:\n{error}\n"
                
                success = process.returncode == 0
                return success, full_output
                
            except subprocess.TimeoutExpired:
                process.kill()
                st.error("⏰ Test execution timed out after 5 minutes")
                return False, "Error: Test execution timed out after 5 minutes"
            
        except Exception as e:
            error_msg = f"Error executing test: {str(e)}\n"
            error_msg += f"Command attempted: {test_pattern}\n"
            error_msg += f"Working directory: {self.project_dir}\n"
            st.error(f"⚠️ {error_msg}")
            return False, error_msg
