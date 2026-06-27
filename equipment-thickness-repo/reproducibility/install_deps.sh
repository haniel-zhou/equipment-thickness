#!/usr/bin/env bash
# Install dependencies for Equipment Thickness Theory reproduction.
# Tested on: macOS 14+, Ubuntu 22.04+, Python 3.10+
# Usage: bash install_deps.sh

set -euo pipefail

echo "=== Equipment Thickness Theory: dependency install ==="
echo ""

# 1. Python check
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    echo "ERROR: Python 3.10+ required. Found: $PYTHON_VERSION"
    echo "Install via: brew install python@3.11  (macOS)"
    echo "             sudo apt install python3.11  (Ubuntu)"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION"

# 2. pip packages
echo ""
echo "Installing pip packages (numpy, no proprietary ML required)..."
python3 -m pip install --quiet --user 'numpy>=1.24' 'pyyaml>=6.0'

echo "✓ numpy + pyyaml installed"

# 3. Optional: sentence-transformers for v2.0 semantic recall (not required for v1.0 reproduction)
echo ""
echo "Optional: For semantic_recall.py v2.0 (embedding-based), also install:"
echo "    python3 -m pip install --user 'sentence-transformers>=2.2' 'faiss-cpu>=1.7'"
echo "(Not required for v1.0 weekly-eval reproduction; v1.0 uses BM25-lite + IDF)"

# 4. Verify
echo ""
echo "Verifying install..."
python3 -c "import numpy; print(f'  numpy: {numpy.__version__}')"
python3 -c "import yaml; print(f'  pyyaml: {yaml.__version__}')"

echo ""
echo "=== Install complete ==="
echo "Next: bash reproducibility/run_all.sh"