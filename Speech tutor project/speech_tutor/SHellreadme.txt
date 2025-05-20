pkill -f "python app.py"

tail -f logs/app_output.log

tail -n 100 logs/app_output.log

bash run_speech_tutor.sh
