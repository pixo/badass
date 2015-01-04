'''
Created on Jan 3, 2015

@author: pixo
'''
import imp
import os
import glob
from blessings import Terminal


class PluginError(Exception):
    """
    Error raised by the Plugin pack.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PluginCmd():
    author = False
    version = False
    name = False
    hook = False

    def __init__(self, **kwargs):
        if not all([self.author, self.version, self.name, self.hook]):
            raise PluginError("'%s' Wrong initialization" % self.name)

        if kwargs["hooked"] != self.hook:
            self.desactive()
        else:
            self.active()

    def desactive(self):
        self.pre = self.dummy
        self.post = self.dummy

    def __setHeader(self):
        t = Terminal()
        h = t.bold(t.yellow("Initializing: ")) + t.normal() + self.name + "\n"
        h += t.bold(t.yellow("Authored: ")) + t.normal() + self.author + "\n"
        h += t.bold(t.yellow("Version: ")) + t.normal() + self.version + "\n"
        h += t.bold(t.yellow("Hooked: ")) + t.normal() + self.hook + "\n"
        print h

    def active(self):
        self.__setHeader()

    def preCmds(self, **kwargs):
        print "preCmds", kwargs
        pass

    def pre(self, **kwargs):
        try:
            self.preCmds(**kwargs)
        except:
            raise PluginError("Fail %s 'preCmd' Failed" % self.name)

    def postCmds(self, **kwargs):
        print "postCmds", kwargs
        pass

    def post(self, **kwargs):
        try:
            self.postCmds(**kwargs)
        except:
            raise PluginError("%s 'postCmds' Failed" % self.name)

    def dummy(self):
        pass


def getPlugins():
    bd_plugs = os.getenv("BD_PLUGINS_PATH")
    if not bd_plugs:
        return list()

    bd_plugs = bd_plugs.split(":")
    pys = list()

    for path in bd_plugs:
        pys += glob.glob(path+"/*.py")

    modules = list()
    for py in pys:
        dirname = os.path.dirname(py)
        pack, ext = os.path.splitext(py)
        mname = pack.split(os.sep)[-1]
        module = imp.find_module(mname, [dirname])
        modules.append([mname, module])
    return modules


def loadPlugin(plugin):
    return imp.load_module(plugin[0], *plugin[1])


def runPreCmds(hooked, plugins):
    for plugin in plugins:
        module = loadPlugin(plugin)
        module = module.initialize(hooked=hooked)
        module.pre()


def runPostCmds(hooked, plugins):
    for plugin in plugins:
        module = loadPlugin(plugin)
        module = module.initialize(hooked=hooked)
        module.pre()
