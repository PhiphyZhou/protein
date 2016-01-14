'''
This module is for preprocessing the DE Shaw BPTI data,ie, to:
- read in trajectory files and reform the data into desired window structre
- unify the reference for all frames
- rescale the coordinates into [-1,1] for feature learning
- arrange the data into batches and epochs for training
'''

import mdtraj as md
import numpy as np
import pickle, random

# Data file parameters
num_files = 2 # number of dcd files we want to analyze 
dcd_path = "/protein-data/bpti-all/bpti-all-"
pdb_file = "/protein-data/bpti-all.pdb"
window_size = 10 # number of frames to be averaged
batch_size = 10  # number of sequences in a batch

def load_data(store_ref=False):
    '''   
    Read trajectory data and preprocess.
    If store_ref==True(usually for the first time of reading data),
    the reference frame and the coordinate boundaries are stored into disk.
    '''
    dcd_files = []
    for i in xrange(num_files):
        if(i<10):
            num="00"+str(i)
        elif(i<100):
            num="0"+str(i)
        else: 
            num=str(i)
        dcd_file=dcd_path+num+".dcd"
        dcd_files.append(dcd_file)
    
    traj = md.load(dcd_files,top=pdb_file)
    
        
    # Superpose each frame with the first frame as the reference
    traj.superpose(traj,0)
    
    # bounds for rescaling
    xyz_max=np.amax(traj.xyz,axis=0)
    xyz_min=np.amin(traj.xyz,axis=0)
    mm_sum = np.add(xyz_max,xyz_min)/2
    mm_dif = np.subtract(xyz_max,xyz_min)/2
#    print "mm_sum[0]="+str(mm_sum[0])
#    print "mm_dif[0]="+str(mm_dif[0])
#    print traj[0].xyz
    
    # store the reference and boundaries
    if store_ref:
        with open("/output/protein/ref_frame","w") as ref,\
            open("/output/protein/xyz_max","w") as ma,\
            open("/output/protein/xyz_min","w") as mi:
            pickle.dump(traj[:1],ref)
            pickle.dump(xyz_max,ma)
            pickle.dump(xyz_min,mi)
#    print pickle.load(open("/output/protein/ref_frame","r"))
#    print pickle.load(open("/output/protein/xyz_max","r"))
#    print pickle.load(open("/output/protein/xyz_min","r"))

    # make window averages, rescale and break into sequences
    data = []
    seq_size = len(traj)//window_size//batch_size
#    print seq_size
    for i in xrange(0,traj.n_frames,window_size*seq_size):
        coords = []
        for j in xrange(i,i+window_size*seq_size, window_size):
            xyz_ave = np.mean(traj[j:j+window_size].xyz,axis=0)
#            print xyz_ave[0,0]
#            if(i==0 and j==0):
#                print "before rescaling: "+str(xyz_ave[0])
            xyz_rescaled = np.divide(np.subtract(xyz_ave,mm_sum),mm_dif)
#            if(i==0 and j==0):
#                print "after rescaling: "+str(xyz_rescaled[0])
            xyz_rescaled = xyz_rescaled.flatten()
#            print "rescale: ",xyz_rescaled[0]
            coords.append(xyz_rescaled) # one sequence
        data.append(coords) 
    return data

def split_train_test(data,frac):
    '''split the whole data set randomly into train and test sets
       frac: gives the fraction of the train set
    '''
    train = []
    test = []
    if frac<0.5 or frac>1:
        raise ValueError("frac must be a real number in [0.5,1]")
    # random splitting
#    for i in xrange(len(data)):
#        r = random.random()
#        if r<frac:
#            train.append(data[i])
#        else: 
#            test.append(data[i])
    
    # determined splitting
    dense = int(1/(1-frac))
    for i in xrange(0,len(data)):
        if i%dense == dense//2:
            test.append(data[i])
        else:
            train.append(data[i])
    return train, test

if __name__=="__main__":
    data = load_data(True)
    train, test = split_train_test(data,0.7)
    print len(train),len(test)
#    print np.amax(data,axis=(0,1,2))
#    print np.amin(data,axis=(0,1,2))
#    print data[0]

