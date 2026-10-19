#!/usr/bin/env bash
# ValleyRBX - Cinematic Linux Roblox Studio Runtime
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$DIR/src:$PYTHONPATH"

# Run ValleyRBX with provided arguments
exec python3 -m studio_strapper "$@"
