'''
standard classification methods
'''

from sklearn.cross_validation import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
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

def train(clf, features, labels):
    '''
    train the classifier 
    Args:
        - clf: classifier object to use
        - features: float 2D array of sample features 
        - labels: int 1D array of sample labels
    Returns:
        - a trained classifier object
    '''

def main(protein,clf,encoding=False):
    '''
    Args:
        - protein: "bpti" or "alanine", name of the protein
        - encode: if False, classify on coordinates; 
                  if True, classify on encoded hidden states
        - clf: classifier to use
    '''

    if encoding==False:
        # get flattened coordinates of each frame
        traj = dr.load_traj(protein)
        coords = traj.xyz
        coords = np.reshape(coords,(len(coords),-1))
        X = np.asmatrix(coords)    
#        print coords    
    else:
        # get encoded hidden states
        X = np.asmatrix(encode())
    
    # get labels
    with open("/output/"+protein+"/labels","r") as lb:
        Y = np.asarray(pickle.load(lb))
    if encoding==True:
        # need to match the number of sequences 
        end = -seq_size+1
        if end == 0:
            end = Y.size
        Y = Y[0:end:sliding]
#    print Y

    # training and cross validation
    data_scores = cross_val_score(clf,X,Y,cv=int(fold))
    print("Accuracy with %s folds: %0.2f (+/- %0.2f)" % 
        (fold, data_scores.mean(), data_scores.std()))

if __name__ == "__main__":
#    main(protein,classifier)
    main(protein,classifier,True)






