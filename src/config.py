'''
##################### Global PARAMETERS ###########################
### Modify the following parameters for experiments ###

modules using this config file:
data_reader
encoder_decoder
classify
cluster

'''
## Data selection ##
protein = "alanine"
suffix = "-10000-1" # alanine file suffix for number of samples

#protein = "bpti"
num_files = 4000 # number of dcd files we want to analyze, for bpti data 
file_stride = 40 # files to increment when reading bpti dcd files

num_states = 2 # number of states for the protein

## Data configuration ##
# smoothing parameters
window_size = 1 # number of frames averaged, it decreases frame number
smooth_window = 10 # smoothing not decreasing frame number. Set to 1 to turnoff
# building sequences
seq_size = 4 # number of averaged frames in a sequence (>1)
sliding = 1 # sliding for sequence 

## Model parameters ##
# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
buckets = [(seq_size,seq_size)] # all sequences will be of the same length
feature_size = 0 # to be decided after reading training data
hidden_size = 5 # dimension of encoded states
num_layers = 2 # total hidden dimension=hidden_size*num_layers 
# num_steps = 3 # number of depth of unroll for continuous sequence

## Training parameters ##
train_dir = "/output/"+protein+"/"+protein+suffix # directory for model checkpoints
train_portion = 0.9 # ratio of training data among (train+dev)
batch_size = 64
max_gradient_norm = 3.0
learning_rate = 1.0 # initial learning rate
min_learning_rate = 0.01 # the minimum learning rate for terminating the training
learning_rate_decay_factor = 0.9 # rate <- decay_factor*rate
steps_per_checkpoint = 5
max_steps = 1000 # the maximum number of steps for each training

########################################################


