import os, time
max_log_size=100000
log_file_name='log/app.log'
if not os.path.exists('log'):
    os.makedirs('log')

def log(s,log_name='',add_time=1,clear_log=0):
    global log_file_name
    if log_name!='':
        log_file_name=log_name
    sTime=time.strftime('%Y%m%d-%H.%M.%S',time.localtime())
    if os.path.exists(log_file_name):
        stat=os.stat(log_file_name)
        if stat.st_size>max_log_size:
            os.rename(log_file_name,log_file_name+'.'+sTime)
    mode=(clear_log and 'w') or 'a'
    s_pre=''
    if add_time:
        s_pre=sTime+' : '
    with open(log_file_name,mode) as f:
        f.write(s_pre+s+'\n')

def _log_main():
    log('works')

if __name__ == '__main__':
    _log_main()
