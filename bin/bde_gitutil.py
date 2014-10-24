import re
import os
import subprocess

def getBranch():
    """
    Return the current branch for the local git repository.
    """
    return subprocess.check_output(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"]).rstrip()

def getStatus():
    """
    Returns the current status of the local git repository.
    """
    return subprocess.check_output(
                        ["git", "status", "--porcelain"]).rstrip()

def getDiff(path):
    """
    Returns the current diff for the local git repository.
    """
    return subprocess.check_output(
                        ["git", "diff"]).rstrip()

def checkoutBranch(branch):
    """
    Perform a 'git checkout' for the specified 'branch' in the local git 
    repository.
    """
    subprocess.check_call(["git", "checkout", branch]);

def checkoutBranchAndPull(branch, forceCheckout):
    """
    Perform a 'git checkout' for the specified 'branch' in the local git
    repository.   If 'forceCheckout' is 'false', throw an exception if there
    are uncommitted changes in the repository.
    """
    if (not forceCheckout):
        try:
            subprocess.check_call(
                ["git", "diff-files", "--quiet", "--ignore-submodules"])
        except subprocess.CalledProcessError:
            print "##### {0} repo state is not clean - aborting".format(path)
            raise

    subprocess.check_call(["git", "checkout", branch]);
    subprocess.check_call(["git", "pull", "--ff-only"])

def gitFetch():
    """
    Does a fetch for the local git repository.
    """
    try:
        subprocess.check_call(["git", "fetch"])
    except subprocess.CalledProcessError:
        print "##### {0} repo fetch failed - aborting".format(path)
        raise

def gitClone(repositoryUri, branch = None):
    """
    Preforms a 'git clone' in the current working directory for the specified
    'repositoryUri'.
    """
    if (branch is None): 
        subprocess.check_call(["git", "clone", repositoryUri])
    else:
        subprocess.check_call(["git", "clone", "--single-branch", "--branch",
                               branch, repositoryUri])

def parseRepositoryString(repositoryString):
    """
    Parse the specified 'repositoryString' and return a tuple containing
    (uri, path, branch, isRemote).

    Args:
        repositoryString (string) : a string indicating the URI and possible
           and possible branch name, in the form:
           (<URI> | <PATH>) ('|' <BRANCH>)?
           for example: https://github.com/bloomberg/bde.git|master

    Returns a tuple:
        uri (string) : a string identifying the repository
        
        path (string) : the path the repository is (or will be after it is
           cloned) located
           
        branch (string) : the branch in the repository (may be None)
        
        isRemote (boolean) : 'true' if the 'uri' refers to a remote respository
           (that may need to be cloned), and 'false' if 'uri' is a local path.
    """

    uriAndBranch = re.match("([^|]*)(?:\|(.*))?", repositoryString);

    if (uriAndBranch is None   or
        len(uriAndBranch.groups()) == 0 or
        len(uriAndBranch.groups()) > 2):
        raise Exception("Repository specifier '{0}' is invalid".format(
                                                             repositoryString))

    uri    = uriAndBranch.groups()[0]
    branch = None

    if (uriAndBranch.groups()):
        branch = uriAndBranch.groups()[1]
        
    isRemote = re.match(".*:.*", uri) is not None

    if (not isRemote):
        path = uri
    else:
        pathMatch = re.match("(?:.*/)?([^.]*).*", uri)
        path = pathMatch.groups()[0]
    
    return (uri, path, branch, isRemote)


def checkout(repositories, clean, forceCheckout):
    """
    Checkout each repository in the list of repositories.

    Args:
        repositories ([(string,string,string,bool)]) : A list of tuples, each
          containing a (uri, path, branch, isRemote).

        clean (boolean) : if True and a repository's 'isRemote' is False, then
           perform a 'git clean' on the directory.

        forceCheckout (boolean) :  if True and a repository's 'isRemote' is
           False, then the branch change is forced (possibly orphaning
           changes in the active working set of the repository)
    """
    for (uri, path, branch, isRemote) in repositories:
        if (isRemote):
            gitClone(uri, branch)
        elif (branch is not None):
            currentPath = os.getcwd()
            os.chdir(path)
            checkoutBranchAndPull(branch, forceCheckout)
            os.chdir(currentPath)
