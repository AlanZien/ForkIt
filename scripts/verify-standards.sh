#!/bin/bash
#
# verify-standards.sh - Verify code standards compliance for ForkIt
#
# Usage: ./scripts/verify-standards.sh [--fix]
#
# Options:
#   --fix    Attempt to auto-fix issues where possible
#
# Exit codes:
#   0 - All checks passed
#   1 - Some checks failed
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track overall status
OVERALL_STATUS=0
FIX_MODE=false

# Parse arguments
if [[ "$1" == "--fix" ]]; then
    FIX_MODE=true
fi

# Get project root
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ForkIt Standards Compliance Check${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ---------------------------------------------
# 1. Backend Python Linting (Ruff)
# ---------------------------------------------
echo -e "${YELLOW}[1/5] Backend Python Linting (Ruff)${NC}"

if [ -d "backend" ]; then
    cd backend

    if command -v python3 &> /dev/null; then
        if $FIX_MODE; then
            echo "  Running ruff with --fix..."
            if python3 -m ruff check app/ --fix 2>/dev/null; then
                echo -e "  ${GREEN}✓ Backend linting passed (with fixes applied)${NC}"
            else
                echo -e "  ${RED}✗ Backend linting failed${NC}"
                OVERALL_STATUS=1
            fi
        else
            if python3 -m ruff check app/ 2>/dev/null; then
                echo -e "  ${GREEN}✓ Backend linting passed${NC}"
            else
                echo -e "  ${RED}✗ Backend linting failed${NC}"
                echo "  Run with --fix to auto-correct issues"
                OVERALL_STATUS=1
            fi
        fi
    else
        echo -e "  ${YELLOW}⚠ Python3 not found, skipping${NC}"
    fi

    cd "$PROJECT_ROOT"
else
    echo -e "  ${YELLOW}⚠ Backend directory not found, skipping${NC}"
fi

echo ""

# ---------------------------------------------
# 2. Mobile TypeScript Type Check
# ---------------------------------------------
echo -e "${YELLOW}[2/5] Mobile TypeScript Type Check${NC}"

if [ -d "mobile" ]; then
    cd mobile

    if [ -f "node_modules/.bin/tsc" ] || command -v npx &> /dev/null; then
        if npx tsc --noEmit 2>/dev/null; then
            echo -e "  ${GREEN}✓ TypeScript type check passed${NC}"
        else
            echo -e "  ${RED}✗ TypeScript type check failed${NC}"
            OVERALL_STATUS=1
        fi
    else
        echo -e "  ${YELLOW}⚠ TypeScript not available, skipping${NC}"
    fi

    cd "$PROJECT_ROOT"
else
    echo -e "  ${YELLOW}⚠ Mobile directory not found, skipping${NC}"
fi

echo ""

# ---------------------------------------------
# 3. Security Checks
# ---------------------------------------------
echo -e "${YELLOW}[3/5] Security Checks${NC}"

# Check for hardcoded secrets
echo "  Checking for potential hardcoded secrets..."

SECRETS_FOUND=0

# Common secret patterns to check (actual secrets, not error messages or validation)
SECRET_PATTERNS=(
    "password\s*=\s*['\"][A-Za-z0-9!@#$%^&*]{8,}['\"]"
    "api_key\s*=\s*['\"][A-Za-z0-9_-]{20,}['\"]"
    "secret_key\s*=\s*['\"][A-Za-z0-9_-]{20,}['\"]"
    "AUTH_TOKEN\s*=\s*['\"][A-Za-z0-9_-]{20,}['\"]"
)

# Files to exclude from secret scanning
EXCLUDE_DIRS="node_modules|.git|__pycache__|.venv|venv|dist|build|.expo"

for pattern in "${SECRET_PATTERNS[@]}"; do
    MATCHES=$(grep -rE --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
        "$pattern" backend/app/ mobile/app/ mobile/services/ mobile/stores/ 2>/dev/null | \
        grep -vE "$EXCLUDE_DIRS" | grep -vE "\.test\.|\.spec\.|mock|example|template|conftest" | head -5)
    if [ -n "$MATCHES" ]; then
        echo "$MATCHES"
        SECRETS_FOUND=1
    fi
done

if [ $SECRETS_FOUND -eq 0 ]; then
    echo -e "  ${GREEN}✓ No obvious hardcoded secrets found${NC}"
else
    echo -e "  ${RED}✗ Potential hardcoded secrets detected (review above)${NC}"
    OVERALL_STATUS=1
fi

# Check for .env files that shouldn't be committed
if [ -f "backend/.env" ] && git ls-files --error-unmatch backend/.env &>/dev/null; then
    echo -e "  ${RED}✗ backend/.env is tracked by git (should be in .gitignore)${NC}"
    OVERALL_STATUS=1
fi

if [ -f "mobile/.env" ] && git ls-files --error-unmatch mobile/.env &>/dev/null; then
    echo -e "  ${RED}✗ mobile/.env is tracked by git (should be in .gitignore)${NC}"
    OVERALL_STATUS=1
fi

echo ""

# ---------------------------------------------
# 4. API Contract Consistency
# ---------------------------------------------
echo -e "${YELLOW}[4/5] API Contract Consistency${NC}"

echo "  Checking if generated types are in sync with backend models..."

if [ -f "scripts/sync-api-types.py" ]; then
    if $FIX_MODE; then
        echo "  Regenerating types from backend models..."
        if python3 scripts/sync-api-types.py 2>/dev/null; then
            echo -e "  ${GREEN}✓ API types synchronized${NC}"
        else
            echo -e "  ${RED}✗ Failed to sync API types${NC}"
            OVERALL_STATUS=1
        fi
    else
        if python3 scripts/sync-api-types.py --check 2>/dev/null; then
            echo -e "  ${GREEN}✓ API types are in sync${NC}"
        else
            echo -e "  ${RED}✗ API types out of sync with backend models${NC}"
            echo "  Run: python scripts/sync-api-types.py"
            OVERALL_STATUS=1
        fi
    fi
else
    echo -e "  ${YELLOW}⚠ sync-api-types.py not found, skipping${NC}"
fi

echo ""

# ---------------------------------------------
# 5. Code Quality Checks
# ---------------------------------------------
echo -e "${YELLOW}[5/5] Code Quality Checks${NC}"

# Check for console.log in production code (mobile)
if [ -d "mobile/app" ]; then
    CONSOLE_LOGS=$(grep -r "console\.log" mobile/app/ mobile/components/ mobile/stores/ mobile/services/ 2>/dev/null | grep -v "\.test\." | grep -v "\.spec\." | wc -l | tr -d ' ')

    if [ "$CONSOLE_LOGS" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠ Found $CONSOLE_LOGS console.log statements in mobile production code${NC}"
        echo "    Consider removing or replacing with proper logging"
    else
        echo -e "  ${GREEN}✓ No console.log in mobile production code${NC}"
    fi
fi

# Check for print statements in Python (excluding tests)
if [ -d "backend/app" ]; then
    PRINT_STMTS=$(grep -r "^[^#]*print(" backend/app/ 2>/dev/null | grep -v "__pycache__" | wc -l | tr -d ' ')

    if [ "$PRINT_STMTS" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠ Found $PRINT_STMTS print() statements in backend code${NC}"
        echo "    Consider using logger instead"
    else
        echo -e "  ${GREEN}✓ No print() statements in backend code${NC}"
    fi
fi

echo ""

# ---------------------------------------------
# Summary
# ---------------------------------------------
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}========================================${NC}"

if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ All standards checks passed!${NC}"
else
    echo -e "${RED}✗ Some standards checks failed${NC}"
    echo ""
    echo "Fix issues and re-run: ./scripts/verify-standards.sh"
    echo "Auto-fix where possible: ./scripts/verify-standards.sh --fix"
fi

exit $OVERALL_STATUS
