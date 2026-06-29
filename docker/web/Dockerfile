# =============================================================================
# Nomen Web — Production Multi-Stage Dockerfile
# Stage 1: base     — Node.js with pnpm
# Stage 2: deps     — installs locked dependencies
# Stage 3: builder  — compiles Next.js production bundle
# Stage 4: runner   — minimal runtime image
# =============================================================================

# ---- Stage 1: base ----
FROM node:20-alpine AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

# ---- Stage 2: dependency installer ----
FROM base AS deps
WORKDIR /workspace

# Copy package manifests for deterministic install
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json ./apps/web/
COPY packages/ts-config/tsconfig.base.json ./packages/ts-config/

RUN pnpm install --frozen-lockfile --prefer-offline

# ---- Stage 3: Next.js builder ----
FROM base AS builder
WORKDIR /workspace

# Copy node_modules from deps stage
COPY --from=deps /workspace/node_modules ./node_modules
COPY --from=deps /workspace/apps/web/node_modules ./apps/web/node_modules

# Copy full source
COPY . .

# Build-time env vars (public only — no secrets)
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_APP_ENV=production
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_APP_ENV=$NEXT_PUBLIC_APP_ENV
ENV NODE_ENV=production

# Build the Next.js standalone bundle
RUN pnpm --filter web build

# ---- Stage 4: production runner ----
FROM node:20-alpine AS runner

LABEL org.opencontainers.image.title="Nomen Web"
LABEL org.opencontainers.image.description="Nomen Brand Intelligence Platform — Next.js Frontend"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="Nomen AI"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Create non-root runtime user
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 --ingroup nodejs nextjs

# Copy standalone server output (Next.js standalone mode)
COPY --from=builder /workspace/apps/web/public ./public
COPY --from=builder --chown=nextjs:nodejs /workspace/apps/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /workspace/apps/web/.next/static ./.next/static

USER nextjs

EXPOSE 3000

# Healthcheck against root route
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD node -e "require('http').get({hostname:'localhost',port:3000,path:'/',timeout:5000},(r)=>{r.statusCode<500?process.exit(0):process.exit(1)}).on('error',()=>process.exit(1))"

CMD ["node", "server.js"]
