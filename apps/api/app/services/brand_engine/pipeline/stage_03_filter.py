import re

class Stage3Filter:
    """Stage 3: Filters out candidates exceeding character limits or matching banned word lists."""
    
    def __init__(self, banned_words: list[str] = None):
        # Default banned list containing typical naming collision flags
        self.banned = banned_words or ["scam", "spam", "virus", "hack", "fraud"]
        self.char_filter = re.compile(r"^[a-zA-Z0-9\-']+$")
        
    def execute(self, candidates: list[str]) -> list[str]:
        filtered = []
        for name in candidates:
            # Length validation (between 2 and 18 chars)
            if len(name) < 2 or len(name) > 18:
                continue
                
            # Character validation
            if not self.char_filter.match(name):
                continue
                
            # Banned word check
            if any(b in name.lower() for b in self.banned):
                continue
                
            filtered.append(name)
        return filtered
