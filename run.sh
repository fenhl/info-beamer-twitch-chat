#!/bin/zsh

if [[ -f data.json ]]; then
    rm data.json
fi
echo '[]' > data.json

INFOBEAMER_INFO_INTERVAL=86400 info-beamer . &

sleep 1

./update.py "$@" || {
    exit_code=$?
    sudo killall info-beamer
    exit $exit_code
}