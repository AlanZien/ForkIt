#!/bin/sh
# Setup git hooks for ForkIt
# Run this script after cloning the repository

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_SOURCE="$SCRIPT_DIR/hooks"
HOOKS_TARGET="$PROJECT_ROOT/.git/hooks"

echo "🔧 Setting up git hooks..."

# Copy pre-commit hook
if [ -f "$HOOKS_SOURCE/pre-commit" ]; then
    cp "$HOOKS_SOURCE/pre-commit" "$HOOKS_TARGET/pre-commit"
    chmod +x "$HOOKS_TARGET/pre-commit"
    echo "✅ pre-commit hook installed"
else
    echo "❌ pre-commit hook not found in $HOOKS_SOURCE"
    exit 1
fi

echo ""
echo "🎉 Git hooks setup complete!"
echo "   Hooks will run automatically on commit."
echo "   Use 'git commit --no-verify' to skip (not recommended)."
