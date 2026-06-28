# Similarity Detection Design: Nomen

This document specifies the algorithms and logic flows used by Nomen to detect spelling, sound, and semantic conflicts between generated names and existing prominent brands.

---

## 1. The Three Dimensions of Similarity

To flag names that could trigger trademark disputes or user confusion, Nomen checks similarity across three vectors:

```text
                           [ Candidate Name ]
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
  ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
  │ 1. Orthographic│        │ 2. Phonetic  │          │ 3. Semantic  │
  │ (Spelling)   │          │ (Sound)      │          │ (Meaning)    │
  └──────┬───────┘          └──────┬───────┘          └──────┬───────┘
         │                         │                         │
  Levenshtein &             Double Metaphone          pgvector Cosine
  Jaro-Winkler              Match Checks              Similarity (embeddings)
```

---

## 2. Algorithm Implementations

### 2.1. Orthographic (Spelling) Similarity
We calculate structural text distances to check for near-typos:
- **Levenshtein Distance**: Counts minimum single-character edits (insertions, deletions, substitutions). We flag any match in our brand directory with a distance of $\le 1$ (e.g., "Strype" vs. "Stripe").
- **Jaro-Winkler Similarity**: Measures character matching sequences, favoring prefixes. A score of $\ge 0.90$ triggers a warning:
  $$d_w = d_j + \ell \, p (1 - d_j)$$
  Where $d_j$ is the Jaro distance, $\ell$ is the length of common prefix, and $p = 0.1$ is the constant scaling factor.

### 2.2. Phonetic (Sound) Similarity
Many brands spell names differently but pronounce them identically (e.g. "Lyft" vs. "Lift").
- We convert both names to their **Double Metaphone** representation.
- If primary metaphones are identical (e.g. `LFT` for both Lyft and Lift), they are marked as **Phonetic Collisions** and penalized on the brand scorecard.

### 2.3. Semantic (Meaning) Similarity
Traditional tools miss synonyms (e.g. naming an AI storage tool "SkyBox" when "CloudBox" already exists).
- We generate a 384-dimension vector embedding for the candidate name and its target vertical.
- We run a cosine similarity query against the database of top tech companies:
  ```sql
  SELECT name, 1 - (embedding <=> :candidate_embedding) AS similarity
  FROM target_companies
  ORDER BY similarity DESC
  LIMIT 3;
  ```
- If the cosine similarity exceeds **0.85** in the same market sector, the system flags a **Semantic Similarity Warning**.

---

## 3. Brand Collision Directory

To perform these checks without expensive external lookups, the system maintains a local database table (`target_companies`) populated with:
- Top 10,000 global domains (Alexa/Tranco top sites list).
- Y Combinator company directory (fetched via public startup API).
- Fortune 500 company registry.
- Crunchbase open data export fields.

This catalog is stored and indexed in PostgreSQL using `pgvector` HNSW indexes, ensuring all three similarity dimensions check resolve in under **100ms** total.
