'''
* Project:
    NeuroCartography: Scalable Automatic Visual Summarization of
    Concepts in Deep Neural Networks
* File name:
    InceptionV1Compressed.py
* Description:
    Define compressed InceptionV1 model wrapper
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Mar 20, 2021
'''

import tensorflow as tf
from utils.path import *

class InceptionV1Compressed:

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Compressed InceptionV1 model
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def __init__(self, args):

        '''
        User setting
        '''
        self.args = args
        self.ratio = args.compression_ratio
        self.data_path = DataPath(args)
        self.num_imgs = self.get_number_of_input_imgs()

        '''
        Model 
        '''
        self.model = None


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Load model
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def load_model(self):
        '''
        Load InceptionV1 model from lucid.modelzoo
        * input
            - N/A
        * output
            - N/A
        '''
        
        model_path = self.data_path['compressed_model']
        model = tf.saved_model.load(model_dir)