import inspect, os, datetime

def isCallable(obj):
    """ Return True if an object is callable, or False if not. """
    return hasattr(obj, "__call__")

class Core(object):
    """ General template to store all properties. If attributes do not exist, assign them and return Core(). """
    def __init__(_, *args, **kwargs):
        if args:
            _.args = args
        # Get keyword arguments.
        _.__dict__.update(kwargs)

    def __nonzero__(_):
        return _.__len__()

    def __len__(_):
        l=[1 for x in _.__dict__ if not (x.startswith('__') and x.endswith('__'))]
        return len(l)

    def __bool__(_):
         return len(_.__dict__) > 0

    def __cast__(_,o):
        if (len(_)==0):
            return type(o)()
        return _

    def __add__(_, o):
        return _.__cast__(o)+o

    def __sub__(_, o):
        return _.__cast__(o)-o

    def __mul__(_, o):
        return _.__cast__(o)*o

    def __div__(_, o):
        return _.__cast__(o)/o

    def __eq__(_, o):
        return _.__cast__(o) ==o

    def __ne__(_, o):
        return _.__cast__(o)!=o

    def __lt__(_, o):
        return _.__cast__(o)<o

    def __le__(_, o):
        return _.__cast__(o)<=o

    def __gt__(_, o):
        return _.__cast__(o)>o

    def __ge__(_, o):
        return _.__cast__(o)>=o

##        return
##
##    def __call__(self):
##        return self.states[state]
##    def __sub__(self, other):
##
##    def __mul__(self, other):
##
##    def __div__(self, other):
##object.__floordiv__(self, other)
##object.__mod__(self, other)
##object.__divmod__(self, other)
##object.__pow__(self, other[, modulo])
##object.__lshift__(self, other)
##object.__rshift__(self, other)
##object.__and__(self, other)
##object.__xor__(self, other)
##object.__or__(self, other)

    def __getitem__(_, key):
        if not isinstance(key, str):
            key=str(key)
        return _.__getattribute__(key)
#        return getattr(_, key)

    def __iter__(_):
        return iter(_.__dict__)

    def __delete__(_, key):
        del _.__dict__[key]

    def __delitem__(_, key):
        fl_stop=0
        if not isinstance(key, str):
            #search by object
            for k,v in tuple(_.__dict__.items()):
                if v==key:
                    del _.__dict__[k]
                    fl_stop=1

        if fl_stop:
            return
        key=str(key)
        del _.__dict__[key]

    def __setitem__(_, key, value):
        #setattr(_, key, value)
        return _.__setattr__(key, value)

    def __setattr__(_, key, value):
        # so this func will be called in __init__ and will
        # enter __getattribute__
#        if self.is_testing:
#            name = name.lower()
        return object.__setattr__(_, key, value)

    def __getattribute__(_, name):
        """ If an attribute is a function without arguments, return the call. """
        try:
            attributes = object.__getattribute__(_, name)
        except AttributeError as e:
           # For unknown attributes, return a fresh instance of Core (except for system attributes `__*__`).
            if name.startswith('__') and name.endswith('__'):
                raise
            attributes = Core()
            object.__setattr__(_, name, attributes)

        if isCallable(attributes):
            insp = inspect.getargspec(attributes)
            if (len(insp.args) == 0) and (attributes.__name__ == '<lambda>'):
                # Return the function call result.
                return attributes()
        return attributes

    def __as_json__(_,tabs='',tab=' ',flt=[]):
        if not _:
            return '""';
        ret='{'
        for k,v in _.__dict__.items():
            #ret+=tabs+k+'\n'
#            v_tabs=tabs+'\t'
            if isinstance(v,Core):
#                ret+=tabs+k+':\n'
                val=v.__as_json__(tabs+tab,tab,flt)
                ret+='"'+k+'"'+':'+val+','
                #ret+=val#+'\n'
            else:
                if isinstance(v,str):
                    val='"'+v+'"'
                    #val=val.replace('\n','\\n').replace('\r','\\r')
                else: #isinstance(v,datetime.datetime):
                    val=repr(v)
                #ret+=tabs+k+':'+val+',\n'
                ret+='"'+k+'"'+':'+val
                if not ret.endswith(','):
                    ret+=','
        ret+='}'
                #ret+=v_tabs+str(v)+'\n'

        return ret

    def __as_tree__(_,tabs='',tab=' '):
        ret=''
        for k,v in _.__dict__.items():
            #ret+=tabs+k+'\n'
#            v_tabs=tabs+'\t'
            if isinstance(v,Core):
                ret+=tabs+k+'\n'
                val=v.__as_tree__(tabs+tab)
                ret+=val#+'\n'
            else:
                if isinstance(v,str):
                    val=v
                    val=val.replace('\n','\\n').replace('\r','\\r')
                    val='"""'+val+'"""'
                else: #isinstance(v,datetime.datetime):
                    val=repr(v)
                ret+=tabs+k+'='+val+'\n'
                #ret+=v_tabs+str(v)+'\n'

        return ret
        """
        ret=''
        for k,v in _.__dict__.items():
            ret+=tabs+k+'\n'
            v_tabs=tabs+'\t'
            if isinstance(v,Core):
                val=v.__as_tree__(v_tabs)
                ret+=val+'\n'
            else:
                ret+=v_tabs+str(v)+'\n'

        return ret
        """

    def __load_tree__(_,tree_text=''):
        ret=tree_text.split('\n')
        ls=[(len(x)-len(x.lstrip()),x) for x in ret if (x.lstrip()!='') and (x.lstrip()[0]!='#')]
        min_tabs=0
        if ls:
            min_tabs=min(ls,key=lambda x:x[0])[0]
        last_objs={-1:_}
        for _len,s in ls:
            pos=_len-min_tabs
            line=s.lstrip()
            parent=last_objs[pos-1]
            if ('=' in line):
                p1,p2=line.split('=',1)
                parent[p1]=eval(p2)
            else:
                lo=parent[line]#._dummy=0
                last_objs[pos]=lo
        return _

    def __str__(_):
        return _.__as_tree__()
        #return 'Person(name='+self.name+', age='+str(self.age)+ ')'

    def __repr__(_):
        return _.__as_json__()

    def __save__(_,fname):
        with open(fname,'w') as f:
            s=_.__as_tree__()
            f.write(s)
        return _

    def __restore__(_,fname):
        if os.path.exists(fname):
            with open(fname,'r') as f:
                s=f.read()
                _.__load_tree__(s)
        return _
                #_.__dict__.update(eval(s))

    def pop(_,o):
        _.__dict__.pop(o,'')

    def update(_,d):
        for x in d:
            _[x]=d[x]

def restore(fname):
    return Core().__restore__(fname)

def save(fname,obj):
    if isinstance(obj,Core):
        return obj.__save__(fname)
    else:
        raise Exception('This method could be used only for Core objects and his descendants')

"""
class Reverse:
    def __init__(_, data):
        _.data = data
        _.index = len(data)

    def __iter__(_):
        return iter(_.__dict__)

    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.data[self.index]

rev = Reverse('spam')
#iter(rev)
for ch in rev:
    print(ch)

exit(0)
https://stackoverflow.com/questions/38700734/how-to-implement-next-for-a-dictionary-object-to-be-iterable
def __iter__(self):
    return iter(self.container)
If you must make your class an iterator, you'll have to somehow track a current iteration position and raise StopIteration once you reach the 'end'. A naive implementation could be to store the iter(self.container) object on self the first time __iter__ is called:

def __iter__(self):
    return self

def next(self):
    if not hasattr(self, '_iter'):
        self._iter = iter(self.container)
    return next(self._iter)
"""
def core_main_test():
#    global c
    #tests
    #c=Core()
    #del c.aa
    #c.pop('aa')
    #return
    c=Core(a=1,b={2:3})
    c.dt=datetime.datetime.now()
    c.__save__('aaa.txt')
    c.__restore__('aaa.txt')
    print(c.dt,type(c.dt))
    print(c.__as_json__())
    return
    c.not_denined+=1
    print('c.not_denined+1',c.not_denined)
    for x in c:
        print(x)
    c['a']=1
    c['1']=2
    c.a=1
    c.k.t=1
    print(c.__as_tree__())
    c.__save__('aaa.txt')
#    print(c.a,c.b)
#    print(c)
    tst=Core()
    lev=tst.lev
    lev.utug='zebra\ngnu'
    tst.__restore__('aaa.txt')
    tst.__save__('aaa1.txt')
    tst.__restore__('aaa1.txt')
    print(tst.__as_tree__())

if __name__ == '__main__':
    #if Core():
    #    print('1243')
    core_main_test()
