'''
Use rnn to learn features from trajectory data
'''

import tensorflow.python.platform
import rnn
import rnn_cell
from tensorflow.python.ops.rnn_cell import *
from tensorflow.python.ops.rnn import *

class RNNModel(object):
    ''' The gated recurrent unit rnn model '''
    def __init__(self, is_training, config):
        self.batch_size = batch_size = config.batch_size
        self.num_steps = num_steps = config.num_steps
        size = config.hidden_size
        cell = rnn_cell.GRUCell(num_units)

class SmallConfig(object):
    """Small config."""
    init_scale = 0.1
    batch_size = 20
    learning_rate = 1.0
    max_grad_norm = 5
    num_layers = 2
    num_steps = 20
    hidden_size = 200
    max_epoch = 4
    max_max_epoch = 13
    keep_prob = 1.0
    lr_decay = 0.5
    vocab_size = 10000

def main(unused_args):
    config = SmallConfig()
    with tf.Graph().as_default(), tf.Session() as session:
        m = RNNModel(True,config)

if __name__ == "__main__":
   tf.app.run() 
