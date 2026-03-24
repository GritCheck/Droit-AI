#!/bin/bash

# Move to site root
cd /home/site/wwwroot

# Use the Oryx-provided virtual env if it exists
if [ -d "$ORCHESTRATOR_VENV_PATH" ]; then
    source "$ORCHESTRATOR_VENV_PATH/bin/activate"
elif [ -d "/tmp/*/antenv" ]; then
    # Find the dynamically created antenv
    VENV_PATH=$(find /tmp -maxdepth 2 -name "antenv" -type d 2>/dev/null | head -1)
    if [ -n "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate"
    fi
elif [ -d "antenv" ]; then
    source antenv/bin/activate
else
    echo "Creating virtual environment and installing dependencies..."
    python -m venv antenv
    source antenv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Set Python Path
export PYTHONPATH=$PYTHONPATH:/home/site/wwwroot

# Launch App
echo "Launching Uvicorn..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
