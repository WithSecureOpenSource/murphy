cd \utils

wget.py http://192.168.56.1:8901/helpers.exe
helpers.exe -oc:\utils\helpers

start /D \utils helpers\tooltip_killer.py
start /D \utils helpers\helper.py
exit
