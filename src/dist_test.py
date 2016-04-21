'''
testing script for distributed TF
'''

import tensorflow as tf

# define cluster 
cluster_dict = {"ps": ["localhost:2222"], 
                "worker": ["localhost:3332", "localhost:3333"]}

cluster = tf.train.ClusterSpec(cluster_dict)

# create servers in the cluster
server_ps0 = tf.train.Server(cluster.as_cluster_def(), job_name="ps", task_index=0)
server_w0 = tf.train.Server(cluster.as_cluster_def(), job_name="worker", task_index=0)
server_w1 = tf.train.Server(cluster.as_cluster_def(), job_name="worker", task_index=1)

#device_ps0 = tf.train.replica_device_setter(
 #       worker_device="/job:ps/task:0", cluster=cluster)
device_w0 = tf.train.replica_device_setter(ps_tasks=1,
        worker_device="/job:worker/task:0", cluster=cluster)

#with tf.device(device_ps0):
#with tf.device("/job:ps/task:0"):
#with tf.device("/cpu:0"):

with tf.device(device_w0):
#with tf.device("/job:worker/task:0"):
#with tf.device("/cpu:0"):
    v = tf.Variable(tf.zeros([3]),name="v1")
    c = tf.constant(1.0)
    op = v.assign(tf.add(v,c))

saver = tf.train.Saver()

with tf.Session(server_w0.target) as sess:
    sess.run(tf.initialize_all_variables())
    for _ in range(10):
        sess.run(tf.Print(op,[v,c]))
    saver.save(sess, "/output/model.ckpt")
    print(tf.train.get_checkpoint_state("/output/model.ckpt"))









