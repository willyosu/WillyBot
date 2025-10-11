#!/bin/bash
cd /home/will/WillyBot
tmux new -d -s discord
while [ "$(hostname -I)" = "" ]; do
    sleep 5
done
tmux send-keys -t discord "python3 ./bot.py" Enter
