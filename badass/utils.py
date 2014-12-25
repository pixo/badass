'''
Created on Nov 12, 2013

@author: pixo
'''
import os
import hashlib
import time


def getTextureTypes():
    # TODO: Documentation
    return {  # TODO: Create a dict instead of a list for the type parameters
        "bump": ("R", "8-bit 16-bit", "rgb(127,127,127)",
                 True, "bspline", "1"),
        "bumpbk": ("R", "8-bit 16-bit", "rgb(127,127,127)",
                   True, "bspline", "1"),
        "cavt": ("R", "8-bit 16-bit", "rgb(127,127,127)",
                 True, "bspline", "1"),
        "cavtbk": ("R", "8-bit 16-bit", "rgb(127,127,127)",
                   True, "bspline", "1"),
        "disp": ("R", "8-bit 16-bit 32-bit",
                 False, True, "bspline", "1"),
        "diff1": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                  True, "triangle", "sRGB"),
        "diff1bk": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                    True, "triangle", "sRGB"),
        "diff1col": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                     True, "triangle", "sRGB"),
        "diff1colbk": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                       True, "triangle", "sRGB"),
        "diff1rgh": ("R", "8-bit", "rgb(255,255,255)",
                     True, "triangle", "1"),
        "diff1rghbk": ("R", "8-bit", "rgb(255,255,255)",
                       True, "triangle", "1"),
        "diff2": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                  True, "triangle", "sRGB"),
        "diff2bk": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                    True, "triangle", "sRGB"),
        "diff2col": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                     True, "triangle", "sRGB"),
        "diff2colbk": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                       True, "triangle", "sRGB"),
        "diff2rgh": ("R", "8-bit", "rgb(255,255,255)",
                     True, "triangle", "1"),
        "diff2rghbk": ("R", "8-bit", "rgb(255,255,255)",
                       True, "triangle", "1"),
        "veltcol": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                    True, "triangle", "sRGB"),
        "velt": ("R", "8-bit", "rgb(255,255,255)",
                 True, "triangle", "1"),
        "veltbcol": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                     True, "triangle", "sRGB"),
        "veltb": ("R", "8-bit", "rgb(255,255,255)",
                  True, "triangle", "1"),
        "veltedg": ("R", "8-bit", "rgb(255,255,255)",
                    True, "triangle", "1"),
        "veltbrgh": ("R", "8-bit", "rgb(255,255,255)",
                     True, "triangle", "1"),
        "dirt": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                 True, "triangle", "1"),
        "dirtcol": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                    True, "triangle", "sRGB"),
        "emis": ("R", "8-bit 16-bit", "rgb(0,0,0)",
                 True, "triangle", "1"),
        "emiscol": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                    True, "triangle", "sRGB"),
        "emisbk": ("R", "8-bit 16-bit", "rgb(0,0,0)",
                   True, "triangle", "1"),
        "emiscolbk": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                      True, "triangle", "sRGB"),
        "glascol": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                    True, "triangle", "sRGB"),
        "glasrgh": ("R", "8-bit", "rgb(255,255,255)",
                    True, "triangle", "1"),
        "glasabscol": ("RGB", "8-bit 16-bit", "rgb(255,255,255)",
                       True, "triangle", "sRGB"),
        "glasabsscl": ("R", "8-bit", "rgb(255,255,255)",
                       True, "triangle", "1"),
        "mask": ("R", "8-bit", "rgb(0,0,0)", "Triangle", "1"),
        "maskbk": ("R", "8-bit", "rgb(0,0,0)",
                   True, "triangle", "1"),
        "mtal": ("R", "8-bit 16-bit", "rgb(0,0,0)", True,
                 "triangle", "1"),
        "mtalcol": ("RGB", "8-bit 16-bit", "rgb(0,0,0)",
                    True, "triangle", "sRGB"),
        "mtalrgh": ("R", "8-bit 16-bit", "rgb(0,0,0)",
                    True, "triangle", "1"),
        "mtalirid": ("R", "8-bit 16-bit", "rgb(0,0,0)",
                     True, "triangle", "1"),
        "norm": ("RGB", "8-bit", "rgb(127,127,255)",
                 True, "triangle", "1"),
        "normbk": ("RGB", "8-bit", "rgb(127,127,255)",
                   True, "triangle", "1"),
        "spec1": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                  True, "triangle", "1"),
        "spec1bk": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                    True, "triangle", "1"),
        "spec1col": ("RGB", "8-bit", "rgb(127,127,255)",
                     True, "triangle", "1"),
        "spec1rgh": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                     True, "triangle", "1"),
        "spec1rghbk": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                       True, "triangle", "1"),
        "spec2": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                  True, "triangle", "1"),
        "spec2bk": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                    True, "triangle", "1"),
        "spec2col": ("RGB", "8-bit", "rgb(127,127,255)",
                     True, "triangle", "1"),
        "spec2rgh": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                     True, "triangle", "1"),
        "spec2rghbk": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                       True, "triangle", "1"),
        "spec1irid": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                      True, "triangle", "1"),
        "spec2irid": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                      True, "triangle", "1"),
        "spec2thick": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                       True, "triangle", "1"),
        "spec2bmp": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                     True, "triangle", "1"),
        "sss": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                True, "triangle", "1"),
        "ssswidth": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                     True, "triangle", "1"),
        "sssbsct": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                    True, "triangle", "1"),
        "trans": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                  True, "triangle", "1"),
        "transcol": ("RGB", "8-bit 16-bit", "rgb(127,127,255)",
                     True, "triangle", "1"),
        "dens": ("R", "8-bit 16-bit", "rgb(255,255,255)",
                 True, "triangle", "1")}


def getAssetTypes():
    # TODO: Documentation getAssetTypes()
    return {'camera': 'cam',
            'character': 'chr',
            'prop': 'prp',
            'vehicle': 'vcl',
            'interior': 'int',
            'exterior': 'ext',
            'material': 'mtl',
            'sequence': 'seq',
            'scene': 'scn',
            'shot': 'sht',
            'visual-effect': 'vfx'}


def getAssetTasks():
    # TODO: Documentation getAssetTasks()
    return {'animation': 'ani',
            'compositing': 'cmp',
            'render': 'ren',  # TODO: automate creation of main(CG)/COMP forks
            'matte-painting': 'dmp',
            'dynamic': 'dyn',
            'fluid': 'fld',
            'ibl': 'ibl',
            'layout': 'lay',
            'lighting': 'lit',
            # TODO: automate creation of main/sculpt/retopo forks
            'modeling': 'mod',
            'override': 'ovr',
            'particle': 'pcl',
            # TODO: automate creation of main(render)/projection forks
            'camera': 'cam',
            'previz': "viz",
            'rig': 'rig',
            'rotoscopy': 'rot',
            'shader': 'shd',
            'surfacing': 'sur',
            # TODO: automate creation of main(surfacing)/grooming forks
            'texturing': 'tex',
            'grooming': 'grm',
            'sound': 'snd',
            'concept': 'cpt',
            'model-sheet': 'mst'}


def getDefaultTasks():
    # TODO: Documentation getDefaultTasks()
    return {"chr": {'animation': 'ani',
                    'bash-comp': 'bcp',
                    'render-comp': 'rcp',
                    'render-cg': 'rcg',
                    'matte-painting': 'dmp',
                    'dynamic': 'dyn',
                    'fluid': 'fld',
                    'ibl': 'ibl',
                    'layout': 'lay',
                    'lighting': 'lit',
                    'modeling': 'mod',
                    'override': 'ovr',
                    'particle': 'pcl',
                    'camera-projection': 'cpj',
                    'camera-render': 'crn',
                    'previz': "viz",
                    'rig': 'rig',
                    'retopo': 'rtp',
                    'rotoscopy': 'rot',
                    'sculpt': 'sct',
                    'shader': 'shd',
                    'surfacing': 'sur',
                    'texture': 'tex',
                    'texture-grooming': 'tgr',
                    'sound': 'snd',
                    'concept': 'cpt',
                    'model-sheet': 'mst'}}


# System ######################################################################


def hashTime():
    """
    This function return a hash based on sha1 current time.
    Useful to get a random value.

    :returns:  str -- Return the current time 'sha1' hash.

    >>> random_value = hashTime ()
    >>> 'a8f2aa40f66a763dde036f83e854d1762436e97d'
    """
    # Get the hash from current time
    sha1 = hashlib.sha1(str(time.time()))

    return str(sha1.hexdigest())


def hashFile(path=""):
    # TODO: Documentation hashFile()
    """
    This function compare the two files contains, based on sha1.
    It is very useful if you need to know if the two file are the same.

    :param path: The file path
    :type path: str
    :returns:  str -- sha1 hash file
    :raises: RepositoryError if the path doesn't exists.

    **Example:**

    >>> hashFile ( path = "/home/user/filea" )
    >>> 'a8f2aa40f66a763dde036f83e854d1762436e97d'
    """
    # Check if the file exists
    if os.path.exists(path):
        raise Exception("Can't compare '%s', file doesn't exists." % path)

    # Get the sha1lib
    sha1 = hashlib.sha1()

    # Get the file for read
    f = open(path, 'rb')

    # Try to get the hash
    try:
        sha1.update(f.read())
    finally:
        f.close()

    # return the hash
    return sha1.hexdigest()


def getVersionType():
    # TODO: Documentation for getVersionType()
    return ["review", "release"]


def compareFile(file_a="", file_b=""):
    # TODO: Documentation for compareFile()
    # TODO: use default python function filecmp.cmp
    """
    This function compare two files contains based on sha1.
    It is very useful if you need to know if two files are the same.

    :param file_a: The first file path
    :type file_a: str
    :param file_b: The second file path
    :type file_b: str
    :returns:  bool -- True if file are the same.
    :raises: RepositoryError if one of the file doesn't exists.

    **Example:**

    >>> compareFile(file_a="/home/user/filea", file_b="/home/user/fileb")
    >>> True
    """

    # Check if the file_a exists
    if os.path.exists(file_a):
        raise Exception("Can't compare '%s', file doesn't exists." % file_a)

    # Check if the file_b exists
    if not os.path.exists(file_b):
        raise Exception("Can't compare '%s', file doesn't exists." % file_b)

    # Compare the sha1 hash of the files
    if hashFile(file_a) == hashFile(file_b):
        # if the file are the same return True
        return True
    else:
        # if they are not the same return False
        return False


def createFile(path="", content="", overwrite=False):
    # TODO: documentation createFile()
    if os.path.exists(path) and (not overwrite):
        print "createFile (): %s already exists." % path
        return False

    dirnam = os.path.dirname(path)

    if not os.path.exists(dirnam):
        os.makedirs(dirnam, 0o775)

    else:
        os.chmod(dirnam, 0o775)

    path = open(path, 'w')
    path.write(content)
    path.close()

    return True


def getBadassVersion():
    """
    This function return the version of the Badass SDK.
    :returns:  str -- The assetmanager used version

    **Example:**

    >>> getBadassVersion ()
    >>> '0.1.0'

    """
    return os.getenv("BD_ASSVER", False)


def getUser():
    # TODO: getUser()
    stat = os.getenv("USER", False)
    if not stat:
        print("getUser(): can't get USER")
    return stat


def getLocalRoot():
    # TODO: Documentation getLocalRoot()
    stat = os.getenv("BD_ROOT", False)
    if not stat:
        print("getLocalRoot(): can't get BD_ROOT")
    return stat


def getHostRoot():
    # TODO: Documentation getHostRoot()
    stat = os.getenv("BD_HOSTROOT", False)
    if not stat:
        print("getHostRoot(): can't get BD_HOSTROOT")
    return stat


def getRepo():
    # TODO: Documentation getRepo()
    stat = os.getenv("BD_REPO", False)
    if not stat:
        print("getRepo(): can't get BD_REPO")
    return stat


def getUserRepo():
    # TODO: Documentation getUserRepo()
    stat = os.getenv("BD_USER_REPO", False)
    if not stat:
        print("getUserRepo(): can't get BD_USER_REPO")
    return stat


def getDbName():
    # TODO: Documentation getDbName()
    stat = os.getenv("BD_DBNAME", False)
    if not stat:
        print("getDbName(): can't get BD_DBNAME")
    return stat


def getDbAdress():
    # TODO: Documentation getDbAdress()
    stat = os.getenv("BD_DBADRESS", False)
    if not stat:
        print("getDbAdress(): can't get BD_DBADRESS")
    return stat


def getProjectName():
    # TODO: Documentation getProjectName()
    stat = os.getenv("BD_PROJECT", False)
    if not stat:
        print("getProjectName(): can't get BD_PROJECT")
    return stat


def getProjectEnv(project=""):
    # TODO: Documentation getProjectEnv()
    # Return a path for the project env file
    if project == "":
        project = getProjectName()

    repo = getRepo()
    if repo:
        envfile = os.path.join(repo, project, "config", project + ".env")
        return envfile
    else:
        print "getProjectEnv():can't get network repository"
        return False


def isEnvSet():
    # TODO: Documentation isEnvSet()
    stat = [getUser(),
            getLocalRoot(),
            getHostRoot(),
            getRepo(),
            getUserRepo(),
            getDbName(),
            getDbAdress(),
            getProjectName()]
    return all(stat)
