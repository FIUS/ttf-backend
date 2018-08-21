SESSION=TTF-DEPLOY

tmux has-session -t $SESSION
if [ $? -eq 0 ]; then
    echo "Session $SESSION already exists. Attaching."
    sleep 1
    tmux attach -t $SESSION
    exit 0;
fi

tmux new-session -d -s $SESSION
tmux split-window -t :0
tmux split-window -t :0

tmux select-pane -t :.1
tmux send-keys cd Space total_tolles_ferleihsystem Enter
tmux send-keys npm Space run Space start Enter

tmux select-pane -t :.2
tmux send-keys . Space venv/bin/activate Enter
tmux send-keys export Space FLASK_APP=total_tolles_ferleihsystem Enter
tmux send-keys export Space MODE=production Enter
tmux send-keys celery Space -A space total_tolles_ferleihsystem.celery Space worker Space -B Space --loglevel=info Enter

tmux select-pane -t :.0
tmux send-keys . Space venv/bin/activate Enter
tmux send-keys export Space FLASK_APP=total_tolles_ferleihsystem Enter
tmux send-keys export Space FLASK_DEBUG=1 Enter
tmux send-keys export Space MODE=production Enter
tmux send-keys flask Space create_db Enter
tmux send-keys flask Space run Space --host=0.0.0.0 Space --port=80 Enter

tmux attach -t $SESSION:0
