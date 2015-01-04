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
        self.active()

    def desactive(self):
        self.pre = self.dummy
        self.post = self.dummy

    def __setHeader(self):
        t = Terminal()
        h = t.bold(t.yellow("Initializing: ")) + t.normal() + self.name + "\n"
        h += t.bold(t.yellow("Authored: ")) + t.normal() + self.author + "\n"
        h += t.bold(t.yellow("Version: ")) + t.normal() + self.version + "\n"
        h += t.bold(t.yellow("Info: ")) + t.normal() + self.info
        print h

    def active(self):
        self.__setHeader()

    def preCmds(self, **kwargs):
        print "preCmds", kwargs, "\n"
        pass

    def pre(self, **kwargs):
        try:
            self.preCmds(**kwargs)
        except:
            raise PluginError("Fail %s 'preCmd' Failed\n" % self.name)

    def postCmds(self, **kwargs):
        print "postCmds", kwargs, "\n"
        pass

    def post(self, **kwargs):
        try:
            self.postCmds(**kwargs)
        except:
            raise PluginError("%s 'postCmds' Failed\n" % self.name)

    def dummy(self):
        pass


def loadPlugin(plugin):
    return imp.load_module(plugin[0], *plugin[1])


def getBdPluginsPath():
    bd_plugs = os.getenv("BD_PLUGINS", False)
    if bd_plugs:
        bd_plugs = bd_plugs.split(":")
    return bd_plugs


def getCallbackCmds(callback):
    bd_plugs = getBdPluginsPath()
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
    '''
    '''
    bd_plugs = getBdPluginsPath()   # Get badass plugins paths
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


def runCmds(runCmd=False, **kwargs):
    # TODO: Documentation for runCmds()
    callback = kwargs["callback"]
    callbackCmds = getCallbackCmds(callback)
    t = Terminal()
    msg = "\n[Begin %sCmd] " % runCmd
    header = t.bold(t.yellow(msg))+t.bold(t.white(callback))

    if not callbackCmds:
        header += t.bold(t.red("\nCan't get callbackCmds"))
        print header
        return False

    modules = getPlugins(callbackCmds)
    if not modules:
        header += t.bold(t.red("\nCan't get Plugins for this callback"))
        print header
        return False

    cmdLaunched = list()

    print header

    for cmd in callbackCmds:
        if cmd not in cmdLaunched:
            module = loadPlugin((cmd, modules[cmd]))
            module = module.create()

            if runCmd == "pre":
                module.pre(**kwargs)
            elif runCmd == "post":
                module.post(**kwargs)

            cmdLaunched.append(cmd)

    print t.bold(t.yellow("[Finish %sCmd]\n" % runCmd))


def runPreCmds(**kwargs):
    # TODO: Documentation for runCmdsPre()
    runCmds(runCmd="pre", **kwargs)


def runPostCmds(**kwargs):
    # TODO: Documentation for runCmdsPost()
    runCmds(runCmd="post", **kwargs)
