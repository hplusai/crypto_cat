Decription:
=============
Crypto Cat - Very simple trading bot (safe mode, aka smart invest). Partial profit close and partial rebuy.
IMPORTANT!: I checked this version only with USDT pairs.
More testing needed.

How it works : You may select a pair of tokens via web interface 
(https://127.0.0.1:8080 or https://<YOUR SERVER>:8080
Then, you may turn auto trading mode on, it's very simple automatization : 

Every Rebuy% down (price) we will buy Amo% and every Sell% - sell.
All % counts from last operation price.
The key of this strategy is a partial profit close and partial rebuy. Balance.
If rebuy% different from sell%,  Amo% will be calculated proportionally for buy and sell operations.
So, there is only 1 recommendation, example :
You may choose params like this :
Rebuy : every 20%
Sell : every 10% (Rebuy/2)
Amo : 5% (Sell/2)

For crypto market (for scam coins =) ) more recommended : 
Rebuy : 50%
Sell : 20%
Amo : 10%

In this case (when amo is less than min(Rebuy,Sell)) you may sell your token infinitely (while price going up). 
There is also some trick:
To keep it work with small balances (less than 10$ - min val for order on binance) 
To keep diversity of coins real =) Such pairs (orders) processing via 2 orders. 
We need to sell 5$ of some token : so we will buy 10$ (usd equvivalent to amo) and sell 15$ =).
Also it is strictly recommended to have a provision (at least 30$ for small opers).

Demo:
=============
To check how it works:
https://elcrypto.top:8080/
(we will try to keep this service running, but no garantee =) )
Add new pair to auto trading
.. image:: https://raw.githubusercontent.com/hplusai/crypto_cat/main/add_pair_window.png
Trade window
https://raw.githubusercontent.com/hplusai/crypto_cat/main/trade_window.png

Installation:
=============
This version contains webserver (built-in), so it could work as standalone app on your pc or on server (for many users).
(please do not forget to replace file "server.pem" if started on server, and you need to setup correct host name in cat.py : line webserv.StartServer(host='localhost',...)
Tested on Windows, CentOs should work on Mac as well. 
Messaging system through log files and telegram channel (Just click on links in web interface : BotFather and Your chat id).

To create API keys for trading (you may also try with view-access key =) - to check balance).
https://www.binance.com/en/my/settings/api-management

system reqs:
pip install -r requirements.txt

You may try to start task (server) manually:
python cat.py

Register job (cat.py task works for ~13 mins, just to avoid any accumulated errors, then it will be restarted via cron or windows scheduler - depends from you OS):
python reg_cron_job.py
After registration job will start automatically.

*Small tip, to completly remove annoying command-line window in Windows
you need to open your scheduler tasks, find task crypto_cat and change Security options to : "Run whether user is logged on or not".
