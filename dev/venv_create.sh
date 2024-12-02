#!bin/bash

# path of the script
SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TARGET_PATH="$SCRIPT_PATH/.."
echo "Preparing virtual environment in $TARGET_PATH"
# Create a virtual environment
if [ -d "$TARGET_PATH/.venv" ]; then
    rm -rf "$TARGET_PATH/.venv"
fi
    python3 -m venv "$TARGET_PATH/.venv"

# update pip
"$TARGET_PATH/.venv/bin/python" -m pip install --upgrade pip setuptools wheel

# install requirements
"$TARGET_PATH/.venv/bin/python" -m pip install -r "$TARGET_PATH/requirements-bot.txt"

# install osintkit
"$TARGET_PATH/.venv/bin/python" -m pip install -e "$TARGET_PATH"
