'''
Cluster and label the frames with coordinates or rmsd 
'''

import mdtraj as md
import numpy as np
from scipy.cluster.vq import kmeans2
import scipy.cluster.hierarchy as hi
from sklearn.decomposition import PCA
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt
import pickle
import datareader as dr
from config import *

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

def seq_cluster(traj, seq_len,K):
    

if __name__ == "__main__":
	traj = dr.load_traj(protein)
#  labels = k_means(traj,num_states,dim_red=10)
	labels = hierarchy(traj,num_states)
	print labels
	with open("/output/"+protein+"/labels"+suffix,"w") as lb:
		pickle.dump(labels,lb)
#  with open("/output/"+protein+"/labels","r") as lb:
#		 print(pickle.load(lb))




