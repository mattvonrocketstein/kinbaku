""" kinbaku.scope.cli

    command-line-interface aspect of scope plugin
"""
import sys
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline

class CLI(KinbakuPlugin):

    @classmethod
    def spawn(kls, **kargs):
        return kls() #Pythoscope()
