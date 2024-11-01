from pathlib import Path
import re

def scan_test_files(directory: str) -> list[Path]:
    """
    Scan a directory for Jest test files
    
    Args:
        directory: Directory path to scan
        
    Returns:
        list: List of paths to test files
    """
    test_patterns = [
        "**/*.test.js",
        "**/*.test.jsx",
        "**/*.test.ts",
        "**/*.test.tsx",
        "**/__tests__/**/*.js",
        "**/__tests__/**/*.jsx",
        "**/__tests__/**/*.ts",
        "**/__tests__/**/*.tsx"
    ]
    
    test_files = []
    directory_path = Path(directory)
    
    for pattern in test_patterns:
        test_files.extend(directory_path.glob(pattern))
    
    return sorted(test_files)

def parse_test_commands(test_files: list[Path]) -> list[str]:
    """
    Parse test files to extract available test commands
    
    Args:
        test_files: List of test file paths
        
    Returns:
        list: List of available test commands
    """
    commands = []
    
    for test_file in test_files:
        # Add the file path as a command to run all tests in the file
        commands.append(str(test_file))
        
        # Read the file and extract describe/test blocks
        try:
            content = test_file.read_text()
            
            # Find test names using regex
            describe_blocks = re.findall(r'describe\([\'"](.+?)[\'"]\s*,', content)
            test_blocks = re.findall(r'test\([\'"](.+?)[\'"]\s*,', content)
            it_blocks = re.findall(r'it\([\'"](.+?)[\'"]\s*,', content)
            
            # Add specific test patterns
            for describe in describe_blocks:
                commands.append(f"-t '{describe}'")
            
            for test in test_blocks + it_blocks:
                commands.append(f"-t '{test}'")
                
        except Exception:
            continue
    
    return sorted(set(commands))
