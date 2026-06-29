class Stage2Deduplicate:
    """Stage 2: Standardizes text, strips whitespaces, and removes duplicate strings."""
    
    def execute(self, candidates: list[str]) -> list[str]:
        seen = set()
        deduplicated = []
        for c in candidates:
            cleaned = c.strip()
            # Normalize casing for duplicate checks
            norm = cleaned.lower()
            if norm and norm not in seen:
                seen.add(norm)
                deduplicated.append(cleaned)
        return deduplicated
