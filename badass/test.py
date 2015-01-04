import shutil
import badass.core as core
import badass.utils as utils
import time


def measureTime(a):
    start = time.clock()
    l = a()
    elapsed = time.clock()
    elapsed = elapsed - start
    print "Time spent in (function name) is: ", elapsed
    return l


def getAllAssetVersions():
    """
    This is a simple example to get all asset versions.
    """
    db = core.getDb()
    versions = core.getVersions(db=db, doc_id="bls_chr_belanus_mod_main")
    print versions
    return versions


def getAnAssetVersion():
    """
    This is a simple example to get a particular asset version path.
    """
    db = core.getDb()
    version = core.getVersionPath(
        db=db,
        doc_id="cpt_chr_jdoe_mod_a",
        version="last")
    print version
    return version


def pullAnAssetVersion():
    """
    This is a simple example to pull to workspace a particular asset version.
    """
    db = core.getDb()
    version = 2
    result = core.pull(
        db=db,
        doc_id="bls_chr_belanus_mod_main",
        version=version)
    print result


def getFileTexType():
    """
    This is a simple example to pull to workspace a particular asset version.
    """
    path = "bls_chr_belanus_tex_spec1.1001.tif"
    result = core.getTextureAttr(path)
    print result


def lsAllType():
    db = core.getDb()
    typ = "asset"
    startkey = "loc"
    asset_ls = core.lsDb(db, typ, startkey)
    return asset_ls


def createAssetWS(doc_id):
    core.createWorkspace(doc_id)


def createAssetOnDB(doc_id):
    description = "Test"
    stat = core.createAsset(
        db=None,
        doc_id=doc_id,
        description=description,
        debug=True)
    return stat


def createTaskOnDB(doc_id):
    db = core.getDb()
    description = "Test"
    stat = core.createTask(
        db=db,
        doc_id=doc_id,
        description=description,
        debug=True)
    return stat


def createMassiveAssets():
    prj = utils.getProjectName()
    types = utils.getAssetTypes()
    tasks = utils.getAssetTasks()

    for i in range(0, 454):
        for t in types:
            docId = "%s_%s_donald%s%d" % (prj, types[t], types[t], i)
            createAssetOnDB(docId)
            print docId

            for k in tasks:
                docId = "%s_%s_donald%s%d_%s_a" % (
                    prj, types[t], types[t], i, tasks[k])
                createTaskOnDB(docId)


def changeAttr(db=None, docId="", attr=None, value=None):
    if docId == "" or attr or value:
        print ("setAssetAttr(): please provide proper attributes.")
        return

    if not db:
        db = core.getDb()

    doc = db[docId]
    doc[attr] = value
    _id, _rev = db.save(doc)


def copydir():
    try:
        shutil.copytree(
            "/homeworks/users/pixo/projects/test/cam/donaldcam/ani/a",
            "/homeworks/users/pixo/projects/test/cam/donaldcam/ani/b")
    except:
        print "fail to copy"


if __name__ == '__main__':
    print 'initialize'
