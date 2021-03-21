'''
* Project:
    Neuro-Cartography: Drawing Concept-based Neural Maps to Interpret 
    Deep Neural Networks by Automatically Discovering and Visualizing 
    Cell Assemblies
* File name:
    path.py
* Description:
    Utilities for retrieving paths for other codes and data
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Jan 30, 2020
'''


import os
import glob
import errno


class DataPath:
    '''
    Class for data path. Here's the file structure:
    
    neuro-cartography/data/
     |
     +-- <Model>/ (e.g., InceptionV1/)
     |   |
     |   +-- activation_threshold/
     |   +-- aggregated_bucket/
     |   +-- bucket/
     |   +-- example_patch/
     |   +-- hash_array/
     |   +-- hash_order/
     |   +-- hash_value/
     |   +-- time/
     |   +-- model/ (When the model is compressed)
     |
     +-- tfrec/
     |   |
     |   +-- train-<synset>.tfrec
     |   +-- ...
     
         
    '''
    
    def __init__(self, args):
        '''
        Constructor of DataPath class
        * input
            - args: parsed dataset
        * output
            - N/A
        '''
        
        # Arguments
        self.args = args
        
        # Base directory of data -- do not touch this
        self.base_dir = '../../data'
        
        # Data paths
        self.paths = {}

        # Sub directories
        self.SUB_DIRS = [
            'activation_threshold',
            'aggregated_bucket',
            'bucket',
            'co_activation',
            'embedding',
            'embedding_2d',
            'example_patch',
            'graph',
            'hash_array',
            'hash_order',
            'hash_value',
            'preprocess',
            'time'
        ]

        # Hyperparameters
        self.HYPER_PARAMETERS = {
            'activation_threshold': {
                'act_range': {
                    'neuron': [],
                    'connection': []
                },
                'act_hist': {
                    'neuron': [self.args.nbins],
                    'connection': [self.args.nbins]
                },
                'act_thr': {
                    'neuron': [
                        self.args.nbins,
                        self.args.thr_neuron
                    ],
                    'connection': [
                        self.args.nbins,
                        self.args.thr_connection
                    ]
                }
            },
            'preprocess': {
                'top_imgs': [
                    self.args.synset,
                    self.args.num_top_imgs
                ],
                'preprocessed_buckets': [
                    self.args.synset,
                    self.args.num_top_imgs,
                    self.args.band_size_top_imgs,
                    self.args.num_bands_top_imgs
                ],
                'agg_top_imgs': [
                    self.args.synset,
                    self.args.num_top_imgs,
                    self.args.band_size_top_imgs,
                    self.args.num_bands_top_imgs
                ]
            },
            'permutation': {
                'hash_array': [
                    self.args.H,
                    self.args.W
                ],
                'hash_order': [
                    self.args.synset,
                    self.args.num_hash_per_img
                ]
            },
            'lsh': {
                'hash_value': [
                    self.args.synset,
                    self.args.band_size,
                    self.args.num_bands
                ],
                'bucket': [
                    self.args.synset,
                    self.args.band_size,
                    self.args.num_bands
                ],
            },
            'graph': {
                'graph': {
                    'neuron': [
                        self.args.synset,
                        self.args.num_hash_per_img,
                        self.args.patch_size,
                        self.args.thr_neuron,
                        self.args.band_size,
                        self.args.thr_of_non_act
                    ],
                    'connection': [
                        self.args.synset,
                        self.args.num_hash_per_img,
                        self.args.patch_size,
                        self.args.thr_neuron,
                        self.args.thr_connection,
                        self.args.band_size,
                        self.args.thr_of_non_act
                    ]
                }   
            },
            'embedding': {
                'co_activation': [
                    self.args.num_top_imgs
                ],
                'embedding': [
                    self.args.embedding_dimension,
                    self.args.epoch,
                    self.args.num_negative_samples,
                    self.args.learning_rate
                ],
                'embedding_2d': [
                    self.args.embedding_dimension,
                    self.args.epoch,
                    self.args.num_negative_samples,
                    self.args.learning_rate
                ]
            }
        }

        # Data extension
        self.DATA_TYPE = {
            'activation_threshold': {
                'act_range': 'json',
                'act_hist': 'json',
                'act_thr': 'json'
            },
            'permutation': {
                'hash_array': 'dir',
                'hash_order': 'txt'
            },
            'lsh': {
                'hash_value': 'dir',
                'bucket': 'dir'
            },
            'graph': {
                'graph': 'dir',
            }
        }



    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Util functions
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def gen_dir(self, path):
        '''
        Generate a directory for a given path
        * input
            - path: directory path to generate
        * output
            - N/A
        '''
        
        try:
            os.mkdir(path)
            print('\'{}\' is generated'.format(path))
        except Exception as err:
            if err.errno != errno.EEXIST:
                print(err)


    def rm_empty_dirs(self, root):
        '''
        Removee empty directories
        * input
            - root: root directory
        * output
            - N/A 
        '''
        folders = list(os.walk(root))[1:]
        for folder in folders:
            if not folder[2]:
                os.rmdir(folder[0])

        

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Generate highest-level directories
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
   
    def gen_data_dirs(self):
        '''
        Generate data directories
        * input
            - N/A
        * output
            - N/A
        '''
        
        # Generate base data directory
        dir_path = self.base_dir
        self.gen_dir(dir_path)
        
        # Generate data directory for the model
        dir_path = '{}/{}'.format(dir_path, self.args.model_name)
        self.gen_dir(dir_path)
        
        # Generate data directories for Neuro-Cartography output
        for out_type in self.SUB_DIRS:
            out_dir_path = '{}/{}'.format(dir_path, out_type)
            self.gen_dir(out_dir_path)


    
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Generate data paths
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def gen_imagenet_path(self):
        '''
        Generate path for imagenet data in trecord
        * input
            - N/A
        * ouput
            - N/A
        '''

        # Check if there exist paths already
        if 'imagenet' in self.paths:
            return

        # Initialize self.paths['imgenet']
        imagenet_dir = '{}/tfrec'.format(self.base_dir)
        self.paths['imagenet'] = {
            'all': [],
            'synset': [],
            'synsets': []
        }

        # 'all': Imagenet path of all classes
        self.paths['imagenet']['all'] = sorted(
                glob.glob(imagenet_dir + '/*')
            ) 

        # 'synsets': Imagenet path of selected synsets
        with open('{}/synsets.txt'.format(self.base_dir), 'r') as f:
            synsets = f.readlines()
        synsets = [s[:-1] for s in synsets]
        self.paths['imagenet']['synsets'] = [
            '{}/train-{}.tfrec'.format(imagenet_dir, s)
            for s in synsets
        ]

        # 'synset': Imagenet path of selected one synset
        synset = self.args.synset
        img_path = '{}/train-{}.tfrec'.format(imagenet_dir, synset)
        self.paths['imagenet']['synset'] = [img_path]


    def gen_activation_threshold_path(self):
        '''
        Generate data path for activation thresholds
        * input
            - N/A
        * output
            - N/A
        '''

        start_dir = '{}/{}/activation_threshold'.format(
            self.base_dir, self.args.model_name
        )
        act_thr_hyp = self.HYPER_PARAMETERS['activation_threshold']

        for item in act_thr_hyp:

            if item in self.paths:
                continue

            self.paths[item] = {}
            
            for target in ['neuron', 'connection']:
                self.paths[item][target] = {}
                hy_paras = act_thr_hyp[item][target]
                apdx = [item, target] + list(map(str, hy_paras))
                self.paths[item][target]['data'] = '{}/{}.json'.format(
                    start_dir,
                    '-'.join(apdx)
                )
                self.paths[item][target]['time'] = '{}/{}.txt'.format(
                    start_dir,
                    '-'.join(apdx)
                )


    def gen_preprocess_path(self): 
        '''
        Generate path for preprocessed data
        '''

        # Get ready
        start_dir = '{}/{}'.format(
            self.base_dir, self.args.model_name
        )
        hy_paras = self.HYPER_PARAMETERS['preprocess']
        
        for item in hy_paras:

            if item in self.paths:
                continue
            
            hyps = hy_paras[item]
            apdx = [item] + list(map(str, hyps))
            apdx = '-'.join(apdx)
            self.paths[item] = {
                'data': '{}/preprocess/{}'.format(start_dir, apdx),
                'time': '{}/time/{}.txt'.format(start_dir, apdx)
            }


    def gen_permutation_path(self):
        '''
        Generate data path for activation permutation
        * input
            - N/A
        * output
            - N/A
        '''

        # Get ready
        start_dir = '{}/{}'.format(
            self.base_dir, self.args.model_name
        )
        hy_paras = self.HYPER_PARAMETERS['permutation']

        # Generate path
        for item in hy_paras:
            if item in self.paths:
                continue
            hyps = hy_paras[item]
            apdx = [item] + list(map(str, hyps))
            apdx = '-'.join(apdx)
            path = '{}/{}/{}'.format(
                start_dir, item, apdx
            )
            if item == 'hash_order':
                path += '.txt'
            self.paths[item] = {
                'data': path,
                'time': '{}/{}/{}.txt'.format(
                    start_dir, 'time', apdx
                )
            }


    def gen_hash_value_path(self):
        '''
        Generate hash value path
        '''

        # Check if the path is already generated
        item = 'hash_value'
        if item in self.paths:
            return

        # Get ready
        start_dir = '{}/{}'.format(self.base_dir, self.args.model_name)
        hy_paras = self.HYPER_PARAMETERS['lsh'][item]

        # Data path
        apdx = [item] + list(map(str, hy_paras))
        apdx = '-'.join(apdx)
        path = '{}/{}/{}'.format(
            start_dir, item, apdx
        )
        self.paths[item] = {
            'data': path,
            'time': '{}/{}/{}.txt'.format(
                start_dir, 'time', apdx
            )
        }


    def gen_bucket_path(self):
        '''
        Generate bucket path
        '''

        # Get ready
        item = 'bucket'
        start_dir = '{}/{}'.format(
            self.base_dir, self.args.model_name
        )
        hy_paras = self.HYPER_PARAMETERS['lsh'][item]

        # Dir path
        apdx = [item] + list(map(str, hy_paras))
        apdx = '-'.join(apdx)
        path = '{}/{}/{}'.format(
            start_dir, item, apdx
        )

        # Data path 
        self.paths[item] = {
            'data': path,
            'time': '{}/{}/{}-{}.txt'.format(
                start_dir, 'time', self.args.blk, apdx
            )
        }


    def gen_graph_path(self):
        '''
        Generate paths for graph
        * input
            - N/A
        * output
            - N/A
        '''

        # TODO: Do this later and remove gen_data_path()
        pass


    def gen_emb_path(self):
        '''
        Generate paths for embedding
        * input
            - N/A
        * output
            - N/A
        '''

        # Get ready
        start_dir = '{}/{}'.format(
            self.base_dir, self.args.model_name
        )
        hy_paras = self.HYPER_PARAMETERS['embedding']

        # Generate path
        for item in hy_paras:

            # Check if the path is already generated
            if item in self.paths:
                continue

            # Dir path
            apdx = [item] + list(map(str, hy_paras[item]))
            apdx = '-'.join(apdx)
            path = '{}/{}/{}'.format(
                start_dir, item, apdx
            )

            # Data path
            self.paths[item] = {
                'data': path,
                'time': '{}/{}/{}.txt'.format(
                    start_dir, 'time', apdx
                )
            }


    def gen_comp_model_path(self):
        '''
        Generate compressed model path
        '''

        start_dir = '{}/{}'.format(
            self.base_dir, self.args.model_name
        )

        self.paths['compressed_model'] = \
            '{}/model/saved_model_{}.pb'.format(
                start_dir, self.args.compression_ratio
            )


    def gen_data_path(self, category):
        '''
        Generate paths for the given category
        * input
            - category: data category
        * output
            - N/A
        '''
        
        return
        
        # Get ready
        start_dir = '{}/{}'.format(self.base_dir, self.args.model_name)
        
        # Get the relevant data paths
        hyperparas = self.HYPER_PARAMETERS[category]
        for item in hyperparas:
            
            # Get ready
            self.paths[item] = {}
            hy_paras = hyperparas[item]

            # If there is target
            if 'neuron' in hy_paras:
                for target in ['neuron', 'connection']:

                    # Appendix for file path
                    hy_paras = hyperparas[item][target]
                    apdx = [item, target] + list(map(str, hy_paras))

                    # Generate data path
                    self.paths[item][target] = {}
                    ext = self.DATA_TYPE[category][item]
                    path = '{}/{}/{}'.format(
                        start_dir,
                        category if 'act' in category else item,
                        '-'.join(apdx)
                    )
                    if ext == 'dir':
                        if (item == 'hash_value') and (target == 'target'):
                            continue
                        # self.gen_dir(path)
                    else:
                        path += '.{}'.format(ext)
                    self.paths[item][target]['data'] = path

                    # Generate time path
                    self.paths[item][target]['time'] = \
                        '{}/{}/{}.txt'.format(
                            start_dir,
                            'time',
                            '-'.join(apdx)
                        )

            # If there is no target
            else:

                # Appendix for file path
                apdx = [item] + list(map(str, hy_paras))

                # Generate data path
                self.paths[item] = {}
                ext = self.DATA_TYPE[category][item]
                path = '{}/{}/{}'.format(
                    start_dir,
                    category if 'act' in category else item,
                    '-'.join(apdx)
                )
                if ext == 'dir':
                    pass
                    # self.gen_dir(path)
                else:
                    path += '.{}'.format(ext)
                self.paths[item]['data'] = path
                
                # Generate time path
                self.paths[item]['time'] = \
                    '{}/{}/{}.txt'.format(
                        start_dir,
                        'time',
                        '-'.join(apdx)
                    )

        self.paths['example_patch'] = '{}/{}'.format(
            start_dir,
            'example_patch'
        )


    
        
        
    




    def get_imagenet_path(self, option=None):
        '''
        Get imagenet paths
        * input
            - option: 'All', 'Samples', or synset id
        * output
            - imagenet paths
        '''

        if option is None:
            option = self.args.synset

        if 'all' in self.args.synset.lower():
            return self.paths['imagenet']['all']
        elif 'sample' in self.args.synset.lower():
            return self.paths['imagenet']['synsets']
        else:
            return self.paths['imagenet']['synset']


    def get_data_path(self, item, target=None, data_or_time='data'):
        '''
        Get data path
        * input
            - item: data item (e.g., 'act_range')
            - target: either 'neuron' or 'connection'
            - data_or_time: either 'data' or 'time'
        * output
            - the corresponding data path
        '''

        if item == 'imagenet':
            self.gen_imagenet_path()
            return self.get_imagenet_path()

        elif 'act_' in item:
            self.gen_activation_threshold_path()
            return self.paths[item][target][data_or_time]

        elif 'top_imgs' in item:
            self.gen_preprocess_path()
            return self.paths[item][data_or_time]   

        elif 'prepro' in item:
            self.gen_preprocess_path()
            return self.paths[item][data_or_time]    

        elif 'hash_array' in item:
            self.gen_permutation_path()
            return self.paths[item][data_or_time]

        elif 'hash_order' in item:
            self.gen_permutation_path()
            return self.paths[item][data_or_time]

        elif 'hash_value' in item:
            self.gen_hash_value_path()
            return self.paths[item][data_or_time]
        
        elif 'bucket' in item: 
            self.gen_bucket_path()
            return self.paths[item][data_or_time]

        elif 'co_act' in item:
            self.gen_emb_path()
            return self.paths[item][data_or_time]
        
        elif 'embedding' in item:
            self.gen_emb_path()
            return self.paths[item][data_or_time]


        def get_path():
            if target is None:
                return self.paths[item]
            elif target in self.paths[item]:
                return self.paths[item][target][data_or_time]
            else:
                if data_or_time in self.paths[item]:
                    return self.paths[item][data_or_time]
                else: 
                    return self.paths[item]
        
        try:
            return get_path()                       
        except:

            # Generate path
            if 'imagenet' in item:
                self.gen_imagenet_path()
            elif 'act_' in item:
                self.gen_data_path('activation_threshold')
            elif 'hash' in item:
                self.gen_data_path('permutation')
                self.gen_data_path('lsh')
            else:
                self.gen_data_path('graph')

            # Get path
            return get_path()
            
            
    