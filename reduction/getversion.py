"""
Get the current git version
"""
import os
import subprocess

path = os.path.split(__file__)[0]
cwd = os.getcwd()

os.chdir(path)

gitcmd = "git log -1 --date=short --format=%h"
git_version = subprocess.check_output(gitcmd.split()).decode().strip()
gitcmd = "git log -1 --date=short --format=%ad"
git_date = subprocess.check_output(gitcmd.split()).decode().strip()

os.chdir(cwd)
