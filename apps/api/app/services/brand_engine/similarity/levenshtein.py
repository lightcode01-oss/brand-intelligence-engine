def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates the Levenshtein edit distance between two strings."""
    str1 = s1.lower().strip()
    str2 = s2.lower().strip()
    
    if len(str1) < len(str2):
        return levenshtein_distance(str2, str1)
        
    if len(str2) == 0:
        return len(str1)
        
    previous_row = range(len(str2) + 1)
    for i, c1 in enumerate(str1):
        current_row = [i + 1]
        for j, c2 in enumerate(str2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        
    return previous_row[-1]

def levenshtein_similarity(s1: str, s2: str) -> float:
    """Returns a similarity coefficient between 0.0 and 1.0 based on edit distance."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    distance = levenshtein_distance(s1, s2)
    return 1.0 - (distance / max_len)
