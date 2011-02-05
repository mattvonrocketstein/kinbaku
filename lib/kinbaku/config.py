""" kinbaku.config

      The config plugin

"""
import sys
import json
import os

from kinbaku.report import console, report
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline

class ConfigPlugin(KinbakuPlugin):
    """ """

class Config(ConfigPlugin):
    """ """
    @classmethod
    def spawn(kls, **kargs):
        return Config()

    @publish_to_commandline
    def set(self, *args):
        """ set a value in kinbaku's persistent configuration """
        if not args: return

        if isinstance(args[0], dict):
            self.write(json.dumps(args[0]))
            return
        try:
            obj = eval(args[0])
        except SyntaxError:
            # ie one=two,three=four
            if len(args)==1:
                args = dict([ arg.split('=') for arg in args[0].split(',') ])
            #ie one=two three=four
            else:
                args = dict([ arg.split('=') for arg in args ])
            report("Updating config with: {data}",data=args)
        else:
            if isinstance(obj,dict):
                args=obj
            else:
                raise Exception,obj

        current = self.dct or {}
        current.update(args)
        fhandle = self.open()
        fhandle.write(json.dumps(current))
        fhandle.close()

    @publish_to_commandline
    def show(self, setting_name=None):
        """ display current configuration """
        if not setting_name:
            print "  kinbaku settings:"
            extras = {'config-file':self.fpath}
            for k in self.dct:
                print "\t{key}\t{val}".format(key=k, val=self.dct[k])
            for k in extras:
                print "\t{key}\t{val}".format(key=k, val=extras[k])
        else:
            print "\t{key}\t{val}".format(key=setting_name, val=self.dct[setting_name])


    def __getitem__(self, x):
        """ """
        return self.dct.get(x)

    @property
    def dct(self):
        """ """
        x = self.read()
        try:
            return json.loads(x)
        except ValueError:
            print "Error decoding: ",x
            sys.exit()

    @publish_to_commandline
    def keys(self):
        """ show all keys in config dictionary """
        self.dct.keys()

    def get(self, arg=None, default=None):
        """ dict compatibility """
        return self.dct.get(arg, default)

        v = self.read()
        if not v:
            return default
        else:
            try:
                return self[arg] or default
            except ValueError:
                raise ValueError,"Could not load: {f}".format(f=self.read())
            raise Exception,'test'

    @property
    def default_fpath(self):
        name    = '.kinbaku.conf.py'
        choice1 = os.path.join( os.environ['HOME'], name)
        choice2 = os.path.join(os.getcwd(), name) #path.join( os.environ['HOME'], '.kinbaku.conf.py')
        for choice in [choice1,choice2]:
            if os.path.exists(choice):
                break
        choice = (os.path.exists(choice) and choice) or choice1
        return choice

    def write(self,contents):
        fhandle = self.open()
        fhandle.write(contents)
        fhandle.close()

    @publish_to_commandline
    def wipe(self):
        """ destroys all of the persistent settings """
        report("Wiping kinbaku configuration in {fp}",fp=self.fpath)
        self.set({})

    def save(self, dictionary):
        pass

    def open(self, mode='w'):
        """ """
        assert self.fpath
        if not os.path.exists(self.fpath):
            report("Writing empty config file to {fp}",fp=self.fpath)
            try:
                fhandle = open(self.fpath, mode)
            except IOError:
                # file doesnt exist?
                fhandle = open(self.fpath,'w')
                fhandle.close()
                return self.open(mode)
            fhandle.write(json.dumps({}))
            fhandle.close()
            return self.open()

        return open(self.fpath, mode)

    def read(self):
        fhandle=self.open('r')
        out = fhandle.read() or '{}'
        fhandle.close()
        return out

    def readlines(self):
        return self.read().split('\n')

    def __init__(self, fpath=None):
        self.fpath=fpath or self.default_fpath


plugin=Config
class ConfigContext(object):
    """ azucar syntactico: contextmanager protocol """
    def __exit__(self, type, value, tb):
        console.draw_line(msg=" __exit__ ")
        if not any([type, value, tb]):
            report("  closing project:", self.project.close())
            report("  removing shadow", remove_recursively(self.pth_shadow))
        else:
            report("exit with error", type, value, tb)

    def __enter__(self):
        """ """
        console.draw_line(msg="__enter__")
        report("  running _open")
        return self
