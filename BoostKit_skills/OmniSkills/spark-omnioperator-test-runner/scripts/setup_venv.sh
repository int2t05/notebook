#!/bin/bash
# Virtual Environment Setup Script for Omni Spark Test Framework
# Usage: ./setup_venv.sh [venv_name]

set -e  # Exit on error

VENV_NAME="${1:-omni_test_env}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "========================================"
echo "Setting up Python Virtual Environment"
echo "========================================"
echo "Project Root: $PROJECT_ROOT"
echo "Venv Name: $VENV_NAME"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python Version: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Step 1: Creating virtual environment..."
if [ -d "$PROJECT_ROOT/$VENV_NAME" ]; then
    echo "Virtual environment already exists at $PROJECT_ROOT/$VENV_NAME"
    read -p "Do you want to recreate it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_ROOT/$VENV_NAME"
        python3 -m venv "$PROJECT_ROOT/$VENV_NAME"
        echo "Virtual environment recreated successfully"
    else
        echo "Using existing virtual environment"
    fi
else
    python3 -m venv "$PROJECT_ROOT/$VENV_NAME"
    echo "Virtual environment created successfully"
fi

# Activate virtual environment
echo ""
echo "Step 2: Activating virtual environment..."
source "$PROJECT_ROOT/$VENV_NAME/bin/activate"
echo "Virtual environment activated"

# Install dependencies
echo ""
echo "Step 3: Installing dependencies..."
pip install --upgrade pip
pip install pytest pytest-json-report pytest-timeout pytest-xdist paramiko

echo ""
echo "Dependencies installed:"
pip list

# Create pytest.ini if not exists
echo ""
echo "Step 4: Creating pytest.ini configuration..."
if [ ! -f "$PROJECT_ROOT/pytest.ini" ]; then
    cat > "$PROJECT_ROOT/pytest.ini" << 'EOF'
[pytest]
addopts = -v --html=reports/test.html --self-contained-html -n 8 --dist=loadscope --maxfail=50
timeout = 600
timeout_method = thread
pythonpath = .

[ssh]
pool_size = 30
EOF
    echo "pytest.ini created with default configuration"
else
    echo "pytest.ini already exists, skipping creation"
fi

# Create directory structure
echo ""
echo "Step 5: Creating project directory structure..."
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/reports"
mkdir -p "$PROJECT_ROOT/tests"
mkdir -p "$PROJECT_ROOT/config"
mkdir -p "$PROJECT_ROOT/core"
echo "Directory structure created"

# Create activation script
echo ""
echo "Step 6: Creating activation script..."
cat > "$PROJECT_ROOT/activate_env.sh" << 'EOF'
#!/bin/bash
# Quick activation script for Omni Spark test environment
source omni_test_env/bin/activate
echo "Omni Spark test environment activated"
echo "Run tests with: pytest tests/ -v"
EOF
chmod +x "$PROJECT_ROOT/activate_env.sh"
echo "Activation script created: activate_env.sh"

# Print usage instructions
echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To activate the environment:"
echo "  source $VENV_NAME/bin/activate"
echo "  OR"
echo "  ./activate_env.sh"
echo ""
echo "To run tests:"
echo "  pytest tests/ -v"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "To run tests with custom parallelism:"
echo "  pytest tests/ -n <num_workers>  # e.g., -n 8"
echo ""