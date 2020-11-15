SESSION=TTF

tmux has-session -t $SESSION
if [ $? -eq 0 ]; then
    echo "Session $SESSION already exists. Attaching."
    sleep 1
    tmux attach -t $SESSION
    exit 0;
fi

tmux new-session -d -s $SESSION
tmux split-window -t :0

tmux select-pane -t :.0
tmux send-keys "pipenv run upgrade-db" Enter
tmux send-keys "pipenv run start" Enter

tmux select-pane -t :.1
tmux send-keys "pipenv run start-celery-worker" Enter

tmux attach -t $SESSION:0

