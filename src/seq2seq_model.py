"""
Sequence-to-sequence model for learning frame features.
Adapted from Tensorflow code:
https://github.com/tensorflow/tensorflow/blob/master/tensorflow/models/rnn/translate/seq2seq_model.py
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random

import numpy as np
from six.moves import xrange    # pylint: disable=redefined-builtin
import tensorflow as tf

from tensorflow.models.rnn import rnn_cell
from tensorflow.models.rnn import seq2seq
from tensorflow.python.framework import ops
from tensorflow.python.ops import variable_scope as vs

import data_utils


class Seq2SeqModel(object):
    """Sequence-to-sequence model with attention and for multiple buckets.

    This class implements a multi-layer recurrent neural network as encoder,
    and an attention-based decoder. This is the same as the model described in
    this paper: http://arxiv.org/abs/1412.7449 - please look there for details,
    or into the seq2seq library for complete model implementation.
    This class also allows to use GRU cells in addition to LSTM cells, and
    sampled softmax to handle large output vocabulary size. A single-layer
    version of this model, but with bi-directional encoder, was presented in
        http://arxiv.org/abs/1409.0473
    and sampled softmax is described in Section 3 of the following paper.
        http://arxiv.org/pdf/1412.2007v2.pdf
    """

    def __init__(self, feature_size, buckets, size,
                             num_layers, max_gradient_norm, batch_size, learning_rate,
                             learning_rate_decay_factor, use_lstm=False,
                             forward_only=False):
        """Create the model.

        Args:
            feature_size: size of the raw data feature.
            buckets: a list of pairs (I, O), where I specifies maximum input length
                that will be processed in that bucket, and O specifies maximum output
                length. Training instances that have inputs longer than I or outputs
                longer than O will be pushed to the next bucket and padded accordingly.
                We assume that the list is sorted, e.g., [(2, 4), (8, 16)].
            size: number of units in each layer of the model.
            num_layers: number of layers in the model.
            max_gradient_norm: gradients will be clipped to maximally this norm.
            batch_size: the size of the batches used during training;
                the model construction is independent of batch_size, so it can be
                changed after initialization if this is convenient, e.g., for decoding.
            learning_rate: learning rate to start with.
            learning_rate_decay_factor: decay learning rate by this much when needed.
            use_lstm: if true, we use LSTM cells instead of GRU cells.
            forward_only: if set, we do not construct the backward pass in the model.
        """
        self.feature_size = feature_size
        self.buckets = buckets
        self.batch_size = batch_size
        self.learning_rate = tf.Variable(float(learning_rate), trainable=False)
        self.learning_rate_decay_op = self.learning_rate.assign(
                self.learning_rate * learning_rate_decay_factor)
        self.global_step = tf.Variable(0, trainable=False)

        # Loss function - square loss
        def square_loss(inputs, targets):
            with tf.device("/cpu:0"):
                l2 = np.sum((inputs-targets)**2)
                return l2
        square_loss_function = square_loss

#        # If we use sampled softmax, we need an output projection.
#        output_projection = None
#        softmax_loss_function = None
#        # Sampled softmax only makes sense if we sample less than vocabulary size.
#        if num_samples > 0 and num_samples < self.target_vocab_size:
#            with tf.device("/cpu:0"):
#                w = tf.get_variable("proj_w", [size, self.target_vocab_size])
#                w_t = tf.transpose(w)
#                b = tf.get_variable("proj_b", [self.target_vocab_size])
#            output_projection = (w, b)
#
#
#            def sampled_loss(inputs, labels):
#                with tf.device("/cpu:0"):
#                    labels = tf.reshape(labels, [-1, 1])
#                    return tf.nn.sampled_softmax_loss(w_t, b, inputs, labels, num_samples,
#                                                      self.target_vocab_size)
#            softmax_loss_function = sampled_loss
#
        
        # Create the internal multi-layer cell for our RNN.
        single_cell = rnn_cell.GRUCell(size)
        if use_lstm:
            single_cell = rnn_cell.BasicLSTMCell(size)
        cell = single_cell
        if num_layers > 1:
            cell = rnn_cell.MultiRNNCell([single_cell] * num_layers)

        # The seq2seq function: we use embedding for the input and attention.
#        def seq2seq_f(encoder_inputs, decoder_inputs, do_decode):
#            return seq2seq.embedding_attention_seq2seq(
#                    encoder_inputs, decoder_inputs, cell, source_vocab_size,
#                    target_vocab_size, output_projection=output_projection,
#                    feed_previous=do_decode)
#        
        def seq2seq_f(encoder_inputs, decoder_inputs):
            return seq2seq.basic_rnn_seq2seq(
                   encoder_inputs, decoder_inputs, cell)
        
        # Feeds for inputs.
        self.encoder_inputs = []
        self.decoder_inputs = []
        self.target_weights = []
        for i in xrange(buckets[-1][0]):    # Last bucket is the biggest one.
            self.encoder_inputs.append(tf.placeholder(tf.float32, shape=[None,self.feature_size],
                                                    name="encoder{0}".format(i)))

        # changed from Tensorflow: do not increase decoder size by 1
        for i in xrange(buckets[-1][1] + 1):
#        for i in xrange(buckets[-1][1]):
            self.decoder_inputs.append(tf.placeholder(tf.float32, shape=[None,self.feature_size],
                                                    name="decoder{0}".format(i)))
            self.target_weights.append(tf.placeholder(tf.float32, shape=[None],
                                                     name="weight{0}".format(i)))

        # Our targets are decoder inputs shifted by one.
        targets = [self.decoder_inputs[i + 1]
                             for i in xrange(len(self.decoder_inputs) - 1)]

        # Training outputs and losses.
        self.outputs, self.losses = model_with_buckets(
                    self.encoder_inputs, self.decoder_inputs, targets,
                    self.target_weights, buckets, self.feature_size,
                    lambda x, y: seq2seq_f(x, y),
                    loss_function=square_loss_function)


#        if forward_only:
#            self.outputs, self.losses = seq2seq.model_with_buckets(
#                    self.encoder_inputs, self.decoder_inputs, targets,
#                    self.target_weights, buckets, self.target_vocab_size,
#                    lambda x, y: seq2seq_f(x, y, True),
#                    softmax_loss_function=softmax_loss_function)
#            # If we use output projection, we need to project outputs for decoding.
#            if output_projection is not None:
#                for b in xrange(len(buckets)):
#                    self.outputs[b] = [tf.nn.xw_plus_b(output, output_projection[0],
#                                                       output_projection[1])
#                                       for output in self.outputs[b]]
#        else:
#            self.outputs, self.losses = seq2seq.model_with_buckets(
#                    self.encoder_inputs, self.decoder_inputs, targets,
#                    self.target_weights, buckets, self.target_vocab_size,
#                    lambda x, y: seq2seq_f(x, y, False),
#                    softmax_loss_function=softmax_loss_function)
#
        # Gradients and SGD update operation for training the model.
        params = tf.trainable_variables()
        if not forward_only:
            self.gradient_norms = []
            self.updates = []
            opt = tf.train.GradientDescentOptimizer(self.learning_rate)
            for b in xrange(len(buckets)):
                gradients = tf.gradients(self.losses[b], params)
                clipped_gradients, norm = tf.clip_by_global_norm(gradients,
                                                                 max_gradient_norm)
                self.gradient_norms.append(norm)
                self.updates.append(opt.apply_gradients(
                        zip(clipped_gradients, params), global_step=self.global_step))

        self.saver = tf.train.Saver(tf.all_variables())


    def step(self, session, encoder_inputs, decoder_inputs, target_weights,
                     bucket_id, forward_only):
        """Run a step of the model feeding the given inputs.

        Args:
            session: tensorflow session to use.
            encoder_inputs: list of numpy int vectors to feed as encoder inputs.
            decoder_inputs: list of numpy int vectors to feed as decoder inputs.
            target_weights: list of numpy float vectors to feed as target weights.
            bucket_id: which bucket of the model to use.
            forward_only: whether to do the backward step or only forward.

        Returns:
            A triple consisting of gradient norm (or None if we did not do backward),
            average perplexity, and the outputs.

        Raises:
            ValueError: if length of enconder_inputs, decoder_inputs, or
                target_weights disagrees with bucket size for the specified bucket_id.
        """
        # Check if the sizes match.
        encoder_size, decoder_size = self.buckets[bucket_id]
        if len(encoder_inputs) != encoder_size:
            raise ValueError("Encoder length must be equal to the one in bucket,"
                                             " %d != %d." % (len(encoder_inputs), encoder_size))
        if len(decoder_inputs) != decoder_size:
            raise ValueError("Decoder length must be equal to the one in bucket,"
                                             " %d != %d." % (len(decoder_inputs), decoder_size))
        if len(target_weights) != decoder_size:
            raise ValueError("Weights length must be equal to the one in bucket,"
                                             " %d != %d." % (len(target_weights), decoder_size))

        # Input feed: encoder inputs, decoder inputs, target_weights, as provided.
        input_feed = {}
        for l in xrange(encoder_size):
            input_feed[self.encoder_inputs[l].name] = encoder_inputs[l]
        for l in xrange(decoder_size):
            input_feed[self.decoder_inputs[l].name] = decoder_inputs[l]
            input_feed[self.target_weights[l].name] = target_weights[l]
#        print(input_feed.keys())
#        print(input_feed['encoder0:0'])

        # Since our targets are decoder inputs shifted by one, we need one more.
#        last_target = self.decoder_inputs[decoder_size].name
#        input_feed[last_target] = np.zeros([self.batch_size], dtype=np.int32)

        # Output feed: depends on whether we do a backward step or not.
        if not forward_only:
            output_feed = [self.updates[bucket_id],  # Update Op that does SGD.
                           self.gradient_norms[bucket_id],    # Gradient norm.
                           self.losses[bucket_id]]    # Loss for this batch.
        else:
            output_feed = [self.losses[bucket_id]]  # Loss for this batch.
            for l in xrange(decoder_size):  # Output logits.
                output_feed.append(self.outputs[bucket_id][l])

        outputs = session.run(output_feed, input_feed)
        if not forward_only:
            return outputs[1], outputs[2], None  # Gradient norm, loss, no outputs.
        else:
            return None, outputs[0], outputs[1:]    # No gradient norm, loss, outputs.


    def get_batch(self, data, bucket_id):
        """Get a random batch of data from the specified bucket, prepare for step.

        To feed data in step(..) it must be a list of batch-major vectors, while
        data here contains single length-major cases. So the main logic of this
        function is to re-index data cases to be in the proper format for feeding.

        Args:
            data: a tuple of size len(self.buckets) in which each element contains
                lists of pairs of input and output data that we use to create a batch.
            bucket_id: integer, which bucket to get the batch for.

        Returns:
            The triple (encoder_inputs, decoder_inputs, target_weights) for
            the constructed batch that has the proper format to call step(...) later.
            shape: encoder_input[seq_length,batch_size,feature_size]
        """
        encoder_size, decoder_size = self.buckets[bucket_id]
        encoder_inputs, decoder_inputs = [], []

        # Get a random batch of encoder and decoder inputs from data,
        for _ in xrange(self.batch_size):
            encoder_input, decoder_input = random.choice(data[bucket_id])
            encoder_inputs.append(encoder_input)
            decoder_inputs.append(decoder_input)

        # Now we create batch-major vectors from the data selected above.
        # Different from Tensorflow code: here we assume all sequences are
        # of the same length and we don't do padding
        batch_encoder_inputs, batch_decoder_inputs, batch_weights = [], [], []
#        print(self.batch_size)
#        print(len(encoder_inputs))
#        print(encoder_size)
#        print(len(encoder_inputs[0]))
#        print(encoder_inputs)
#
        # Batch encoder inputs are just re-indexed encoder_inputs.
        for length_idx in xrange(encoder_size):
            batch_encoder_inputs.append(
                    np.array([encoder_inputs[batch_idx][length_idx]
                                        for batch_idx in xrange(self.batch_size)]))

        # Batch decoder inputs are re-indexed decoder_inputs, we create weights.
        for length_idx in xrange(decoder_size):
            batch_decoder_inputs.append(
                    np.array([decoder_inputs[batch_idx][length_idx]
                                        for batch_idx in xrange(self.batch_size)]))

            batch_weight = np.ones(self.batch_size, dtype=np.float32)
#            for batch_idx in xrange(self.batch_size):
#                # We set weight to 0 if the corresponding target is a PAD symbol.
#                # The corresponding target is decoder_input shifted by 1 forward.
#                if length_idx < decoder_size - 1:
#                    target = decoder_inputs[batch_idx][length_idx + 1]
#                if length_idx == decoder_size - 1 or target == data_utils.PAD_ID:
#                    batch_weight[batch_idx] = 0.0
            batch_weights.append(batch_weight)
        return batch_encoder_inputs, batch_decoder_inputs, batch_weights


def model_with_buckets(encoder_inputs, decoder_inputs, targets, weights,
                        buckets, feature_size, seq2seq,
                        loss_function=None, name=None):
    """ 
    A function similar to seq2seq.model_with_buckets,but using square loss
        instead of softmax 

    Create a sequence-to-sequence model with support for bucketing.

    The seq2seq argument is a function that defines a sequence-to-sequence model,
    e.g., seq2seq = lambda x, y: basic_rnn_seq2seq(x, y, rnn_cell.GRUCell(24))

    Args:
    encoder_inputs: a list of Tensors to feed the encoder; first seq2seq input.
    decoder_inputs: a list of Tensors to feed the decoder; second seq2seq input.
    targets: a list of 2D batch-sized*feature_size float32 Tensors (desired output sequence).
    weights: list of 2D batch-sized*feature_size float32 Tensors to weight the targets.
    buckets: a list of pairs of (input size, output size) for each bucket.
    feature_size: integer, dimension of output.
    seq2seq: a sequence-to-sequence model function; it takes 2 input that
      agree with encoder_inputs and decoder_inputs, and returns a pair
      consisting of outputs and states (as, e.g., basic_rnn_seq2seq).
    loss_function: function (inputs-batch, labels-batch) -> loss-batch
      to be used instead of the standard softmax (the default if this is None).
    name: optional name for this operation, defaults to "model_with_buckets".

    Returns:
    outputs: The outputs for each bucket. Its j'th element consists of a list
      of 2D Tensors of shape [batch_size x feature_size] (j'th outputs).
    losses: List of scalar Tensors, representing losses for each bucket.
    Raises:
    ValueError: if length of encoder_inputsut, targets, or weights is smaller
      than the largest (last) bucket.
    """
    if len(encoder_inputs) < buckets[-1][0]:
        raise ValueError("Length of encoder_inputs (%d) must be at least that of la"
                     "st bucket (%d)." % (len(encoder_inputs), buckets[-1][0]))
    if len(targets) < buckets[-1][1]:
        raise ValueError("Length of targets (%d) must be at least that of last"
                     "bucket (%d)." % (len(targets), buckets[-1][1]))
    if len(weights) < buckets[-1][1]:
        raise ValueError("Length of weights (%d) must be at least that of last"
                     "bucket (%d)." % (len(weights), buckets[-1][1]))

    print(np.shape(encoder_inputs))
    print(encoder_inputs)
    all_inputs = encoder_inputs + decoder_inputs + targets + weights
    losses = []
    outputs = []
    with ops.op_scope(all_inputs, name, "model_with_buckets"):
        for j in xrange(len(buckets)):
            with vs.variable_scope(vs.get_variable_scope(),
                             reuse=True if j > 0 else None):
                bucket_encoder_inputs = [encoder_inputs[i]
                                     for i in xrange(buckets[j][0])]
                bucket_decoder_inputs = [decoder_inputs[i]
                                     for i in xrange(buckets[j][1])]
                bucket_outputs, _ = seq2seq(bucket_encoder_inputs,
                                        bucket_decoder_inputs)
                outputs.append(bucket_outputs)

                bucket_targets = [targets[i] for i in xrange(buckets[j][1])]
                bucket_weights = [weights[i] for i in xrange(buckets[j][1])]
                loss = loss_function(bucket_weights,bucket_targets)
                losses.append(loss)
    #           losses.append(sequence_loss(
    #            outputs[-1], bucket_targets, bucket_weights, num_decoder_symbols,
    #            softmax_loss_function=softmax_loss_function))
    #
    return outputs, losses











