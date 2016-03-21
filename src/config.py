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
#protein = "bpti"
num_files = 4000 # number of dcd files we want to analyze, for bpti data 
file_stride = 40 # files to increment when reading bpti dcd files
num_states = 4 # number of states for the protein

## Data configuration ##
window_size = 1 # number of frames averaged, it decreases frame number
smooth_window = 10 # another way of smoothing, not decreases frame number
seq_size = 5 # number of averaged frames in a sequence (>1)
sliding = 1 # sliding for sequence 

## Model inputs ##
# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
buckets = [(seq_size,seq_size)] # all sequences will be of the same length
feature_size = 0 # to be decided after reading training data
hidden_size = 10 # dimension of encoded states
num_layers = 1 
max_gradient_norm = 1.0
batch_size = 64
learning_rate = 0.5
learning_rate_decay_factor = 0.9
train_dir = "/output/"+protein
steps_per_checkpoint = 5
max_steps = 100 # the maximum number of steps for each training
min_learning_rate = 0.01 # the minimum learning rate for terminating the training
# num_steps = 3 # number of depth of unroll

########################################################


