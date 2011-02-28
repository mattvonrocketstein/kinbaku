""" kinbaku.python.comments
"""

class PythonComment(object):
    def rparent(self): pass

    def rowner(self):
        """ render owner """
        if isinstance(self.owner,str): return self.owner
        p  = self.owner.parent or ''
        pp = p and p.parent or ''
        ppp = pp and pp.parent or ''
        p = p and p[0].tagname
        pp = pp and pp[0].tagname
        ppp = ppp and ppp[0].tagname
        def fmt(x):
            if not x: return
            if isinstance(x,str):
                return x,x
            return x.tagname, str(x[0].astext()).strip()
        # eg: [('class_section', 'CBPlugin'), ('method_section', 'files')]
        tmp = [fmt(self.owner.parent), fmt(self.owner),]
        tmp = filter(None,tmp)
        tmp = [tpl[1] for tpl in tmp]
        tmp= '.'.join(tmp)
        return tmp


    def __str__(self):
        dox = console.color(self.text).rstrip()
        return '{lineno}:\t{dox}'.format(lineno=self.lineno,
                                          dox=dox, )
    def display(self):
        print str(self)

    def __init__(self,lineno=-1, text='', full_line=False,owner='??'):
        self.owner     = owner
        self.lineno    = int(lineno)
        self.text      = text
        self.full_line = full_line
Comment = PythonComment
