#!/usr/bin/env python

from __future__ import print_function
import getpass, os
user = getpass.getuser()
site_url = "https://jupyter.sns.gov"
nb_dir = os.path.expanduser('~/notebooks')
if not os.path.exists(nb_dir): os.makedirs(nb_dir)

BOLD = '\033[1m'
UNBOLD = '\033[0m'
def copy(subdir, description):
    target_dir = "notebooks/IPythonNotebookTutorial-%s" % subdir
    target_path = os.path.join(os.path.expanduser('~'), target_dir)
    cmd = "rsync -q -av /EXAMPLES/IPythonNotebookTutorial/%s/ %s/" % (subdir, target_path)
    if os.system(cmd):
        raise RuntimeError("%s failed" % cmd)
    print(BOLD+description+UNBOLD+": %s/user/%s/tree/%s/" % (site_url, user, target_dir))
    return

print('*'*95)
print()
print(BOLD+"Open the following links:"+UNBOLD)
print()
copy('notebooks', 'tutorials')
copy('solutions', 'solutions')

print()
print('*'*95)

