""" kinbaku.bin.kinbaku:  the command line script

        $ kinbaku code --path=$HOME/code --search foobar
        $ kinbaku code --path=$HOME/code --search foobar --rules inst:xyz

        $ kinbaku detect --path=$HOME/code --tests

        $ kinbaku validate --path=$HOME/code

"""

from optionparser import OptionParser
