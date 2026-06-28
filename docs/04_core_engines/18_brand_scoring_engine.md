# Brand Scoring Engine Design: Nomen

This document details the mathematical models, metric weightings, and processing pipelines of Nomen's proprietary **Brand Score Index (BSI)**.

---

## 1. Scoring Criteria & Metrics

The BSI evaluates every candidate name out of a maximum score of **100**. It is calculated based on five distinct inputs:

| Metric | Code | Weight ($w$) | Description | Evaluation Logic |
| :--- | :--- | :--- | :--- | :--- |
| **Length & Complexity** | $L$ | 15% (0.15) | Favors short, clean names. | $1.0$ for <= 5 chars; linear decay down to $0.0$ for >= 18 chars. |
| **Pronounceability** | $P$ | 25% (0.25) | Grades phonetic ease of use. | Evaluates phonetic structure, syllable count, and letter transitions (G2P). |
| **Domain Availability** | $D$ | 30% (0.30) | Access to prime digital space. | $1.0$ for `.com` free; $0.7$ for `.co`/`.io` free; $0.2$ if only premium; $0.0$ if taken. |
| **Trademark Risk** | $T$ | 20% (0.20) | Security against legal threats. | $1.0$ for Low Risk; $0.4$ for Medium Risk; $0.0$ for High Risk. |
| **Semantic Alignment** | $S$ | 10% (0.10) | Relevance to user prompt. | Cosine similarity between prompt embeddings and name concept metadata. |

---

## 2. Mathematical Formulation

The overall Brand Score is calculated using a weighted sum model, subject to a **Trademark Deal-Breaker Multiplier**:

$$\text{Raw Score} = (w_L \cdot L + w_P \cdot P + w_D \cdot D + w_T \cdot T + w_S \cdot S) \times 100$$

### 2.1. The Trademark Penalty Multiplier ($M_{TM}$)
To ensure we never recommend a name that has severe legal conflicts, we apply a multiplicative constraint:
- If Trademark Risk = High (Red), $M_{TM} = 0.2$
- If Trademark Risk = Medium (Yellow), $M_{TM} = 0.7$
- If Trademark Risk = Low (Green), $M_{TM} = 1.0$

$$\text{Final Brand Score} = \text{Raw Score} \times M_{TM}$$

---

## 3. Metric Calculations (Step-by-Step)

### 3.1. Length Score ($L$)
Let $N$ be the character length of the name string:
- If $N \le 5$: $L = 1.0$
- If $5 < N < 15$: $L = 1.0 - \frac{N - 5}{10}$
- If $N \ge 15$: $L = 0.0$

### 3.2. Domain Score ($D$)
Calculated from cached lookup structures:
- `.com` is available: $D = 1.0$
- `.com` is taken, but `.io` or `.co` is available: $D = 0.7$
- `.com` is taken, and only premium TLD variants are available (e.g. `.app` at $500/yr): $D = 0.3$
- All target TLDs taken: $D = 0.0$

### 3.3. Pronounceability ($P$)
Determined by parsing phonetic syllable structures (detailed in the Pronunciation Engine Design):
- Syllable count penalty: $S_{\text{pen}} = 1.0 - (Syllables - 1) \times 0.25$ (Max penalty limit at 4 syllables).
- Linguistic Transition Score ($T_{\text{ling}}$): Checks consonant cluster density. Banned double consonants or hard consonant combinations reduce $T_{\text{ling}}$ towards $0$.
- $P = T_{\text{ling}} \times S_{\text{pen}}$.

---

## 4. Implementation Example (Python Pseudocode)

```python
def calculate_brand_score(name: str, domain_status: dict, trademark_status: str, syllables: int, phonetic_ease: float, semantic_sim: float) -> int:
    # 1. Length Score
    char_len = len(name)
    l_score = 1.0 if char_len <= 5 else max(0.0, 1.0 - (char_len - 5) / 10.0)
    
    # 2. Domain Score
    if domain_status.get(".com", False):
        d_score = 1.0
    elif domain_status.get(".io", False) or domain_status.get(".co", False):
        d_score = 0.7
    elif domain_status.get("premium", False):
        d_score = 0.3
    else:
        d_score = 0.0
        
    # 3. Trademark Score
    t_score = 1.0 if trademark_status == "clear" else (0.5 if trademark_status == "warning" else 0.0)
    
    # 4. Pronounceability
    s_penalty = max(0.0, 1.0 - (syllables - 1) * 0.25)
    p_score = phonetic_ease * s_penalty
    
    # 5. Semantic Alignment
    s_align = semantic_sim
    
    # Calculate Raw Weighted Score
    raw_score = (0.15 * l_score + 0.25 * p_score + 0.30 * d_score + 0.20 * t_score + 0.10 * s_align) * 100
    
    # Apply Trademark Risk Multiplier
    if trademark_status == "conflict":
        multiplier = 0.2  # Severe penalty
    elif trademark_status == "warning":
        multiplier = 0.7  # Moderate penalty
    else:
        multiplier = 1.0
        
    return round(raw_score * multiplier)
```
This multi-layered approach guarantees that only names that are short, legal, easy to say, and domain-available receive top marks.
