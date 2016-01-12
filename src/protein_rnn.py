'''
Use rnn to learn features from trajectory data
'''

import tensorflow.python.platform
import tensorflow as tf

import time

import numpy as np

import rnn
import rnn_cell
import datareader

from tensorflow.python.ops.rnn_cell import *
from tensorflow.python.ops.rnn import *

tf.flags.DEFINE_string("data_path", None, "data_path")
FLAGS = tf.flags.FLAGS

class RNNModel(object):
    ''' The basic rnn model '''
    def __init__(self, is_training, config):
        self.batch_size = batch_size = config.batch_size # size for mini batch training
        self.num_steps = num_steps = config.num_steps # maximum number of training iteration?
        size = config.hidden_size # state size
        feature_size = config.feature_size

        self._input_data = tf.placeholder(tf.int32, [batch_size, num_steps])
        self._targets = tf.placeholder(tf.int32, [batch_size, num_steps])

        basic_cell = rnn_cell.BasicLSTMCell(size)
        if is_training and config.keep_prob < 1: # use dropout 
            basic_cell = rnn_cell.DropoutWrapper(
                basic_cell, output_keep_prob=config.keep_prob)
        cell = rnn_cell.MultiRNNCell(  
                [basic_cell] * config.num_layers) # multiple layers
        self._initial_state = cell.zero_state(batch_size, tf.float32)

        with tf.device("/cpu:0"):
            embedding = tf.get_variable("embedding", [feature_size, size])
            inputs = tf.nn.embedding_lookup(embedding, self._input_data)

        if is_training and config.keep_prob < 1:
            inputs = tf.nn.dropout(inputs, config.keep_prob)

class SmallConfig(object):
    """Small config for training"""
    init_scale = 0.1
    batch_size = 10
    learning_rate = 1.0
    max_grad_norm = 5
    num_layers = 1
    num_steps = 5
    hidden_size = 200
    max_epoch = 4
    max_max_epoch = 13
    keep_prob = 1.0
    lr_decay = 0.5
    feature_size = 10000

def main(unused_args):
    if not FLAGS.data_path:
        raise ValueError("Must set --data_path to PTB data directory")
    config = SmallConfig()
    with tf.Graph().as_default(), tf.Session() as session:
        m = RNNModel(True,config)
    print "done"

if __name__ == "__main__":
   tf.app.run() 
