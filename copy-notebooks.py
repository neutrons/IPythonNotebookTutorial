#!/usr/bin/env python

from __future__ import print_function
import getpass, os
user = getpass.getuser()
site_url = "https://jupyter.sns.gov"
target_dir = "notebooks/IPythonNotebookTutorial-notebooks"

nb_dir = os.path.expanduser('~/notebooks')
if not os.path.exists(nb_dir): os.makedirs(nb_dir)
target_path = os.path.join(os.path.expanduser('~'), target_dir)
cmd = "rsync -av /EXAMPLES/IPythonNotebookTutorial/notebooks/ %s/" % target_path
os.system(cmd)

print()
BOLD = '\033[1m'
UNBOLD = '\033[0m'
print('*'*80)
print(BOLD+"Open the following link to open the tutorials"+UNBOLD)
print()
print("%s/user/%s/tree/%s/" % (site_url, user, target_dir))
print('*'*80)
