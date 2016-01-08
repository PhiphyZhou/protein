'''
read in protein trajectory files and get the coordinates of atoms
'''

import mdtraj as md

def dcd_raw_data(dcdfile,pdbfile):
    '''
    Read trajectory data and split it into train and test data sets.
    '''
    traj = md.load(dcdfile,top=pdbfile)
    
    return traj

if __name__=="__main__":
    traj = dcd_raw_data("/protein-data/bpti-all/bpti-all-000.dcd","/protein-data/bpti.pdb")
    print traj
