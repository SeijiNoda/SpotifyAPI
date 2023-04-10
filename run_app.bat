:: This file executes the Flask server on a new CMD window and calls itself on 
:: the original tab by executing caller.py
ECHO OFF
ECHO running playlist maker
START CMD /k run_server.bat
ECHO MESSAGE: Running server...
TIMEOUT 2
python "caller.py"
ECHO MESSAGE: Finished program, ending now.
PAUSE
EXIT