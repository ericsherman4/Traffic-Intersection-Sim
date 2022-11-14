@ECHO OFF
ECHO Hello, I will execute your commands now.
REM call is used when you are calling another script, the keyword tells it to return to this bat script when the called script terminates.
call conda deactivate
ECHO deactivated
call conda activate vpython
ECHO activated
jupyter notebook