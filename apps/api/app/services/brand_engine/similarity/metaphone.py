def metaphone_key(word: str) -> str:
    """Generates a simplified Metaphone phonetic key representation for a word."""
    w = word.strip().upper()
    if not w:
        return ""
        
    # Remove non-alphabetic characters
    w = "".join(c for c in w if c.isalpha())
    if not w:
        return ""
        
    # 1. Initial letters transformations
    if w.startswith("KN") or w.startswith("GN") or w.startswith("PN") or w.startswith("AE") or w.startswith("WR"):
        w = w[1:]
    elif w.startswith("X"):
        w = "S" + w[1:]
    elif w.startswith("WH"):
        w = "W" + w[2:]
        
    # 2. Collapse duplicate characters
    collapsed = [w[0]]
    for char in w[1:]:
        if char != collapsed[-1]:
            collapsed.append(char)
    w = "".join(collapsed)
    
    # 3. Simple Metaphone key mapping
    result = []
    vowels = "AEIOUY"
    
    for i, char in enumerate(w):
        # Keep initial vowels as-is, strip subsequent ones
        if char in vowels:
            if i == 0:
                result.append(char)
            continue
            
        if char == "B":
            result.append("B")
        elif char == "C":
            # Soft C check (followed by I, E, Y)
            if i + 1 < len(w) and w[i + 1] in "IEY":
                result.append("S")
            else:
                result.append("K")
        elif char in "DT":
            result.append("T")
        elif char in "FGV":
            result.append("F")
        elif char in "KSXZ":
            result.append("S")
        elif char in "J":
            result.append("J")
        elif char in "LMNR":
            result.append(char)
        elif char == "P":
            # PH sound check
            if i + 1 < len(w) and w[i + 1] == "H":
                result.append("F")
            else:
                result.append("P")
        elif char == "Q":
            result.append("K")
        elif char == "W":
            # Keep if followed by a vowel
            if i + 1 < len(w) and w[i + 1] in vowels:
                result.append("W")
        elif char == "H":
            # Keep only after vowels if not followed by another consonant
            if i > 0 and w[i - 1] in vowels:
                if i + 1 == len(w) or w[i + 1] in vowels:
                    result.append("H")
                    
    return "".join(result)
