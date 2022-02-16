import os, sys

def reg_cronjob():
    from crontab import CronTab
    my_cron = CronTab(user='root')
    for job in my_cron:
        if ('run_cat.sh' in job.command):
            return

    job = my_cron.new(command='cd '+os.path.dirname(__file__)+' && ./run_cat.sh')
    job.minute.every(1)
    my_cron.write()

def reg_winjob():
#    os.system('schtasks /create /sc MINUTE /tn crypto_cat /tr "python %s" /mo 1'%os.path.dirname(__file__))
    with open('crypto_cat.xml.tmp','r') as fr:
        s=fr.read()
        with open('crypto_cat.xml','w+') as fw:
            fw.write(s%os.path.dirname(__file__))

    os.system('schtasks /create /tn crypto_cat /xml "crypto_cat.xml" /f')
    os.system('schtasks /run /tn crypto_cat')

def reg_job():
    if sys.platform == "win32":
        reg_winjob()
    else:
        reg_cronjob()

reg_job()