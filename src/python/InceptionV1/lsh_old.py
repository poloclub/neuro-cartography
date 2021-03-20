'''
* Project:
    Neuro-Cartography: Drawing Concept-based Neural Maps to Interpret 
    Deep Neural Networks by Automatically Discovering and Visualizing 
    Cell Assemblies
* File name:
    lsh.py
* Description:
    Hash neurons and connections by LSH
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Jan 30, 2020
'''

import json
import tqdm
import numpy as np
from time import time
import tensorflow as tf


class LSH:

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Class for computing hash value
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def __init__(self, args, data_path, model_wrapper):
        
        # Objects of other classes
        self.act_thr = model_wrapper.act_thr
        self.perm_2d = model_wrapper.perm_2d

        # Model
        self.model = model_wrapper.model

        # Hyperparameters - general
        self.layer = args.layer
        self.batch_size = args.batch_size

        # Hyperparameters - compute hash value
        self.num_imgs = self.model.num_imgs
        self.num_hash_per_img = args.num_hash_per_img
        self.H, self.W = self.model.ACT_MAP_SIZE[self.layer]
        self.num_hash = self.num_hash_per_img * self.num_imgs

        # Hyperparameters - generate bucket
        self.band_size = args.band_size
        self.thr_of_non_act = args.thr_of_non_act
        self.thr_co_occur = args.thr_co_occur

        # Hyperparmeters - generate connection
        self.high_act_patch_size = args.high_act_patch_size

        # Data path
        self.data_path = self.update_data_path(data_path)
        
        # Blocks
        self.BLKS = self.model.BLKS
        self.BLKS_CURR_LAYER = self.generate_blks_of_curr_layer()
        # self.CONCAT_OFFSET = self.model.CONCAT_OFFSET
        
        # Global variable
        self.img_idx = 0


    def update_data_path(self, data_path):
        '''
        Update data path for lsh. Update H and W to the height
        and width of activation map of the given layer
        * input
            - data_path: data_path before updated
        * ouput
            - data_path: updated data_path
        '''

        # H and W for the given class
        H, W = self.model.ACT_MAP_SIZE[self.layer]
        
        # Update H and W in data_path
        data_path.args.H = H
        data_path.args.W = W
        data_path.HYPER_PARAMETERS \
            ['permutation']['hash_array'] = [
                H, W
            ]

        # Update H and W in perm_2d.data_path
        self.perm_2d.H = H
        self.perm_2d.W = W
        self.perm_2d.data_path.HYPER_PARAMETERS \
            ['permutation']['hash_array'] = [
                H, W
            ]

        # Update paths
        data_path.gen_data_path('permutation')
        self.perm_2d.data_path.gen_data_path('permutation')
        data_path.gen_data_path('lsh')
        self.perm_2d.data_path.gen_data_path('lsh')

        return data_path
    

    def generate_blks_of_curr_layer(self): 
        '''
        Generate blocks of current layer
        * input
            - N/A
        * output
            - blks_curr_layer: blocks of current layer
        '''
        
        blks_curr_layer = []
        if self.layer != None:
            blks_curr_layer = [
                blk for blk in self.BLKS if self.layer in blk
            ]
        else:
            print('ERR: self.layer is unknown')
        return blks_curr_layer



    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for computing hash value - general
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def parse_hash_value_data(self, data, sess_data, target):
        '''
        Parse hash value data of neurons for a batch
        * input
            - data: data before udpated
            - sess_data: data in the current session
            - target: either 'neuron' or 'connection'
        * output
            - data: updated data 
        '''

        # Index out of range
        if len(sess_data) == 0:
            return data

        # Index to save data
        hash_from, hash_to = self.get_curr_hash_indexes()

        # Parse hash values
        if target == 'neuron':
            iter_target = self.BLKS_CURR_LAYER 
        elif target == 'connection':
            iter_target = self.model.BLK_APPENDIXES
        else:
            print('ERR: unknown iterating_target {}'.format(iter_target))
        
        for i, chunk in enumerate(iter_target):
            chunk_data = sess_data[i][0]
            chunk_non_activated = sess_data[i][1]
            chunk_data[chunk_non_activated == 0] = -1
            
            if chunk not in data:
                num_entities = chunk_data.shape[-1]
                data[chunk] = np.zeros((self.num_hash, num_entities))
            data[chunk][hash_from: hash_to, :] = chunk_data

        # Update img_idx after this batch
        self.img_idx += self.batch_size
        
        return data


    def compute_hash_val_from_act_map(self, t_a_map, a_thr, p_idxs, N):
        '''
        Compute hash value of given activation map
        * input
            - t_a_map: tensor of activation map of shape (N, H, W, C)
            - a_thr: activation threshold
            - p_idxs: permutation indexes
            - N: number of hashs (rows)
        * output
            - t_idx_nnz: the minimum index of permuted activation map
            - t_no_act: (image, neuron) pairs of no activated map
        '''

        # Height and width of activation map
        H, W = self.H, self.W

        # Resize and quantize the block tensor
        t_resized = tf.image.resize_images(t_a_map, [H, W])
        t_quantized = t_resized > a_thr
        t_quantized = tf.dtypes.cast(t_quantized, tf.int32)

        # TODO: OR pooling
        
        # Convert (N, H, W, C) to (C, H, W, N)
        t_transposed = tf.transpose(t_quantized, [3, 1, 2, 0])
        
        # Permutate values
        t_hashed = tf.map_fn(
            fn=lambda t: tf.gather_nd(t, p_idxs), 
            elems=t_transposed
        )
        
        # Convert t_hashed's shape from (C, H, W, N) to (N, C, H * W)
        C = t_hashed.shape[0]
        t_hashed_transposed = tf.transpose(t_hashed, [3, 0, 1, 2])
        t_hashed_reshaped = tf.reshape(
            t_hashed_transposed, 
            (N, C, H * W)
        )
        
        # Find the minimum index of 1, shape: (N, C)
        t_idx_nnz = tf.math.argmax(t_hashed_reshaped, axis=2)
        
        # Find (image, neuron) pairs,
        # where the neuron is not activated in the image
        t_no_act = tf.math.reduce_sum(t_hashed_reshaped, axis=2)
        
        return t_idx_nnz, t_no_act


    def get_curr_img_indexes(self):
        '''
        Get current batch's image indexes
        * input
            - N/A
        * output
            - from_img_idx: starting index of image
            - to_img_idx: ending index of image
        '''

        from_img_idx = self.img_idx
        to_img_idx = min(self.img_idx + self.batch_size, self.num_imgs)
        return from_img_idx, to_img_idx


    def get_curr_hash_indexes(self):
        '''
        Get current batch's hash indexes 
        (i.e., row index of hash value table)
        * input
            - N/A
        * output
            - hash_from: starting index of hash
            - hash_to: ending index of hash
        '''

        from_img_idx, to_img_idx = self.get_curr_img_indexes()
        hash_from = from_img_idx * self.num_hash_per_img
        hash_to = to_img_idx * self.num_hash_per_img
        
        return hash_from, hash_to


    def gen_permutation_indexes(self, perm_arrs):
        '''
        Generate permutation indexes for a (H, W, N) tensor,
        where H=width, W=width, N=#hashes.
        * input
            - perm_arrs: permutation array of shape (N, H, W)
            - N: Number of hashes
        * output
            - perm_indexes: premutation indexes of shape (H, W, N, 3)
        '''

        # Initialize perm_indexes
        N = perm_arrs.shape[0]
        H, W = self.H, self.W
        perm_indexes = np.zeros((H, W, N, 3), dtype=int)

        # Generate perm_indexes
        for hash_i, perm_arr in enumerate(perm_arrs):
            img_i = int(hash_i // self.num_hash_per_img)
            for coord_i, coord in enumerate(perm_arr):
                r, c = int(coord_i // W), int(coord_i % W)             
                perm_r, perm_c = int(coord[0]), int(coord[1])
                perm_indexes[r, c, hash_i] = [perm_r, perm_c, img_i]

        return perm_indexes
    
    

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for computing hash value - neuron
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def compute_hash_value_of_neurons(self):
        '''
        Compute hash values of neurons of the given layer
        * input
            - N/A
        * output
            - N/A
        '''

        # Get ready
        act_threshold = self.act_thr.load_act_thr('neuron')
        hash_order = self.perm_2d.load_hash_order()
        hash_arrs = self.perm_2d.load_all_hash_arrs()
                
        # Compute hash value of neurons
        data, time_log = self.model.compute_data(
            self.compute_t_hash_val_neuron, 
            [hash_order, hash_arrs, act_threshold], 
            self.parse_hash_value_data, 
            ['neuron']
        )
        
        # Restore self.img_idx
        self.img_idx = 0
        
        # Save data into a file
        self.save_hash_value(data)
        
        # Save time log into a file
        self.save_time_log(time_log, 'hash_value', 'neuron')


    def compute_t_hash_val_neuron(self, h_order, h_arrs, a_thr):
        '''
        Compute hash value tensor of neurons
        * input
            - h_order: hashing order
            - h_arrs: permutation arrays
            - a_thr: activation threshold
        * output
            - tensors: tensors of hash values and non-activation info
        '''

        # Get hash order
        hash_from, hash_to = self.get_curr_hash_indexes()
        curr_hash_order = h_order[hash_from: hash_to]
        
        # Range out of order
        curr_num_hash = hash_to - hash_from
        if curr_num_hash <= 0:
            return []
        
        # Generate permutation idexes
        perm_arrs = h_arrs[curr_hash_order]
        perm_indexes = self.gen_permutation_indexes(perm_arrs)
        
        # Compute hash values and mark non-activated cases
        tensors = []
        for blk in self.BLKS_CURR_LAYER:
            
            t_blk = self.model.get_t_blk(blk)
            t_idx_nnz, t_no_act = \
                self.compute_hash_val_from_act_map(
                    t_blk, a_thr[blk], perm_indexes, curr_num_hash
                )
            tensors.append([t_idx_nnz, t_no_act])
        
        return tensors



    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for computing hash value - connection 
    (Currently not used)
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def compute_hash_value_of_connections(self):
        '''
        Compute hash values of connections of the given layer gap
        * input
            - N/A
        * output
            - N/A
        '''

        # Get ready
        act_threshold = self.model.act_thr.load_act_thr('connection')
        hash_order = self.load_hash_order()
        hash_arrs = self.load_all_hash_arrs()
        prev_layer = self.model.get_prev_layer(self.layer)
        
        # Compute lash value of connections
        data, time_log = self.model.compute_data(
            self.compute_t_hash_val_connection, 
            [hash_order, hash_arrs, act_threshold, prev_layer], 
            self.parse_hash_value_data, 
            ['connection']
        )
        
        # Restore self.img_idx
        self.img_idx = 0
        
        # Save data into a file
        # self.save_hash_value(data, 'connection')
        
        # Save time log into a file
        self.save_time_log(time_log, 'hash_value', 'connection')


    def compute_t_hash_val_connection(self, h_order, h_arrs, a_thr, p_layer):
        '''
        Compute hash value tensor of connections
        * input
            - h_order: hashing order
            - h_arrs: permutation arrays
            - a_thr: activation threshold
            - p_layer: prev_layer
        * output
            - tensors: tensors of hash values and non-activation info
        '''

        # Get hash order
        hash_from, hash_to = self.get_curr_hash_indexes()
        curr_hash_order = h_order[hash_from: hash_to]
        
        # Range out of order
        curr_num_hash = hash_to - hash_from
        if curr_num_hash <= 0:
            return []

        # Generate permutation idexes
        perm_arrs = h_arrs[curr_hash_order]
        perm_indexes = self.gen_permutation_indexes(perm_arrs)

        # Block tensors for the layer
        t_l_input, t_l_3x3, t_l_5x5 = \
            self.model.get_t_blks(p_layer, self.layer)
                
        # Weight tensors for the layer
        t_w_1x1, t_w_3x3_btl, t_w_3x3, t_w_5x5_btl, t_w_5x5, t_w_p_r = \
            self.model.get_t_weights_layer_gap(self.layer)

        # Tensors in order
        blk_tensors = [
            t_l_input, t_l_3x3, t_l_5x5, t_l_input, t_l_input, t_l_input
        ]
        w_tensors = [
            t_w_1x1, t_w_3x3, t_w_5x5, t_w_p_r, t_w_3x3_btl, t_w_5x5_btl
        ]   
        appendix = self.model.BLK_APPENDIXES

        # Compute hash value tensors
        tensors = []
        for apdx, t_b, t_w in zip(appendix, blk_tensors, w_tensors):
            
            t_conn = tf.nn.depthwise_conv2d(
                t_b, 
                t_w, 
                strides=[1, 1, 1, 1], 
                padding='SAME'
            )
            thr = a_thr['{}_{}'.format(self.layer, apdx)]
            t_idx_nnz, t_no_act = \
                self.compute_hash_val_from_act_map(
                    t_conn, thr, perm_indexes, curr_num_hash
                )
            tensors.append([t_idx_nnz, t_no_act])
            
        return tensors



    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for loading and saving data
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def save_hash_value(self, hash_value):
        '''
        Save hash value
        * input
            - hash_value: hash value data
            - target: either 'neuron' or 'connection'
        * output 
            - N/A
        '''
        
        dir_path = self.data_path.get_data_path(
            'hash_value', data_or_time='data'
        )
        self.data_path.gen_dir(dir_path)
        
        for blk in hash_value:
            file_path = '{}/{}.txt'.format(
                dir_path, 
                blk
            )
            np.savetxt(file_path, hash_value[blk], fmt='%d')


    def load_hash_value(self, blk):
        '''
        Load hash value
        * input
            - blk: block name
        * output 
            - hash_value: hash value data
        '''

        dir_path = self.data_path.get_data_path(
            'hash_value',
            data_or_time='data'
        )
        file_path = '{}/{}.txt'.format(dir_path, blk)
        hash_value = np.loadtxt(file_path)
        return hash_value


    def load_all_hash_value_neuron(self):
        '''
        Load hash value of neurons in all layers
        * input
            - N/A
        * output 
            - hash_value: hash value data
        '''

        # Hash value of neurons
        hash_val_neuron = {}
        for blk in self.BLKS:
            hash_val_neuron[blk] = self.load_hash_value(blk)
        return hash_val_neuron

    
    def load_all_hash_value_connection(self):
        '''
        Load hash value of connectons in all layers
        * input
            - N/A
        * output 
            - hash_value: hash value data
        '''

        hash_val_conn = {}
        for layer in self.model.LAYERS:
            if layer == 'mixed3a':
                continue
            for appdx in self.model.BLK_APPENDIXES:
                conn = '{}_{}'.format(layer, appdx)
                # hash_val_conn[conn] = self.load_hash_value(
                #     conn, 'connection'
                # )
        return hash_val_conn



    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for buckets of neurons
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def gen_bucket(self):
        '''
        Generate buckets for the given layer
        * input
            - N/A
        * output
            - buckets: hashed buckets
        '''

        # Get ready
        time_log, tic, blks = '', time(), self.BLKS_CURR_LAYER
        num_iters = {blk: {'iter': 0, 'proc': 0} for blk in blks}

        # Hash value of neurons
        for blk in blks:

            # Load hash values
            hash_val = self.load_hash_value(blk)

            # Hash neurons into buckets
            num_bands, buckets = self.get_num_bands(), {} 
            with tqdm.tqdm(total=num_bands, unit='bands') as pb:
                for band_i in range(num_bands):

                    # Initialize buckets of current band
                    buckets[band_i] = {}

                    # Hash neurons
                    buckets = self.hash_entities_into_buckets(
                        blk, hash_val, buckets, band_i
                    )

                    # Update pbar
                    pb.update(1)

            # Aggregate buckets
            aggregated_buckets, num_iter, num_processed = \
                self.aggregate_bucket_CO_OC(buckets)
                # self.aggregate_bucket_AND_OR(buckets)
            num_iters[blk]['iter'] += num_iter
            num_iters[blk]['proc'] += num_processed

            # Save aggregated buckets
            self.save_aggregated_buckets(
                aggregated_buckets, blk
            )

        # Save time
        toc = time()
        time_log = 'total time: {:.2f} sec\n'.format(toc - tic)
        for blk in blks:
            time_log += blk + '\n'
            time_log += '# iter: {}\n'.format(
                num_iters[blk]['iter']
            )
            time_log += '# processed: {}\n'.format(
                num_iters[blk]['proc']
            )
        self.save_time_log(time_log, 'bucket')

        return buckets


    def hash_entities_into_buckets(self, blk, hash_val, buckets, i):
        '''
        Hash entities (neurons or connections) into buckets
        * input
            - blk: block name
            - hash_val: hash value data
            - buckets: buckets before updated
            - i: index of band
        * output
            - buckets: updated buckets
        '''

        # Hash row index
        row_from = i * self.band_size
        row_to = (i + 1) * self.band_size        

        # Get hash vectors of neurons
        hash_vecs = hash_val[row_from: row_to]

        # Number of entity
        num_entities = hash_vecs.shape[-1]

        # Hash neurons into buckets
        for e in range(num_entities):

            # Entity's hash key
            hash_key = self.gen_hash_key(hash_vecs[:, e])
            
            # Entity's id
            e_id = self.get_neuron_id(blk, e)
            
            # Add hash key
            if hash_key not in buckets[i]:
                buckets[i][hash_key] = []

            # Add neuron into a bucket
            buckets[i][hash_key].append(e_id)

        return buckets


    def gen_hash_key(self, hash_vec):
        '''
        Generate hash key from hash vector
        * input
            - hash_vec: hash vector, size = band_size
        * output
            - N/A
        '''

        return ','.join([str(int(v)) for v in hash_vec])


    def get_num_bands(self):
        '''
        Get the number of bands
        '''

        num_bands = int(self.num_hash / self.band_size)
        return num_bands


    def get_neuron_id(self, blk, neuron):
        '''
        Get neuron's id
        * input
            - blk: block name
            - neuron: neuron index
        * output
            - neuron's id
        '''

        return '{}-{}'.format(blk, neuron)


    def aggregate_bucket_AND_OR(self, buckets):
        '''
        Aggregate buckets of all bands with AND-OR approach
        * input
            - buckets: buckets by band
        * output
            - aggregated_buckets: aggregated buckets
        '''

        # Get ready
        num_bands = len(buckets)
        entity_to_group, group_to_entity, group_number = {}, {}, 0
        num_iter, num_processed = 0, 0
        tic = time()

        # Aggregate buckets
        with tqdm.tqdm(total=num_bands, unit='bands') as pbar:
            for band_i in buckets:

                # Cluster buckets
                bucket = buckets[band_i]
                for hash_key in bucket:

                    # Ignore current bucket if it's not good enough
                    num_iter += 1
                    if self.ignore_bucket(bucket, hash_key):
                        continue
                    num_processed += 1

                    # Find groups to merge
                    groups_to_merge = self.find_groups_to_merge_AND_OR(
                        bucket[hash_key], 
                        group_number, 
                        entity_to_group, 
                        group_to_entity
                    )
                    
                    # Merge the groups
                    entity_to_group, group_to_entity = \
                        self.merge_entity_group(
                            groups_to_merge, 
                            group_number,
                            entity_to_group, 
                            group_to_entity
                        )

                    # Update group number
                    group_number += 1

                # Update progress bar
                pbar.update(1)

        # Parse groups
        aggregated_buckets = self.gen_aggregated_buckets(
            group_to_entity
        )
        
        return aggregated_buckets, num_iter, num_processed


    def find_groups_to_merge_AND_OR(self, one_bucket, group_n, e2g, g2e):
        '''
        Find groups to merge in the given bucket
        * input
            - one_bucket: one bucket
            - group_n: current group_number
            - e2g: dictionary mapping entity to group
            - g2e: dictionary mapping group to entity
        * output
            - groups_to_merge: groups to merge
        '''

        groups_to_merge = {}
        for entity in one_bucket:
            if entity in e2g:  
                group_of_entity = e2g[entity]
                groups_to_merge[group_of_entity] = True
            else:
                groups_to_merge[group_n] = True
                e2g[entity] = group_n
                if group_n not in g2e:
                    g2e[group_n] = []
                g2e[group_n].append(entity)
        return groups_to_merge


    def aggregate_bucket_CO_OC(self, buckets):
        '''
        Aggregate buckets with co-occurence frequency approach
        * input
            - buckets: buckets by band
        * output
            - N/A
        '''

        # Get ready
        tic = time()
        num_bands = len(buckets)
        entity_to_group, group_to_entity, group_number = {}, {}, 0
        
        # Co-occurence frequency
        co_occur, num_iter, num_processed = self.count_co_occur(buckets)

        # Pick threshold
        co_occur_cnt = sorted(list(co_occur.values()))
        co_occur_cnt_dict = {}
        for cnt in co_occur_cnt:
            if cnt not in co_occur_cnt_dict:
                co_occur_cnt_dict[cnt] = 0    
            co_occur_cnt_dict[cnt] += 1
        
        agg_sum = 0
        thr = 0
        total = np.sum(list(co_occur_cnt_dict.values()))
        for co_oc_cnt, cnt in sorted(co_occur_cnt_dict.items(), key=lambda x: x[1], reverse=True):
            agg_sum += (cnt / total)
            if agg_sum >= (1 - self.thr_co_occur):
                thr = co_oc_cnt
                break

        # Aggregate buckets based on the co-occurence
        with tqdm.tqdm(total=num_bands, unit='bands') as pbar:

            for e_pair in co_occur:

                # Ignore less co-occured entity pair
                if co_occur[e_pair] < thr:
                    continue

                # Find groups to merge
                groups_to_merge = self.find_groups_to_merge_CO_OC(
                    e_pair, group_number, entity_to_group, group_to_entity
                )

                # Merge the groups
                entity_to_group, group_to_entity = \
                    self.merge_entity_group(
                        groups_to_merge, 
                        group_number,
                        entity_to_group, 
                        group_to_entity
                    )

                # Update group number
                group_number += 1

                # Update progress bar
                pbar.update(1)
                    
        # Parse groups
        aggregated_buckets = self.gen_aggregated_buckets(group_to_entity)

        return aggregated_buckets, num_iter, num_processed


    def ignore_bucket(self, bucket, hash_key):
        '''
        Whether to ignore a bucket
        * input
            - bucket: series of bucket of a band
            - hash_key: hash_key of a bucket
        * outout
            - Whether to ignore a bucket of hash_key
        '''

        # Ignore if there are too many non activated cases
        thr_num_non_act = int(self.band_size * self.thr_of_non_act)
        num_non_act = self.get_num_non_act(hash_key)
        if num_non_act > thr_num_non_act:
            return True

        # Ignore bucket of size 1
        if len(bucket[hash_key]) < 2:
            return True

        return False


    def get_num_non_act(self, hash_key):
        '''
        Get the number of non activated cases given hash_key
        * input
            - hash_key: hash key in buckets
        * output
            - n: the number of non activated cases
        '''

        hash_vals = hash_key.split(',')
        n = 0
        for hash_val in hash_vals:
            if '-1' in hash_val:
                n += 1

        return n


    def find_groups_to_merge_CO_OC(self, e_pair, group_n, e2g, g2e):
        '''
        Find groups to merge
        * input
            - e_pair: enity pair
            - group_n: current group number
            - e2g: dictionary mapping entity to group
            - g2e: dictionary mapping group to entities
        * output
            - groups_to_merge: groups to merge
        '''

        groups_to_merge = {}
        groups_to_merge[group_n] = True
        g2e[group_n] = []
        
        for e in e_pair:
            if e in e2g:
                groups_to_merge[e2g[e]] = True
            else:
                e2g[e] = group_n
                g2e[group_n].append(e)

        return groups_to_merge


    def merge_entity_group(self, groups_to_merge, group_n, e2g, g2e):
        '''
        Merge groups of entities
        * input
            - groups_to_merge: groups to merge
            - group_n: current group number
            - e2g: dictionary mapping entity to group
            - g2e: dictionary mapping group to entities
        * output
            - e2g: updated e2g after merging
            - g2e: updated g2e after merging
        '''

        if len(groups_to_merge) > 1:

            merged_entities = {}
            for group in groups_to_merge:

                # Update entities' group number
                for entity in g2e[group]:
                    e2g[entity] = group_n
                    merged_entities[entity] = True

                # Update old group's entity list
                g2e[group] = []

            # Update the new group's entity list
            merged_entities = list(merged_entities.keys())
            g2e[group_n] = merged_entities

        return e2g, g2e


    def gen_aggregated_buckets(self, g2e):
        '''
        Generate aggregated buckets
        * input
            - g2e: dictionary mapping group to entities
        * output
            - aggregated_buckets: aggregated bucktes
        '''

        aggregated_buckets, group_id = {}, 0
        for group in g2e:
            if len(g2e[group]) > 0:
                buckets = self.split_bucket_by_blk(g2e[group])
                for bucket in buckets:
                    aggregated_buckets[group_id] = bucket 
                    group_id += 1

        return aggregated_buckets


    def split_bucket_by_blk(self, bucket):
        '''
        Split bucket by blocks
        * input
            - bucket: a bucket of neurons
        * output
            - new_buckets: buckets after splitted
        '''

        new_buckets = [bucket]
        if (len(bucket) > 0):
            if '_' not in bucket[0]:

                # Split buckets
                new_buckets = {}
                for n in bucket:
                    i = self.model.get_concat_blk_from_neuron(n)
                    if i not in new_buckets:
                        new_buckets[i] = []
                    new_buckets[i].append(n)

                # Filter out buckets of length 1
                new_buckets = [
                    b 
                    for b in new_buckets.values()
                    if len(b) > 1
                ]

        return new_buckets


    def count_co_occur(self, buckets):
        '''
        Count co-occurence
        * input
            - buckets: buckets of all bands
        * output
            - co_occur_freq: co-occurence dictionary
            - num_iter: number of total iterations
            - num_processed: number of non-skip iterations
        '''

        # Get ready
        co_occur = {}
        num_bands = len(buckets)
        num_iter, num_processed = 0, 0

        # Count the co-occuence of entities
        with tqdm.tqdm(total=num_bands, unit='bands') as pbar:
            for band_i in buckets:

                # Cluster buckets
                bucket = buckets[band_i]
                for hash_key in bucket:

                    # Ignore current bucket if it's not good enough
                    num_iter += 1
                    if self.ignore_bucket(bucket, hash_key):
                        continue
                    num_processed += 1

                    # Count co-occurence
                    for e1 in bucket[hash_key]:
                        for e2 in bucket[hash_key]:
                            if e1 != e2:
                                key = tuple(sorted([e1, e2]))
                                if key not in co_occur:
                                    co_occur[key] = 0
                                co_occur[key] += 0.5
                    
                # Update progress bar
                pbar.update(1)

        return co_occur, num_iter, num_processed


    def save_aggregated_buckets(self, aggregated_buckets, blk):
        '''
        Save aggregated buckets
        * input
            - aggregated_buckets: aggregated buckets
            - blk: block name
        * output 
            - N/A
        '''
        
        # File path
        dir_path = self.data_path.get_data_path(
            'bucket',
            target='neuron',
            data_or_time='data'
        )
        self.data_path.gen_dir(dir_path)
        file_path = '{}/bucket-{}.json'.format(dir_path, blk)

        # Save file
        with open(file_path, 'w') as f:
            json.dump(aggregated_buckets, f)


    def aggregate_clusters(self):
        '''
        Aggregate cluster data of different datastes
        TODO: This is used only for a test currently
        * input
            - N/A
        * output
            - N/A
        '''

        synsets = ['n02114367', 'n01755581', 'n09468604', 'n02687172', 'n10565667', 'n02391049', 'n02113799', 'n03595614', 'n03599486', 'n04252077', 'n01729977', 'n02342885', 'n02132136', 'n01744401',
            'n02497673', 'n02085936', 'n02085620', 'n02133161', 'n01749939', 'n03602883', 'n01828970', 'n01872401', 'n02128757', 'n02112350', 'n01833805', 'n06359193', 'n09835506', 'n02110806', 
            'n02134084', 'n01882714', 'n01667114', 'n01860187', 'n02606052', 'n02124075', 'n04254680', 'n03495258', 'n02480855', 'n02007558', 'n02398521', 'n04146614', 'n04355338', 'n02643566', 
            'n03544143', 'n01877812', 'n02099601', 'n02110958', 'n07615774', 'n04404412', 'n04347754', 'n03584254', 'n02443114', 'n04456115', 'n01704323', 'n02977058', 'n07718472', 'n02396427', 
            'n02444819', 'n02395406', 'n03394916', 'n01806143', 'n04485082', 'n02120079', 'n01687978', 'n01698640', 'n02129165']

        aggregated_clusters = {}
        cluster_number = {blk: 0 for blk in self.BLKS}
        e2g = {blk: {} for blk in self.BLKS}
        g2e = {blk: {} for blk in self.BLKS}

        for synset in synsets:

            dir_path = '../../data/InceptionV1/bucket'
            dir_path += '/bucket-{}-{}-{}-{}-{}-{}-{}'.format(
                synset, 
                self.num_hash_per_img,
                1,
                0.05, 
                self.band_size,
                self.thr_of_non_act,
                self.thr_co_occur
            )
            
            for blk in self.BLKS:

                file_path = '{}/bucket-{}.json'.format(
                    dir_path, blk
                )
                try:
                    with open(file_path, 'r') as f:
                        clusters = json.load(f)
                except:
                    clusters = {}

                for cluster_id in clusters:

                    groups_to_merge = \
                        self.find_groups_to_merge_AND_OR(
                            clusters[cluster_id],
                            cluster_number[blk],
                            e2g[blk],
                            g2e[blk]
                        )

                    e2g[blk], g2e[blk] = self.merge_entity_group(
                        groups_to_merge, 
                        cluster_number[blk],
                        e2g[blk], 
                        g2e[blk]
                    )

                    cluster_number[blk] += 1

        for blk in g2e:
            aggregated_clusters[blk] = {}
            g_number = 0
            for g in g2e[blk]:
                if len(g2e[blk][g]) > 1:
                    aggregated_clusters[blk][g_number] = g2e[blk][g]
                    g_number += 1

        file_path = '../../data/InceptionV1/aggregated_bucket/buckets.json'
        with open(file_path, 'w') as f:
            json.dump(aggregated_clusters, f)

                
            



    def load_aggregated_buckets(self, blk):
        '''
        Load aggregated buckets
        * input
            - blk: block name
        * output
            - N/A
        '''

        # File path
        dir_path = self.data_path.get_data_path(
            'bucket',
            target='neuron',
            data_or_time='data'
        )
        file_path = '{}/bucket-{}.json'.format(dir_path, blk)

        # Load bucket
        with open(file_path, 'r') as f:
            buckets = json.load(f)

        return buckets


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for for buckets of connections (currently not used)
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def get_connection_id(self, conn, conn_i):
        '''
        Get connection's id
        * input
            - conn: connection name
            - conn_i: connection index
        * output
            - conn_id: connection's id
        '''

        # Get blocks of the connection
        blk1, blk2 = self.get_blk_names(conn)

        # Get neuron numbers of the connection
        n1, n2 = self.get_neuron_numbers(blk2, conn_i)

        # Remove '_concat*' in blk2
        if 'concat' in blk2:
            blk2 = blk2.split('_')[0]

        # Connection id
        neuron1 = '{}-{}'.format(blk1, n1)
        neuron2 = '{}-{}'.format(blk2, n2)
        conn_id = '{},{}'.format(neuron1, neuron2)

        return conn_id


    def get_blk_names(self, conn):
        '''
        Get blocks' name of connction
        * input
            - conn: connection chunk
        * output
            - blk1: block of earlier layer
            - blk2: block of later layer
        '''

        layer, appdx = conn.split('_')
        prev_layer = self.model.get_prev_layer(layer)
        
        if appdx in ['concat0', 'concat3']:
            blk1 = prev_layer
            blk2 = '{}_{}'.format(layer, appdx)
        elif appdx == 'concat1':
            blk1 = '{}_3x3'.format(layer)
            blk2 = '{}_{}'.format(layer, appdx)
        elif appdx == 'concat2':
            blk1 = '{}_5x5'.format(layer)
            blk2 = '{}_{}'.format(layer, appdx)
        elif appdx == 'conn3x3':
            blk1 = prev_layer
            blk2 = '{}_3x3'.format(layer)
        elif appdx == 'conn5x5':
            blk1 = prev_layer
            blk2 = '{}_5x5'.format(layer)

        return blk1, blk2


    def get_neuron_numbers(self, blk2, conn_i):
        '''
        Get neuron numbers of connection
        * input
            - blk2: later block in the connection
            - conn_i: connection index
        * output
            - n1: neuron number in blk1
            - n2: neuron number in blk2
        '''

        num_neurons_blk2 = self.model.LAYER_BLK_SIZE[blk2]
        n1 = int(conn_i / num_neurons_blk2)
        n2 = int(conn_i % num_neurons_blk2)
        if 'concat' in blk2:
            n2 -= self.CONCAT_OFFSET[blk2]
        return n1, n2

        
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Function for generating connections among buckets
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def gen_connection(self):
        '''
        Generate connections 
        * input
            - N/A
        * output
            - N/A
        '''

        # Load buckets
        buckets = self.load_bucekts()

        # Load activation threshold
        act_threshold = self.load_act_thr_neuron_connection()

        # Get activation map of connections
        data, time_log = self.model.compute_data(
            self.compute_t_act_map_neuron_connection, 
            [], 
            self.parse_act_map_neuron_conn, 
            [buckets, act_threshold]
        )

        # Save data (connection)        
        dir_path = self.data_path.get_data_path(
            'bucket', 
            target='connection',
            data_or_time='data'
        )
        file_path = '{}/bucket.json'.format(dir_path)
        with open(file_path, 'w') as f:
            json.dump(data, f)
        

    def load_bucekts(self):
        '''
        Load buckets of blocks for the given layer
        * input
            - N/A
        * output
            - buckets: buckets of blocks
        '''

        buckets = {}
        for blk in self.BLKS_CURR_LAYER:
            buckets[blk] = self.load_aggregated_buckets(blk)
        return buckets


    def load_act_thr_neuron_connection(self):
        '''
        Load activation threshld of neurons and connections
        * input
            - N/A
        * output
            - act_threshold: activation threshold
        '''

        act_threshold_neuron = self.act_thr.load_act_thr(
            'neuron'
        )
        act_threshold_conn = self.act_thr.load_act_thr(
            'connection'
        )

        act_threshold = {}
        for key in act_threshold_neuron:
            act_threshold[key] = act_threshold_neuron[key]
        for key in act_threshold_conn:
            act_threshold[key] = act_threshold_conn[key]        

        return act_threshold


    def compute_t_act_map_neuron_connection(self):
        '''
        Compute tensor of thresholded activation map of 
        neurons and connections
        * input
            - N/A
        * output
            - tensors: tensors of activation map
        '''

        # Previous layer
        p_layer = self.model.get_prev_layer(self.layer)

        # Block tensors for the layer
        t_l_input, t_l_3x3, t_l_5x5 = \
            self.model.get_t_blks(p_layer, self.layer)
                
        # Weight tensors for the layer
        t_w_1x1, t_w_3x3_btl, t_w_3x3, t_w_5x5_btl, t_w_5x5, t_w_p_r = \
            self.model.get_t_weights_layer_gap(self.layer)

        # Block tensor for output block
        t_l_output = self.model.get_t_blk(self.layer)

        # Tensors in order
        blk_tensors = [
            t_l_input, t_l_3x3, t_l_5x5, t_l_input, t_l_input, t_l_input
        ]
        w_tensors = [
            t_w_1x1, t_w_3x3, t_w_5x5, t_w_p_r, t_w_3x3_btl, t_w_5x5_btl
        ]   
        appendix = self.model.BLK_APPENDIXES

        # Tensors of activation map of neurons
        tensors = [t_l_output, t_l_3x3, t_l_5x5]

        # Tensors of activation map of connections        
        for i, (t_b, t_w) in enumerate(zip(blk_tensors, w_tensors)):
            
            # Maxpool input block if needed
            if self.layer in ['mixed4a', 'mixed5a']:

                # Maxpool the input block if it's a concat block
                if i in [0, 3, 4, 5]:
                    t_b = tf.nn.max_pool(
                        t_b,
                        ksize=self.model.MAX_POOL_SETTING['ksize'],
                        strides=self.model.MAX_POOL_SETTING['strides'],
                        padding=self.model.MAX_POOL_SETTING['padding'],
                    )

            # Connection
            t_conn = tf.nn.depthwise_conv2d(
                t_b, 
                t_w, 
                strides=[1, 1, 1, 1], 
                padding='SAME'
            )

            tensors.append(t_conn)
            
        return tensors


    def parse_act_map_neuron_conn(self, data, sess_data, buckets, a_thr):
        '''
        Parse activation map of neurons and connections
        * input
            - data: data before udpated
            - sess_data: data in the current session
            - buckets: hased buckets of neurons
        * output
            - data: updated data 
        '''

        # Index out of range
        if len(sess_data) == 0:
            return data

        # Activation maps of neurons and connections
        act_map_neurons = sess_data[:3]
        act_map_conns = sess_data[3:]

        # Find stong connections based on Jaccard similarity
        for blk in buckets:

            # Add blk
            if blk not in data:
                data[blk] = {}
            
            for bucket_i in buckets[blk]:

                # Add bucket_i
                if bucket_i not in data:
                    data[blk][bucket_i] = {}

                for neuron in buckets[blk][bucket_i]:

                    # Add neuron
                    if neuron not in data[blk][bucket_i]:
                        data[blk][bucket_i][neuron] = {}

                    # Get input block and activation maps
                    prev_blk = self.model.get_prev_blk(neuron)
                    act_map_neuron = self.find_neuron_act_maps(
                        neuron, act_map_neurons
                    )
                    act_map_conn = self.find_conn_act_maps(
                        neuron, act_map_conns
                    )

                    # Find strong connections
                    for batch_i, A in enumerate(act_map_neuron):

                        # Threshold activation map of the neuron
                        thr_A = A > a_thr[blk]
                        thr_A = A.astype(int)
                        if np.sum(thr_A) == 0:
                            continue

                        # Find range of rows and columns to look at
                        min_r, max_r, min_c, max_c = \
                            self.find_high_act_range(A)
                        
                        # Connections' act map of the range
                        C = act_map_conn[
                            batch_i, 
                            min_r: max_r, 
                            min_c: max_c, 
                            :
                        ]
                        
                        # Find top previous neurons and their act map
                        max_C = np.max(C, axis=(0, 1))
                        top_prev_neurons = np.argsort(-max_C)[:50]
                        thr_A_top_C = act_map_conn[
                            batch_i, :, :, top_prev_neurons
                        ]

                        # Threshold connections' act map
                        conn = self.model.get_conn_name(neuron)
                        thr_A_top_C = thr_A_top_C > a_thr[conn]
                        thr_A_top_C = thr_A_top_C.astype(int)
                        
                        # Measure Jaccard similarity
                        J = np.array(list(map(
                            lambda x: self.jaccard_sim(x, thr_A), 
                            thr_A_top_C
                        )))
                        
                        # Sort the top previous neurons
                        sorted_idx = np.argsort(-J)
                        sorted_prev_neurons = top_prev_neurons[
                            sorted_idx
                        ][:10]

                        # Count the top connection
                        for prev_n in sorted_prev_neurons:
                            prev_n_name = '{}-{}'.format(prev_blk, prev_n)
                            if prev_n_name not in data[blk][bucket_i][neuron]:
                                data[blk][bucket_i][neuron][prev_n_name] = 0
                            data[blk][bucket_i][neuron][prev_n_name] += 1 

        return data


    def find_high_act_range(self, A):
        '''
        Find range of row and column for high activation
        * input 
            - A: actvation map
        * output
            - min_r: minimum row of the range
            - max_r: maximum row of the range
            - min_c: minimum column of the range
            - max_c: maximum column of the range
        '''

        s = self.high_act_patch_size
        max_coord = np.argmax(A)
        h, w = A.shape
        r, c = max_coord // w, max_coord % w
        min_r = np.max([0, r - s])
        max_r = np.min([h - 1, r + s])
        min_c = np.max([0, c - s])
        max_c = np.min([w - 1, c + s])

        return min_r, max_r, min_c, max_c


    def find_neuron_act_maps(self, neuron, act_map_neurons):
        '''
        Get activation maps of neuron of all images
        * input
            - neuron: neuron id
            - act_map_neurons: activation map of all neurons
        * output
            - act_map_neuron: activation map of the neuron
        '''

        # Get activation map of the belonging block
        blk, n = neuron.split('-')
        n = int(n)
    
        if '_3x3' in blk:
            act_map_blk = act_map_neurons[1]
        elif '_5x5' in blk:
            act_map_blk = act_map_neurons[2]
        else:
            act_map_blk = act_map_neurons[0]

        # Activation map of the given neuron
        act_map_neuron = act_map_blk[:, :, :, n]
        return act_map_neuron


    def find_conn_act_maps(self, neuron, act_map_conns):
        '''
        Get activation maps of neuron of all images
        * input
            - neuron: neuron id
            - act_map_conns: activation map of all connections
        * output
            - act_map_conn: activation map of connections 
                of the given neuron
        '''

        # Get activation map of the belonging connection
        blk, n = neuron.split('-')
        n = int(n)
    
        if '_3x3' in blk:
            act_map_conn_blk = act_map_conns[-2]
            num_neurons_output = self.model.LAYER_BLK_SIZE[blk]
        elif '_5x5' in blk:
            act_map_conn_blk = act_map_conns[-1]
            num_neurons_output = self.model.LAYER_BLK_SIZE[blk]
        else:
            i = self.model.get_concat_blk_from_neuron(neuron)
            act_map_conn_blk = act_map_conns[i]
            o_blk = '{}_concat{}'.format(self.layer, i)
            num_neurons_output = self.model.LAYER_BLK_SIZE[o_blk]
            o_blk = '{}_concat{}'.format(self.layer, i)
            n -= self.model.CONCAT_OFFSET[o_blk]

        # Number of neurons in the input and output block
        num_conns = act_map_conn_blk.shape[-1]
        num_neurons_input = num_conns // num_neurons_output

        # Connection of the given neuron
        conn_idxs = np.array([
            i * num_neurons_output + n
            for i in range(num_neurons_input)
        ], dtype=np.intp)
        act_map_conn = act_map_conn_blk[:, :, :, conn_idxs]
        return act_map_conn    


    def jaccard_sim(self, A, B):
        '''
        Jaccard similarity of 2D matrix A and B
        * input
            - A
            - B
        * output
            - sim: jaccard similarity of A and B
        '''

        num_or = np.count_nonzero(A + B)
        num_and = np.count_nonzero(A * B)
        if num_or == 0:
            return 0
        else:
            return num_and / num_or



    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Function for time log
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def save_time_log(self, time_log, data_item, target='neuron'):
        '''
        Save activation data
        * input
            - time_log: Time log
            - data_item: one among 
                ['hash_value', 'gen_bucket', 'aggregated_bucket']
            - target: one among ['neuron', 'connection']
        * output
            - N/A
        '''

        # Path to save time log
        file_path = self.data_path.get_data_path(
            data_item,
            target=target,
            data_or_time='time'
        )

        # Save the time log
        with open(file_path, 'w') as f:
            f.write(time_log)
            
            
    
    