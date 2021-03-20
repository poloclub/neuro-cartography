'''
* Project:
    Neuro-Cartography: Drawing Concept-based Neural Maps to Interpret 
    Deep Neural Networks by Automatically Discovering and Visualizing 
    Cell Assemblies
* File name:
    hasharr.py
* Description:
    Generate 2D permutation data
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Jan 30, 2020
'''

import numpy as np


class Perm2D:
    
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Class for generating hash arrays and orders for LSH
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def __init__(self, args, data_path, model_wrapper):

        self.args = args
        self.data_path = data_path
        self.H, self.W = args.H, args.W
        self.num_perm_sample = args.num_perm_sample
        self.num_hash_per_img = args.num_hash_per_img
        self.num_imgs = model_wrapper.model.num_imgs
        self.num_hash = self.num_hash_per_img * self.num_imgs


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for hash arrays
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def gen_hash_arrs(self):
        '''
        Generate hash arrays
        * input
            - N/A
        * ouput
            - N/A
        '''
        
        # Save permutations
        H, W = self.H, self.W
        num_pixels = H * W
        i, permute_dict = 0, {}
        while True:
            
            if i == self.num_perm_sample:
                break
            
            rand_permutation = np.random.permutation(np.arange(num_pixels))
            
            key = tuple(rand_permutation)
            if key not in permute_dict:
                rand_permutation = np.array(list(map(
                    lambda v: [v // W, v % W],
                    rand_permutation
                )))
                permute_dict[key] = rand_permutation
                i += 1

        for i, key in enumerate(permute_dict):
            self.save_hash_arr(permute_dict[key], i)
            
            
    def save_hash_arr(self, arr, i):
        '''
        Save hash array
        * input
            - arr: hash array
            - i: index of hash array
        * output
            - N/A
        '''
        
        # Generate data directory
        dir_path = self.data_path.get_data_path(
            'hash_array', 
            data_or_time='data'
        )
        self.data_path.gen_dir(dir_path)
        
        # Save array
        file_path = '{}/{}.txt'.format(dir_path, i)
        np.savetxt(file_path, arr, fmt='%d')
        
    
    def load_hash_arr(self, i, reshape=None):
        '''
        Load hash array
        * input
            - i: index of hash array
            - reshape: shape of reshaped array
        * output
            - N/A
        '''
        
        dir_path = self.data_path.get_data_path(
            'hash_array', 
            data_or_time='data'
        )
        file_path = '{}/{}.txt'.format(dir_path, i)
        data = np.loadtxt(file_path).astype(int)
        
        if reshape is not None:
            data = data.reshape(reshape)
            
        return data
    
    
    def load_all_hash_arrs(self):
        '''
        Load all hash arrays
        * input
            - N/A
        * output
            - data: all hash arrays (N, H, W)
        '''
        
        H, W = self.H, self.W
        data = np.zeros((self.num_perm_sample, H * W, 2))
        for i in range(self.num_perm_sample):
            arr = self.load_hash_arr(i)
            data[i] = arr
        
        return data


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for hash orders
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def gen_hash_order(self):
        '''
        Generate and save hash order
        * input
            - N/A
        * output
            - N/A
        '''
        
        hash_order = np.random.randint(
            0, self.num_perm_sample, self.num_hash
        )
        self.save_hash_order(hash_order)
        

    def save_hash_order(self, hash_order):
        '''
        Save hash order
        * input
            - hash_order: hash order array
        * output
            - N/A
        '''
        
        # Save hash order
        file_path = self.data_path.get_data_path(
            'hash_order',
            data_or_time='data'
        )
        np.savetxt(file_path, hash_order, fmt='%d')
        
        
    def load_hash_order(self):
        '''
        load hash order
        * input
            - N/A
        * output
            - hash order: hash order array
        '''
        
        file_path = self.data_path.get_data_path(
            'hash_order',
            data_or_time='data'
        )
        data = np.loadtxt(file_path).astype(int)
        return data
        