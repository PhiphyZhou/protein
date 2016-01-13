'''
This module is for preprocessing the DE Shaw BPTI data,ie, to:
- read in trajectory files and reform the data into desired window structre
- unify the reference for all frames
- rescale the coordinates into [-1,1] for feature learning
- arrange the data into batches and epochs for training
'''

import mdtraj as md
import numpy as np
import pickle

# Data file parameters
num_files = 2 # number of dcd files we want to analyze 
dcd_path = "/protein-data/bpti-all/bpti-all-"
pdb_file = "/protein-data/bpti-all.pdb"
window_size = 10 # number of frames to be averaged
seq_size = 10  # number of averaged frames in a sequence

def load_data(store_ref=False):
    '''   
    Read trajectory data.
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
    for i in xrange(0,traj.n_frames,window_size*seq_size):
        coords = []
        for j in xrange(i,i+window_size*seq_size, window_size):
            xyz_ave = np.mean(traj[i:i+window_size].xyz,axis=0)
#            if(i==0 and j==0):
#                print "before rescaling: "+str(xyz_ave[0])
            xyz_rescaled = np.divide(np.subtract(xyz_ave,mm_sum),mm_dif)
#            if(i==0 and j==0):
#                print "after rescaling: "+str(xyz_rescaled[0])
            xyz_rescaled = xyz_rescaled.flatten()
            coords.append(xyz_rescaled) # one sequence
        data.append(coords) 
    return data

if __name__=="__main__":
    data = load_data(True)
#    print np.amax(data,axis=(0,1))
#    print np.amin(data,axis=(0,1))
#    print data[0]

