#For ZSH/Linux
#!/bin/zsh

cd ~/SubstanceSearch
source .venv/bin/activate
python app.py & firefox --new-window http://127.0.0.1:5000
exit 0
