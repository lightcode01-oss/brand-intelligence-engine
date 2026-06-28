# Domain Availability Strategy: Nomen

This document specifies how Nomen verifies domain availability across multiple Top-Level Domains (TLDs) at scale, keeping costs at zero and bypassing strict registrar rate limits.

---

## 1. The Tiered Domain Lookup Engine

Checking availability by spamming Registrar APIs (e.g., Namecheap or GoDaddy) leads to rapid IP bans or high costs. Nomen implements a 3-tier checks strategy:

```text
                     [ Candidate Domain Name ]
                                │
                                ▼
                   ┌──────────────────────────┐
                   │  Tier 1: DNS Resolution   │ (dnspython: A/AAAA/MX records)
                   └────────────┬─────────────┘
                                │
                     ┌──────────┴──────────┐
                     ▼ Resolves            ▼ Resolves
                (Domain Active)      (No DNS Records)
                     │                     │
                     ▼                     ▼
               [ Taken / Save ]    ┌──────────────────────────┐
                                   │   Tier 2: WHOIS Query    │ (Socket TCP check)
                                   └───────────┬──────────────┘
                                               │
                                     ┌─────────┴─────────┐
                                     ▼ Registered        ▼ NXDOMAIN
                                 (WHOIS hit)         (WHOIS clear)
                                     │                   │
                                     ▼                   ▼
                               [ Taken / Save ]    ┌──────────────────────────┐
                                                   │  Tier 3: Registrar API   │ (Optional / Premium Check)
                                                   └───────────┬──────────────┘
                                                               │
                                                               ▼
                                                     [ Available / Premium ]
```

---

## 2. Tier Details

### 2.1. Tier 1: DNS Resolution (Fast & Zero-Cost)
Using the python `dnspython` library, the worker executes a high-speed asynchronous DNS lookup targeting Google (`8.8.8.8`) or Cloudflare (`1.1.1.1`) public resolvers:
- If `A`, `AAAA`, `MX`, or `CNAME` records are returned, the domain is immediately marked as **Registered (Taken)**.
- **Cost**: $0.
- **Latency**: ~10ms - 50ms.

### 2.2. Tier 2: WHOIS Socket Query (Fallback for Parked Domains)
If Tier 1 resolves nothing, the domain could still be registered but "parked" without DNS settings. The worker establishes a direct TCP connection on port `43` to the appropriate registry WHOIS server (e.g. `whois.verisign-grs.com` for `.com` domains) and parses the text response.
- If keywords like `"No match for"`, `"NOT FOUND"`, or `"AVAILABLE"` are detected, the domain is likely free.
- Otherwise, it is marked as **Taken**.
- **Cost**: $0.
- **Latency**: ~200ms - 500ms.
- **Rate-Limits**: We route WHOIS requests through a rotating proxy pool of backend workers if IP rate limits are hit.

### 2.3. Tier 3: Registrar API Verification (Premium Valuation)
When a user clicks on a candidate name to see details, the backend queries registrar APIs (we prioritize Namecheap API or GoDaddy API) to:
- Confirm availability.
- Fetch standard purchase price.
- Determine if the domain is listed on a secondary marketplace as a **Premium Domain** (returning valuation price, e.g. $2,500).
- **Cost**: Free dev credentials.
- **Latency**: ~800ms.

---

## 3. Caching & Mitigation Strategy

To prevent redundant lookups and respect registry guidelines:
- **Redis Cache**: Every lookup is stored in Redis:
  - Key: `domain:check:<domain_name>:<tld>`
  - Value: `{"available": true, "is_premium": false, "price": null}`
  - Expiry: 24 Hours.
- **Queue Throttling**: The Celery `dns_check.py` worker pool limits concurrent Tier 2 WHOIS queries to 10 requests per second to avoid triggering registry blocks.
- **Affiliate Handoff**: For domain registration, we generate affiliate links pointing to Cloudflare Registrar (at-cost registrations) and Namecheap.
