'''
##################### Global PARAMETERS ###########################
### Modify the following parameters for experiments ###

modules using this config file:

encoder_decoder
classify
cluster

'''
## Data inputs ##
#protein_name = "bpti"
protein = "alanine"
num_files = 1 # number of dcd files we want to analyze, for bpti data 
window_size = 1 # number of frames to be averaged
seq_size = 3 # number of averaged frames in a sequence (>1)
sliding = 1 # sliding for sequence 
data_para = (protein,num_files,window_size,seq_size,sliding)
num_states = 4 # number of states for the protein

## Model inputs ##
# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
buckets = [(seq_size,seq_size)] # all sequences will be of the same length
feature_size = 0 # to be decided after reading training data
hidden_size = 10 # dimension of encoded states
num_layers = 1 
max_gradient_norm = 1.0
batch_size = 5
learning_rate = 0.5
learning_rate_decay_factor = 0.9
train_dir = "/output/"+protein
steps_per_checkpoint = 5
max_steps = 100 # the maximum number of steps for each training
min_learning_rate = 0.01 # the minimum learning rate for terminating the training
# num_steps = 3 # number of depth of unroll

########################################################


