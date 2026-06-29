def jaro_similarity(s1: str, s2: str) -> float:
    """Calculates the Jaro similarity score between two strings."""
    str1 = s1.lower().strip()
    str2 = s2.lower().strip()
    
    len1 = len(str1)
    len2 = len(str2)
    
    if len1 == 0 and len2 == 0:
        return 1.0
    if len1 == 0 or len2 == 0:
        return 0.0
        
    match_distance = max(len1, len2) // 2 - 1
    
    str1_matches = [False] * len1
    str2_matches = [False] * len2
    
    matches = 0
    transpositions = 0
    
    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        
        for j in range(start, end):
            if str2_matches[j]:
                continue
            if str1[i] == str2[j]:
                str1_matches[i] = True
                str2_matches[j] = True
                matches += 1
                break
                
    if matches == 0:
        return 0.0
        
    # Calculate transpositions
    k = 0
    for i in range(len1):
        if not str1_matches[i]:
            continue
        while not str2_matches[k]:
            k += 1
        if str1[i] != str2[k]:
            transpositions += 1
        k += 1
        
    t = transpositions / 2
    return (matches / len1 + matches / len2 + (matches - t) / matches) / 3

def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1) -> float:
    """Calculates the Jaro-Winkler similarity score with scaling prefix factor."""
    j = jaro_similarity(s1, s2)
    
    # Calculate common prefix length (up to 4 characters)
    prefix_len = 0
    min_len = min(len(s1), len(s2))
    for i in range(min(min_len, 4)):
        if s1[i].lower() == s2[i].lower():
            prefix_len += 1
        else:
            break
            
    return j + (prefix_len * p * (1.0 - j))
