'''
* Project:
    Neuro-Cartography: Drawing Concept-based Neural Maps to Interpret 
    Deep Neural Networks by Automatically Discovering and Visualizing 
    Cell Assemblies
* File name:
    activation_threshold.py
* Description:
    Find activation threshold for InceptionV1
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Jan 30, 2020
'''


import json
import numpy as np
from time import time
import tensorflow as tf


class ActThreshold:

    '''
    Class for computing activation threshold
    '''
    
    def __init__(self, args, data_path, model_wrapper):
        
        # Hyperparameters
        self.nbins = args.nbins
        self.thr_neuron = args.thr_neuron
        self.thr_connection = args.thr_connection
        
        # Data paths
        self.data_path = data_path
        self.data_path.gen_data_path('activation_threshold')
        
        # Model
        self.model = model_wrapper.model
            
        
    def compute_act_range_of_neurons(self):
        '''
        Compute activation range of resized activation maps
        of all neurons in all layers
        * input
            - N/A
        * output
            - N/A
        '''
        
        # Define a function to compute tensors for activation range
        def compute_act_range_tensors():
            
            t_min_max = []
            blocks = self.model.BLKS
            for blk in blocks:
                t_blk = self.model.get_t_blk(blk)
                t_min = tf.math.reduce_min(t_blk)
                t_max = tf.math.reduce_max(t_blk)
                t_min_max.append([t_min, t_max])
            
            return t_min_max
        
        # Define a function to parse the activation range data
        def parse_act_range_data(data, sess_data, *p_args):
            
            blocks = self.model.BLKS
            for i, blk in enumerate(blocks):
                
                # Add block in the data
                if blk not in data:
                    data[blk] = {'min': 100000, 'max': 0}
                
                # Update block min max value
                blk_min, blk_max = sess_data[i]
                data[blk]['min'] = min(blk_min, data[blk]['min'])
                data[blk]['max'] = max(blk_max, data[blk]['max'])
                
            return data
                
        # Compute activation range of neurons
        data, time_log = self.model.compute_data(
            compute_act_range_tensors, 
            [], 
            parse_act_range_data, 
            []
        )
        
        # Save data into a file
        self.save_act_range(data, 'neuron')
        
        # Save time log into a file
        self.save_time_log(time_log, 'act_range', 'neuron')
        
        
    def compute_act_range_of_connections(self):
        '''
        Compute activation range of resized activation maps
        of all connections across all layers
        * input
            - N/A
        * output
            - N/A
        '''
        
        # Define a function to compute tensors for activation range
        def compute_act_range_tensors():
            
            t_min_max = []
            layers = self.model.LAYERS
            for i, layer in enumerate(layers):
                
                # Ignore mixed3a
                if layer == 'mixed3a':
                    continue
                
                # Previous layer
                prev_layer = layers[i - 1]
                
                # Tensors
                t_input, t_3x3, t_5x5 = \
                    self.model.get_t_blks_layer_gap(prev_layer, layer)
                t_w_1x1, t_w_3x3_b, t_w_3x3, t_w_5x5_b, t_w_5x5, t_w_pr = \
                    self.model.get_t_weights_layer_gap(layer)
                
                # Tensors in order
                blocks = [
                    t_input, t_3x3, t_5x5, t_input, t_input, t_input
                ]
                weights = [
                    t_w_1x1, t_w_3x3, t_w_5x5, t_w_pr, t_w_3x3_b, t_w_5x5_b
                ]
                
                # Add min and max acivation
                for t_b, t_w in zip(blocks, weights):
                    t_conn = tf.nn.depthwise_conv2d(
                        t_b, 
                        t_w, 
                        strides=[1, 1, 1, 1], 
                        padding='SAME'
                    )
                    t_relu = tf.nn.relu(t_conn)
                    t_min = tf.math.reduce_min(t_relu)
                    t_max = tf.math.reduce_max(t_relu)
                    t_min_max.append([t_min, t_max])
            
            return t_min_max
        
        # Define a function to parse the activation range data
        def parse_act_range_data(data, sess_data):
            
            layers = self.model.LAYERS
            appendixes = self.model.BLK_APPENDIXES
            i = 0
            for layer in layers:
                
                # Ignore mixed3a
                if layer == 'mixed3a':
                    continue
                    
                for appendix in appendixes:
                    
                    # Add connection in the data
                    conn = '{}_{}'.format(layer, appendix)
                    if conn not in data:
                        data[conn] = {'min': 100000, 'max': 0}
                        
                    # Update connection activation range
                    conn_min, conn_max = sess_data[i]
                    data[conn]['min'] = min(conn_min, data[conn]['min'])
                    data[conn]['max'] = max(conn_max, data[conn]['max'])
                    i += 1

            return data
                
        # Compute activation range of neurons
        data, time_log = self.model.compute_data(
            compute_act_range_tensors, 
            [], 
            parse_act_range_data, 
            []
        )
        
        # Save data into a file
        self.save_act_range(data, 'connection')
        
        # Save time log into a file
        self.save_time_log(time_log, 'act_range', 'connection')
        
        
    def compute_act_histogram_of_neurons(self):
        '''
        Compute activation histogram of resized activation maps
        of all neurons in all layers
        * input
            - N/A
        * output
            - N/A
        '''
        
        # Load activation range
        act_range = self.load_act_range('neuron')
        
        # Define a function to compute tensors for activation histogram
        def compute_act_hist_tensors():
            
            t_hist = []
            blocks = self.model.BLKS
            for blk in blocks:
                
                # Activation values of resized activation maps
                t_blk = self.model.get_t_blk(blk)
                t_values = tf.reshape(t_blk, [-1])
                
                # Histogram of the activation values
                t_idxs = tf.histogram_fixed_width_bins(
                    t_values, act_range[blk], nbins=self.nbins
                )
                t_hists = tf.unique_with_counts(t_idxs, name=None)
                t_bins = t_hists.y
                t_counts = t_hists.count
                t_hist.append([t_bins, t_counts])
                
            return t_hist

        # Define a function to parsee the activation histogram data
        def parse_act_hist_data(data, sess_data):
            
            blocks = self.model.BLKS
            for i, blk in enumerate(blocks):
    
                # Block histogram
                hist_data = np.zeros(self.nbins)
                hist_bins, hist_cnts = sess_data[i]
                hist_data[hist_bins] = hist_cnts
                
                # Update block activation histogram in the data
                if blk not in data:
                    data[blk] = hist_data
                else:
                    data[blk] += hist_data
            
            return data
        
        # Compute activation range of neurons
        data, time_log = self.model.compute_data(
            compute_act_hist_tensors, 
            [], 
            parse_act_hist_data, 
            []
        )
        
        # Save data into a file
        self.save_act_hist(data, 'neuron')
        
        # Save time log into a file
        self.save_time_log(time_log, 'act_hist', 'neuron')
        
    
    def compute_act_histogram_of_connections(self):
        '''
        Compute activation histogram of resized activation maps
        of all connections across all layers
        * input
            - N/A
        * output
            - N/A
        '''
        
        # Load activation range
        act_range = self.load_act_range('connection')
        
        # Layers
        layers = self.model.LAYERS
        
        # Connecion appendix
        appendixes = self.model.BLK_APPENDIXES
        
        # Define a function to compute tensors for activation histogram
        def compute_act_hist_tensors():
            
            t_hist = []
            for i, layer in enumerate(layers):
                
                # Ignore mixed3a
                if layer == 'mixed3a':
                    continue
                
                # Previous layer
                prev_layer = layers[i - 1]
                
                # Tensors
                t_input, t_3x3, t_5x5 = \
                    self.model.get_t_blks_layer_gap(prev_layer, layer)
                t_w_1x1, t_w_3x3_b, t_w_3x3, t_w_5x5_b, t_w_5x5, t_w_pr = \
                    self.model.get_t_weights_layer_gap(layer)
                
                # Tensors in order
                blocks = [
                    t_input, t_3x3, t_5x5, t_input, t_input, t_input
                ]
                weights = [
                    t_w_1x1, t_w_3x3, t_w_5x5, t_w_pr, t_w_3x3_b, t_w_5x5_b
                ]
                
                # Add min and max acivation
                for t_b, t_w, appendix in zip(blocks, weights, appendixes):
                    
                    # Connection name
                    conn = '{}_{}'.format(layer, appendix)
                    
                    # Activation values
                    t_conn = tf.nn.depthwise_conv2d(
                        t_b, 
                        t_w, 
                        strides=[1, 1, 1, 1], 
                        padding='SAME'
                    )
                    t_relu = tf.nn.relu(t_conn)
                    t_values = tf.reshape(t_relu, [-1])

                    # Histogram of the activation values
                    t_idxs = tf.histogram_fixed_width_bins(
                        t_values, act_range[conn], nbins=self.nbins
                    )
                    t_hists = tf.unique_with_counts(t_idxs, name=None)
                    t_bins = t_hists.y
                    t_counts = t_hists.count
                    t_hist.append([t_bins, t_counts])
                
            return t_hist

        # Define a function to parsee the activation histogram data
        def parse_act_hist_data(data, sess_data):
            
            i = 0
            for layer in layers:
                
                if layer == 'mixed3a':
                    continue
                    
                for appendix in appendixes:
                    
                    conn = '{}_{}'.format(layer, appendix)
                    hist_data = np.zeros(self.nbins)
                    hist_bins, hist_cnts = sess_data[i]
                    hist_data[hist_bins] = hist_cnts
                    i += 1
                
                    # Update connection activation histogram in the data
                    if conn not in data:
                        data[conn] = hist_data
                    else:
                        data[conn] += hist_data
            
            return data
        
        # Compute activation range of neurons
        data, time_log = self.model.compute_data(
            compute_act_hist_tensors, 
            [], 
            parse_act_hist_data, 
            []
        )
        
        # Save data into a file
        self.save_act_hist(data, 'connection')
        
        # Save time log into a file
        self.save_time_log(time_log, 'act_hist', 'connection')
        
        
    def compute_act_threshold(self, target):
        '''
        Compute activation threshold
        * input
            - target: either 'neuron' or 'connection'
        * output
            - N/A
        '''
        
        # Check time
        tic = time()
        
        # Load activation data
        act_range = self.load_act_range(target)
        act_hist = self.load_act_hist(target)
        
        # Activation probability density
        act_pdf = {
            act_unit: act_hist[act_unit] / np.sum(act_hist[act_unit]) 
            for act_unit in act_hist
        }
    
        # Compute activation threshold
        act_thr = {}
        if target == 'neuron':
            thr = self.thr_neuron
        else:
            thr = self.thr_connection
        for act_unit in act_pdf:

            # Make bins
            bins = []
            act_min, act_max = act_range[act_unit][0], act_range[act_unit][1]
            act_width = (act_max - act_min) / self.nbins
            for i in range(self.nbins):
                bins.append(act_min + (i * act_width))

            # Find bins for the threshold
            bin_thr, prob_sum = -1, 0
            for bin_idx in range(len(act_pdf[act_unit]) - 1, -1, -1):
                prob_sum += act_pdf[act_unit][bin_idx]
                if prob_sum >= thr:
                    bin_thr = bin_idx
                    break

            # Save threhold
            act_thr[act_unit] = bins[bin_thr]
            
        # Save threshold
        self.save_act_thr(act_thr, target)
        
        # Save time log into a file
        toc = time()
        time_log = 'total time: %.2lf' % (toc - tic)
        self.save_time_log(time_log, 'act_thr', target)
        
    
    def load_data(self, data_item, target):
        '''
        Load activation data
        * input
            - data_item: one among ['act_range', 'act_hist', 'act_thr']
            - target: one among ['neuron', 'connection']
        * output
            - N/A
        '''
        
        data_path = self.data_path.get_data_path(data_item, target, 'data')
        with open(data_path, 'r') as f:
            data = json.load(f)
        return data
    
    
    def save_data(self, data, data_item, target):
        '''
        Save activation data
        * input
            - data: dictionary data to save
            - data_item: one among ['act_range', 'act_hist', 'act_thr']
            - target: one among ['neuron', 'connection']
        * output
            - N/A
        '''
        
        data_path = self.data_path.get_data_path(data_item, target, 'data')
        with open(data_path, 'w') as f:
            f.write(json.dumps(data))
      
    
    def save_time_log(self, time_log, data_item, target):
        '''
        Save activation data
        * input
            - time_log: Time log
            - data_item: one among ['act_range', 'act_hist', 'act_thr']
            - target: one among ['neuron', 'connection']
        * output
            - N/A
        '''
        
        data_path = self.data_path.get_data_path(data_item, target, 'time')
        with open(data_path, 'w') as f:
            f.write(time_log)
        
        
    def save_act_range(self, data, target):
        '''
        Save activation range into a json file
        * input
            - data: activation range data
            - target: either 'neuron' or 'connection'
        * output
            - N/A
        '''
        
        # Change the format of data
        data = {
            blk:[
                str(data[blk]['min']), 
                str(data[blk]['max'])
            ] 
            for blk in data
        }
        
        # Save the data
        self.save_data(data, 'act_range', target)
        
        
    def load_act_range(self, target):
        '''
        Load activation range
        * input
            - target: either 'neuron' or 'connection'
        * output
            - N/A
        '''
        
        data = self.load_data('act_range', target)
        data = {
            blk: [
                float(data[blk][0]), 
                float(data[blk][1])
            ]
            for blk in data
        }
        
        return data
        
        
    def save_act_hist(self, data, target):
        '''
        Save activation histogram into a json file
        * input
            - data: activation range data
            - target: either 'neuron' or 'connection'
        * output
            - N/A
        '''
        
        # Change the format of data
        data = {blk: [str(v) for v in data[blk]] for blk in data}
        
        # Save the data
        self.save_data(data, 'act_hist', target)
        
        
    def load_act_hist(self, target):
        '''
        Load activation histogram data
        * input
            - target: either 'neuron' or 'connection'
        * output
            - N/A
        '''
        
        data = self.load_data('act_hist', target)
        data = {
            blk: [float(v) for v in data[blk]]
            for blk in data
        }
        return data
    
    
    def save_act_thr(self, data, target):
        '''
        Save activation threshold into a json file
        * input
            - data: activation range data
            - target: either 'neuron' or 'connection'
        * output
            - N/A
        '''
        
        # Change the format of data
        data = {blk: str(data[blk]) for blk in data}
        
        # Save the data
        self.save_data(data, 'act_thr', target)
        
        
    def load_act_thr(self, target):
        '''
        Load activation threshold
        * input
            - target: either 'neuron' or 'connection'
        * output
            - N/A
        '''
        
        data = self.load_data('act_thr', target)
        data = {blk: float(data[blk]) for blk in data}
        return data