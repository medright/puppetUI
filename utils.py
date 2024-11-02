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

def parse_test_blocks(content: str) -> list[dict]:
    """
    Parse describe, test, and it blocks from test file content
    
    Args:
        content: Test file content
        
    Returns:
        list: List of test block information
    """
    test_blocks = []
    
    # Find all describe blocks with their content
    describe_pattern = r'describe\([\'"](.+?)[\'"]\s*,\s*\(\s*\)\s*=>\s*{([^}]+)}'
    describe_matches = re.finditer(describe_pattern, content, re.DOTALL)
    
    for describe_match in describe_matches:
        describe_name = describe_match.group(1)
        describe_content = describe_match.group(2)
        
        # Find test/it blocks within describe block
        test_pattern = r'(?:test|it)\([\'"](.+?)[\'"]\s*,'
        test_matches = re.finditer(test_pattern, describe_content)
        
        for test_match in test_matches:
            test_name = test_match.group(1)
            test_blocks.append({
                'describe': describe_name,
                'test': test_name,
                'pattern': f"-t '{describe_name} {test_name}'"
            })
    
    # Find standalone test/it blocks
    standalone_pattern = r'(?:test|it)\([\'"](.+?)[\'"]\s*,'
    standalone_matches = re.finditer(standalone_pattern, content)
    
    for match in standalone_matches:
        test_name = match.group(1)
        if not any(block['test'] == test_name for block in test_blocks):
            test_blocks.append({
                'describe': None,
                'test': test_name,
                'pattern': f"-t '{test_name}'"
            })
    
    return test_blocks

def parse_test_commands(test_files: list[Path]) -> list[dict]:
    """
    Parse test files to extract available test commands and patterns
    
    Args:
        test_files: List of test file paths
        
    Returns:
        list: List of test commands with metadata
    """
    commands = []
    
    for test_file in test_files:
        # Add the file path as a command to run all tests in the file
        file_command = {
            'file': str(test_file),
            'type': 'file',
            'name': str(test_file),
            'pattern': str(test_file)
        }
        commands.append(file_command)
        
        # Read the file and extract test blocks
        try:
            content = test_file.read_text()
            test_blocks = parse_test_blocks(content)
            
            for block in test_blocks:
                command = {
                    'file': str(test_file),
                    'type': 'test',
                    'name': f"{block['describe'] + ' > ' if block['describe'] else ''}{block['test']}",
                    'pattern': block['pattern']
                }
                commands.append(command)
                
        except Exception:
            continue
    
    return commands
