# IPythonNotebookTutorial
IPython Notebook Tutorial for the scientists

# Get notebooks
For SNS users, run the following command:

```
$ /EXAMPLES/IPythonNotebookTutorial/copy-notebooks.py
```

# Contents

1. Introduction to Python with Jupyter Notebooks
  - ```<shift>+<enter>```
  - ```<shift>+<tab>```
  - print 
  - numpy arrays
  - functions
  - matplotlib plot
  
2. Loading and plotting data from a text file
 - `numpy` record arrays and `genfromtxt`
 - Matplotlib: scatter, log, error bars and legend

3. Loading and viewing image data.

4. Glob:
 - `glob`
 - For loops
 - `os.path`
 - string manipulation
 
5. Fitting TAS data
 - Defining functions
 - LMFit
 - Two Pannel plot
 
6. Loading and plotting a log from a NeXus file
- h5py

7. Working with Mantid and Python
 

# Setup environment using conda

```
$ conda create -n ipythonnotebooktutorial
$ source activate ipythonnotebooktutorial
$ conda install python=3 scipy numpy matplotlib h5py astropy lmfit jupyter
```

# Links
* A gallery of jupyter notebooks: https://github.com/jupyter/jupyter/wiki/A-gallery-of-interesting-Jupyter-Notebooks
* Coursera data science course using jupyter https://en.coursera.org/learn/python-data-analysis
* Jupyter notebook "BINARY BLACK HOLE SIGNALS IN LIGO OPEN DATA": http://nbviewer.jupyter.org/urls/losc.ligo.org/s/events/LOSC_Event_tutorial.ipynb
