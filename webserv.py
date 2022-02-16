# taken from http://www.piware.de/2011/01/creating-an-https-server-in-python/
# generate server.xml with the following command:
#    openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
# run as follows:
#    python simple-https-server.py
# then in your browser, visit:
#    https://localhost:4443
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver, selectors
import ssl
import utils
cached={}
poll_interval=0.01
ext_filter='js,png,html,css,gif'.split(',')

class CatServ(HTTPServer):
    pass

class CatReq(BaseHTTPRequestHandler):
    def _set_response(_):
        _.send_response(200)
        _.send_header('Content-type', 'text/html')
        _.end_headers()

    def do_GET(_):
        global httpd, _custom_get
        #logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(_.path), str(_.headers))
        p=_.path.lstrip('/').strip()
        p=p.split('?')
        pars=((len(p)>1) and p[1]) or ''
        if pars=='':
            pars={}
        else:
            pars=dict([x.split('=',1) for x in pars.strip().split('&')])
        p=p[0]
        #print(p)
        if (p == 'stop'):
            _.server.shutd=True
            return
        spl=p.split('.')
        if (len(spl)>1) and (spl[-1].lower() not in ext_filter):
            log('rejected:'+p)
            _._set_response()
            _.wfile.write('')
            return

        if (p!='') and (len(p.split('?')[0].split('.'))==1) and _.server._custom_get:
            ret=_.server._custom_get(p,pars)
            #else:
            #ret=b'<html><span>info</span></html>'
        else:               
            if (p == ''):
                p = 'cat.html'
            if p not in cached:
                with open(p,'rb') as f:
                    ret=f.read()
                    #cached[p]=ret
            else:
                ret=cached[p]
        _._set_response()
        _.wfile.write(ret)
        #else:_._set_response()
        #_.wfile.write("GET request for {}".format(_.path).encode('utf-8'))

    def do_POST(_):
        content_length = int(_.headers['Content-Length']) # <--- Gets the size of data
        post_data = _.rfile.read(content_length) # <--- Gets the data it_
        #print(post_data)
        #logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #        str(_.path), str(_.headers), post_data.decode('utf-8'))
        ret="POST request for {}".format(_.path).encode('utf-8')

        p=_.path.lstrip('/').strip()
        if (p!='') and (len(p.split('?')[0].split('.'))==1) and _.server._custom_post:
            ret=_.server._custom_post(p,post_data)
        _._set_response()
        _.wfile.write(ret)

def StartServer(host='127.0.0.1',port=8080, user_func=None, get_custom_handler=None, post_custom_handler=None):
    httpd=CatServ((host, port),  CatReq)
    httpd._custom_get=get_custom_handler
    httpd._custom_post=post_custom_handler
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile='./server.pem', server_side=True)
    #httpd.serve_forever()
    #exit(0)
    user_func_gen=None
    if user_func:
        user_func_gen=user_func()
    with socketserver._ServerSelector() as selr:
#    print(httpd.fileno())
        selr.register(httpd, selectors.EVENT_READ)
        httpd.shutd=False
        while not httpd.shutd:
            ready = selr.select(poll_interval)
        # bpo-35017: shutdown() called during select(), exit immediately.
            if httpd.shutd:
                break
            if ready:
                #print('ready1')
                httpd._handle_request_noblock()
                httpd.service_actions()
                #print('ready2')
            if user_func_gen:
                #print('user_func_gen1')
                try:
                    next(user_func_gen)
                except StopIteration:
                    break
                #print('user_func_gen2')

if __name__ == '__main__':
    StartServer()