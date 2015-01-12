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
        stat = self.initialize(**kwargs)
        if stat:
            self.__setHeader()

    def __setHeader(self):
        t = Terminal()
        h = "\n"
        h += t.bold_yellow("Initializing: ") + t.bold_white(self.name + "\n")
        h += t.bold_yellow("Author: ") + t.bold_white(self.author + "\n")
        h += t.bold_yellow("Version: ") + t.bold_white(self.version + "\n")
        h += t.bold_yellow("Info: ") + t.bold_white(self.info)
        print h

    def dummy(self, **kwargs):
        return True

    def initialize(self, **kwargs):
        return kwargs

    def execute(self, **kwargs):
        return kwargs


def loadPlugin(plugin):
    return imp.load_module(plugin[0], *plugin[1])


def getPluginsPath():
    bd_plugs = os.getenv("BD_PLUGINS", False)
    bd_plugs = os.getenv("BD_PLUGINS_DEBUG", bd_plugs)
#     bd_plugs = "/badass/users/pixo/packages/int/badplugs/plugins"

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


def executeCmds(stat, **kwargs):
    # TODO: Documentation for executeCmds()
    t = Terminal()
    exeCmd = kwargs['cmd']
    kwargs.update(stat)
    callback = kwargs["callback"]
    msg = "\n[Begin %s] " % exeCmd  # exeCmd
    header = t.bold(t.yellow(msg))+t.bold(t.white(callback))

    callback = kwargs["callback"]
    callbackCmds = getCallbackCmds(callback)
    modules = getPlugins(callbackCmds)

    if not callbackCmds:
        header += t.bold(t.red("\nCan't get callbackCmds"))
        print header
        return False

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
            lastCmdStat = module.execute(**kwargs)
            cmdLaunched.append(cmd)

    print t.bold(t.yellow("[Finish %s]\n" % exeCmd))
    return lastCmdStat
