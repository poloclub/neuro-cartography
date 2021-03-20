'''
* Project:
    Neuro-Cartography: Drawing Concept-based Neural Maps to Interpret 
    Deep Neural Networks by Automatically Discovering and Visualizing 
    Cell Assemblies
* File name:
    main.py
* Description:
    Run the whole code
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Jan 30, 2020
'''

import json
import tqdm
import numpy as np
import tensorflow as tf
from time import time


class Preprocess:

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Class for preprocessing
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def __init__(self, args, data_path, model_wrapper):

        # Data
        self.top_imgs = {}
        self.hash_fn = {}
        self.buckets = {}
        self.aggregated_buckets = {}
        self.top_imgs_for_groups = {}

        # Model
        self.model = model_wrapper.model
        self.blk = args.blk
        self.num_imgs = self.model.get_number_of_input_imgs()

        # Data path
        self.data_path = data_path

        # Hyperparameters
        self.N = args.num_top_imgs
        self.batch_size = args.batch_size
        self.R = args.band_size_top_imgs
        self.B = args.num_bands_top_imgs

        # Global variable
        self.img_idx = 0


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Find top images for each neuron
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def find_top_imgs(self):
        '''
        Find top images and save the information 
        into self.imgs
        * input
            - N/A
        * output
            - N/A
        '''

        # Max activation matrix
        data, time_log = self.model.compute_data(
            self.compute_t_act_max,
            [],
            self.parse_t_act_max,
            []
        )
        self.img_idx = 0
        time_log_starter = self.blk + '\n'
        time_log_starter += 'Max act\n'
        time_log = time_log_starter + time_log

        # Find top images
        tic = time()
        blk = self.blk
        num_neurons = data[blk].shape[-1]
        self.top_imgs[blk] = np.zeros(
            (self.N, num_neurons)
        )
        with tqdm.tqdm(total=num_neurons) as pbar:
            for n in range(num_neurons):
                acts_n = data[blk][:, n]
                top_imgs_n = np.argsort(-acts_n)[:self.N]
                self.top_imgs[blk][:, n] = top_imgs_n
                pbar.update(1)

        toc = time()
        time_log += 'Find top imgs: %.2lf sec' % (toc - tic)

        # Save self.top_imgs
        self.save_top_imgs()

        # Save time log
        self.save_time_log('top_imgs', time_log)


    def compute_t_act_max(self):
        '''
        Compute tensor of activation max
        * input
            - N/A
        * output
            - tensors: tensors of max activation
        '''

        t_blk = self.model.get_t_blk(self.blk)
        t_max = tf.math.reduce_max(t_blk, axis=[1, 2])

        return t_max


    def parse_t_act_max(self, data, sess_data):
        '''
        Parse max activation
        * input
            - data: data before udpated
            - sess_data: data in the current session
        * output
            - data: updated data
        '''

        # Index out of range
        if len(sess_data) == 0:
            return data

        # Image index
        img_s = self.img_idx
        img_e = self.img_idx + self.batch_size

        # Reduced max activation map
        act_max = sess_data
        num_neurons = act_max.shape[-1]

        if self.blk not in data:
            data[self.blk] = np.zeros(
                (self.num_imgs, num_neurons)
            )
        data[self.blk][img_s: img_e, :] = act_max

        self.img_idx += self.batch_size

        return data

    

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    LSH to group neurons based on top images
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def lsh_by_top_imgs(self):
        '''
        Run LSH to group neurons based on the top images
        '''

        # Check time
        tic = time()

        # Load top_imgs
        self.load_top_imgs()

        # Generate hash functions
        self.gen_hash_functions()

        # Hash neurons into buckets by bands        
        self.hash_neurons_by_bands()

        # Aggregate buckets
        self.aggregate_buckets()

        # Save aggregated buckets
        self.save_aggregated_buckets()

        # Save time log
        toc = time()
        time_log = 'LSH by top images\n'
        time_log += 'blk: {}\n'.format(self.blk)
        time_log += '%.2lf sec\n' % (toc - tic)
        self.save_time_log(
            'preprocessed_buckets', time_log
        )


    def gen_hash_functions(self):
        '''
        Generate random pemutation function
        * input
            - N/A
        * output
            - N/A
        '''

        # Number of images
        num_imgs = np.max(self.top_imgs[self.blk]) + 1

        # Generate hash functions
        hash_fn = {}
        for b in range(self.B):
            hash_fn[b] = {}
            for r in range(self.R):
                hash_fn[b][r] = \
                    np.random.permutation(
                        np.arange(num_imgs)
                    )

        self.hash_fn = hash_fn


    def hash_neurons_by_bands(self):
        '''
        Hash neurons by bands
        * input
            - N/A
        * output
            - N/A
        '''

        # Number of images
        data = self.top_imgs[self.blk] 
        num_imgs = np.max(data) + 1
        num_neurons = data.shape[-1]

        # LSH by bands
        buckets = {}
        with tqdm.tqdm(total=self.B) as pbar:
            for b in range(self.B):
                buckets[b] = {}
                for n in range(num_neurons):
                    hash_vals = []
                    for r in range(self.R):
                        vals = [
                            self.hash_fn[b][r][i] 
                            for i in data[:, n]
                        ]
                        h = np.min(vals)
                        hash_vals.append(h)
                    hash_key = ','.join(list(map(str, hash_vals)))
                    if hash_key not in buckets[b]: 
                        buckets[b][hash_key] = []
                    buckets[b][hash_key].append(n)
                pbar.update(1)
        self.buckets = buckets


    def aggregate_buckets(self):
        '''
        Aggregate buckets of all bands
        * input
            - N/A
        * output
            - N/A
        '''

        # Aggregate buckets of all bands
        entity_to_group, group_to_entity, group_number = {}, {}, 0
        with tqdm.tqdm(total=self.B, unit='bands') as pbar:
            
            for band_i in self.buckets:

                # Cluster buckets
                bucket = self.buckets[band_i]
                for hash_key in bucket:

                    # Find groups to merge
                    groups_to_merge = self.find_groups_to_merge(
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

        # Parse aggregated buckets
        aggregated_buckets, group_id = {}, 0
        for group in group_to_entity:
            if len(group_to_entity[group]) > 1:
                aggregated_buckets[group_id] = group_to_entity[group] 
                group_id += 1

        self.aggregated_buckets = aggregated_buckets

                
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
    Generate set of top images for each group
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def find_top_imgs_for_each_group(self):
        '''
        Find set of top images for each group
        * input
            - N/A
        * output
            - N/A
        '''

        # Load data
        self.load_top_imgs()
        self.load_aggregated_buckets()

        # Find top images for each group
        for group in self.aggregated_buckets:
            self.top_imgs_for_groups[group] = {}
            for neuron in self.aggregated_buckets[group]:
                top_imgs = self.top_imgs[self.blk][:, neuron]
                for i in top_imgs:
                    self.top_imgs_for_groups[group][i] = True

        for group in self.top_imgs_for_groups:
            self.top_imgs_for_groups[group] = list(
                self.top_imgs_for_groups[group].keys()
            )

        # Save top images for each group
        self.save_top_imgs_for_groups()


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Load and save data
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def save_top_imgs(self):
        '''
        Save top images of neurons
        * input
            - N/A
        * output
            - N/A
        '''

        dir_path = self.data_path.get_data_path(
            'top_imgs', data_or_time='data'
        )
        print(dir_path)
        self.data_path.gen_dir(dir_path)

        file_path = '{}/top_imgs-{}.txt'.format(
            dir_path, self.blk
        )
        np.savetxt(file_path, self.top_imgs[self.blk], fmt='%d')

    
    def load_top_imgs(self):
        '''
        Load top images of neurons
        * input
            - N/A
        * output
            - N/A
        '''

        dir_path = self.data_path.get_data_path(
            'top_imgs', data_or_time='data'
        )

        file_path = '{}/top_imgs-{}.txt'.format(
            dir_path, self.blk
        )
        data = np.loadtxt(file_path, dtype=int)
        self.top_imgs[self.blk] = data

    
    def save_aggregated_buckets(self):
        '''
        Save aggregated buckets
        * input
            - N/A
        * output
            - N/A
        '''

        dir_path = self.data_path.get_data_path(
            'preprocessed_buckets', data_or_time='data'
        )
        self.data_path.gen_dir(dir_path)

        file_path = '{}/preprocessed_buckets-{}.json'.format(
            dir_path, self.blk
        )

        agg_buckets = {
            key:
            list(map(str, self.aggregated_buckets[key]))
            for key in self.aggregated_buckets
        }
        with open(file_path, 'w') as f:
            json.dump(agg_buckets, f)


    def load_aggregated_buckets(self):
        '''
        Load aggregated buckets
        * input
            - N/A
        * output
            - N/A
        '''

        dir_path = self.data_path.get_data_path(
            'preprocessed_buckets', data_or_time='data'
        )

        file_path = '{}/preprocessed_buckets-{}.json'.format(
            dir_path, self.blk
        )

        with open(file_path, 'r') as f:
            data = json.load(f)

        self.aggregated_buckets = {
            key:
            list(map(int, data[key]))
            for key in data
        }


    def save_top_imgs_for_groups(self):
        '''
        Save top images for each group
        '''

        dir_path = self.data_path.get_data_path(
            'agg_top_imgs', data_or_time='data'
        )
        self.data_path.gen_dir(dir_path)

        file_path = '{}/agg_top_imgs-{}.json'.format(
            dir_path, self.blk
        )

        top_imgs_for_groups = {
            key:
            list(map(str, self.top_imgs_for_groups[key]))
            for key in self.top_imgs_for_groups
        }

        with open(file_path, 'w') as f:
            json.dump(top_imgs_for_groups, f)



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
