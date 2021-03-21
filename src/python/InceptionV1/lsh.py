'''
* Project:
    Neuro-Cartography: Drawing Concept-based Neural Maps to Interpret 
    Deep Neural Networks by Automatically Discovering and Visualizing 
    Cell Assemblies
* File name:
    lsh.py
* Description:
    Hash neurons by LSH after preprocessing
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
    Class for grouping neurons by LSH
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def __init__(self, args, data_path, model_wrapper):

        # Model
        self.model = model_wrapper.model

        # Data path
        self.data_path = data_path

        # Hyperparameters
        self.blk = args.blk
        self.batch_size = args.batch_size
        self.R = args.band_size
        self.B = args.num_bands

        # Global variables
        self.batch_idx = 0

        # Data
        self.top_imgs = {}
        self.pre_groups = {}
        self.hash_vals = {}
        self.group_img_i = {}
        self.agg_groups = {}


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Compute hash values
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def compute_hash_values(self):
        '''
        Compute hash values
        '''

        # Check time
        tic = time()

        # Load top images
        self.load_top_imgs()

        # Load preprocessed groups
        self.load_preprocessed_groups()

        # Initialize self.hash_vals
        self.init_hash_vals()

        # Compute hash values
        data, time_log = self.model.compute_data(
            self.compute_t_act,
            [],
            self.compute_hash_vals_neurons,
            []
        )
        self.batch_idx = 0

        # Save hash_vals
        self.save_hash_vals()

        # Save time log
        toc = time()
        time_log = 'compute_hash_values after preprocess\n'
        time_log += '%.2lf \n' % (toc - tic)
        self.save_time_log('hash_value', time_log)


    def init_hash_vals(self):
        '''
        Initialize self.hash_vals
        * input
            - N/A
        * output
            - N/A
        '''

        for group in self.pre_groups:

            self.hash_vals[group] = {}
            self.group_img_i[group] = 0

            num_imgs = 0
            for batch_idx in self.top_imgs[group]:
                num_imgs += len(self.top_imgs[group][batch_idx])

            for n in self.pre_groups[group]:
                neuron = '{}-{}'.format(self.blk, n)
                self.hash_vals[group][neuron] = \
                    np.zeros((num_imgs, self.B, self.R)) - 1
                

    def compute_t_act(self):
        '''
        Compute activation maps
        * input
            - N/A
        * output
            - t_blk: act map of the block
        '''

        t_blk = self.model.get_t_blk(self.blk)
        return t_blk


    def compute_hash_vals_neurons(self, data, sess_data):
        '''
        Compute hash values based on activation map
        * input
            - N/A
        * output
            - N/A
        '''

        for group in self.pre_groups:
            
            # Skip if there is no top images for this batch
            if self.batch_idx not in self.top_imgs[group]:
                continue
            
            # Get activation maps of neurons for top images
            img_indexes = self.top_imgs[group][self.batch_idx]
            neurons = self.pre_groups[group]
            act_maps = sess_data[img_indexes]
            act_maps = act_maps[:, :, :, neurons]
            
            # Compute hash values for each neuron
            H, W = act_maps.shape[1], act_maps.shape[2]
            for img_ii, img_i in enumerate(img_indexes):

                for b in range(self.B):

                    for neuron_i, n in enumerate(neurons):

                        # Find activated grid in act map
                        act_map = act_maps[img_ii, :, :, neuron_i]
                        act_r, act_c = np.where(act_map > 0)

                        # Compute hash values for each r
                        for r in range(self.R):
                            
                            # Hash function
                            h_f = np.random.permutation(
                                np.arange(H * W)
                            )

                            # Permutation value
                            p_vals = [
                                h_f[row * W + col]
                                for row, col in zip(act_r, act_c)
                            ]

                            # Min hash value
                            if len(p_vals) == 0:
                                h = -1
                            else:
                                h = np.min(p_vals)

                            # Add min hash value to self.hash_vals
                            neuron = '{}-{}'.format(self.blk, n)
                            hash_val_img_i = self.group_img_i[group]
                            self.hash_vals[group][neuron][
                                hash_val_img_i, b, r
                            ] = h
                self.group_img_i[group] += 1

        self.batch_idx += 1


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    LSH
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def lsh_neurons(self):
        '''
        LSH
        * input
            - N/A
        * output
            - N/A
        '''

        # Check time
        tic = time()

        # Load hash values
        self.load_hash_vals()

        # Hash neurons by bands for each group, image
        buckets = {}
        for group in self.hash_vals:

            # Get ready
            buckets[group] = {}
            fst_neuron = list(self.hash_vals[group].keys())[0]
            num_imgs = self.hash_vals[group][fst_neuron].shape[0]
            neurons = list(self.hash_vals[group].keys())

            for img_i in range(num_imgs):

                buckets[group][img_i] = {}

                # For each band, hash neurons by AND approach
                for b in range(self.B):

                    buckets[group][img_i][b] = {}
                    for n in neurons:
                        hash_key = ','.join(list(map(
                            str,
                            self.hash_vals[group][n][img_i, b, :]
                        )))
                        if hash_key not in buckets[group][img_i][b]:
                            buckets[group][img_i][b][hash_key] = []
                        buckets[group][img_i][b][hash_key].append(n)

                # Aggregate buckets by OR approach
                e2g, g2e, group_number = {}, {}, 0
                for band_i in buckets[group][img_i]:

                    # Cluster buckets
                    bucket = buckets[group][img_i][band_i]
                    for hash_key in bucket:

                        # Find groups to merge
                        groups_to_merge = self.find_groups_to_merge(
                            bucket[hash_key], 
                            group_number, 
                            e2g, 
                            g2e
                        )

                        # Merge the groups
                        e2g, g2e = self.merge_entity_group(
                                groups_to_merge, 
                                group_number,
                                e2g, 
                                g2e
                            )

                        # Update group number
                        group_number += 1

                # Parse aggregated buckets
                aggregated_buckets, group_id = {}, 0
                for g in g2e:
                    if len(g2e[g]) > 1:
                        aggregated_buckets[group_id] = g2e[g]
                        group_id += 1

                buckets[group][img_i] = {
                    g: aggregated_buckets[g]
                    for g in aggregated_buckets
                }

        # Count co-occurrence for neuron pairs
        stats = {}
        for g in buckets:
            stats[g] = {}
            stats[g]['total'] = len(buckets[g])
            for img_i in buckets[g]:
                for gg in buckets[g][img_i]:
                    neurons = buckets[g][img_i][gg]
                    for n1 in neurons:
                        for n2 in neurons:
                            if n1 == n2:
                                continue
                            key = tuple(sorted([n1, n2]))
                            if key not in stats[g]:
                                stats[g][key] = 0
                            stats[g][key] += 0.5

        # Aggregate neurons
        agg_groups, agg_group_i = {}, 0
        for g in stats:

            total = stats[g]['total']
            e2g, g2e, group_number = {}, {}, 0

            for key in stats[g]:

                if key == 'total':
                    continue

                n_pair = key
                cnt = stats[g][n_pair]

                if cnt > 0:

                    # Find groups to merge
                    groups_to_merge = self.find_groups_to_merge_CO_OC(
                        n_pair, group_number, e2g, g2e
                    )

                    # Merge the groups
                    e2g, g2e = \
                    self.merge_entity_group(
                        groups_to_merge, 
                        group_number,
                        e2g, 
                        g2e
                    )

                    group_number += 1

            if len(g2e) > 0:
                for subgroup in g2e:
                    if len(g2e[subgroup]) > 1:
                        agg_groups[agg_group_i] = g2e[subgroup]
                        agg_group_i += 1
                        
        # Save agg_groups
        self.agg_groups = agg_groups
        self.save_aggregated_groups()

        # Check time
        toc = time()
        time_log = 'LSH main clustering after computing hash vals\n'
        time_log += '%.2lf sec\n' % (toc - tic)
        self.save_time_log('bucket', time_log)
        


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

    
    def find_groups_to_merge(self, one_bucket, group_n, e2g, g2e):
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


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Save and load data
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def load_top_imgs(self):
        '''
        Load top images for the groups
        '''

        # File path
        dir_path = self.data_path.get_data_path(
            'agg_top_imgs', data_or_time='data'
        )
        file_path = '{}/agg_top_imgs-{}.json'.format(
            dir_path, self.blk
        )

        # Load top imgs
        with open(file_path, 'r') as f:
            data = json.load(f)
        data = {
            group:
            list(map(int, data[group]))
            for group in data
        }

        # Split the images by batch idx
        for group in data:
            self.top_imgs[group] = {}
            for img in data[group]:

                batch_idx = img // self.batch_size
                if batch_idx not in self.top_imgs[group]:
                    self.top_imgs[group][batch_idx] = []
                self.top_imgs[group][batch_idx].append(
                    img % self.batch_size
                )


    def load_preprocessed_groups(self):
        '''
        Load preprocessed groups
        * input
            - N/A
        * output
            - N/A
        '''

        # File path
        dir_path = self.data_path.get_data_path(
            'preprocessed_buckets', data_or_time='data'
        )
        file_path = '{}/preprocessed_buckets-{}.json'.format(
            dir_path, self.blk
        )

        # Load data
        with open(file_path, 'r') as f:
            data = json.load(f)
        self.pre_groups = {
            key:
            sorted(list(map(int, data[key])))
            for key in data
        }

    
    def save_hash_vals(self):
        '''
        Save hash values
        * input
            - N/A
        * output
            - N/A
        '''

        # Generate path
        dir_path = self.data_path.get_data_path(
            'hash_value', data_or_time='data'
        )
        self.data_path.gen_dir(dir_path)
        file_path = '{}/hash_values-{}.json'.format(
            dir_path, self.blk
        )

        # Parse self.hash_vals
        data = {}
        for group in self.hash_vals:
            data[group] = {}
            for neuron in self.hash_vals[group]:
                data[group][neuron] = \
                    ','.join(list(map(
                        lambda x: str(int(x)), 
                        self.hash_vals[group][neuron].reshape(-1)
                    )))
        
        # Save self.hash_vals
        with open(file_path, 'w') as f:
            json.dump(data, f)

    
    def load_hash_vals(self):
        '''
        Load hash values
        * input
            - N/A
        * output
            - N/A
        '''

        # Generate path
        dir_path = self.data_path.get_data_path(
            'hash_value', data_or_time='data'
        )
        self.data_path.gen_dir(dir_path)
        file_path = '{}/hash_values-{}.json'.format(
            dir_path, self.blk
        )

        # Load data
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Parse data
        for group in data:
            self.hash_vals[group] = {}
            for neuron in data[group]:
                arr = np.array(list(map(
                        int,
                        data[group][neuron].split(',')
                    )))
                num_imgs = len(arr) // (self.B * self.R)

                arr = arr.reshape(
                        num_imgs,
                        self.B,
                        self.R
                    )
                self.hash_vals[group][neuron] = arr


    def save_aggregated_groups(self):
        '''
        Save aggregated groups
        '''

        # Data path
        dir_path = self.data_path.get_data_path(
            'bucket', data_or_time='data'
        )
        self.data_path.gen_dir(dir_path)
        file_path = '{}/buckets-{}.json'.format(
            dir_path, self.blk
        )

        # Save data
        with open(file_path, 'w') as f:
            json.dump(self.agg_groups, f)


    def save_time_log(self, item, time_log):
        '''
        Save time log
        * input
            - N/A
        * output
            - N/A
        '''

        file_path = self.data_path.get_data_path(
            item, data_or_time='time'
        )

        with open(file_path, 'w') as f:
            f.write(time_log + '\n')

