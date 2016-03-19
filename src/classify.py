'''
standard classification methods
'''

import numpy as np
from sklearn.cross_validation import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.svm import SVC
from sklearn import preprocessing
from random import shuffle
import json
import pandas as pd

def classify(traj):
    # get flattened coordinates of each frame
    coords = traj.xyz
    coords = np.reshape(coords,(len(coords),-1))
 
