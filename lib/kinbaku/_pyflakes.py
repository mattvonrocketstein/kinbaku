""" kinbaku.pyflakes
"""

import compiler, sys
import os

checker = __import__('pyflakes.checker').checker

def check(codeString, filename):
   """ Check the Python source given by C{codeString} for flakes. """
   # Since compiler.parse does not reliably report syntax errors, use the
   # built in compiler first to detect those.
   try:
       compile(codeString, filename, "exec")
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
   except UnicodeError, msg:
       print >> sys.stderr, 'encoding error at %r: %s' % (filename, msg)
       return 1

   else:
       # Okay, it's syntactically valid.  Now parse it into an ast and check
       # it.
       tree = compiler.parse(codeString)
       w = checker.Checker(tree, filename)
       w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
       #for warning in w.messages:
       #   print warning
       return w.messages #len(w.messages)


def checkPath(filename):
   """ Check the given path, printing out any warnings detected."""
   fd = file(filename, 'U')
   try:
       return check(fd.read(), filename)
   finally:
       fd.close()
