'''
* Project:
    Neuro-Cartography: Drawing Concept-based Neural Maps to Interpret 
    Deep Neural Networks by Automatically Discovering and Visualizing 
    Cell Assemblies
* File name:
    load_model.py
* Description:
    Load CNN model
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Jan 30, 2020
'''


import sys
from InceptionV1.activation_threshold import *
from InceptionV1.perm_2d import *
from InceptionV1.lsh import *
from InceptionV1.gen_graph import *
from InceptionV1.example_patch import *
from InceptionV1.preprocessing import *
from InceptionV1.neuron_embedding import *


class ModelWrapper:

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Class for model wrapper
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def __init__(self, args, data_path):

        sys.path.append('..')
        self.model_name = args.model_name
        self.args = args
        self.model = None
        self.act_thr = None
        self.preprocess = None
        self.perm_2d = None
        self.lsh = None
        self.graph = None
        self.ex_patch = None
        self.emb = None
        self.data_path = data_path



    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Load model of the user's choice
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def load_model(self):
        
        if self.model_name == 'InceptionV1':
            
            from InceptionV1.InceptionV1 import InceptionV1
            self.model = InceptionV1(self.args)
            self.model.load_model()


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for activation threshold
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def get_act_thr_obj(self): 
        '''
        Get object of activation threshold
        * input
            - N/A
        * output
            - self.act_thr: object of ActThreshold
        '''
        
        if self.act_thr is None:
            
            self.data_path.gen_activation_threshold_path()
                
            # Check model
            if self.model is None:
                self.load_model()
                
            # Generate activation threshold object
            self.act_thr = ActThreshold(
                self.args, self.data_path, self
            )
            
        return self.act_thr
    
    
    def compute_activation_threshold_for_neurons(self):
        '''
        Compute activation threshold for neurons
        * input
            - N/A
        * output
            - N/A
        '''
        
        act_thr = self.get_act_thr_obj()
        
        if self.args.act_range_neuron:
            act_thr.compute_act_range_of_neurons()
            
        if self.args.act_hist_neuron:
            act_thr.compute_act_histogram_of_neurons()
            
        if self.args.act_thr_neuron:
            act_thr.compute_act_threshold('neuron')
            
            
    def compute_activation_threshold_for_connections(self):
        '''
        Compute activation threshold for connections
        * input
            - N/A
        * output
            - N/A
        '''
        
        act_thr = self.get_act_thr_obj()
        
        if self.args.act_range_connection:    
            act_thr.compute_act_range_of_connections()
            
        if self.args.act_hist_connection:
            act_thr.compute_act_histogram_of_connections()
            
        if self.args.act_thr_connection:
            act_thr.compute_act_threshold('connection')
            

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for preprocessing
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def get_preprocess_obj(self):
        '''
        Get object of preprocessing
        * input
            - N/A
        * output
            - N/A
        '''

        if self.preprocess is None:

            # Check data path
            self.data_path.gen_preprocess_path()

            # Check model
            if self.model is None:
                self.load_model()

            # Generate preprocessing object
            self.preprocess = Preprocess(
                self.args, self.data_path, self
            )

        return self.preprocess

    
    def preprocessing(self):
        '''
        Preprocess
        '''

        preprocess = self.get_preprocess_obj()

        if self.args.find_top_imgs:
            preprocess.find_top_imgs()

        if self.args.lsh_top_imgs:
            preprocess.lsh_by_top_imgs()

        if self.args.save_top_imgs:
            preprocess.find_top_imgs_for_each_group()


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for 2D permutation
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def get_perm_2d_obj(self): 
        '''
        Get object of hash arrays and orders
        * input
            - N/A
        * output
            - self.perm_2d: object of Perm2D
        '''
        
        if self.perm_2d is None:
            
            # Check data_path
            self.data_path.gen_permutation_path()
                
            # Check model
            if self.model is None:
                self.load_model()
                
            # Generate activation threshold object
            self.perm_2d = Perm2D(
                self.args, self.data_path, self
            )
            
        return self.perm_2d


    def generate_permutation_data(self):
        '''
        Generate hash array and hash orders
        * input
            - N/A
        * output
            - N/A
        '''

        perm_2d = self.get_perm_2d_obj()

        # Generate hash arrays
        if self.args.gen_hash_array:
            perm_2d.gen_hash_arrs()
            
        # Generate hash order
        if self.args.gen_hash_order:
            perm_2d.gen_hash_order()



    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for LSH
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def get_lsh_obj(self):
        '''
        Get object of LSH
        * input
            - N/A
        * output
            - self.lsh: object of LSH
        '''
        
        if self.lsh is None:
            
            # Check model
            if self.model is None:
                self.load_model()
            
            # Generate LSH object
            self.lsh = LSH(
                self.args, self.data_path, self
            )
            
        return self.lsh
    
    
    def compute_hash_values(self):
        '''
        Compute hash value for neurons
        * input
            - N/A
        * output
            - N/A
        '''
        
        lsh = self.get_lsh_obj()
            
        # Compute hash values
        if self.args.compute_hash_value_neuron:
            lsh.compute_hash_values()
            
            
    def generate_bucket(self):
        '''
        Generate hased buckets of neurons and connections
        * input 
            - N/A
        * output
            - N/A
        '''
        
        lsh = self.get_lsh_obj()

        if self.args.gen_bucket:
            # lsh.gen_bucket()
            lsh.lsh_neurons()

        if self.args.agg_clusters:
            lsh.aggregate_clusters()

        if self.args.gen_connection:
            lsh.gen_connection()
            # lsh.aggregate_bucket_AND_OR()
            # lsh.aggregate_bucket_CO_OC(buckets)



    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for generating graph
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def get_graph_obj(self):
        '''
        Get object of ClusteredGraph
        * input
            - N/A
        * output
            - self.graph: object of ClusteredGraph
        '''
        
        if self.graph is None:
            
            # Check model
            if self.model is None:
                self.load_model()
            
            # Generate graph object
            self.graph = ClusteredGraph(
                self.args, self.data_path, self
            )
            
        return self.graph


    def generate_graph(self):
        '''
        Generate graph of neuron clusters and their connections 
        * input
            - N/A
        * output
            - N/A
        '''

        graph = self.get_graph_obj()

        if self.args.gen_graph:
            graph.gen_graph()



    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for generating example patches
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def get_ex_patch_obj(self):
        '''
        Get object of ExamplePatch
        * input
            - N/A
        * output
            - self.ex_patch: object of ExamplePatch
        '''
        
        if self.ex_patch is None:
            
            # Check model
            if self.model is None:
                self.load_model()

            # Generate ex patch object
            self.ex_patch = ExamplePatch(
                self.args, self.data_path, self
            )
            
        return self.ex_patch
    
    
    def generate_example_patches(self):
        '''
        Generate example patches
        * input
            - N/A
        * output
            - N/A
        '''
        
        ex_patch = self.get_ex_patch_obj()
        if self.args.gen_ex_patch:
            ex_patch.gen_act_max_matrix()
            ex_patch.pick_candidate_images()
            ex_patch.find_example_patches_act_map()
            # ex_patch.find_example_patches_grad()

 
 
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for embedding
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def get_emb_obj(self):
        '''
        Get object of NeuralEmbedding
        * input
            - N/A
        * output
            - self.emb: object of NeuralEmbedding
        '''
        
        if self.emb is None:
            
            # Check model
            if self.model is None:
                self.load_model()
            
            # Generate LSH object
            self.emb = NeuralEmbedding(
                self.args, self.data_path, self
            )
            
        return self.emb
    
    
    def generate_embedding(self):
        '''
        Generate neuron embedding
        * input
            - N/A
        * output
            - N/A
        '''
        
        emb = self.get_emb_obj()

        if self.args.gen_co_act:
            emb.gen_pair_dict()

        if self.args.gen_emb:
            emb.learn_embedding()

        if self.args.reduce_emb:
            emb.reduce_embedding_size_umap()