# Patterns in reporting
####################################################################
import sys, inspect

import pygments
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter,Terminal256Formatter
from IPython.ColorANSI import TermColors

# Pygments data
plex  = PythonLexer()
hfom  = HtmlFormatter()
hfom2 = HtmlFormatter(cssclass="autumn")
colorize  = lambda code: highlight(code, plex, hfom)
colorize2 = lambda code: highlight(code, plex, hfom2)


class console:
    """ """
    def __getattr__(self,name):
        x = getattr(TermColors, name.title(),None)
        if x!=None:
            def func(string,_print=False):
                z = x + string + TermColors.Normal
                if _print:
                    print z
                return z
            return func
        else:
            raise AttributeError,name

    @staticmethod
    def blue(string):
        """ TODO: generic function for this
        """
        return TermColors.Blue + string + TermColors.Normal

    @staticmethod
    def color(string):
        return highlight(string, plex, Terminal256Formatter())

    @staticmethod
    def draw_line(length=80,msg='',display=True):
        #out = style.ERROR('-' * length)
        print
        afterl = (length-len(msg)-2)
        endred = endblue = TermColors.Normal
        msg    = msg and ' '+msg.strip()+' '
        blue   = TermColors.Blue
        red    = TermColors.Red
        out    = '{red}--{endred}{blue}{msg}{endblue}{red}{rest}{endred}'
        out    = out.format(red=red,blue=blue,endred=endred,endblue=endblue,
                         msg=msg, rest= '-'* afterl)

        if display:
            print out
        return out
console=console()

def whoami():
    """ gives information about the caller """
    return inspect.stack()[1][3]

def whosdaddy():
    """ displays information about the caller's caller149
    """
    x = inspect.stack()[2]
    frame = x[0]
    fname = x[1]
    flocals = frame.f_locals
    func_name = x[3]
    if 'self' in flocals:
        header = flocals['self'].__class__.__name__
    else:
        header = '<??>'
    header = '  ' + header + '.' + func_name
    print '+', fname, '\n  ', header, '--',

def report(*args, **kargs):
    """ the global reporting mechanism.

          TODO: clean this up and allow subscribers like
               <log>, <syndicate>,  and <call-your-moms-cell-phone>.
    """
    global console
    whosdaddy()
    used_kargs=False
    if len(args)==1:
        main=args[0]
        ## If it can be formatted, apply kargs towards that effort
        if hasattr(main,'format'):
            try:
                print console.color(main.format(**kargs)).strip()
            except KeyError:
                print console.color(main)#,kargs
            else:
                used_kargs = True

        ## Otherwise, str it and send it to color console
        else:
            print console.color(str(main))

    elif args:
        print '\n        args=',
        if len(args)<3:
            print console.color(str(args)),
        else:
            prefix = '\n          '
            for arg in args:
                print '{prefix}{n} :: {arg}'.format(prefix=prefix, n=args.index(arg),
                                                             arg=console.color(str(arg)).strip()),
            print

    if kargs and not used_kargs:
        print '\n\tkargs({n})='.format(n=len(kargs))
        #flush = kargs.pop('flush',False)
        for k,v in kargs.items():
            print "\t  {k} {v}".format(k=console.red(str(k)),v=console.blue(str(v)).strip())

    #if flush:
    #    sys.stdout.flush() # is this even working with ipython?
