'''
Created on Jan 3, 2015

@author: pixo
'''
import imp
import os
import glob
import yaml
from blessings import Terminal


class PluginError(Exception):
    """
    Error raised by the Plugin pack.
    """


class BadassCmd():
    author = False
    version = False
    name = False
    info = False

    def __init__(self, **kwargs):
        if not all([self.author, self.version, self.name, self.info]):
            raise PluginError("'%s' Wrong initialization" % self.name)
        self.initCmd(**kwargs)

    def __setHeader(self):
        t = Terminal()
        h = t.bold(t.yellow("\nInitializing: ")) + t.normal(self.name + "\n")
        h += t.bold(t.yellow("Author: ")) + t.normal(self.author + "\n")
        h += t.bold(t.yellow("Version: ")) + t.normal(self.version + "\n")
        h += t.bold(t.yellow("Info: ")) + t.normal(self.info)
        print h

    def initCmd(self, **kwargs):
        self.__setHeader()
        return self.init(**kwargs)

    def init(self, **kwargs):
        print "initCmd", kwargs, "\n"
        return True

    def preCmd(self, **kwargs):
        self.__setHeader()
        return self.pre(**kwargs)

    def pre(self, **kwargs):
        print "pre", kwargs, "\n"
        return True

    def postCmd(self, **kwargs):
        self.__setHeader()
        return self.post(**kwargs)

    def post(self, **kwargs):
        print "post", kwargs, "\n"
        return True


def loadPlugin(plugin):
    return imp.load_module(plugin[0], *plugin[1])


def getPluginsPath():
    bd_plugs = os.getenv("BD_PLUGINS", False)
    if bd_plugs:
        bd_plugs = bd_plugs.split(":")
    return bd_plugs


def getCallbackCmds(callback):
    bd_plugs = getPluginsPath()
    doc = False

    if bd_plugs:
        cbyamls = list()
        for path in bd_plugs:
            cbyamls += glob.glob(path+"/callbacks.yaml")

        callbackDep = cbyamls[-1]
        if os.path.exists(callbackDep):
            with open(callbackDep, 'r') as f:
                doc = yaml.load(f)
    if doc:
        if callback in doc:
            doc = doc[callback]

    return doc


def getPlugins(callbackCmds):
    # TODO: Documentation for getPlugins()
    """ """

    bd_plugs = getPluginsPath()   # Get badass plugins paths
    if not bd_plugs:                # Check badass plugins path is not empty
        return False
    pys = list()                    # Initialize packages list
    for path in bd_plugs:           # Get all packages in BD plugins path
        pys += glob.glob(path+"/*.py")

    modules = dict()                # Initialize modules dict
    for py in pys:                  # Get modules corresponding to packages
        dirname = os.path.dirname(py)
        pack = os.path.splitext(py)[0]
        mname = pack.split(os.sep)[-1]

        if mname in callbackCmds:   # Check package name is in callback list
            module = imp.find_module(mname, [dirname])
            modules[mname] = module

    return False if modules == {} else modules


def runCmds(**kwargs):
    # TODO: Documentation for runCmds()
    runCmd = kwargs['cmd']
    callback = kwargs["callback"]
    callbackCmds = getCallbackCmds(callback)
    t = Terminal()

    msg = "\n[Begin %sCmd] " % runCmd
    header = t.bold(t.yellow(msg))+t.bold(t.white(callback))
    if not callbackCmds:
        header += t.bold(t.red("\nCan't get callbackCmds"))
        print header
        return False

    if 'stat' not in kwargs:
        kwargs['stat'] = True

    modules = getPlugins(callbackCmds)
    if not modules:
        header += t.bold(t.red("\nCan't get Plugins for this callback"))
        print header
        return False
    print header

    lastCmdStat = True
    cmdLaunched = list()
    for cmd in callbackCmds:
        if not lastCmdStat:
            break
        elif cmd not in cmdLaunched:
            module = loadPlugin((cmd, modules[cmd]))
            module = module.create(**kwargs)
            if runCmd == "pre":
                lastCmdStat = module.preCmd(**kwargs)
            elif runCmd == "post":
                lastCmdStat = module.postCmd(**kwargs)
            cmdLaunched.append(cmd)

    print t.bold(t.yellow("[Finish %sCmd]\n" % runCmd))
    return lastCmdStat


def runPreCmds(**kwargs):
    # TODO: Documentation for runCmdsPre()
    kwargs["cmd"] = "pre"
    runCmds(**kwargs)


def runPostCmds(**kwargs):
    # TODO: Documentation for runCmdsPost()
    kwargs["cmd"] = "post"
    runCmds(**kwargs)
