import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import json

import tensorflow as tf

import lucid.modelzoo.vision_models as models
from lucid.misc.io import show
import lucid.optvis.objectives as objectives
import lucid.optvis.param as param
import lucid.optvis.render as render
import lucid.optvis.transform as transform
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input
import tqdm

import time

def main():
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "4"
    blk_size = {
        'mixed3a': 256,
        'mixed3b': 480,
        'mixed3b_3x3': 128,
        'mixed3b_5x5': 32,
        'mixed4a': 508,
        'mixed4a_3x3': 96,
        'mixed4a_5x5': 16,
        'mixed4b': 512,
        'mixed4b_3x3': 112,
        'mixed4b_5x5': 24,
        'mixed4c': 512,
        'mixed4c_3x3': 128,
        'mixed4c_5x5': 24,
        'mixed4d': 528,
        'mixed4d_3x3': 144,
        'mixed4d_5x5': 32,
        'mixed4e': 832,
        'mixed4e_3x3': 160,
        'mixed4e_5x5': 32,
        'mixed5a': 832,
        'mixed5a_3x3': 160,
        'mixed5a_5x5': 48,
        'mixed5b': 1024,
        'mixed5b_3x3': 192,
        'mixed5b_5x5': 48
    }
    
    googlenet = models.InceptionV1()
    googlenet.load_graphdef()
    
    num_class = 1000
    prob_mass_threshold = 0.03
    batch = 500
    
    for blk in blk_size:
        print(blk)
        if ('3x3' not in blk) and ('5x5' not in blk):
            continue
        gen_A_mat(blk, prob_mass_threshold, num_class, blk_size, batch, googlenet)
    
    
def gen_A_mat(blk, prob_mass_threshold, num_class, blk_size, batch, googlenet):
    
    filenames = glob.glob('../../../data/tfrec/*')
    
    A = np.zeros((num_class, blk_size[blk]), dtype=int)
    
    with tf.Graph().as_default():
        
        dataset = tf.data.TFRecordDataset(filenames)
        dataset = dataset.map(_parse_function)
        dataset = dataset.map(lambda img, lab, syn: (preprocess_input(img), lab, syn))
        dataset = dataset.batch(batch)

        iterator = dataset.make_one_shot_iterator()
        t_preprocessed_images, t_labels, t_synsets = iterator.get_next()

        T = render.import_model(googlenet, t_preprocessed_images, None)
        T('mixed3a')
        tensors = tf.math.reduce_max(get_t_blk(blk), axis=[1, 2])

        progress_counter = 0
        with tf.Session() as sess:
            start = time.time()

            try:
                with tqdm.tqdm(total=1281167, unit='imgs') as pbar:
                    while(True):
                        progress_counter += 1
                        imgs_acts_max, labels, synsets = sess.run([tensors, t_labels, t_synsets])

                        # no sess.run after this
                        # python code here on out
                        for i in range(imgs_acts_max.shape[0]):

                            top_channels = []
                            working_acts_max = imgs_acts_max[i] / np.sum(imgs_acts_max[i])
                            prob_mass = 0
                            sorted_working_acts_max, sorted_inds = (list(t) for t in zip(*sorted(zip(working_acts_max, list(range(working_acts_max.shape[0]))), reverse=True)))
                            k = 0
                            while prob_mass < prob_mass_threshold:
                                top_channels.append(sorted_inds[k])
                                prob_mass += sorted_working_acts_max[k]
                                k += 1
                            for top_channel in top_channels:
                                A[labels[i] - 1][top_channel] += 1

                        pbar.update(len(labels))

            except tf.errors.OutOfRangeError:
                pass

            end = time.time()
            print(end - start)
            print(progress_counter)
            print(progress_counter*batch)

    output_path = '../../../data/InceptionV1/summit/A-mat-nc/A-{}-{}.csv'.format(prob_mass_threshold, blk)
    np.savetxt(output_path, A, delimiter=',', fmt='%i')
    
    
def _parse_function(example_proto, image_size=224):
    def _bytes_feature(value):
        return tf.train.Feature(
            bytes_list=tf.train.BytesList(value=[value]))

    def _int64_feature(value):
        return tf.train.Feature(
            int64_list=tf.train.Int64List(value=[value]))
    
    feature_set = {
        'image/encoded': tf.FixedLenFeature([], tf.string),
        'image/class/label': tf.FixedLenFeature([], tf.int64),
        'image/class/synset': tf.FixedLenFeature([], tf.string)
    }
  
    parsed_features = tf.parse_single_example(example_proto, feature_set)
    label = parsed_features['image/class/label']
    synset = parsed_features['image/class/synset']
    
    image = parsed_features['image/encoded']
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize_images(image, tf.constant([image_size, image_size]))
    
    return image, label, synset


def get_t_blk(block):
    '''
    Get block tensor
    * input
        - block: the name of block (e.g., 'mixed3a', 'mixed3b_3x3')
    * output
        - t_block: the tensor of the block
    '''

    # The name of tensor of the given block
    block_name = 'import/%s' % block
    if ('_' in block) and (block[-2:] != '_w'):
        block_name += '_bottleneck'
    block_name += ':0'

    # Get the tensor
    t_block = tf.get_default_graph().get_tensor_by_name(block_name)

    return t_block

if __name__ == '__main__':
    main()