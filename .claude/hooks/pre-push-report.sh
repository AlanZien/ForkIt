#!/bin/bash
# Pre-push test report hook for Claude Code
# Runs all tests and displays structured report before allowing push

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📊 COMPTE-RENDU DES TESTS AVANT PUSH"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Backend tests
echo "BACKEND (Python/FastAPI):"
cd "$PROJECT_ROOT/backend"
BACKEND_RESULT=$(uv run pytest tests/ -q 2>&1 || true)
BACKEND_PASSED=$(echo "$BACKEND_RESULT" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' || echo "0")
BACKEND_FAILED=$(echo "$BACKEND_RESULT" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' || echo "0")
BACKEND_WARNINGS=$(echo "$BACKEND_RESULT" | grep -oE '[0-9]+ warning' | grep -oE '[0-9]+' || echo "0")

if [ "$BACKEND_FAILED" = "0" ]; then
  echo "  ✅ $BACKEND_PASSED tests passés | ❌ $BACKEND_FAILED échecs | ⚠️  $BACKEND_WARNINGS warnings"
else
  echo "  ❌ $BACKEND_PASSED tests passés | ❌ $BACKEND_FAILED échecs | ⚠️  $BACKEND_WARNINGS warnings"
fi
echo ""

# Mobile tests
echo "MOBILE (React Native/Expo):"
cd "$PROJECT_ROOT/mobile"
MOBILE_RESULT=$(npm test 2>&1 || true)
MOBILE_PASSED=$(echo "$MOBILE_RESULT" | grep -oE 'Tests:.*[0-9]+ passed' | grep -oE '[0-9]+' | head -1 || echo "0")
MOBILE_FAILED=$(echo "$MOBILE_RESULT" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' || echo "0")
MOBILE_SUITES=$(echo "$MOBILE_RESULT" | grep -oE 'Test Suites:.*[0-9]+ passed' | grep -oE '[0-9]+' | head -1 || echo "0")

if [ "$MOBILE_FAILED" = "0" ]; then
  echo "  ✅ $MOBILE_PASSED tests passés | ❌ $MOBILE_FAILED échecs | $MOBILE_SUITES suites"
else
  echo "  ❌ $MOBILE_PASSED tests passés | ❌ $MOBILE_FAILED échecs | $MOBILE_SUITES suites"
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════════════════"
echo "RÉSUMÉ"
echo "════════════════════════════════════════════════════════════════"

TOTAL=$((BACKEND_PASSED + MOBILE_PASSED))
TOTAL_FAILED=$((BACKEND_FAILED + MOBILE_FAILED))

if [ "$TOTAL_FAILED" = "0" ]; then
  echo "┌─────────────────────────────────────────────────────────────┐"
  echo "│  TOTAL: $TOTAL tests | ✅ $TOTAL passés | ❌ $TOTAL_FAILED échecs"
  echo "│  Régression: ✅ Aucune                                      │"
  echo "│  Prêt à push: ✅ OUI                                        │"
  echo "└─────────────────────────────────────────────────────────────┘"
  exit 0
else
  echo "┌─────────────────────────────────────────────────────────────┐"
  echo "│  TOTAL: $TOTAL tests | ✅ $((TOTAL - TOTAL_FAILED)) passés | ❌ $TOTAL_FAILED échecs"
  echo "│  Régression: ❌ Détectée                                    │"
  echo "│  Prêt à push: ❌ NON                                        │"
  echo "└─────────────────────────────────────────────────────────────┘"
  echo ""
  echo "⛔ Push bloqué - corrigez les tests en échec avant de push"
  exit 1
fi
