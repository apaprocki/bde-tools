#!/usr/bin/env python

import os
import sys
import bde_gitutil

import optparse
from optparse import OptionParser

USAGE = "Usage: %prog [options] repository*"

DESCRIPTION = """
Checkout the indicated set of repositories. Each 'repository' on the command
line should have the form:

Repositry Format:
    repository    = repository-id "|" [branch-name]
    repository-id = URI | relative-path

Where:
    URI           : A URI accepted by 'git clone' (e.g., devgit:bde/bde-core)
    relative-path : A relative path to a git repository
    branch-name   : The name of a valid branch in the indicated repository
    
For example:
    https://github.com/bloomberg/bde.git|master
       The master branch of the BDE github repository

    bde-tools|releases/2.22.x
       The 2.22 release branch of the repository in the 'bde-tools' directory

For each repository either:
1. If the repository is a identified by a URI, clone that repository to
   the current working directory, and checkout the indicated branch

2. 'cd' to the relative-path, and checkout the indicated branch, then perform
   a 'git pull'

If no branch is indicated with the respository, the branch indicated by the
'--branch' option is used.  If there is no branch indicated, either with the
repository, or through the '--branch' options, then no 'checkout' is performed.
Note that for a relative path to a git repositor, if no branch is indicated,
this operation has no effect.

If no repositories are provided, the checkout and pull will be peformed on the
list of repositories in the 'BDE_PATH' environment variable'.
""".strip()

EPILOG = """
Note that this script will abort if one of the git repositories contains
uncommitted changes (unless the --force option is used) and attempt to return
any modified repositories to their original branches.
""".strip()


class PlainHelpFormatter(optparse.IndentedHelpFormatter): 
    def format_description(self, description):
        if description:
            return description + "\n"
        else:
            return ""
        

def pathList(path):     # return a list of paths from a ':' separated string
    """
    Return a list containing the set of paths encoded in the specified 'path'
    environment variable style string (':' separated on UNIX, ';' on windows).
    """
    return path.split(os.pathsep)


def main():
    parser = OptionParser(usage = USAGE,
                          description = DESCRIPTION,
                          epilog = EPILOG,
                          formatter = PlainHelpFormatter());
    parser.add_option("-b",
                      "--branch",
                      action="store",
                      dest="branch",
                      type="string",
                      default=None,
                      help="the branch name to checkout (if no explicity branch is provided")
    parser.add_option("-f",
                      "--force",
                      action="store_true",
                      dest="force",
                      default=False ,
                      help="force a checkout (even with uncommitted changes)")
    parser.add_option("-c",
                      "--clean",
                      action="store_true",
                      dest="clean",
                      default=False ,
                      help="Clean the git repository ('git clean -xfd')")

    (options, args) = parser.parse_args()

    repositories = []  # list of tuple(uri, path, branch, isRemote) 
    if (len(args) == 0):
        paths = pathList(os.environ['BDE_PATH'])
        repositories = map(lambda path: (path, path, None, False), paths)
    else:
        repositories = map(bde_gitutil.parseRepositoryString, args)
        

    # Apply the default branch.
    repositories = map(lambda (uri, path, branch, remote):
                    (uri,
                     path,
                     branch if branch is not None else options.branch,
                     remote),
                     repositories)

    bde_gitutil.checkout(repositories, options.clean, options.force)
    
if __name__ == "__main__":
    main()
