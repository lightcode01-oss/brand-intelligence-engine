# Trademark Checking Strategy: Nomen

This document details Nomen's methodology for conducting automated, multi-jurisdiction trademark clearance checks, maintaining legal data compliance, and scoring collision risks.

---

## 1. Multi-Stage Trademark Filtering

Trademark databases are heavily protected and expensive to query programmatically via commercial APIs. Nomen bypasses this constraint by implementing a hybrid approach using a **local pre-filter database** and **live public scraping fallback**:

```text
                       [ Candidate Brand Name ]
                                  │
                                  ▼
                   ┌─────────────────────────────┐
                   │ Phase 1: Local DB Pre-Filter │ (Fuzzy match on USPTO Bulk download)
                   └──────────────┬──────────────┘
                                  │
                       ┌──────────┴──────────┐
                       ▼ Clean               ▼ Hits Found
                (No local match)         (Conflicting Trademarks)
                       │                     │
                       ▼                     ▼
               ┌────────────────┐     [ High Risk Flag ]
               │ Phase 2: Live  │
               │ Registry Query │ (Scrape USPTO TSDR, UK-IPO, EUIPO)
               └───────┬────────┘
                       │
             ┌─────────┴─────────┐
             ▼ Clean             ▼ Hits Found
          [ Low Risk ]     [ Medium/High Risk ]
```

---

## 2. Phase Implementations

### 2.1. Phase 1: Local Pre-Filter Database (USPTO Bulk Data)
- **Data Source**: Every week, a background celery worker downloads the USPTO trademark bulk data (XML zip logs) from the USPTO developer portal (free public data).
- **Processing**: A Python parser processes the XML files and populates our PostgreSQL `names_trademark_cache` table with:
  - Mark Text (lowercased, stripped of symbols).
  - International Class (IC code, e.g., Class 009 for software).
  - Status (Active, Dead, Abandoned).
- **Matching Algorithm**: When checking a candidate name, we run a query:
  ```sql
  SELECT mark_text, ic_class, status 
  FROM uspto_trademarks 
  WHERE mark_text = :name 
     OR levenshtein(mark_text, :name) <= 1;
  ```
- **Cost**: $0.
- **Latency**: ~10ms.

### 2.2. Phase 2: Live Registry Scraping (Fallback & Verification)
If the local cache yields no matches but the user requests a deep verification report:
- **US (USPTO TSDR)**: The worker executes a headless HTTP GET request using python `httpx` targeting the public USPTO Trademark Status Document Retrieval (TSDR) web portal search page. We parse the HTML DOM using `BeautifulSoup`.
- **UK (UK-IPO)**: The worker queries the UK Intellectual Property Office public lookup system using rate-limited API requests or public scraping.
- **EU (EUIPO)**: The worker targets the eSearch Plus portal using its basic public query endpoints.

---

## 3. The "Likelihood of Confusion" Phonetic Algorithm

Trademark infringement is not limited to exact matches; it covers phonetic similarity that could confuse consumers. We check phonetics in our trademark scraper:
- We compute the **Double Metaphone** codes of the candidate name and comparing them with the Double Metaphone codes of cached active trademarks in the database.
- E.g. If the user generates "Krypt", the metaphone code matches "Crypt" (`KRPT`). The engine flags this as a **High Risk** phonetic clash.

---

## 4. Risk Classification Matrix

The frontend displays trademark results categorized under three clear risk profiles:

| Risk Level | Trigger Criteria | UI Display | User Guidance |
| :--- | :--- | :--- | :--- |
| **Low Risk** | No exact or phonetic matches found in local DB or live registry. | Green Badge | *"No active trademarks blocking this name. Proceed to domain registration."* |
| **Medium Risk** | Near spelling match (Levenshtein distance <= 2) or phonetically identical match in an **unrelated** International Class. | Yellow Badge | *"Phonetically similar names exist (e.g. 'X' in Class 025 - Clothing). Consult a lawyer if you operate in similar fields."* |
| **High Risk** | Exact match in target International Class (e.g. Class 042 - Tech) or active trademark in major global markets. | Red Badge | *"Exact/Close conflict found. This name is highly likely to trigger trademark infringement warnings."* |
