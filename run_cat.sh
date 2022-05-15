#!/usr/bin/bash
cur_time=`date +%s`
last_mod=`stat -c "%Y" log/app.log`
c_pid=`pgrep -f "cat.py"`
diff_sec=$(($cur_time-$last_mod))
#if process is running
if [ ! -z "$c_pid" ]; then
#if there is no log update for 5 min - kill it and restart.
  if [ $diff_sec -gt 300 ]; then
    kill $c_pid
    python3 cat.py
  else 
    exit
  fi  
else 
    python3 cat.py
fi
