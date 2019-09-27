"""
Get the current git version
"""
import os
import subprocess

if "__file__" not in locals():
    print("LIKELY FAILURE: This script is being called from an environment "
          "that doesn't know where it is.  Report this please.")

path = os.path.dirname(os.path.abspath(__file__))
almaimf_rootdir = os.getenv('ALMAIMF_ROOTDIR')

# almaimf_rootdir must be set to this file's pathii!
assert os.path.dirname(almaimf_rootdir) == os.path.dirname(path)


cwd = os.getcwd()

os.chdir(path)

gitcmd = "git log -1 --date=short --format=%h"
git_version = subprocess.check_output(gitcmd.split()).decode().strip()
gitcmd = "git log -1 --date=short --format=%ad"
git_date = subprocess.check_output(gitcmd.split()).decode().strip()

os.chdir(cwd)

print("Loaded ALMA-IMF pipeline version {0} {1}".format(git_version, git_date))


if __name__ == "__main__":

    print(git_version)
    print(git_date)

    gitcmd = "git --version"
    git_tool_version = subprocess.check_output(gitcmd.split()).decode().strip()
    print(git_tool_version)
