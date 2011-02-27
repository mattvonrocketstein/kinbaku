""" kinbaku: use cases for rope

    This file is just used for scratch-work / notes
      for testing: see http://pylib.org/io.html#io-capturing-examples
"""

def sig_example():
    from pep362 import signature
    def f(a,b,c): pass
    sig = signature(f)
    parameters = sig._parameters #{'a':parameter1,'b':parameter2, .. }
    print 'sig_example',sig, parameters
    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()

if __name__=='__main__':
    sig_example()
