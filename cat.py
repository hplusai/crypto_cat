import os,time, json, subprocess, json
from core import *
import order,datetime, math
import traceback,urllib
from order import *
import ssl
import webserv
ssl._create_default_https_context = ssl._create_unverified_context
tstamp2date=datetime.datetime.fromtimestamp
now=datetime.datetime.now
t_last_oper=now()
#f_data='data.txt'
#f_tmp='tmp.txt'
f_setts='setts.txt'
#upd_last_check=now()

setts=restore(f_setts)
#pairs_pop_queue=[]

def get_float(f,defv=0.0):
    if isinstance(f,str):
        if f=='':
            return defv
        f=f.replace(',','.')
    return float(f)

def save_setts():
    save(f_setts,setts)

def upd_act_prices(p):
    _sell=1+p.profit/100.0
    _buy=1-p.rebuy/100.0

    p.sell_price=_sell*p.last_p
    p.buy_price=_buy*p.last_p

def get_tok_base(symb, toks):
#    log('ahueli blyadi')
#    log(symb)
    if '/' in symb:
        return symb.split('/')
    if '_' in symb:
        return symb.split('_')

    if symb.endswith('USDT'):
        return [symb[:-4],'USDT']

    if symb.endswith('BUSD'):
        return [symb[:-4],'BUSD']

    if symb.endswith('BTC'):
        return [symb[:-3],'BTC']

    if symb.endswith('ETH'):
        return [symb[:-3],'ETH']

    if symb.endswith('BNB'):
        return [symb[:-3],'BNB']

    if symb.endswith('XRP'):
        return [symb[:-3],'XRP']

    if symb.endswith('TRX'):
        return [symb[:-3],'TRX']

    for x in toks:
        if symb.endswith(x) and (symb[:-len(x)] in toks):
            return [symb[:-len(x)],x]

    #log('cannot split: '+symb)
    return None

def _custom_get(p,pars):
    global t_last_oper
#    line=data
    c=Core(**pars)
    ret=[]
    if (p=='info'):
        tot={}
        cur=setts[c.key]
        t_last_oper=now()
        try:
            cl=get_client(c)
            bal=cl.get_account()
            #log(str(order.prices.items()))
            for key in bal['balances']:
                token=key['asset']
                amo=float(key['free'])+float(key['locked'])
                t_usd=token+'USDT'
                t_btc=token+'BTC'
                b_usd='BTCUSDT'
                usd=0
                if token=='USDT':
                    usd=amo
                elif t_usd in order.prices:
                    usd=amo*order.prices[t_usd]
                else:
                    if t_btc in order.prices:
                        in_btc=amo*order.prices[t_btc]
                        usd=in_btc*order.prices[b_usd]
                    else:
                        usd=0
                tot[token]=Core(usd=usd,amo=amo,name=token)

            tok,bas=get_tok_base('BTCUSDT',tot.keys())
            for n in cur.pairs:
                v=cur.pairs[n]
                v.price=order.prices[v.symbol]
                tok,bas=get_tok_base(n,tot.keys())
                v.token=tot[tok]
                v.base=tot[bas]
                ret.append(v)
        except:
            info('error')

        for (symb,price) in order.prices.items():
            if symb in cur.pairs:
                continue
            #_b=bal[symb]
            tbase=get_tok_base(symb,tot.keys())
            if tbase is None:
                continue
            tok,bas=tbase
            try:
                if (bas not in tot) or (tok not in tot):
                    t,b=Core(usd=0,amo=0,name=tok),Core(usd=0,amo=0,name=bas)
                else:
                    t,b=tot[tok],tot[bas]
                pars={'symbol':symb,'price':price,'mode':'none','token':t,'base':b}
                ret.append(pars)
            except:
                info('error')

    return bytes(str(ret),'utf-8')

def _custom_post(p,data):
    #global pairs_pop_queue
    line=data.decode("utf-8")
    log(line)
    pars=dict([r[0],urllib.parse.unquote(r[1])] for r in [x.split('=',1) for x in line.strip().split('&')])
    c=Core(**pars)
    if p=='trade':
        save_acc=order.acc
        save_pair=order.pair
        try:
            order.acc=c
            order.pair=c
            post_order(float(c.amo))
        finally:
            order.pair=save_pair
            order.acc=save_acc
    if p!='upd':
        return
    if str(c.key).strip()=='':
        return
    try:
        cur=setts[c.key]
        token=c.tok
        base=c.bas
        #c.symbol.split('_')
        symbol=c.symbol.replace('_','')
        if c.mode=='none':
            #pairs_pop_queue.append(symbol)
            cur.pairs.pop(symbol)
        else:
            cur.key=c.key
            cur.secret=c.secret
            cur.tg_token=c.tg_token
            cur.tg_chat_id=c.tg_chat_id
            c.pop('secret')
            c.pop('key')
            c.pop('tg_token')
            c.pop('tg_chat_id')
            v=cur.pairs[symbol]
            v.symbol=symbol
            v.token=Core(usd=0,amo=0,name=token)
            v.base=Core(usd=0,amo=0,name=base)
            v.mode='auto'
            v.profit=get_float(c.profit)
            v.rebuy=get_float(c.rebuy)
            v.act_amo=get_float(c.act_amo)
            #log(c.price)
            v.last_p=get_float(c.last_p)
            upd_act_prices(v)
        save_setts()
    except:
        error()
    return b''#bytes(p+data,'utf-8')

def as_secs(time_delta):
    return time_delta.seconds+(time_delta.microseconds/1e6)

def main():
    global stop_time,t_last_oper
#    while 1:
#        yield
#    return
    t_last_oper=now()
    t_last_req=now()
    _now=now()
    stop_time=_now+datetime.timedelta(minutes = 13)
    iter_cnt=0
    time_koef=2
    upd_prices()
    while _now<stop_time:
        iter_cnt+=1
        if iter_cnt%100==0:
            log('iter=%d'%iter_cnt)
        while as_secs((now()-t_last_req))<time_koef:
            yield
        upd_prices()
        t_last_req=now()
        accs=[x for x in setts]
        for acc_name in accs:
            acc=setts[acc_name]
            order.acc=acc
            symbs=[x for x in acc.pairs]
            for symbol in symbs:
                try:
                    pair=acc.pairs[symbol]
                    order.pair=pair
                    p=price()
                    if not pair.last_p:
                        pair.last_p=p

                    #log(symbol+':secs='+str(as_secs((now()-t_last_oper))))
                    #log('mlya %s<%s<%s:'%(pair.buy_price,p,pair.sell_price))
                    if (p>pair.buy_price) and (p<pair.sell_price):
                        continue

                    #log(symbol+':try secs')
                    while as_secs((now()-t_last_oper))<1*time_koef:
                        yield

                    if symbol not in acc.pairs:
                        continue #probably was removed

                    log(symbol+':anal')
                    t_last_oper=now()
                    p_koef=p/pair.last_p
                    std_base_amo=std_base_amount(pair.base.name)
                    std_amo=std_base_amo/p
                    bal=get_balances()
                    amo=bal.token.free*(pair.act_amo/100)
                    #amo=max(amo,std_amo)
                    #log('che za her:'+str(p)+';'+str(pair.buy_price))
                    log(symbol+'cmp')
                    if (p>pair.sell_price):
                        _sell=1+pair.profit/100.0
                        amo=amo*math.log(p_koef,_sell)*max(pair.profit/pair.rebuy,1)/_sell
                        #log(symbol+': Free='+str(bal.token.free)+'Amo='+str(amo))
                        if bal.token.free<amo:
                            continue
                        amo=-amo
                    elif (p<pair.buy_price):
                        if bal.base.free<std_base_amo*1.5:
                            continue
                        _buy=1-pair.rebuy/100.0
                        amo=amo*math.log(p_koef,_buy)*max(pair.rebuy/pair.profit,1)/_buy
                        if bal.base.free<amo*p:
                            continue
                        #amo=max(min(bal.base.free/2,amo*p),std_base_amo)/p
                    else:
                        continue
                    #if bal.token.free<std_amo:
                    #    continue
                    #need to move this part into post_order
                    flDone=0
                    if abs(amo)<std_amo:
                        safe_koef=1.2
                        if amo<0:
                            if bal.base.free>std_base_amo*safe_koef:
                                #buy std
                                post_order(std_amo)
                                #sell sum std+amo. reminder amo with minus
                                post_order(amo-std_amo)
                                flDone=1
                            elif bal.token.free>(abs(amo)+std_amo)*safe_koef:
                                #sell sum std+amo. reminder amo with minus
                                post_order(amo-std_amo)
                                #buy std
                                post_order(std_amo)
                                flDone=1
                        elif amo>0:
                            if bal.base.free>(std_base_amo+amo*p)*safe_koef:
                                #buy sum
                                post_order(std_amo+amo)
                                #sell std
                                post_order(-std_amo)
                                flDone=1
                            elif bal.token.free>amo*safe_koef:
                                #sell std
                                post_order(-std_amo)
                                #buy sum
                                post_order(std_amo+amo)
                                flDone=1
                        else:
                            continue
                    if not flDone:
                        post_order(amo)
                    sMsg='%s:%.2f$(%.8f); %s'%(symbol,amo*p,amo,acc_name[:10])
                    info(sMsg)
                    pair.last_p=p
                    upd_act_prices(pair)
                    t_last_oper=now()
                    save_setts()
                except:
                    error()

        _now=now()
        t_last_req=_now
        yield
        #time.sleep(1)
    webserv.shutd=True

try:
    log('Init app.')
    webserv.StartServer(host='localhost',user_func=main,get_custom_handler=_custom_get,post_custom_handler=_custom_post)
    save_setts()
except:
    error()

p = subprocess.Popen(['python3','cat.py'], start_new_session=True)
#os.startfile('python3 cat.py &')
