import json
from pathlib import Path
from typing import List, Dict

class PresetManager:
    def __init__(self, presets_file: str = "test_presets.json"):
        self.presets_file = Path(presets_file)
        self._ensure_presets_file()
    
    def _ensure_presets_file(self):
        """Create presets file if it doesn't exist"""
        if not self.presets_file.exists():
            self.save_presets({})
    
    def load_presets(self) -> Dict[str, List[str]]:
        """Load saved test presets"""
        try:
            with open(self.presets_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_presets(self, presets: Dict[str, List[str]]) -> bool:
        """Save test presets to file"""
        try:
            with open(self.presets_file, 'w') as f:
                json.dump(presets, f, indent=2)
            return True
        except Exception:
            return False
    
    def add_preset(self, name: str, test_commands: List[str]) -> bool:
        """Add a new preset"""
        presets = self.load_presets()
        presets[name] = test_commands
        return self.save_presets(presets)
    
    def delete_preset(self, name: str) -> bool:
        """Delete a preset"""
        presets = self.load_presets()
        if name in presets:
            del presets[name]
            return self.save_presets(presets)
        return False
