"""Binary for training translation models and decoding from them.
This file is adapted from the Tensorfile code:
https://github.com/tensorflow/tensorflow/blob/master/tensorflow/models/rnn/translate/translate.py
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os
import random
import sys
import time

import tensorflow.python.platform

import numpy as np
from six.moves import xrange    # pylint: disable=redefined-builtin
import tensorflow as tf

import seq2seq_model
from tensorflow.python.platform import gfile

import datareader as dr

##################### TUNING PARAMETERS ###########################
### Modify the following parameters for experiments ###

## Data inputs ##
num_files = 100 # number of dcd files we want to analyze, for bpti data 
protein_name = "bpti"
#protein_name = "alanine"
window_size = 10 # number of frames to be averaged
seq_size = 5 # number of averaged frames in a sequence
data_para = (protein_name,num_files,window_size,seq_size)

## Model inputs ##
# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
_buckets = [(5,5)] # all sequences will be of the same length
feature_size = 0 # to be decided after reading training data
hidden_size = 500
num_layers = 3
max_gradient_norm = 5.0
batch_size = 64
learning_rate = 0.5
learning_rate_decay_factor = 0.99
train_dir = "/output/"+protein_name
steps_per_checkpoint = 100
max_steps = 1000 # the maximum number of steps for each training
min_learning_rate = 0.01 # the minimum learning rate for terminating the training
num_steps = 3 # number of depth of unroll

########################################################

def create_model(session, forward_only):
    """Create translation model and initialize or load parameters in session."""
    model = seq2seq_model.Seq2SeqModel(feature_size, _buckets,
            hidden_size, num_layers, max_gradient_norm, batch_size,
            learning_rate, learning_rate_decay_factor,
            forward_only=forward_only)
    ckpt = tf.train.get_checkpoint_state(train_dir)
    if ckpt and gfile.Exists(ckpt.model_checkpoint_path):
        print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
        model.saver.restore(session, ckpt.model_checkpoint_path)
    else:
        print("Created model with fresh parameters.")
        session.run(tf.initialize_all_variables())
    return model


def train():
    """Train an encoder for learning the hidden state of a sequence"""
    train_set, dev_set, _ = get_data()
   
    train_bucket_sizes = [len(train_set[b]) for b in xrange(len(_buckets))]
    train_total_size = float(sum(train_bucket_sizes))

    # A bucket scale is a list of increasing numbers from 0 to 1 that we'll use
    # to select a bucket. Length of [scale[i], scale[i+1]] is proportional to
    # the size if i-th training bucket, as used later.
    train_buckets_scale = [sum(train_bucket_sizes[:i + 1]) / train_total_size
                                                 for i in xrange(len(train_bucket_sizes))]


    with tf.Session() as sess:

        # Create model
        print("Creating %d layers of %d units." % (num_layers, hidden_size))
        model = create_model(sess, False)
        
        # This is the training loop.
        step_time, loss = 0.0, 0.0
        current_step = 0
        previous_losses = []
        print("Begin training")
        for _ in xrange(max_steps):
            # Choose a bucket according to data distribution. We pick a random number
            # in [0, 1] and use the corresponding interval in train_buckets_scale.
            random_number_01 = np.random.random_sample()
            bucket_id = min([i for i in xrange(len(train_buckets_scale))
                            if train_buckets_scale[i] > random_number_01])
#            print(bucket_id)

            # Get a batch and make a step.
            start_time = time.time()
            encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                    train_set, bucket_id, True)
#            print(len(encoder_inputs))
            _,step_losses,grad_norm = model.step(sess, encoder_inputs, decoder_inputs,
                                         target_weights, bucket_id, False)
            step_loss = np.mean(step_losses)
            step_time += (time.time() - start_time) / steps_per_checkpoint
            loss += step_loss / steps_per_checkpoint
            current_step += 1
            print("step %d:\nlosses: %s \ngrad_norms: %s" % (
                        current_step, step_losses, grad_norm))
            

            # Once in a while, we save checkpoint, print statistics, and run evals.
            if current_step % steps_per_checkpoint == 0:
                # Print statistics for the previous epoch.
                print ("global step %d learning rate %.4f step-time %.2f loss "
                             "%.2f" % (model.global_step.eval(), model.learning_rate.eval(),
                                                 step_time, loss))
                # Decrease learning rate if no improvement was seen over last 3 times.
                if len(previous_losses) > 2 and loss > max(previous_losses[-3:]):
                    sess.run(model.learning_rate_decay_op)
                if model.learning_rate.eval() < min_learning_rate:
                    break
                previous_losses.append(loss)
                # Save checkpoint and zero timer and loss.
                checkpoint_path = os.path.join(train_dir, "encoder-decoder.ckpt")
                model.saver.save(sess, checkpoint_path, global_step=model.global_step)
                step_time, loss = 0.0, 0.0
                # Run evals on development set and print their losses.
                for bucket_id in xrange(len(_buckets)):
                    encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                            dev_set, bucket_id, True)
                    _, eval_losses, _ = model.step(sess, encoder_inputs, decoder_inputs,  
                                                 target_weights, bucket_id, True)
                    eval_loss = np.mean(eval_losses)
                    print("  eval: bucket %d loss %.2f" % (bucket_id, eval_loss))
                sys.stdout.flush()


def encode():
    ''' given a set sequences, output their encoded states
    
    Returns:
        - states: list of arrays of states
    '''
#    data = dr.load_data()
#    global feature_size
#    feature_size = len(data[0][0])
    data_set,_,_ = get_data(1.0) 
#    print(data_set)
    print("# of samples: ",len(data_set[0]))

    with tf.Session() as sess:
        # Create model and load parameters.
        model = create_model(sess, False)

        encoded_states = []
        bucket_id = 0 
        # Get encoded states
        encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                    data_set, bucket_id, get_all=True)
 #       print(encoder_inputs)
        states,_,_ = model.step(sess, encoder_inputs, decoder_inputs,
                                         target_weights, bucket_id, True)
        print("\nEncoded states:")
        print(states)
        print(np.shape(states))

    return encoded_states

def get_data(train_portion=0.7):
    ''' put the protein data into bucketes and split into train, dev, test sets
        
        Args:
            train_portion(default=0.7): the ratio of training data for splitting

        Returns:
            train_set, dev_set, test_set: data sets paired and put in buckets
    '''
    print("Reading data...")
    raw_data = dr.load_data(data_para)
    print(np.array(raw_data).shape)
    global feature_size
    feature_size = len(raw_data[0][0])
    pair_data = []
    for i in xrange(len(raw_data)):
        pair = (raw_data[i],raw_data[i])
        pair_data.append(pair)

    train_data, test_data =dr.split_train_test(pair_data,train_portion)
    train_set = (train_data,) # only one bucket
    test_set = (test_data,)
    dev_set = (test_data,) # for simplicity
#    print(np.array(train_set).shape)
    
    return train_set,dev_set,test_set

def self_test():
    """Test the translation model."""
    with tf.Session() as sess:
        print("Self-test for neural translation model.")
        # args: (feature_size, buckets, hidden_size,
        #       num_layers, max_gradient_norm, batch_size, learning_rate,
        #       learning_rate_decay_factor, use_lstm=False,
        #       num_samples=512, forward_only=False):
        model = seq2seq_model.Seq2SeqModel(2, [(3, 3)], 10, 2,
                                           5.0, 5, 0.5, 0.99)
        print("model created")
        sess.run(tf.initialize_all_variables())
        print("model initialized")
        

        # Fake data set for both the (3, 3) and (6, 6) bucket.
        data_set =([([[1.0,2.0],[1.3,2.4],[1.0,3.3]],[[1.0,2.0],[1.3,2.4],[1.0,3.3]]),
                     ([[3,2],[4,6],[2,4]],[[3,2],[4,6],[2,4]]),
                     ([[5,4],[6,7],[1,3]],[[5,4],[6,7],[1,3]])],)

        data_set1 = ([([[5.0,0],[-5,0],[0,5]],[[5,0],[-5,0],[0,5]])],)

        for i in xrange(10):  # Train the fake model for 5 steps.
            print("\nTraining iteration %d" % i)
#            bucket_id = random.choice([0, 1])
            bucket_id = 0
#            print(data_set[0])
            encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                    data_set, bucket_id, True)
            print("get batches:")
#            print(encoder_inputs)
#            print(decoder_inputs)

            states,losses,grad_norm =  model.step(sess, encoder_inputs, decoder_inputs, target_weights,
                                 bucket_id, False)
            print("states:")
            print(states)
 
            print("gradient norm = ",grad_norm)
            print("losses = ",losses)

        # See the reconstruction
        print("\nFinal reconstruction of batches:")
        _,losses,outputs = model.step(sess, encoder_inputs, decoder_inputs, target_weights,
                                      bucket_id, True)
        print("targets:")
        print(decoder_inputs)
        print("outputs:")
        print(outputs)
        print("losses: ",losses)
        print("average loss: ",np.mean(losses))

def main(_):
    train()
#    encode()
#    self_test()

if __name__ == "__main__":
    tf.app.run()
