'''
This module is for preprocessing the DE Shaw BPTI data,ie, to:
- read in trajectory files and reform the data into desired window structre
- unify the reference for all frames
- rescale the coordinates into [-1,1] for feature learning
'''

import mdtraj as md
import mdtraj.testing as mdtesting
import numpy as np
import pickle, random

def load_traj(protein, num_files=1):
  '''
  load the trajectory object from dcd files

  Args: 
    - protein: "bpti" or "alanine"
    - num_files: for bpti only

  Return: traj object
  '''
  
  print("loading traj object...")
  # construct data file path
  if(protein=="bpti"):
    # deal with bpti data
    dcd_path = "/protein-data/bpti-all/bpti-all-"
    pdb_file = "/protein-data/bpti-all.pdb"
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
  elif(protein=="alanine"):
    # deal with alanine data
    dcd_files = "../data/alanine.dcd"  
    pdb_file = "../data/alanine.pdb"         
  else:
    raise ValueError("Unknown protein name: ",protein)
  
  # read trajectories 
  traj = md.load(dcd_files,top=pdb_file)    
  
#  print(traj)
  top = traj.topology
#  print(top)
#  print([a for a in top.atoms])
#  print(top.atom(-100).residue.is_water)

  # slice the atoms to get rid of water
#  protein_atoms = top.select("protein")
  relevant = top.select("not water")
  
  # extract the protein atoms in the trajectory
  traj = traj.atom_slice(relevant)
  print(traj)
    
  # Superpose each frame with the first frame as the reference
  traj.superpose(traj,0)
  return traj

def load_data(data_para,rescale=False,store_ref=False):
  '''   
  Read trajectory data and preprocess for seq2seq training and encoding
  
  Args:
    - data_para: protein_name,num_files,window_size,seq_size,sliding
      sliding:
      number of frames each sequence window slides forward 
      If == 0, no sliding, which means jumping to the next new frame
    - rescale(default=False)
      If True, rescale the coordinates to [-1,1] using the maximum range of the data.
    - store_ref(default=False)
      If store_ref==True(usually for the first time of reading data),
      the reference frame and the coordinate boundaries are stored into disk.
  Returns:
    - data = [num_sequences, sequence_length # of nparray(3*atom_number)]
      smoothed, re-referenced and rescaled(if required) coordinates
  Raise:
    ValueError: if value protein is not an known protein name.
  '''

  # load the trajectory
  protein, num_files, window_size, seq_size, sliding = data_para
  traj = load_traj(protein,num_files)

  # bounds for rescaling
  xyz_max=np.amax(traj.xyz,axis=0)
  xyz_min=np.amin(traj.xyz,axis=0)
  mm_sum = np.add(xyz_max,xyz_min)/2
  mm_dif = np.subtract(xyz_max,xyz_min)/2
#  print "mm_sum[0]="+str(mm_sum[0])
#  print "mm_dif[0]="+str(mm_dif[0])
#  print traj[0].xyz
  
  # store the reference and boundaries
  if store_ref:
    with open("/output/protein/ref_frame","w") as ref,\
      open("/output/protein/xyz_max","w") as ma,\
      open("/output/protein/xyz_min","w") as mi:
      pickle.dump(traj[:1],ref)
      pickle.dump(xyz_max,ma)
      pickle.dump(xyz_min,mi)
#  print pickle.load(open("/output/protein/ref_frame","r"))
#  print pickle.load(open("/output/protein/xyz_max","r"))
#  print pickle.load(open("/output/protein/xyz_min","r"))

  # make window averages, rescale and break into sequences
  data = []
#  seq_size = len(traj)//window_size//batch_size # this is for a long seq
#  print seq_size

  # deal with sliding
  if sliding==0:
    sliding = seq_size
  
  # merge windows and slide to make sequances
  for i in xrange(0,traj.n_frames-window_size*seq_size+1,
          window_size*sliding):
    coords = []
    for j in xrange(i,i+window_size*seq_size, window_size):
      xyz_ave = np.mean(traj[j:j+window_size].xyz,axis=0)
      
      if(rescale):
        xyz_rescaled = np.divide(np.subtract(xyz_ave,mm_sum),mm_dif)
        xyz = xyz_rescaled.flatten()
      else:
        xyz = xyz_ave.flatten()
      coords.append(xyz) # one sequence
    data.append(coords) 
    
  return data

def split_train_test(data,frac):
  '''
  split the whole data set randomly into train and test sets
  
  Args:
    - frac = the fraction of the train set

  Returns:
    - train_set, test_set
  '''
  train = []
  test = []

  if(frac>0.99999999):
    train = data
    return train, test
  if frac<0.5 or frac>1:
    raise ValueError("frac must be a real number in [0.5,1]")
  # random splitting
#  for i in xrange(len(data)):
#    r = random.random()
#    if r<frac:
#      train.append(data[i])
#    else: 
#      test.append(data[i])
  
  # determined splitting
  dense = int(1/(1-frac))
  for i in xrange(0,len(data)):
    if i%dense == dense//2:
      test.append(data[i])
    else:
      train.append(data[i])
  return train, test

def data_iterator(raw_data,num_steps):
  """Iterate on the raw data.

  Args:
  raw_data: one of the raw data outputs from load_data or split_train_test
  num_steps: int, the number of unrolls, indicating the depth
      of truncated back propagation.

  Yields:
  Pairs of the batched data, each a matrix of shape [batch_size, num_steps].
  The second element of the tuple is the same data time-shifted to the
  right by one.

  Raises:
  ValueError: if num_steps are too high.
  """
  data = np.array(raw_data, dtype=np.float32)
#  print raw_data
#  print data
  epoch_size = (data.shape[1] - 1) // num_steps
  print epoch_size  
  if epoch_size == 0:
    raise ValueError("epoch_size == 0, decrease batch_size or num_steps")
  for i in range(epoch_size):
    x = data[:, i*num_steps:(i+1)*num_steps]
    y = data[:, i*num_steps+1:(i+1)*num_steps+1]
    yield (x, y)


if __name__=="__main__":
  num_files = 1
  protein_name = "alanine"
#  protein_name = "bpti"
  window_size = 1 # number of frames to be averaged
  seq_size = 2 # number of averaged frames in a sequence
  data_para = (protein_name,num_files,window_size,seq_size)
  data = load_data(data_para)

#  train, test = split_train_test(data,0.7)
#  for step, (x, y) in enumerate(data_iterator(test,num_steps)):
#    print "x: \n", x
#    print "y: \n", y
#  print len(train),len(test)
#  print np.amax(data,axis=(0,1,2))
#  print np.amin(data,axis=(0,1,2))
#  print data[0]




