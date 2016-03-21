'''
standard classification methods
'''

from sklearn.cross_validation import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.decomposition import PCA

import pickle
import numpy as np

import datareader as dr
from encoder_decoder import encode
from config import *

# choose a classifier
classifier = KNeighborsClassifier() # knn works best for alanine coords
#classifier = RandomForestClassifier()
#classifier = AdaBoostClassifier()
fold = 5 # number of folds for cross validation

def train(protein,clf,dim_red=None,encoding=False):
  '''
  Args:
    - protein: "bpti" or "alanine", name of the protein
    - clf: classifier to use
    - dim_red: int or None. 
          if not None, it's the reduced dimension for PCA 
    - encode: if False, classify on coordinates; 
          if True, classify on encoded hidden states
  '''
  
  # get features
  if encoding==False:
    # get flattened coordinates of each frame
    traj = dr.load_traj(protein)
    coords = traj.xyz
    coords = np.reshape(coords,(len(coords),-1))
    X = coords    
#    print coords  
  else:
    # get encoded hidden states
    X = encode()
  
  # use PCA to reduce dimension
  if dim_red != None:
    pca = PCA(dim_red)
    X = pca.fit(X).transform(X)
#    print X[0]

  # get labels
  with open("/output/"+protein+"/labels","r") as lb:
    Y = np.asarray(pickle.load(lb))
  if encoding==True:
    # need to match the number of sequences 
    end = -seq_size*window_size+1
    if end == 0:
      end = Y.size
    Y = Y[0:end:sliding*window_size]
#  print Y

  # training and cross validation
  data_scores = cross_val_score(clf,X,Y,cv=int(fold))
  print("Accuracy with %s folds: %0.2f (+/- %0.2f)" % 
    (fold, data_scores.mean(), data_scores.std()))

if __name__ == "__main__":
#  train(protein,classifier,dim_red=10)
  train(protein,classifier,encoding=True)






