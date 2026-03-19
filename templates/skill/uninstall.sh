#!/bin/bash
# uninstall.sh - Skill uninstallation hook
# Called with: $1 = install|uninstall
#              $2 = target directory

set -e

ACTION="$1"
TARGET_DIR="$2"

if [ "$ACTION" = "install" ]; then
    echo "Installing skill..."
    # Add setup commands here
elif [ "$ACTION" = "uninstall" ]; then
    echo "Uninstalling skill..."
    # Add cleanup commands here
fi
