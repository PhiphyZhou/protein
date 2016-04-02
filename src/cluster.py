'''
Cluster and label the frames with coordinates or rmsd 
'''

import mdtraj as md
import numpy as np
from scipy.cluster.vq import kmeans2
import scipy.cluster.hierarchy as hi
from sklearn.decomposition import PCA
from sklearn.cross_validation import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt
import pickle
import datareader as dr
from config import *
import sys

def k_means(traj, K, dim_red=None):
    ''' 
    k-means clustering directly on coordinates.
    Args:
        - traj: trajectory object
        - K: number of clusters
        - dim_red: int or None. If not None, do PCA
    Returns:
        1D array of cluster labels
    '''
    # get flattened coordinates of each frame
    coords = traj.xyz
    coords = np.reshape(coords,(len(coords),-1))
    print(coords.shape)

    # PCA
    if dim_red!=None:  
        pca = PCA(dim_red)
        coords = pca.fit(coords).transform(coords)
        print("using PCA")
        print(coords.shape)

    # do k-means clustering 
    print("clustering...")
    centroids, labels = kmeans2(coords,K,iter=100)
    print("done")
    return labels

def hierarchy(traj, K):
    '''
    hierarchical clustering using distance matrix
    '''
    distances = np.empty((traj.n_frames, traj.n_frames))
    for i in range(traj.n_frames):
        distances[i] = md.rmsd(traj, traj, i)
    # Clustering only accepts reduced form. 
    assert np.all(distances - distances.T < 1e-6) # assert symmetry
    reduced_distances = squareform(
                distances, checks=False) # reform to condenced vector
    linkage = hi.linkage(reduced_distances, method='average')
    
    # plot the dendrogram to file
    plt.title('RMSD Average linkage hierarchical clustering')
    _ = hi.dendrogram(linkage, no_labels=True, count_sort='descendent')
    plt.savefig("/output/tempplot")

    # get cluster labels
    labels = hi.fcluster(linkage, t=K, criterion='maxclust')
    
    return labels

def seq_cluster(traj,seq_len,stride,K):
    '''
    Put several frames together to be clustered as a sequence
    
    Args: 
        - traj: the trajectory object
        - seq_len: length of each sequence
        - stride: steps for moving the sequence window
        - K: number of clusters
    Return: labels
    '''
    
    # get flattened coordinates of each frame
    coords = traj.xyz
    coords = np.reshape(coords,(len(coords),-1))
#    print np.shape(coords) 
    # compute the covarance of each sequence as the features
    seqs = []
    for i in xrange(0,len(coords),stride):
        # covariance matrix of the coordinates
        covm = np.cov(np.transpose(coords[i:i+seq_len]))         
#        print np.shape(covm)
        seqs.append(np.diag(covm))
#    print np.shape(seq_data)

    centroids, labels = kmeans2(np.asarray(seqs),K,iter=100)

    # test clustering consistancy using classification
    clf = KNeighborsClassifier() # knn works best for alanine coords
    data_scores = cross_val_score(clf,seqs,labels,cv=5)
    print("Accuracy with 5 folds: %0.2f (+/- %0.2f)" % 
        (data_scores.mean(), data_scores.std()))

    return labels

if __name__ == "__main__":

    task = int(sys.argv[1])

    if task==1:
        # do clustering and save the label file
        traj = dr.load_traj(protein)
#        labels = k_means(traj,num_states,dim_red=10)
        labels = hierarchy(traj,num_states)
        with open("/output/"+protein+"/labels"+suffix,"w") as lb:
            pickle.dump(labels,lb)

    elif task==2:
        # read the label file
#        with open("/output/"+protein+"/labels"+suffix,"r") as lb:
        with open("/protein/data/"+protein+"-labels"+suffix) as lb:
            labels = pickle.load(lb)
#        for l in labels:
#            print(l)    

    elif task==3:
        # cluster the sequences
        traj = dr.load_traj(protein)
        labels = seq_cluster(traj,seq_size,sliding,num_states)

# count the number of each label from 0 to K
    print labels
    print(np.bincount(labels))










