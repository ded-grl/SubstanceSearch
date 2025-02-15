::For cmd.exe

cd ../
::venv doesn't seem to work right on Windows
start python app.py
"C:\Program Files\Mozilla Firefox\firefox.exe" --new-window 127.0.0.1:5000
echo "Done!"
