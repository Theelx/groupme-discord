#!/bin/bash
until python3 everything_main.py; do
    echo "Script 'main.py' crashed with exit code $?.  Respawning.." >&2
    sleep 2
done
