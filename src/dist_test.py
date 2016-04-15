'''
testing script for distributed TF
'''

import tensorflow as tf

v = tf.constant([1,2,3,4,5])

cluster_dict = {"ps": ["localhost:2222", "localhost:2223"], 
                "worker": ["localhost:3333", "localhost:2333"]}

server = tf.train.Server.create_local_server()
cluster = tf.train.ClusterSpec(cluster_dict)

server1 = tf.train.Server(cluster.as_cluster_def(), job_name="ps", task_index=0)
server2 = tf.train.Server(cluster.as_cluster_def(), job_name="worker", task_index=1)




