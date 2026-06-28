# Scaling Strategy: Nomen

This document specifies the horizontal and vertical scaling roadmap for Nomen, detailing how the architecture migrates from a single VPS node to a highly-available, multi-region cluster as traffic grows.

---

## 1. The Scaling Horizons

We divide our scaling journey into three distinct phases:

```text
  [ Phase 1: MVP / Launch ] ───> [ Phase 2: Growth / Scale ] ───> [ Phase 3: High Availability ]
  - Single 8GB Host node         - Decouple DB & Redis            - Multi-region API clusters
  - Local Docker PG & Redis      - Managed Supabase / RDS         - K8s / ECS orchestration
  - Celery on same node          - Dedicated Celery node pools    - Cloudflare load balancing
```

---

## 2. Phase-by-Phase Architecture Migration

### Phase 1: Single-Node (Up to 10,000 Monthly Active Users)
- **Architecture**: As detailed in our Deployment spec, all services run on a single host (4 vCPUs / 8GB RAM).
- **Bottlenecks**: High concurrent name generation queries can saturate worker threads, temporarily slowing down the API response times.
- **Remedy**: Configure Docker resource limits to ensure the API container always retains 1 vCPU and 2GB RAM minimum, preventing database crashes during search spikes.

### Phase 2: Decoupled Services (10,000 - 100,000 Monthly Active Users)
When traffic grows, DB operations and task execution must be separated from the primary API host:
1. **Managed Primary Database**: Migrate PostgreSQL to Supabase or AWS RDS. Enable **read replicas** to offload dashboard portfolio lookup traffic.
2. **Dedicated Worker Pool**: Spin up 2-3 small CPU-optimized worker nodes running only the Celery workers. The API container on the primary host enqueues tasks to the external workers via a secured Redis instance.
3. **Connection Pooling**: Introduce **PgBouncer** in front of PostgreSQL to manage database connection reuse, preventing "too many clients" errors.

### Phase 3: High-Availability Kubernetes Cluster (100,000+ Monthly Active Users)
- **Orchestration**: Deploy Next.js and FastAPI containers on **Kubernetes** (EKS / GKE) or **AWS ECS**.
- **Load Balancing**: A **Cloudflare Load Balancer** distributes incoming traffic across API clusters in multiple regions (e.g. US-East, EU-Central).
- **Auto-Scaling Rules**:
  - Scale API pods horizontally when CPU usage exceeds **70%**.
  - Scale Celery worker nodes based on **Redis queue length** metrics pulled from Prometheus. If the queue length exceeds 100 items, Kubernetes spins up additional Celery worker pods instantly.

---

## 3. Database Read/Write Splitting Pattern

To optimize database throughput, our FastAPI application is updated in Phase 2 to split traffic between the primary writer endpoint and replica readers:

```python
# app/core/database.py (Phase 2 Splitting example)
from sqlalchemy.ext.asyncio import create_async_engine

# Primary engine handles INSERT / UPDATE / DELETE
write_engine = create_async_engine(settings.DATABASE_WRITE_URL)
# Replica engine handles SELECT queries
read_engine = create_async_engine(settings.DATABASE_READ_URL)
```
Since naming applications are read-heavy (users browse hundreds of generated names for every name they save), splitting reads to replica databases reduces writer node load by up to **80%**.
