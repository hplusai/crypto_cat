from binance.client import Client
from binance.enums import *
import traceback,utils,sys
import requests,urllib,core, os, math
from core import Core
real_time=1
from utils import *
import telegram

#_stop=0#0.05 #5%
#fl_buy_side=False
cl=None
acc=None
pair=None
prices={}
cached_price={}

def std_base_amount(s=''):
    if s.upper()=='BTC':
        return 0.00002
    if s.upper()=='ETH':
        return 0.001
    return 11

exch_inf={}
def get_tick_step():
    global exch_inf
    if not exch_inf:
        exch_inf=get_client().get_exchange_info()

    symbs=exch_inf['symbols']
    for x in symbs:
        k=x['symbol']
        if k!=pair.symbol:
            continue
        flt=x['filters']
        tmp=flt[0]
        minPrice,maxPrice,tick=tmp['minPrice'],tmp['maxPrice'],tmp['tickSize']
        tmp=flt[2]
        break
    return (tick,tmp['stepSize'])

def fmt_num_to(num, fmt, fl_buy=True):
#  precision = step_size_to_precision(step_size_str)
  rTo=float(fmt)
  scl=1.0/rTo
  if fl_buy:
    num=math.ceil(num*scl)
  else:
    num=math.floor(num*scl)

  num/=scl
  if rTo<1:
    #print(num,scl,rTo)
    rTo=len(fmt.rstrip('0'))-2
    return "{:0.0{}f}".format(num, rTo)
  else:
    return num

def fmt_amount(a, fl_buy=True):
    tick,token_step=get_tick_step()
    return fmt_num_to(a,token_step,fl_buy)

def fmt_price(p):
    tick,token_step=get_tick_step()
    return fmt_num_to(p,tick)

def is_spot():
    return 1
    #global pair
    #return pair.auto_profit>2.5 #$('#acc_type').val()=='spot';

def _post_order(**kw):
    global pair
    cl=get_client()

    kw['symbol']=pair.symbol
    _price=price()
    _buy_side=kw['side'].lower()=='buy'
    _fmt_amo=fmt_amount(kw['quantity'],_buy_side)
    a_name=(pair and pair.acc_name) or 'undef'
    #if not a_name:
    msg='%s.%s;%s;%s(%.2f$);%s'%(a_name,pair.symbol,kw['side'],_fmt_amo,_price*float(_fmt_amo),fmt_price(kw.get('price',_price)))
    if 'price' in kw:
        _p=kw['price']
        kw['type']=ORDER_TYPE_LIMIT
        fl_price_bigger=kw['price']>_price
        if fl_price_bigger and _buy_side:
            kw['type']=ORDER_TYPE_STOP_LOSS_LIMIT
            kw['stopPrice']=fmt_price(_p/1.001)
        if ((not fl_price_bigger) and (not _buy_side)):
            kw['type']=ORDER_TYPE_STOP_LOSS_LIMIT
            kw['stopPrice']=fmt_price(_p*1.001)
        kw['price']=fmt_price(kw['price'])
    else:
        kw['type']=ORDER_TYPE_MARKET
        kw.pop('timeInForce')

    kw['quantity']=_fmt_amo
    kw['side']=kw['side'].upper()
    print(str(kw))
    if real_time:
        if is_spot():
            #return
            cl.create_order(**kw)
            """symbol='BNBBTC',
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=100,
            price='0.00001')"""
        else:
            kw['isIsolated']='true'
            cl.create_margin_order(**kw)#, price=price)
    else:
        amo=float(kw['quantity'])
        bal=get_balances()
        tok=bal.token
        bas=bal.base
        if (not ('stopPrice' in kw)) and (not ('price' in kw)):
            sign=1
            if not _buy_side:
                sign=-1
            tok.free+=amo*sign
            bas.free-=amo*sign*_price
        else:
            msg='Stop Limit: '+msg
        #tok.locked+=amo
    info(msg)

def post_order(_amount,_price=0):
  global pair
  save_a=pair.last_a
  try:
    kw=None
    if _amount>0:
        side='buy'
        _amount=_amount*1.01
    else:
        side='sell'
        #sometimes not enough funds.
        _amount=_amount/1.01
    o_amo=_amount
    _amount=abs(_amount)
    kw={'side':side,'quantity':_amount,'timeInForce':'GTC'}
    if _price:
        kw['price']=_price
    _post_order(**kw)
    pair.last_p=price()
    if (save_a*_amount)<0: # not same sign
        pair.last_pp=pair.last_p
    pair.last_a=o_amo

  except:
    err_str='ERROR:'+str(kw)+' .'+traceback.format_exc()
    error(err_str)

def cancel_orders():
    try:
        if not real_time:
            info('cancel_orders')
            bal=get_balances()
            bal.token.free+=bal.token.locked
            bal.token.locked=0
            bal.base.free+=bal.base.locked
            bal.base.locked=0
            return

        cl=get_client()
        if not pair.bal:
            #init acc
            get_balances()
        ords=cl.get_open_margin_orders(symbol=pair.symbol,isIsolated=True)
        fl_error=0
        for x in ords:
            try:
                cl.cancel_margin_order(symbol=x['symbol'],type=x['type'],orderId=x['orderId'],isIsolated=True)
            except:
                fl_error=1
        if fl_error:
            err_str='ERROR. (will ignore, but please check. Something wrong with Binance):'+traceback.format_exc()
            error(err_str)
    except:
        err_str='ERROR:'+traceback.format_exc()
        error(err_str)

def norm_bal(b):
   r=Core(interest=float(b['interest']),locked=float(b['locked']),free=float(b['free']), borrowed=float(b['borrowed']))
#   r.bal=r.free+r.locked-r.borrowed#-r.interest
   r.asset=b['asset']
   r.name=r.asset
   return r

def usd_balance():
    bal=get_balances()
    return full_bal(bal.base)+full_bal(bal.token)*price()

def full_bal(tok):
    return tok.free+tok.locked-tok.borrowed-tok.interest

def get_null_bal_rec():
    symb=pair.symbol.upper()

    tok=Core(interest=0,locked=0,free=0, borrowed=0)
    if symb.endswith('BTC'):
        tok.name=pair.symbol[:-3]
    else:
        tok.name=pair.symbol[:-4]
    #property()
    #tok.bal=lambda : tok.free+tok.locked-tok.borrowed-tok.interest
    tok.asset=tok.name

    bas=Core(interest=0,locked=0,free=0, borrowed=0)
    #bas.bal=lambda:bas.free+bas.locked-bas.borrowed-bas.interest
    if symb.endswith('BUSD'):
        bas.name='BUSD'
    elif symb.endswith('USDT'):
        bas.name='USDT'
    elif symb.endswith('BTC'):
        bas.name='BTC'
    else:
        raise Exception('Symbol %s with such base does not supported!'%symb)

    bas.asset=bas.name

    return Core(token=tok,base=bas)

def get_balances(g_bals=None):
    global pair
    if not real_time:
        if not pair.bal:
            pair.bal=get_null_bal_rec()
        return pair.bal

    prop='assets'
    #if not pair.bal:
    if g_bals:
        pair.bal=g_bals[pair.symbol]
    else:
        cl=get_client()
        #pair.bal=cl.get_isolated_margin_account()
        if is_spot():
            bal=cl.get_account()
            p_bal=get_null_bal_rec()
            for key in bal['balances']:
                if (key['asset']==p_bal.token.name):
                    p_bal.token.free=float(key['free'])
                    p_bal.token.locked=float(key['locked'])

                if (key['asset']==p_bal.base.name):
                    p_bal.base.free=float(key['free'])
                    p_bal.base.locked=float(key['locked'])
            pair.bal=p_bal
            return pair.bal
        else:
            pair.bal=cl.get_isolated_margin_account(symbols=pair.symbol)
        if prop not in pair.bal:
            bal=get_null_bal_rec()
            transfer_to_spot(bal.base.asset,-1)
            return bal
        #pair.bal=cl.create_isolated_margin_account(base=pair.token, quote=pair.base)

#    prop='userAssets'
#    if prop not in ma:
#        prop='balances'

    c=Core(token=None,base=None)
    if prop not in pair.bal:
        pair.bal=get_null_bal_rec()
        return pair.bal

    for key in pair.bal[prop]:
        if (key['symbol']==pair.symbol):
            k=key['baseAsset']
            c.token=norm_bal(k)

            k=key['quoteAsset']
            c.base=norm_bal(k)

#    if (not c.token) or (not c.base):
#        bal=get_null_bal_rec()
#        transfer_to_spot(bal.base.asset,-1)

    pair.bal=c
#    for key in ma[prop]:
#        ass=key['asset']
#        if (ass in (token,base)) or (not fl_def_only):
#            bal[ass]=key
#'borrowed': u'0.00000000', u'locked': u'0.00000000'
#    ma.pop(prop)
#    bal['_info']=ma
    return pair.bal

def msg(s):
    global acc
    s=s.strip()+'\n'
    try:  
      bot = telegram.Bot(str(acc.tg_token))
      bot.send_message(chat_id=str(acc.tg_chat_id), text=s)
    except:
      info('error:'+str(acc.tg_token),0)

def error(s=''):
    info('error: '+s)

additional_info=''
def info(s,tg_msg=1):
    global pair
    s=additional_info+'\n'+s
    s_l=s.lower()
    flErr='error' in s_l
    flt_rep_bor=('repay' in s_l) or ('borrow' in s_l)
    if flErr:
        log(s+traceback.format_exc()+str(traceback.format_stack())+'\n')
    else:
        log(s)
    print(s)
    a_name=(pair and pair.acc_name) or 'undef'
    if a_name in ('uni','cat'):
        tg_msg=(not flt_rep_bor) or flErr
    if tg_msg:# and (((not pair.auto_profit) or (not flt_rep_bor)) or flErr):
        max_len=250
        if len(s)>max_len:
            s=s[:max_len]
        msg(s)

clients={}
def get_client(_acc=None):
    global acc
    key=''
    secret=''
    if _acc is None:
        _acc=acc
    if _acc is not None:
        key=_acc.key
        secret=_acc.secret

#    key=''
#    secret=''
    if key in clients:
        ret=clients[key]
    else:
        ret=Client(key, secret)
        clients[key]=ret
    return ret

def upd_prices():
    global prices
    if not real_time:
        return
    cl=clients.get('',None)
    if not cl:
        cl=Client('', '')
        clients['']=cl
    #cl=get_client()
    data=cl.get_all_tickers()
    prices={d["symbol"]: float(d["price"]) for d in data}
    #return prices

def price(_pair=None):
    if _pair is None:
        _pair=pair
    if not real_time:
        return cached_price[_pair.symbol]
    return prices[_pair.symbol]
