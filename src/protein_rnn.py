'''
Use rnn to learn features from trajectory data
'''

import tensorflow.python.platform
import tensorflow as tf

import time

import numpy as np

import datareader

from tensorflow.models.rnn import rnn_cell
from tensorflow.models.rnn import rnn
from tensorflow.models.rnn import seq2seq
from tensorflow.python.ops.rnn_cell import *
from tensorflow.python.ops.rnn import *

# tf.flags.DEFINE_string("data_path", None, "data_path")
# FLAGS = tf.flags.FLAGS
# 
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

#        inputs = [tf.squeeze(input_, [1])
#                   for input_ in tf.split(1, num_steps, inputs)]
#        outputs, states = rnn.rnn(
#            cell, inputs, initial_state=self._initial_state)
#        
        outputs = []
        states = []
        state = self._initial_state
        with tf.variable_scope("RNN"):
            for time_step in range(num_steps):
                if time_step > 0: tf.get_variable_scope().reuse_variables()
                (cell_output, state) = cell(inputs[:, time_step, :], state)
                outputs.append(cell_output)
                states.append(state)

       
        output = tf.reshape(tf.concat(1, outputs), [-1, size])
        logits = tf.nn.xw_plus_b(output,
                      tf.get_variable("softmax_w", [size, feature_size]),
                      tf.get_variable("softmax_b", [feature_size]))

        loss = seq2seq.sequence_loss_by_example([logits],
                                    [tf.reshape(self._targets, [-1])],
                                    [tf.ones([batch_size * num_steps])],
                                    feature_size)
        self._cost = cost = tf.reduce_sum(loss) / batch_size
        self._final_state = states[-1]

        if not is_training:
            return

        self._lr = tf.Variable(0.0, trainable=False)
        tvars = tf.trainable_variables()
        grads, _ = tf.clip_by_global_norm(tf.gradients(cost, tvars),
                                              config.max_grad_norm)
        optimizer = tf.train.GradientDescentOptimizer(self.lr)
        self._train_op = optimizer.apply_gradients(zip(grads, tvars))
        
    def assign_lr(self, session, lr_value):
        session.run(tf.assign(self.lr, lr_value))

    @property
    def input_data(self):
        return self._input_data

    @property
    def targets(self):
        return self._targets

    @property
    def initial_state(self):
        return self._initial_state

    @property
    def cost(self):
        return self._cost

    @property
    def final_state(self):
        return self._final_state

    @property
    def lr(self):
        return self._lr

    @property
    def train_op(self):
        return self._train_op


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
#    if not FLAGS.data_path:
#        raise ValueError("Must set --data_path to PTB data directory")
    config = SmallConfig()
    with tf.Graph().as_default(), tf.Session() as session:
        m = RNNModel(True,config)
    print "done"

if __name__ == "__main__":
   tf.app.run() 
