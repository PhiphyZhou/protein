# This file is adapted from the Tensorfile code:
# https://github.com/tensorflow/tensorflow/blob/master/tensorflow/models/rnn/translate/translate.py

"""Binary for training translation models and decoding from them.

Running this program without --decode will download the WMT corpus into
the directory specified as --data_dir and tokenize it in a very basic way,
and then start training a model saving checkpoints to --train_dir.

Running with --decode starts an interactive loop so you can see how
the current checkpoint translates English sentences into French.

See the following papers for more information on neural translation models.
 * http://arxiv.org/abs/1409.3215
 * http://arxiv.org/abs/1409.0473
 * http://arxiv.org/pdf/1412.2007v2.pdf
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

import data_utils
import seq2seq_model
from tensorflow.python.platform import gfile

import datareader as dr

# tf.app.flags.DEFINE_float("learning_rate", 0.5, "Learning rate.")
# tf.app.flags.DEFINE_float("learning_rate_decay_factor", 0.99,
#                                                       "Learning rate decays by this much.")
# tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,
#                                                       "Clip gradients to this norm.")
# tf.app.flags.DEFINE_integer("batch_size", 64,
#                                                           "Batch size to use during training.")
# tf.app.flags.DEFINE_integer("size", 1024, "Size of each model layer.")
# tf.app.flags.DEFINE_integer("num_layers", 3, "Number of layers in the model.")
# tf.app.flags.DEFINE_integer("en_vocab_size", 40000, "English vocabulary size.")
# tf.app.flags.DEFINE_integer("fr_vocab_size", 40000, "French vocabulary size.")
# tf.app.flags.DEFINE_string("data_dir", "/tmp", "Data directory")
# tf.app.flags.DEFINE_string("train_dir", "/tmp", "Training directory.")
# tf.app.flags.DEFINE_integer("max_train_data_size", 0,
#                                                           "Limit on the size of training data (0: no limit).")
# tf.app.flags.DEFINE_integer("steps_per_checkpoint", 200,
#                                                           "How many training steps to do per checkpoint.")
# tf.app.flags.DEFINE_boolean("decode", False,
#                                                           "Set to True for interactive decoding.")
# tf.app.flags.DEFINE_boolean("self_test", False,
#                                                           "Run a self-test if this is set to True.")
# 
# FLAGS = tf.app.flags.FLAGS

# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
_buckets = [(10,10)] # all sequences will be of the same length

feature_size = 0 # to be decided after reading training data
hidden_size = 100
num_layers = 1
max_gradient_norm = 0.1
batch_size = 5
learning_rate = 0.1 
learning_rate_decay_factor = 0.5
train_dir = "/output"
steps_per_checkpoint = 3


def create_model(session, forward_only):
    """Create translation model and initialize or load parameters in session."""
    model = seq2seq_model.Seq2SeqModel(
            feature_size, feature_size, _buckets,
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
    """Train an encoder."""

    # reading data and put them and copy in pairs
    raw_data = dr.load_data()
#    print(np.array(raw_data).shape)
    global feature_size
    feature_size = len(raw_data[0][0])
    pair_data = []
    for i in xrange(len(raw_data)):
        pair = [raw_data[i],raw_data[i]]
        pair_data.append(pair)

    train_data, test_data =dr.split_train_test(pair_data,0.7)
    train_set = [train_data] # only one bucket
#    print(np.array(train_set).shape)
    
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
        while True:
            # Choose a bucket according to data distribution. We pick a random number
            # in [0, 1] and use the corresponding interval in train_buckets_scale.
            random_number_01 = np.random.random_sample()
            bucket_id = min([i for i in xrange(len(train_buckets_scale))
                            if train_buckets_scale[i] > random_number_01])
#            print(bucket_id)

            # Get a batch and make a step.
            start_time = time.time()
            encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                    train_set, bucket_id)
#            print(len(encoder_inputs))
            _, step_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
                                         target_weights, bucket_id, False)
            step_time += (time.time() - start_time) / steps_per_checkpoint
            loss += step_loss / steps_per_checkpoint
            current_step += 1

            # Once in a while, we save checkpoint, print statistics, and run evals.
            if current_step % steps_per_checkpoint == 0:
                # Print statistics for the previous epoch.
                perplexity = math.exp(loss) if loss < 300 else float('inf')
                print ("global step %d learning rate %.4f step-time %.2f perplexity "
                             "%.2f" % (model.global_step.eval(), model.learning_rate.eval(),
                                                 step_time, perplexity))
                # Decrease learning rate if no improvement was seen over last 3 times.
                if len(previous_losses) > 2 and loss > max(previous_losses[-3:]):
                    sess.run(model.learning_rate_decay_op)
                previous_losses.append(loss)
                # Save checkpoint and zero timer and loss.
                checkpoint_path = os.path.join(train_dir, "encoder-decoder.ckpt")
                model.saver.save(sess, checkpoint_path, global_step=model.global_step)
                step_time, loss = 0.0, 0.0
                # Run evals on development set and print their perplexity.
                for bucket_id in xrange(len(_buckets)):
                    encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                            dev_set, bucket_id)
                    _, eval_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,  
                                                 target_weights, bucket_id, True)
                    eval_ppx = math.exp(eval_loss) if eval_loss < 300 else float('inf')
                    print("  eval: bucket %d perplexity %.2f" % (bucket_id, eval_ppx))
                sys.stdout.flush()


def decode():
    with tf.Session() as sess:
        # Create model and load parameters.
        model = create_model(sess, True)
        model.batch_size = 1    # We decode one sentence at a time.

        # Load vocabularies.
        en_vocab_path = os.path.join(FLAGS.data_dir,
                                     "vocab%d.en" % FLAGS.en_vocab_size)
        fr_vocab_path = os.path.join(FLAGS.data_dir,
                                     "vocab%d.fr" % FLAGS.fr_vocab_size)
        en_vocab, _ = data_utils.initialize_vocabulary(en_vocab_path)
        _, rev_fr_vocab = data_utils.initialize_vocabulary(fr_vocab_path)

        # Decode from standard input.
        sys.stdout.write("> ")
        sys.stdout.flush()
        sentence = sys.stdin.readline()
        while sentence:
            # Get token-ids for the input sentence.
            token_ids = data_utils.sentence_to_token_ids(sentence, en_vocab)
            # Which bucket does it belong to?
            bucket_id = min([b for b in xrange(len(_buckets))
                                             if _buckets[b][0] > len(token_ids)])
            # Get a 1-element batch to feed the sentence to the model.
            encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                    {bucket_id: [(token_ids, [])]}, bucket_id)
            # Get output logits for the sentence.
            _, _, output_logits = model.step(sess, encoder_inputs, decoder_inputs,
                                                                             target_weights, bucket_id, True)
            # This is a greedy decoder - outputs are just argmaxes of output_logits.
            outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
            # If there is an EOS symbol in outputs, cut them at that point.
            if data_utils.EOS_ID in outputs:
                outputs = outputs[:outputs.index(data_utils.EOS_ID)]
            # Print out French sentence corresponding to outputs.
            print(" ".join([rev_fr_vocab[output] for output in outputs]))
            print("> ", end="")
            sys.stdout.flush()
            sentence = sys.stdin.readline()


def self_test():
    """Test the translation model."""
    with tf.Session() as sess:
        print("Self-test for neural translation model.")
        # args: (feature_size, buckets, hidden_size,
        #       num_layers, max_gradient_norm, batch_size, learning_rate,
        #       learning_rate_decay_factor, use_lstm=False,
        #       num_samples=512, forward_only=False):
        model = seq2seq_model.Seq2SeqModel(2, [(3, 3)], 3, 1,
                                           5.0, 1, 0.3, 0.99)
        print("model created")
        sess.run(tf.initialize_all_variables())
        print("model initialized")
        

        # Fake data set for both the (3, 3) and (6, 6) bucket.
        data_set =([([[1.0,2.0],[1.3,2.4],[1.0,3.3]],[[1.0,2.0],[1.3,2.4],[1.0,3.3]]),
                     ([[3,2],[4,6],[2,4]],[[3,2],[4,6],[2,4]]),
                     ([[5,4],[6,7],[1,3]],[[5,4],[6,7],[1,3]])],)

        data_set1 = ([([[0.5,0],[-0.5,0],[0,0.5]],[[0.5,0],[-0.5,0],[0,0.5]])],)

        for i in xrange(10):  # Train the fake model for 5 steps.
            print("\nTraining iteration %d" % i)
#            bucket_id = random.choice([0, 1])
            bucket_id = 0
#            print(data_set[0])
            encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                    data_set1, bucket_id)
            print("get batches:")
            print(encoder_inputs)

            grad_norm,losses,_ =  model.step(sess, encoder_inputs, decoder_inputs, target_weights,
                                 bucket_id, False)
            print("gradient norm = ",grad_norm)
            print("losses = ",losses)

        # See the reconstruction
        print("\nFinal reconstruction of batches:")
        _,losses,outputs = model.step(sess, encoder_inputs, decoder_inputs, target_weights,
                                      bucket_id, True)
        print(decoder_inputs)
        print(outputs)
        print("losses: ",losses)

def test_loss():
    ''' test the loss function '''
    with tf.Session() as sess:
        print("test the loss funcion")


def main(_):
#       if FLAGS.self_test:
#           self_test()
#       elif FLAGS.decode:
#           decode()
#       else:
#           train()
#        train()
        self_test()

if __name__ == "__main__":
    tf.app.run()
