echo off

:start

start /normal  "t-bot" python main.py

echo ------------
echo - t-bot on -
echo ------------

TIMEOUT /T 10800 /NOBREAK

taskkill /FI "WINDOWTITLE eq t-bot" /F /T

echo -------------
echo - t-bot off -
echo -------------

goto start