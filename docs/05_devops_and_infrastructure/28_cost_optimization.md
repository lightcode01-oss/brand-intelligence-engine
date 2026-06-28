# Cost Optimization Strategy: Nomen

This document specifies the strategies Nomen uses to minimize operational infrastructure overhead, enabling the platform to run at near-zero costs during initial deployment.

---

## 1. Cloud Cost Comparison: Self-Hosted vs. Managed Enterprise

To illustrate the financial efficiency of our stack, we compare hosting Nomen on a self-hosted single-node VPS configuration vs. using standard cloud-managed equivalents:

| Service Layer | Managed / Corporate Stack | Monthly Cost | Optimized Open-Source Stack (Ours) | Monthly Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | AWS Amplify / Vercel Pro | $20 | **Cloudflare Pages / Vercel Free** | **$0** |
| **Backend API** | AWS ECS + Fargate + ALB | $80 | **Docker Container on VPS** | In VPS bundle |
| **Database** | Amazon Aurora PostgreSQL | $70 | **Self-hosted Docker PG + pgvector**| In VPS bundle |
| **Cache & Broker**| Upstash Redis (Standard) | $25 | **Self-hosted Docker Redis** | In VPS bundle |
| **Task Workers** | AWS ECS Workers | $60 | **Self-hosted Celery Workers** | In VPS bundle |
| **Object Store** | Amazon S3 (+ Egress bandwidth) | $15+ | **Cloudflare R2 (0 Egress Fees)** | **$0** (under 10GB) |
| **LLM Generation** | OpenAI GPT-4o-mini | $50+ | **Google Gemini Flash Free Tier** | **$0** (Free limit) |
| **Host Node** | - | - | **Hetzner Cloud VPS (4 vCPU / 8GB)** | **$12** |
| **Total Cost** | - | **$320+** | - | **$12 / month** |

---

## 2. Structural Cost-Saving Directives

### 2.1. Leverage Google Gemini Flash Free Tier
- **Strategy**: Gemini 1.5 Flash offers a free tier of **15 requests per minute** and **1,000,000 tokens per minute**, which is more than enough for initial alpha testing and early launch.
- **Fallback**: If rates are exceeded, requests fallback to **Groq API** (which has high free-tier quotas for Llama 3.1) or our **self-hosted Ollama container** running on the host VPS.

### 2.2. Zero-Egress Storage via Cloudflare R2
- **Strategy**: We save generated vector logos, palettes, and zipped export files inside a Cloudflare R2 bucket.
- **Benefit**: Unlike Amazon S3, which charges $0.09 per GB of download transfer (egress fees), R2 charges **$0.00** for downloads. The first **10 GB of storage** per month is completely free.

### 2.3. Caching as a Financial Buffer
- Every API call to third-party endpoints (domain WHOIS lookup, Google Gemini API, USPTO scraper) has a Redis caching decorator.
- If 100 users search for similar prompts or click the same name, we only hit the LLM/Registry API once. The subsequent 99 queries are resolved from local memory in 1ms at **$0 cost**.

### 2.4. Docker Container Density
- Running PostgreSQL, Redis, Celery, and FastAPI on a single VPS host eliminates the network hops and idle-compute billing overhead of multiple cloud instances.
- Docker Compose limits memory configurations per container to ensure database stability is prioritized.
