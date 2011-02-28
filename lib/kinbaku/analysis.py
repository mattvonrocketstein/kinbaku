""" kinbaku.analysis
"""
import os

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
    """ """
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
    return x# print x.cb_list_messages
    #raise Exception,x

def get_comments(fpath):
    """ """
    import inspect
    NotImplemented
    #getsource
    #[ commentopen(fpath).readlines() if line.strip.startswith('#') ]

REMOVE_LIST = 'is a none return else for import def if'.split()
def word_summary(fpath, remove_list=REMOVE_LIST):
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


"""
Implementation of the command-line I{pyflakes} tool.
"""

import compiler, sys
import os

checker = __import__('pyflakes.checker').checker

def pychecker_helper(codeString, filename):
    """
    Check the Python source given by C{codeString} for flakes.

    @param codeString: The Python source to check.
    @type codeString: C{str}

    @param filename: The name of the file the source came from, used to report
        errors.
    @type filename: C{str}

    @return: The number of warnings emitted.
    @rtype: C{int}
    """
    # Since compiler.parse does not reliably report syntax errors, use the
    # built in compiler first to detect those.
    try:
        try:
            compile(codeString, filename, "exec")
        except MemoryError:
            # Python 2.4 will raise MemoryError if the source can't be
            # decoded.
            if sys.version_info[:2] == (2, 4):
                raise SyntaxError(None)
            raise
    except (SyntaxError, IndentationError), value:
        msg = value.args[0]

        (lineno, offset, text) = value.lineno, value.offset, value.text

        # If there's an encoding problem with the file, the text is None.
        if text is None:
            # Avoid using msg, since for the only known case, it contains a
            # bogus message that claims the encoding the file declared was
            # unknown.
            print >> sys.stderr, "%s: problem decoding source" % (filename, )
        else:
            line = text.splitlines()[-1]

            if offset is not None:
                offset = offset - (len(text) - len(line))

            print >> sys.stderr, '%s:%d: %s' % (filename, lineno, msg)
            print >> sys.stderr, line

            if offset is not None:
                print >> sys.stderr, " " * offset, "^"

        return 1
    else:
        # Okay, it's syntactically valid.  Now parse it into an ast and check
        # it.
        tree = compiler.parse(codeString)
        w = checker.Checker(tree, filename)
        w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
        #for warning in w.messages: print warning
        return w
