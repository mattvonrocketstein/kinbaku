""" kinbaku.analysis
"""
def pyflakes(fpath):
    """  given a file, returns a list of messages like:

           [ <pyflakes.messages.UnusedVariable object at 0x973a1ac>,
             <pyflakes.messages.RedefinedWhileUnused object at 0x972cc6c>, ]
    """
    from kinbaku._pyflakes import checkPath
    return checkPath(fpath)

def combine_word_summary(ws):
    """ entry that accumulates results from all individual files """
    all_keys = set(reduce(lambda x,y:x+y,[ ws[fpath].keys() for fpath in ws ]))
    words_in_grammer   = set('return the else a and is in if import or set os sys false true for while'.split())
    all_keys -= words_in_grammer
    _all=[]
    for k in all_keys:
        row=[]
        for fpath in ws:
            res=ws[fpath].get(k,None)
            if res:
                row.append(res)
            if row:
                _all.append([k,row])
    return dict(__all__=dict([ [x, sum(y)] for x,y in _all ]))

def count_lines(fpath):
    out = os.popen('wc -l "{fname}"'.format(fname=fpath))
    out = out.read().strip().split()[0]
    out = int(out)
    return out

def pylint(fpath):
    from pylint import lint
    import sys
    tmp=sys.exit
    sys.exit=lambda x: 1
    x=lint.Run(['--errors-only', fpath])
    print dir(x)
    raise Exception,x

def get_comments(fpath):
    """ """
    import inspect
    #getsource
    #[ commentopen(fpath).readlines() if line.strip.startswith('#') ]

def word_summary(fpath, remove_list=['']):
    """ returns dict(word=frequency) """
    from string import punctuation
    N = 10
    words = {}

    words_gen = (word.strip(punctuation).lower() for line in open(fpath)
                 for word in line.split())

    for word in words_gen:
        words[word] = words.get(word, 0) + 1

    top_words = sorted(words.iteritems(),
                       key=lambda(word, count): (-count, word))[:N]
    top_words   = dict(top_words)

    for x in remove_list:
        if x in top_words: del top_words[x]
    return top_words

