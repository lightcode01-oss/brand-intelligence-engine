#!/bin/bash
set -e

# Nomen Monorepo Local Setup Bootstrapping Script

echo "🚀 Bootstrapping Nomen engineering workspace..."

# 1. Verify pnpm installation
if ! command -v pnpm &> /dev/null; then
    echo "❌ Error: pnpm is not installed. Please install pnpm first: https://pnpm.io/installation"
    exit 1
fi

# 2. Copy environmental configurations
if [ ! -f ".env" ]; then
    echo "📋 Copying .env.example to .env..."
    copy .env.example .env || cp .env.example .env
else
    echo "✅ .env configuration file already exists."
fi

# 3. Install packages
echo "📦 Installing monorepo workspace dependencies..."
pnpm install

# 4. Initialize Husky git hooks
echo "⚓ Setting up Husky configurations..."
pnpm run prepare || echo "Husky initialization skipped (not in a git repository)"

echo "🎉 Workspace is ready! Run local services using:"
echo "   pnpm --filter web dev  # Starts Next.js development server"
echo "   docker compose -f docker-compose.dev.yml up  # Starts complete Docker local stack"
