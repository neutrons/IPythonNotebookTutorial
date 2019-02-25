# Logistics

Getting ready before the class:
* Update teaching materials (notebooks, data files, image files) in this repository
* Goto analysis cluster `/EXAMPLES/IPYthonNotebookTutorial/` and run `git pull`

Starting the class by
* Asking users to click [the get-python-tutorials notebook](https://jupyter.sns.gov/user/%7BUSER%7D/notebooks/notebooks/Get%20Python%20Tutorials.ipynb) and run the notebook

Troubleshooting
* Needs to remember "Data" is a symlink. 
* h5py: needs HDF5_USE_FILE_LOCKING=FALSE
* If missing kernel(s), it is possible that a user's bookkeeping records for the kernels are broken. Need to restablish kernels for him/her. To do that
  - In user's account 
  `$ mv ~/.sns-jupyternotebook-environment ~/.sns-jupyternotebook-environment.obsolete`
  - open [the Welcome notebook](https://jupyter.sns.gov/user/{USER}/notebooks/notebooks/Welcome.ipynb), **restart the kernel**, and run it.
* If a user's remote kernels (**`... at jnrk-sns-analysis`**) keep failing, it is possible that the SNS analysis node that used to work for the user stops working. Modify `~/.ssh/config`, entry `jnrk-sns-analysis`, and change `HostName` to a  working analysis node: it should be something like `analysis-node14.sns.gov`.
  
Misellaneous
* Stickers: quite useful. Ask people to remove the green sticker before starting each exercise
* jupyter.sns.gov only works for SNS users. Other ORNL users have to be added temporarily
* jupyterhub server requirements (~70 simultaneous people):
  - Memory>32GB. better at 64GB 
  
