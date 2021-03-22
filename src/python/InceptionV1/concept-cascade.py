import os
import sys
import cv2
import json
import tqdm
import numpy as np
from time import time
from numpy.lib.stride_tricks import as_strided

import tensorflow as tf
import lucid.optvis.render as render
import lucid.modelzoo.vision_models as models
from keras.applications.inception_v3 import preprocess_input


def main():

    sys.path.insert(0, '..')
    from InceptionV1 import InceptionV1

    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "1"

    model_wrapper = InceptionV1()
    model_wrapper.load_model()

    input_dir_path = '../../../data/InceptionV1/bucket/bucket-all-10-20'
    groups = {}
    for blk in model_wrapper.BLKS:
        file_path = '{}/buckets-{}.json'.format(input_dir_path, blk)
        with open(file_path, 'r') as f:
            groups[blk] = json.load(f)

    with tf.Graph().as_default():
        
        # Model render
        t_input = tf.placeholder(tf.float32, [None, 224, 224, 3])
        T = render.import_model(model_wrapper.model, t_input, t_input)
        t_acts = T('mixed3a')
        
        # Weight tensors
        tensors = {}
        for layer in model_wrapper.LAYERS:
            
            t_w_1x1, t_w_3x3_b, t_w_3x3, t_w_5x5_b, t_w_5x5, t_w_p_r = \
                model_wrapper.get_t_weights_layer_gap(layer)
            
            tensors[layer] = [t_w_1x1, t_w_3x3_b, t_w_3x3, t_w_5x5_b, t_w_5x5, t_w_p_r]
        
        # Weight values
        weights = {}
        with tf.Session() as sess:
            for layer in model_wrapper.LAYERS:
                weights[layer] = sess.run(tensors[layer])

    cascade = {}
    for blk_i, blk in enumerate(model_wrapper.BLKS):
        
        # Size of activation map of the block
        layer = blk.split('_')[0]
        H, W = model_wrapper.ACT_MAP_SIZE[layer]
        C = model_wrapper.get_num_neurons(blk)
        
        # Cascade
        print(blk)
        cascade[blk] = {}
        with tqdm.tqdm(total=C) as pbar:
            
            for n in range(C):

                cascade[blk][n] = {'neuron': {}, 'connection': {}}

                act_maps = {}
                act_maps[blk] = np.zeros((1, H, W, C))
                act_maps[blk][:, :, :, n] = 1

                for later_blk in model_wrapper.BLKS[blk_i + 1:]:
                    
                    # Ignore unnecessary cases
                    if '3x3' in blk:
                        layer = blk.split('_')[0]
                        if later_blk == '{}_{}'.format(layer, '5x5'):
                            continue
                        
                    if '5x5' in blk:
                        layer = blk.split('_')[0]
                        if later_blk == '{}_{}'.format(layer, '3x3'):
                            continue
                            
                    cascade[blk][n][later_blk] = {}
                    init_act_maps(model_wrapper, act_maps, later_blk)

                    # Concat block
                    if '_' not in later_blk:
                        for concat in range(0, 4):
                            act_maps = conv2d_one_concat(
                                model_wrapper, 
                                later_blk, 
                                concat, 
                                weights, 
                                act_maps, 
                                cascade[blk][n]['neuron']
                            )    

                    elif '3x3' in later_blk:
                        act_maps = conv2d_3x3(model_wrapper, later_blk, weights, act_maps, cascade[blk][n]['neuron'])

                    elif '5x5' in later_blk:
                        act_maps = conv2d_5x5(model_wrapper, later_blk, weights, act_maps, cascade[blk][n]['neuron'])

                    num_neurons = act_maps[later_blk].shape[-1]
                    act_max = np.max(act_maps[later_blk][0, :, :, :], axis=(0, 1))
                    top_3 = np.argsort(-act_max)[:3]
                    top_3_act = act_max[top_3]
                    cascade[blk][n]['neuron'][later_blk] = {
                        '{}-{}'.format(later_blk, top_n): top_v
                        for top_n, top_v in zip(top_3, top_3_act)
                    }

                pbar.update(1)

    print(cascade)
    with open('../../../data/InceptionV1/cascade/cascade-neuron-top3.json', 'r') as f:
        json.dump(cascade, f)


def get_start_neuron(model_wrapper, blk, concat):
    
    concat_blk = '{}_concat{}'.format(blk, concat)
    start_neuron = model_wrapper.CONCAT_OFFSET[concat_blk]
    return start_neuron


def get_end_neuron(model_wrapper, blk, concat):
    
    if concat == 3:
        end_neuron = model_wrapper.LAYER_SIZE[blk]
    else:
        next_concat_blk = \
            '{}_concat{}'.format(blk, concat + 1)
        end_neuron = model_wrapper.CONCAT_OFFSET[next_concat_blk]
    return end_neuron


def get_prev_layer(model_wrapper, blk):
    
    curr_layer = blk.split('_')[0]
    return model_wrapper.get_prev_layer(curr_layer)


def init_act_maps(model_wrapper, act_maps, blk):
    
    layer = blk.split('_')[0]
    H, W = model_wrapper.ACT_MAP_SIZE[layer]
    C = model_wrapper.get_num_neurons(blk)
    act_maps[blk] = np.zeros((1, H, W, C))
    

def get_prev_blk(model_wrapper, blk, concat=0):
    
    if (concat == 0) or (concat == 3):
        layer = blk.split('_')[0]
        return model_wrapper.get_prev_layer(layer)
    elif concat == 1:
        return '{}_3x3'.format(blk)
    elif concat == 2:
        return '{}_5x5'.format(blk)
    else:
        print('Err: concat=%d is given' % (concat))
    
    
def get_prev_act_map_of_concat(model_wrapper, blk, concat, act_maps):
    
    prev_blk = get_prev_blk(model_wrapper, blk, concat)
    if prev_blk not in act_maps:
        return None
    return act_maps[prev_blk]


def get_weight_of_concat(weights, blk, concat):
    
    # Weight
    # t_w_1x1, t_w_3x3_b, t_w_3x3, t_w_5x5_b, t_w_5x5, t_w_p_r = \
    #    tensors[later_blk_layer]
    if concat == 0:   
        weight = weights[blk][0]
    elif concat == 1:
        weight = weights[blk][2]
    elif concat == 2:
        weight = weights[blk][4]
    elif concat == 3:
        weight = weights[blk][5]
    else:
        print('Err: concat=%d is given' % (concat))
       
    return weight


def get_weight_of_3x3(weights, blk):
    
    layer = blk.split('_')[0]
    return weights[layer][1]


def get_weight_of_5x5(weights, blk):
    
    layer = blk.split('_')[0]
    return weights[layer][3]


def need_max_pool(blk, concat=0):
    
    if (concat == 1) or (concat == 2):
        return False
    
    if 'mixed4a' in blk:
        return True
    
    if 'mixed5a' in blk:
        return True
    
    return False


def pool2d(A, kernel_size, stride, padding):
    
    # Padding
    A = np.pad(A, padding, mode='constant')

    # Window view of A
    output_shape = ((A.shape[0] - kernel_size) // stride + 1,
                    (A.shape[1] - kernel_size) // stride + 1)
    kernel_size = (kernel_size, kernel_size)
    A_w = as_strided(A, shape = output_shape + kernel_size, 
                        strides = (stride * A.strides[0],
                                   stride * A.strides[1]) + A.strides)
    A_w = A_w.reshape(-1, *kernel_size)

    return A_w.max(axis=(1,2)).reshape(output_shape)
    
    
def conv2d_one_concat(model_wrapper, blk, concat, weights, act_maps, cascade_neuron):
    
    # Neuron range
    start_neuron = get_start_neuron(model_wrapper, blk, concat)
    end_neuron = get_end_neuron(model_wrapper, blk, concat)
                        
    # Previous block's activation map
    prev_act_map = get_prev_act_map_of_concat(model_wrapper, blk, concat, act_maps)
    if prev_act_map is None:
        return act_maps
                    
    # Weight
    weight = get_weight_of_concat(weights, blk, concat)
    
    # Cascade value to each next neuron
    num_prev_neurons = prev_act_map.shape[-1]
    prev_blk = get_prev_blk(model_wrapper, blk)
    for nn in range(start_neuron, end_neuron):
        for pn in range(num_prev_neurons):
            
            if prev_blk in cascade_neuron:
                if pn not in cascade_neuron[prev_blk]:
                    continue
            
            w = weight[:, :, pn, nn - start_neuron]
            p_act = prev_act_map[0, :, :, pn]
            if need_max_pool(blk, concat):
                p_act = pool2d(p_act, 2, 2, 0)
            v = cv2.filter2D(p_act, -1, w)
            v = v * (v > 0)
            act_maps[blk][0, :, :, nn - start_neuron] += v
            
    return act_maps
                
            
            
def conv2d_3x3(model_wrapper, blk, weights, act_maps, cascade_neuron):
    
    # Previous block's activation map
    prev_layer = get_prev_layer(model_wrapper, blk)
    prev_act_map = act_maps[prev_layer]
    
    # Weight
    weight = get_weight_of_3x3(weights, blk)
    
    # Cascade value to each next neuron
    num_prev_neurons = prev_act_map.shape[-1]
    num_curr_neurons = weight.shape[-1]
    prev_blk = get_prev_blk(model_wrapper, blk)
    for nn in range(num_curr_neurons):
        for pn in range(num_prev_neurons):
            
            if prev_blk in cascade_neuron:
                if pn not in cascade_neuron[prev_blk]:
                    continue
                
            w = weight[:, :, pn, nn]
            p_act = prev_act_map[0, :, :, pn]
            if need_max_pool(blk):
                p_act = pool2d(p_act, 2, 2, 0)
            v = cv2.filter2D(p_act, -1, w)
            act_maps[blk][0, :, :, nn] += v
            
    return act_maps
            

def conv2d_5x5(model_wrapper, blk, weights, act_maps, cascade_neuron):
    
    # Previous block's activation map
    prev_layer = get_prev_layer(model_wrapper, blk)
    prev_act_map = act_maps[prev_layer]
    
    # Weight
    weight = get_weight_of_5x5(weights, blk)
    
    # Cascade value to each next neuron
    num_prev_neurons = prev_act_map.shape[-1]
    num_curr_neurons = weight.shape[-1]
    prev_blk = get_prev_blk(model_wrapper, blk)
    
    for nn in range(num_curr_neurons):
        for pn in range(num_prev_neurons):
            
            if prev_blk in cascade_neuron:
                if pn not in cascade_neuron[prev_blk]:
                    continue
                
            w = weight[:, :, pn, nn]
            p_act = prev_act_map[0, :, :, pn]
            if need_max_pool(blk):
                p_act = pool2d(p_act, 2, 2, 0)
            v = cv2.filter2D(p_act, -1, w)
            v = v * (v > 0)
            act_maps[blk][0, :, :, nn] += v
    
    return act_maps
            
if __name__ == '__main__':
    main()
