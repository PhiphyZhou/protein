'''
read in protein trajectory and reform the data into desired window structre
'''

import mdtraj as md
import numpy as np

# Data file parameters
num_files = 2 # number of dcd files we want to analyze 
dcd_path = "/protein-data/bpti-all/bpti-all-"
pdb_file = "/protein-data/bpti-all.pdb"
window_size = 10

def dcd_raw_data():
   
    #  Read trajectory data
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

    # make window averages
    coords = []
    for i in xrange(0,traj.n_frames,window_size):
        xyz_ave = np.mean(traj[i:i+window_size].xyz,axis=0)
        coords.append(xyz_ave)
    return coords

if __name__=="__main__":
    traj = dcd_raw_data()
    print traj
