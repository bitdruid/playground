#!bin/bash

# path of the script
SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TARGET_PATH="$SCRIPT_PATH/.."

pip install -r "$TARGET_PATH/osintkit/requirements.txt" --break-system-packages
pip install -e "$TARGET_PATH" --break-system-packages