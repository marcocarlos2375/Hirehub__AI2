#!/bin/bash
# TypeScript Type Checking Script
# Run this script to check for type errors in the entire Nuxt 3 application

set -e

echo "🔍 Running TypeScript type check..."
echo ""

# Run Nuxt's built-in type checking
npx nuxi typecheck

echo ""
echo "✅ Type check complete!"
