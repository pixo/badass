import os
import time
import glob
import shutil
import re
import commands
import couchdb
import utils
import plugin


# DATABASE ####################################################################
class DatabaseError(Exception):

    """
    Error raised by the project module.

    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def getDesign():
    return "AssetManager"


def getServer(serveradress=""):

    if serveradress == "":
        serveradress = utils.getDbAdress()

    if serveradress.find("http://") == -1:
        serveradress = "http://%s" % serveradress

    db_server = couchdb.Server(serveradress)

    return db_server


def serverExists(serveradress=""):

    if serveradress.find("http://") < 0:
        serveradress = "http://%s" % serveradress

    server = couchdb.Server(serveradress)

    try:
        stats = server.stats()
        return stats

    except:
        return False


def getDb(dbname="", serveradress=""):
    # TODO: Documentation for getDb()
    if dbname == "" or not dbname:
        dbname = utils.getProjectName()

        if dbname == "" or not dbname:
            print "getDb(): wrong dbname '%s'" % str(serveradress)
            return False

    if serveradress == "":
        serveradress = utils.getDbAdress()

    server = getServer(serveradress)

    if dbname in server:
        return server[dbname]
    else:
        return False


def lsDb(db=None, view="", startkey="", endkey=""):

    if db is None:
        db = getDb()

    if endkey == "":
        endkey = startkey + "\u0fff"

    design = getDesign()
    viewname = "_design/%s/_view/%s" % (design, view)
    view = db.view(viewname, startkey=startkey, endkey=endkey)

    doc = dict()
    for row in view.rows:
        doc[row["key"]] = row["value"]
    return doc


def getDefaultViews():
    # TODO: add documentation to the function
    asset = utils.getAssetTypes()
    task = utils.getAssetTasks()

    views = dict()
    # creating project view
    func = 'function(doc) {\n  if(doc.type == "project") '
    func += '{\n    emit(doc.name, doc);\n}\n}'
    views['project'] = {'map': func}
    # creating asset view
    func = "function(doc) {\n  if(doc.type != \"project\" && !doc.task  ) "
    func += "{\n    emit(doc._id, doc);\n}\n}"
    views['asset'] = {'map': func}
    # creating task view
    func = "function(doc) {\n  if(doc.task) {\n    emit(doc._id, doc);\n}\n}"
    views['task'] = {'map': func}

    # creating views per asset type
    for key in asset:
        func = 'function(doc) {\n  if(doc.type == "%s") ' % asset[key]
        func += '{\n    emit(doc._id, doc);\n}\n}'
        views[asset[key]] = {'map': func}

    # creating views per task type
    for key in task:
        func = 'function(doc) {\n  if(doc.task == "%s") ' % task[key]
        func += '{\n    emit(doc._id, doc);\n}\n}'
        views[task[key]] = {'map': func}

    doc = {
        "_id": "_design/AssetManager",
        "language": "javascript",
        "views": views
    }

    return doc


def createDb(name=None, serveradress=None):
    """
    This function create a **DataBase** into the provided server.

    :param name: The database name.
    :type name: str
    :param serveradress: The asset code.
    :type serveradress: str

    :returns: Database -- return the database
    :raises: DatabaseError if database already exist

    **Example:**

    >>> createDb ( name = "prod", serveradress = "admin:pass@192.168.0.100" )
    """

    if not (serveradress) or (serveradress == ""):
        raise DatabaseError("CreateDb (): serveradress doesn't exists" % name)

    # Get Db Server
    server = couchdb.client.Server(serveradress)

    # Check if db name already exist
    if name in server:
        raise DatabaseError("CreateDb (): Database '%s' already exist" % name)

    # Create DataBate
    db = server.create(name)

    return db


# ASSET #######################################################################
class AssetError(Exception):

    """
    Error raised by the Asset module.

    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def createAsset(
        db=None, doc_id="", comment="", overdoc=dict(), debug=False):
    """
    This function create an **asset** into the provided database.

    :param db: The database.
    :type db: couchdb.client.Database
    :param doc_id: The asset code.
    :type doc_id: str
    :param comment: The asset comment.
    :type comment: str
    :param overdoc: A dictionnary that contains extra document attributes.
    :type overdoc: dict
    :returns:  document -- The database document.
    :raises: AttributeError, KeyError

    **Example:**

    >>> db = getDb(dbname="prod" , serveradress="127.0.0.1:5984")
    >>> createAsset(db=db, doc_id="prod_ch_mickey", "This is the mickey ")
    """

    # Check if db exist if not, get the current project db
    if db is None:
        db = getDb()

    # Get data from doc_id
    project, typ, slug = doc_id.split("_")
    asset = "%s_%s" % (typ, slug)

    # Check if project name is right
    if not (project in db):
        print "createAsset: %s project doesn't exist" % project
        return False

    # If asset doesn't exist create the asset
    if doc_id in db:
        print "createAsset: %s already exist" % asset
        return False

    # Create the asset structure
    doc = {
        "_id": doc_id,
        "project": project,
        "name": slug,
        "type": typ,
        "masters": {},
        "tags": {},
        "comments": {},
        "inactive": False,
        "parents": {},
        "children": {},
        "comment": comment,
        "creator": utils.getUser(),
        "created": time.time(),
        "status": {"art": "ns", "tec": "ns"},
        "production": {"bid": 0, "delivery": 20140611.5, "spent": 0,
                       "assigned": ""},
        "subscribers": {}
    }

    # Add extra data if needed
    doc.update(overdoc)

    # Save data structure into the database
    _id, _rev = db.save(doc)

    if not debug:
        print "createAsset: Added %r to project %r" % (asset, project)
    return db[_id]


def createTask(
        db=None, doc_id="", comment="", overdoc=dict(), debug=False):
    """
    This function create a **task** into the provided database.

    :param db: The database.
    :type db: couchdb.client.Database
    :param doc_id: The asset code.
    :type doc_id: str
    :param comment: The asset comment.
    :type comment: str
    :param overdoc: A dictionnary that contains extra document attributes.
    :type overdoc: dict
    :returns:  document -- The database document.
    :raises: AttributeError, KeyError

    **Example:**

    >>> db = getDb(dbname="prod", serveradress="127.0.0.1:5984")
    >>> createTask(db=db, doc_id="prod_ch_mickey_mod_a", "modeling task 'a'")
    """

    # If 'db' isn't provided, get the current project database
    if db is None:
        db = getDb()

    # Get data from doc_id
    project, typ, slug, task, fork = doc_id.split("_")
    asset_id = "%s_%s_%s" % (project, typ, slug)
    asset = "%s_%s_%s_%s" % (typ, slug, task, fork)

    # Check if project name is right
    if not (project in db):
        print "createTask: %s project doesn't exist" % project
        return False

    # Check if the asset exist
    if not (asset_id in db):
        print "createTask: Asset '%s' doesn't exist" % asset_id
        return False

    # If task doesn't exist create it
    if doc_id in db:
        print "createTask: %s already exist" % asset
        return False

    # Create the task structure
    doc = {
        "_id": doc_id,
        "project": project,
        "type": typ,
        "name": slug,
        "task": task,
        "fork": fork,
        "review": dict(),
        "release": dict(),
        "masters": {},
        "tags": {},
        "inactive": False,
        "parents": {},
        "children": {},
        "comments": {},
        "comment": comment,
        "creator": utils.getUser(),
        "created": time.time(),
        "status": {"art": "ns", "tec": "ns"},
        "production": {"bid": 0, "delivery": 20140611.5, "spent": 0,
                       "assigned": ""},
        "subscribers": {}
    }

    # Add extra data if needed
    doc.update(overdoc)

    # Save data structure into the database
    _id, _rev = db.save(doc)
    if not debug:
        print "createTask: Added %r to project %r" % (asset, project)
    return db[_id]


def createPack(db=None, doc_id="", comment="No comment"):
    """
    This function create an asset of type **Pack** into the provided database.

    :param db: The database.
    :type db: couchdb.client.Database
    :param doc_id: The asset code.
    :type doc_id: str
    :param comment: The asset comment.
    :type comment: str
    :returns:  document -- The database document.
    :raises: AttributeError, KeyError

    **Example:**

    >>> db = getDb( dbname = "prod" , serveradress = "127.0.0.1:5984" )
    >>> createPack(db=db, doc_id="prod_pck_mickey",comment = "mickey pack")
    """

    # Extra shot attributes
    overdoc = {"pack": {}}

    # Create asset shot with shot extra attributes
    result = createAsset(db, doc_id, comment, overdoc)

    return result


def createShot(db=None, doc_id="", comment="No comment",
               cut_in=1, cut_out=100):
    """
    This function create an asset of type **Shot** into the provided database.

    :param db: The database.
    :type db: couchdb.client.Database
    :param doc_id: The asset code.
    :type doc_id: str
    :param comment: The asset comment.
    :type comment: str
    :param cut_in: The first frame of the shot.
    :type cut_in: float
    :param cut_out: The last frame of the shot.
    :type cut_out: float
    :returns:  document -- The database document.
    :raises: AttributeError, KeyError

    **Example:**

    >>> db = getDb( dbname = "prod" , serveradress = "127.0.0.1:5984" )
    >>> createShot(db=db, doc_id="prod_shot_op001", cut_in=1, cut_out=100,
                comment="This is the shot openning 001" )

    """

    # Extra shot attributes
    overdoc = {"seq": doc_id.split("_")[2].split("-")[0],
               "cut_in": cut_in,
               "cut_out": cut_out}

    # Create asset shot with shot extra attributes
    result = createAsset(db, doc_id, comment, overdoc)

    return result


def setAssetAttr(db=None, docId="", attr=None, value=None):
    if docId == "" or not attr:
        print ("setAssetAttr(): please provide proper attributes.")
        return

    if not db:
        db = getDb()

    doc = db[docId]
    doc[attr] = value
    _id, _rev = db.save(doc)


# PROJECT #####################################################################
class ProjectError (Exception):

    """
    Error raised by the project module.

    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def isProject(db=None):
    """
    This function check if the current Db is contains a homeworks project.

    :param db: The database.
    :type db: couchdb.client.Database
    :returns:  bool -- True if db contains a homeworks project.

    **Example:**

    >>> db = getDb(dbname = "prod" , serveradress = "127.0.0.1:5984")
    >>> isProject( db )
    >>> True
    """

    # Check if Db contains a Document with the same name
    if not db or not (db.name in db):
        return False

    dbproj = db[db.name]

    # Check if the Document have a type attr
    if not ("type" in dbproj):
        return False

    doctype = dbproj["type"]

    # Check if the Document is a project type Document
    if doctype == "project":
        return True
    else:
        return False


def getProject(db=None):
    """
    This function return the project Document from DB.

    :param db: The database.
    :type db: couchdb.client.Database
    :returns:  couchdb.client.Document -- Return the project Document.

    **Example:**

    >>> db = getDb(dbname="prod", serveradress="127.0.0.1:5984")
    >>> getProject(db)
    >>> <Document 'bls'@'5-97ef4c34350f1c4f5141f05048150bdb' ... >
    """

    # Check if the db contains project
    if not (isProject(db)):
        raise ProjectError("getProject(): '%s' doesn't exists" % db.name)

    # Return the Project Document from db
    return db[db.name]


def getProjectUsers(db=None):
    """
    This function return the list of authorised project users.

    :param db: The database.
    :type db: couchdb.client.Database
    :returns:  list -- Return the list of authorised project users.

    **Example:**

    >>> db = getDb ( dbname = "prod" , serveradress = "127.0.0.1:5984" )
    >>> getProjectUsers(db)
    >>> ['jdoe', 'mickey', 'pixo']
    """

    # Check if db exists
    if not db:
        return False

    # Check if the db contains project
    if not (isProject(db)):
        raise ProjectError("getProjectUsers(): '%s' doesn't exists" % db.name)

    dbproject = db[db.name]

    # Check if the project contains Users
    if not ("users" in dbproject):
        raise ProjectError(
            "getProjectUsers(): Project %s doesn't contains Users" %
            db.name)

    # Return the Users list
    return dbproject["users"]


def lsProjectServer(serveradress):
    """
    This function return a list of all DbServer homeworks projects.

    :param serveradress: The database adress.
    :type serveradress: str
    :returns:  list -- Return the list of authorised project users.

    **Example:**

    >>> lsProjectServer ( serveradress = "admin:pass@127.0.0.1:5984" )
    >>> [ 'prod1', 'prod2', 'prod3' ]
    """

    # Get db server from adress
    server = getServer(serveradress)
    projects = list()
    user = utils.getUser()

    # Iterate over all databases contained in the DB server
    for db_name in server:
        if db_name not in ("_replicator", "_users"):
            db = server[db_name]

            # Check if the current db is a BD project
            if isProject(db):

                # Get project authorized users
                users = getProjectUsers(db)

                # If current user is in the user list append project in the
                # project list
                if user in users:
                    projects.append(db_name)

    # Return a list of projects name (str)
    return projects


def createProject(name="", comment="Default", db_server="", sync_root="",
                  overdoc=dict(), site_root="/badass"):
    """
    This function create a project.

    :param name: The project name
    :type name: str
    :param comment: The project comment
    :type comment: str
    :param db_server: The data base adress
    :type db_server: str
    :param sync_root: The host data server root adress
    :type sync_root: str
    :param site_root: The site root folder
    :type site_root: str
    :param overdoc: A dictionnary that contains extra document attributes.
    :type overdoc: dict
    :returns:  couchdb.client.Database -- return the db.
    :raises: AttributeError, KeyError

    **Example:**

    >>> createProject(name="prod", comment="this is the project prod",
                    db_server="admin:pass@127.0.0.1:5984",
                    sync_root="admin@127.0.0.1:/homeworks" )
    """
    # Check if DB server exists
    adress = "http://%s/" % db_server
    exists = serverExists(adress)

    if site_root[0] is not "/":
        site_root = "/" + site_root

    if not exists:
        print "createProject(): Wrong DB server adress,user or/and password"
        return False

    # Check args
    if name == "":
        print "CreateProject(): Please provide a project name"
        return False

    if db_server == "" or db_server is None:
        print "CreateProject(): No server adress provided"
        return False

    # Check if DB and project already exist
    db = getDb(name, adress)

    # If DB and project exists return
    if db:
        print "CreateProject(): Project already exists."
        return False

    # Adding db project documents
    assets = utils.getAssetTypes()
    tasks = utils.getAssetTasks()

    # Users
    users = dict()
    user = utils.getUser()
    users[user] = "admin"

    doc = {
        "_id": "%s" % name,
        "type": "project",
        "name": name,
        "comment": comment,
        "asset_types": assets,
        "asset_tasks": tasks,
        "creator": user,
        "created": time.time(),
        "root": site_root,
        "users": users,
        "status": {"art": "ns", "tech": "ns"},
        "host": sync_root
    }

    doc.update(overdoc)
    # get views document
    views = getDefaultViews()
    if views and doc:
        # Create DB
        db = createDb(name, adress)
        _id, _rev = db.save(doc)
        _id, _rev = db.save(views)
        print "createProject(): Project '%s' created" % (name)
    else:
        print "createProject(): Can't create Project '%s'" % (name)
    return db


# Repository ##################################################################
class RepositoryError (Exception):

    """
    Error raised by the repository module.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def getIdFromFile(path=""):
    """
    This function return the asset id from a file.
    :param path: The asset file .
    :type path: str
    :returns:  str -- the asset code

    **Example:**

    >>> p="/homeworks/projects/prod/chr/mickey/mod/a/prod_chr_mickey_mod_a.mb"
    >>> getIdFromFile(path=p)
    >>> 'prod_chr_mickey_mod_a'
    """

    # Check if the path exists):
    if not os.path.exists(path):
        raise RepositoryError("getIdFromFile():Can't get 'doc_id' from '%s'." %
                              path)

    basename = os.path.basename(path)
    doc_id = os.path.splitext(basename)[0]
    return doc_id


def getIdFromPath(path=""):
    """
    This function return the asset id from path.

    :param path: The file path
    :type path: str
    :returns:  str -- Return 'doc_id' from the user repository path
    :raises: RepositoryError if the path doesn't exists.

    **Example:**

    >>> getIdFromPath(path="/homeworks/user/jdoe/prod/ch/mimi/mod/a/file.ext")
    >>> 'prod_ch_mimi_mod_a'
    """

    # Check if the path exists
    if not os.path.exists(path):
        raise RepositoryError("getIdFromFile(): path doesn't exists")

    # Expand contained variables
    path = os.path.expandvars(path)

    # Get user repository
    user_repo = utils.getUserRepo() + os.sep

    # Get the doc_id
    path = path.replace(user_repo, "")
    part = path.split(os.sep)
    doc_id = "%s_%s_%s_%s_%s" % (part[0], part[1], part[2], part[3], part[4])

    return doc_id


def getPathFromId(doc_id="", local=False, vtype="review"):
    """
    This function return a path based from a provided 'doc_id'.

    :param doc_id: The asset code.
    :type doc_id: str
    :param local: If true return the user local repository path
    :type local: bool
    :param vtype: Version type *review/release*
    :type vtype: str
    :returns:  str -- The asset or task path.

    **Example:**

    >>> #Repository
    >>> getPathFromId ( doc_id = "prod_chr_mickey_mod_a", local = False )
    >>> '/homeworks/projects/prod/chr/mickey/mod/a'
    >>>
    >>> #Local
    >>> getPathFromId ( doc_id = "prod_chr_mickey_mod_a", local = True )
    >>> '/homeworks/users/jdoe/projects/prod/chr/mickey/mod/a'

    """
    if not (vtype in utils.getVersionType()):
        return False

    # Get the last part of the path
    path = doc_id.replace("_", os.sep)

    # Get the first part of the path
    if local:
        # If true return the local project root
        root = utils.getUserRepo()
    else:
        # If false return the repository project root
        root = utils.getRepo()

    # Check the root path value
    if (not root) or root == "":
        raise RepositoryError("getPathFromId(): incorrect value for root path")

    # Full path
    path = os.path.join(root, path)
    if not local:
        path = os.path.join(path, vtype)

    return path


def getVersions(db=None, doc_id="", vtype="review"):
    """
    This function return all versions in a dictionnary of a particular asset.

    :param db: the database
    :type db: Database
    :param doc_id: The asset code.
    :type doc_id: str
    :param vtype: Version type *trial/stock*
    :type vtype: str
    :returns:  dict -- a dictionary with all versions of the asset,
                the key is a string with the version number without padding.

    **Example:**

    >>> db = core.getDb()
    >>> getVersions ( db = db, doc_id = "bls_chr_belanus_mod_main" )
    >>> {'1': {'files': ['bls_chr_belanus_mod_main.mb'],
                'path': '/homeworks/projects/bls/chr/belanus/mod/main/001',
                'created': '2013 Mar 08 21:16:34',
                'comment': 'names cleaned\nnormal softened',
                'creator': 'pixo'},
        '3': {'files': ['bls_chr_belanus_mod_main.mb'],
                'path': '/homeworks/projects/bls/chr/belanus/mod/main/003',
                'created': '2013 Mar 08 23:13:54',
                'comment': 'test export gproject etc', 'creator': 'pixo'},
        '2': {'files': ['bls_chr_belanus_mod_main.mb'] ... and so ... }
    """

    if not (vtype in utils.getVersionType()):
        return False

    # If db is not provided get the current project DB
    if db is None:
        db = getDb()

    # Get Versions from document
    versions = db[doc_id][vtype]

    return versions


def getVersionPath(doc_id="", version="last", db=None, vtype="review"):
    """
    This function return the asset path of a particular version.

    :param db: the database
    :type db: Database
    :param doc_id: The asset code.
    :type doc_id: str
    :param version: The asset code.
    :type version: str/float/int -- 'last' or 1,2,3,4 etc
    :param vtype: Version type *review/release*
    :type vtype: str
    :returns:  str -- the asset directory

    **Example:**

    >>> db = core.getDb()
    >>> getVersionPath(db=db, doc_id="bls_chr_belanus_mod_main")
    >>> '/homeworks/projects/bls/chr/belanus/mod/main/008'

    """
    if not (vtype in utils.getVersionType()):
        return False

    # Get asset versions
    versions = getVersions(db=db, doc_id=doc_id, vtype=vtype)
    num = None

    # If the queried version is the latest
    if version == "last":
        num = int(len(versions))
    else:
        num = int(version)

    # Get version num attr
    version = versions[str(num)]

    # Get the version path
    path = version["path"]

    return path


def getLocalVersionPath(doc_id="", version=1, vtype="review"):
    """
    This function return the path of an asset version into the user directory.

    :param doc_id: The asset code.
    :type doc_id: str
    :param version: The asset code.
    :type version: str/float/int -- 1,2,3,4 etc
    :param vtype: Version type *trial/stock*
    :type vtype: str
    :returns:  str -- the asset directory path

    **Example:**

    >>> getLocalVersionPath(doc_id="prod_chr_mickey_mod_a", version = 2)
    >>> '../jdoe/projects/prod/chr/mimi/mod/a/prod_chr_mimi_mod_a.v002.base'
    """
    # Make sure vtype exists
    if not (vtype in utils.getVersionType()):
        return False

    # Make sure to get the right type for concatenation
    version = int(version)

    # Get asset local path
    fdir = getPathFromId(doc_id=doc_id, local=True, vtype=vtype)
    name = "%s.from_v%04d.base" % (vtype, version)
    dst = os.path.join(fdir, name)

    # Return a path that doesn't exist
    count = 1
    while os.path.exists(dst):
        dst = os.path.join(fdir, name + str(count))
        count += 1

    return dst


def getTypeFromId(doc_id=None):
    """
    This function return the asset path of a particular version.
    :param doc_id: The asset code.
    :type doc_id: str
    :returns:  str -- the asset type code

    **Example:**

    >>> getTypeFromId ( doc_id = "prod_chr_mickey_mod_a" )
    >>> 'chr'
    """

    if not (doc_id):
        raise RepositoryError(
            "getTypeFromId(): can't get type from wrong 'doc_id'")

    return doc_id.split("_")[1]


def getTaskFromId(doc_id=None):
    """
    This function return the asset path of a particular version.
    :param doc_id: The asset code.
    :type doc_id: str
    :returns:  str -- the asset task code

    **Example:**

    >>> getTaskFromId ( doc_id = "prod_chr_mickey_mod_a" )
    >>> 'mod'
    """

    if not (doc_id):
        raise RepositoryError(
            "getTaskFromId(): can't get type from wrong 'doc_id'")

    return doc_id.split("_")[3]


def createWorkspace(doc_id="", vtype="review"):
    """
    This function create the asset user path of a particular asset.
    :param doc_id: The asset code.
    :type doc_id: str
    :param vtype: Version type *trial/stock*
    :type vtype: str
    :returns:  str/bool -- Return the created workspace path else False.

    **Example:**

    >>> createWorkspace ( doc_id = "prod_chr_mickey_mod_a" )
    >>> '/homeworks/users/jdoe/projects/prod/chr/mickey/mod/a'
    """
    # Make sure vtype exists
    if not (vtype in utils.getVersionType()):
        return False

    # Get the local asset path to create from asset id
    path = getPathFromId(doc_id=doc_id, local=True, vtype=vtype)

    # Check if the path exist
    if os.path.exists(path):
        print ("createWorkspace(): %s already exist" % path)
        return False

    # Create the asset path with the proper permission
    os.makedirs(path, 0o775)

    # Check if the path was created
    if not os.path.exists(path):
        raise RepositoryError(
            "createWorkspace(): cannot create directory %s" %
            path)

    print ("createWorkspace(): %s created" % path)
    return path


def transfer(sources=list(), destination="", doc_id="", rename=True):
    # TODO: documentation for transfer function
    """
    This function create the asset user path of a particular asset.
    :param doc_id: The asset code.
    :type doc_id: str
    :returns:  str/bool -- Return the created path else False.

    **Example:**

    >>> createWorkspace ( doc_id = "prod_chr_mickey_mod_a" )
    >>> '/homeworks/users/jdoe/projects/prod/chr/mickey/mod/a'

    """

    # Check the sources type is a list
    if isinstance(sources, str):
        sources = list([sources])

    files = dict()

    # Iterate over the file to transfer
    for src in sources:

        # Check if the source file exists
        if os.path.exists(src):
            # TODO: Make it simpler
            # Create the destination path
            basename = os.path.basename(src)
            filename = basename.replace(basename.split(".")[0], doc_id)

            # Set filename as key value for source file
            files[src] = os.path.join(destination, filename)

        else:
            print "Warning: %s doesn't exist" % src

    # Set the permission file
    utils.chmod(destination, 755)

    # Iterate over files
    for fil in files:
        dirname = os.path.dirname(files[fil])

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        utils.cp(fil, files[fil])


def pull(db=None, doc_id="", version="last", extension=False,
         progressbar=False, msgbar=False, vtype="review"):
    """
    This function copy the desired file from repository to local workspace.

    :param db: the database
    :type db: Database
    :param doc_id: The asset code
    :type doc_id: str
    :param version: The asset version
    :type version: int/str
    :param extension: The file extension
    :type extension: int/str
    :param progressbar: The pyside progress bar
    :type progressbar: PySide progressbar
    :param msg: The pyside message bar
    :type progressbar: PySide messagebar
    :param vtype: Version type *trial/stock*
    :type vtype: str
    :returns: list -- a list of the pulled file.

    **Example:**

    >>> db = core.getDb()
    >>> pull ( db = db, doc_id = "bls_chr_belanus_mod_main", version = 2 )
    >>> [...chr/foo/mod/a/bls_chr_foo_mod_a.v002.base/bls_chr_foo_mod_a.jpg',
    >>> .../chr/foo/mod/a/bls_chr_foo_mod_a.v002.base/bls_chr_foo_mod_a.mb']
    """
    # Make sure vtype exists
    if not (vtype in utils.getVersionType()):
        return False

    def echoMsg(msg="", msgbar=None):
        print msg
        if msgbar:
            msgbar(msg)

    # If db is not provided get the current project DB
    if db is None:
        db = getDb()

    # Check id is respecting the homeworks naming convention
    docsplit = doc_id.split("_")
    if len(docsplit) < 5:
        echoMsg(msg="pull(): Wrong asset id", msgbar=msgbar)
        return False

    # Get asset repository and local asset path
    src = getVersionPath(doc_id=doc_id, version=version, db=db, vtype=vtype)
    dst = getLocalVersionPath(doc_id=doc_id, version=version, vtype=vtype)

    # Add/Check files to pull
    lsdir = list()
    for root, subFolders, files in os.walk(src):

        for fil in files:
            curfile = os.path.join(root, fil)

            if extension and extension != "":
                if os.path.splitext(curfile)[-1] == extension:
                    lsdir.append(curfile)
            else:
                lsdir.append(curfile)

    # Prepare the progress bar
    if progressbar:
        progress_value = 0
        progress_step = 100.0 / len(lsdir) if len(lsdir) != 0 else 1

    # Check there is something to pull
    if len(lsdir) > 0:
        os.makedirs(dst, 0o775)
        if not os.path.exists(dst):
            raise RepositoryError("Pull(): cannot create %s " % dst)

    # Pull lsdir file
    pulled = list()
    for fil in lsdir:
        fulldst = fil.replace(src, dst)
        shutil.copyfile(fil, fulldst)
        pulled.append(fulldst)

        # Echo message
        msg = "core.Pull(): %s" % fulldst
        echoMsg(msg=msg, msgbar=msgbar)

        if progressbar:
            progress_value += progress_step
            progressbar.setProperty("value", progress_value)

    return pulled


def pushCallback(action):
    plugins = plugin.getPlugins("push")

    def wrapper(**kwargs):
        plugins.pre(**kwargs)
        stat = action(**kwargs)
        plugins.post(stat=stat, **kwargs)

    return wrapper


@pushCallback
def push(doc_id=False, path=False, comment=False, vtype="review"):
    """
    This function copy the desired file from local workspace to repository.

    :param doc_id: The asset code
    :type doc_id: str
    :param path: The list of files to push
    :type path: str/list of str
    :param comment: This is the comment of the push
    :type comment: str
    :param vtype: Version type *review/release*
    :type vtype: str
    :returns: str -- Return the published directory

    **Example:**
    >>> path="/homeworks/users/jdoe/projects/bls/chr/mimi/mod/a/file.mb"
    >>> push(doc_id="bls_chr_mimi_mod_a", path=path, comment="my comments")
    """

    if not all([path, doc_id, comment, vtype]):         # Check arguments
        print("pushfile(): wrong arguments.")
        return

    def getAssetRepo(path, doc_id):
        if os.path.isdir(path):
            return doc_id
        tmp, ext = os.path.splitext(path)               # Get file extension
        name = doc_id+ext
        return name

    db = getDb()                                        # Get DB
    doc = db[doc_id]                                    # Get asset document
    ver_attr = getVersions(db, doc_id, vtype=vtype)     # Get versions document
    ver = len(ver_attr) + 1                             # Get last version num
    ver_num = "%04d" % ver                              # Convert to string

    repo = getPathFromId(doc_id, vtype=vtype)           # Get asset repo
    name = getAssetRepo(path, doc_id)                   # Get name

    tmp_dname = ver_num+'_'+utils.hashTime()            # Get tmpdir name
    source_dir = os.path.join(repo, tmp_dname)          # Get source dir
    source = os.path.join(source_dir, name)             # Get source path
    target_dir = os.path.join(repo, ver_num)            # Get target dir
    target = os.path.join(target_dir, name)             # Get target path

    # Create the version data for "versions" document's attribute
    fileinfo = dict()
    fileinfo["creator"] = utils.getUser()
    fileinfo["created"] = time.time()
    fileinfo["comment"] = comment
    fileinfo["path"] = target
    fileinfo["release"] = list()
    ver_attr[ver] = fileinfo
    doc[vtype] = ver_attr
    db[doc_id] = doc

    utils.cp(path, source)          # Copying local file to temporary
    utils.mv(source, target)        # Move temporary file to destination
    utils.rm(source_dir)            # Remove temporary file
    print target
    return target                   # Return published file/dir full path


def release(db=None, docId=False, version=False):
    ""
    # TODO: Documentation for badass.core.release
    # Check if DB is provided else get the project DB
    if (not db) or db == "":
        db = getDb()

    # Get task document
    doc = db[docId]

    review = doc["review"]
    version = str(int(version))
    reviewVersion = review[version]
    if not ("release" in reviewVersion):
        reviewVersion["release"] = list()

    release = doc["release"]
    last = str(len(release) + 1)
    releaseVersion = dict()
    releaseVersion["comment"] = reviewVersion["comment"]
    releaseVersion["review"] = version
    releaseVersion["path"] = getPathFromId(doc_id=docId, vtype="release")
    releaseVersion["path"] = os.path.join(releaseVersion["path"], "%04d" %
                                          int(last))
    releaseVersion["created"] = time.time()
    releaseVersion["creator"] = utils.getUser()
    release[last] = releaseVersion
    doc["release"] = release

    released = reviewVersion["release"]
    released.append(last)
    reviewVersion["release"] = released
    review[version] = reviewVersion
    doc["review"] = review

    src = reviewVersion["path"]
    dst = releaseVersion["path"]
    utils.cp(src, dst)
    _id, _rev = db.save(doc)

# Texture #####################################################################
# TODO move texture stuff in badtools or in a badplugs (plugins)


class TextureError (Exception):

    """
    Error raised by the texture module.

    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def getTextureAttr(path=None):
    """
    This function return a list containing the type of the texture
    and a list of attributes that should match the textures attribute.
    Used to check the texture naming convention and texture attributes.

    :param path: The list of files to push
    :type path: str
    :returns: str -- Return the directory of the pushed files

    **Example:**
    path = "/homeworks/users/jdoe/projects/bls"
    path += "/chr/belanus/tex/main/bls_chr_belanus_tex_main_spec1.1001.tif"
    >>> getTextureAttr(path=path)
    >>> ('spec1',('R', '8-bit 16-bit','rgb(255,255,255)',True,'triangle','1'))
    """

    # Get authorized texture types list
    textureType = utils.getTextureTypes()

    # Get the texture filename
    fname = os.path.basename(path)

    # Iterate over all the texture types
    for typ in textureType:

        # Define common texture patern
        simpTex = "%s\d*.\d\d\d\d." % typ

        # Define animated texture patern
        animTex = "%s\d*.\d\d\d\d.\d\d\d\d." % typ

        # Combine patterns
        pattern = "%s|%s" % (simpTex, animTex)

        # Check the filename belong to one of the texture type
        if re.findall(pattern, fname) == []:
            return (typ, textureType[typ])

    return (False, False)


def textureBuild(path="", mode="ww", texfilter=None):
    """
    This function build the textures.

    :param path: the path to the texture
    :type path: str
    :param mode: The texture wrap mode
    :type mode: str
    :param texfilter: The texture filter mode
    :type texfilter: str
    :returns: bool -- True if texture builded

    **Example:**
    path = "/homeworks/users/jdoe/projects/bls"
    path += "/chr/belanus/tex/main/bls_chr_belanus_tex_main_spec1.1001.tif"
    >>> textureBuild(path=path)

    **Note:**
        This function use the system 'render' binary from guerilla.
        You can add your custom builder here.
        Make sure to have 'render' in your PATH.
    """

    # TODO: Add Gamma support

    # Check the texture filter
    if (texfilter is None) and (mode != "latlong"):
        # Get default texture filter for this texture
        texattr = getTextureAttr(path)[1]

        if not texattr:
            # It means the texture is not conform to the naming convention
            return False

        texfilter = texattr[4]
        # texgamma = texattr[5]

    # If use for ibl set texture filter to triangle
    if mode == "latlong":
        texfilter = "triangle"

    # Guerilla builder function
    def guerillaBuild(path, mode, texfilter):
        ''
        fil = os.path.splitext(path)[0]
        tex = fil + ".tex"
        # TODO: use subprocess
        cmd = "render --buildtex --in %s --mode %s --filter %s --out %s" % (
            path, mode, texfilter, tex)
        os.system(cmd)
        print "buildtex: building %s" % tex

    # Build guerilla texture file
    guerillaBuild(path, mode, texfilter)

    # Here you can add your custom builder function

    return True


def textureOptimise(path=None):
    """
    This function optimise the provided texture.

    :param path: the path to the texture
    :type path: str

    **Example:**
    path = "/homeworks/users/jdoe/projects/bls"
    path += "/chr/belanus/tex/main/bls_chr_belanus_tex_main_spec1.1001.tif"
    >>> textureOptimise(path=path)

    **Note:**
        This function use system commands that calls 'imagemagick'.
        Make sure to have it installed.

    """
    # Get the filename
    fname = os.path.basename(path)

    # Get the texture attributes
    texattr = getTextureAttr(path)[1]

    if texattr:
        # Default texture attributes
        texchannel = texattr[0]
        texdepth = texattr[1]
        texbgcolor = texattr[2]
        texcompress = texattr[3]
        # texfilter = texattr[4]

        # Create imagemagick identify cmd to get the current image attributes
        cmd_identify = "identify %s" % path

        # Get the current image attributes
        imgattr = commands.getoutput(cmd_identify).split("\n")[-1]
        imgattr = imgattr.split(" ")
        imgdepth = imgattr[4]
        imgformat = imgattr[1]
        # imgres = imgattr[2]

        if texcompress:
            # Zip aka Deflate compression with imagemagick mogrify
            cmd_compress = "mogrify -compress Zip %s" % path
            os.system(cmd_compress)
            print "compress 'Deflate': %s" % fname

        elif texbgcolor != "":
            # Remove image alpha with imagemagick mogrify
            cmd_alpharm = """mogrify -background "%s" -flatten +matte %s""" % (
                path, texbgcolor)
            os.system(cmd_alpharm)
            print "remove alpha: %s" % fname

        if texchannel == "R":
            # Set to single channel with imagemagick mogrify
            cmd_channel = "mogrify -channel R -separate %s" % path
            os.system(cmd_channel)
            print "grayscale: %s" % fname

        if texdepth.find(imgdepth) < 0:
            # Check the image depth
            print "warning: wrong depth '%s', %s should be '%s'" % (imgdepth,
                                                                    fname,
                                                                    texdepth)

        # TODO:check if tiff format warning is working
        if imgformat != "TIFF":
            # Check image format
            print "warning: wrong format '%s', %s should be '%s'" % (imgformat,
                                                                     fname,
                                                                     "TIFF")

    else:
        print "Can't find the '%s' texture type" % fname


def textureExport(path="", progressbar=False):
    # TODO: Documentation for textureExport
    """
    Optimise and build 'tif' textures contained in the provided path.

    :param path: the path to the texture
    :type path: str
    :param progressbar: PySide progressbar
    :type progressbar: PySide progressbar
    :returns: bool -- True if created

    **Example:**
    >>> path = "/homeworks/users/jdoe/projects"
    >>> path += "/bls/chr/mimi/tex/a/bls_chr_mimi_tex_a_spec1.1001.tif"
    >>> textureOptimise(path=path)

    **Note:**
        This function use system commands that calls 'imagemagick'.
        Make sure to have it installed.
    """

    # Get all the tif files in the directory 'path'
    files = glob.glob(os.path.join(path, "*.tif"))

    # TODO: support progressbar for textures optimisation
    for fil in files:
        # Optimise the current texture 'fil'
        textureOptimise(fil)

        # Build the current texture 'fil'
        textureBuild(fil)

    return True


def textureCheck(doc_id="", files=list()):
    """
    This function check if textures respect the Homeworks rules.

    :param doc_id: The asset code
    :type doc_id: str
    :param files: File(s) to check
    :type files: str/list of str
    :returns: list -- list of succeded textures path

    **Example:**
    >>> repo = "/homeworks/users/jdoe/projects"
    >>> path = repo + "/bls/chr/mimi/tex/a/bls_chr_mimi_tex_a_spec1.1001.tif"
    >>> textureOptimise(path=path)

    **Note:**
        This function use system commands that calls 'imagemagick'.
        Make sure to have it installed.
    """
    # Get authorised textures types
    textureType = utils.getTextureTypes()

    # Make sure files is a list
    not_success = list(files)

    # Iterate over provided files
    for fil in files:

        # Get filename
        fname = os.path.basename(fil)

        # Check the texture 'fil' is legal
        for typ in textureType:

            # Common texture pattern
            simpTex = "%s_\d*_%s\d*.\d\d\d\d." % (doc_id, typ)
            simpTex = simpTex + "tif|" + simpTex + "exr"

            # Animated texture pattern
            animTex = "%s_\d*_%s\d*.\d\d\d\d.\d\d\d\d." % (doc_id, typ)
            animTex = animTex + "tif|" + animTex + "exr"

            # Combine patterns
            pattern = "%s|%s" % (simpTex, animTex)

            # If 'fil' texture respect one of the patterns
            if re.findall(pattern, fname):

                texfile = ""
                # Get the extension
                fext = fname.split(".")[-1]

                # Check if the texture is already built
                if fext != "tex":

                    # Replace the current extension by .tex
                    texfile = fil.replace(".%s" % fext, ".tex")

                    # Check if texfile exist
                    if os.path.exists(texfile):

                        # Remove the textures from not_success
                        not_success.remove(fil)
                        not_success.remove(texfile)
                        print "textureCheck: %s OK" % fname

                    else:
                        print "textureCheck: missing .tex for %s" % fname

    return not_success


def texturePush(db=None, doc_id="", path="", comment="",
                progressbar=False, msgbar=False, rename=False, vtype="review"):
    """
    This function copy the desired file from local workspace to repository.

    :param db: the database
    :type db: Database
    :param doc_id: The asset code
    :type doc_id: str
    :param path: The path that contains the textures
    :type path: str
    :param comment: This is the comment of the push
    :type comment: str
    :param progressbar: The pyside progress bar
    :type progressbar: PySide progressbar
    :param msg: The pyside message bar
    :type msg: PySide messagebar
    :param rename: Rename the file (default True)
    :type rename: bool -- if True rename the file(s)
    :param vtype: Version type *trial/stock*
    :type vtype: str
    :returns: bool/list -- list of published textures else False.

    **Example:**

    >>> path = "/homeworks/users/jdoe/projects/bls/chr/mimi/mod/a/ftp.mb"
    >>> db = core.getDb()
    >>> texturePush(db=db, doc_id="bls_chr_mimi_mod_a", path=path,
    >>>            comment="this is a texture version of belanus")
    """
    # Make sure vtype exists
    if not (vtype in utils.getVersionType()):
        return False

    # List the directory
    # TODO: Use glob to get the right textures
    if not os.path.isdir(path):
        return False

    lsdir = os.listdir(path)

    files = list()
    # Iterate over files contained in the directory 'path'
    # and check if the file is a mra or psd
    for fil in lsdir:

        # Get file extension
        ext = os.path.splitext(fil)[-1]

        if ext in (".mra", ".psd"):
            # If current file is a Mari or photoshop file
            # aka extraordinary textures files
            if not (fil.find(doc_id) == 0):
                print fil, "should begin with %s" % doc_id
                return False
        else:
            # else add the file for texture check
            files.append(os.path.join(path, fil))

    # Check the none extraordinary textures files
    texCheck = textureCheck(doc_id, files)

    # If every textures success the check
    if len(texCheck) == 0:
        # Push the directory containing the textures
        pushed = push(doc_id=doc_id, path=path, comment=comment, vtype=vtype)
        return pushed
    else:
        for tex in texCheck:
            print ("texturePush(): %s is wrong" % tex)

        simptex = "%s_%s_%s.%s.%s" % (doc_id, "<variation>", "<type>",
                                      "<udim>", "tif")
        animtex = "%s_%s_%s.%s.%s.%s" % (doc_id, "<variation>", "<type>",
                                         "<udim>", "<frame>", "tif")
        print "texturePush(): expect %s or %s " % (simptex, animtex)

        return False
