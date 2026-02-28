#!/bin/bash
# Lambda Layer Structure Verification Script
#
# AWS Lambda Layer structure for Python:
#   layers/shared/
#     python/
#       session_util.py
#       db_util.py
#       response_util.py
#     requirements.txt    <-- layer dependencies (installed by SAM build)
#
# At runtime, /opt/python/ is on sys.path, so imports are:
#   from session_util import validate_session
#   from db_util import get_table
#   from response_util import success, error

set -e

LAYER_DIR="$(dirname "$0")/../layers/shared"

echo "=== Lambda Layer Structure Verification ==="

# Check required files
REQUIRED_FILES=(
  "python/session_util.py"
  "python/db_util.py"
  "python/response_util.py"
  "python/password_util.py"
  "requirements.txt"
)

PASS=true
for f in "${REQUIRED_FILES[@]}"; do
  if [ -f "$LAYER_DIR/$f" ]; then
    echo "  ✅ $f"
  else
    echo "  ❌ MISSING: $f"
    PASS=false
  fi
done

# Check no __init__.py at python/ level (flat module imports)
if [ -f "$LAYER_DIR/python/__init__.py" ]; then
  echo "  ⚠️  python/__init__.py exists — not needed for flat imports"
fi

if [ "$PASS" = true ]; then
  echo ""
  echo "✅ Layer structure is valid."
else
  echo ""
  echo "❌ Layer structure has issues. Fix before deploying."
  exit 1
fi
