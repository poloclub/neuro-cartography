'''
* Project:
    NeuroCartography: Scalable Automatic Visual Summarization of
    Concepts in Deep Neural Networks
* File name:
    InceptionV1.py
* Description:
    Define InceptionV1 model wrapper
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Mar 20, 2021
'''


import tqdm
import tensorflow as tf
import lucid.optvis.render as render
import lucid.modelzoo.vision_models as models
from keras.applications.inception_v3 import preprocess_input
from utils.path import *


class InceptionV1:

    '''
    InceptionV1 model
    * Going deeper with convolutions (https://arxiv.org/pdf/1409.4842.pdf)
    * structure: http://dgschwend.github.io/netscope/#/preset/googlenet
    '''
    
    def __init__(self, args={}):
        
        '''
        User setting
        '''
        self.args = args
        if len(args) > 0:
            self.data_path = DataPath(args)
            self.num_imgs = self.get_number_of_input_imgs()
        
        '''
        Model 
        '''
        self.model = None

        
        '''
        InceptionV1 structure
        '''
        
        self.LAYERS = [
            'mixed3a', 
            'mixed3b', 
            'mixed4a', 
            'mixed4b', 
            'mixed4c', 
            'mixed4d', 
            'mixed4e', 
            'mixed5a', 
            'mixed5b'
        ]

        self.LAYER_SIZE = {
            'mixed3a': 256,
            'mixed3b': 480,
            'mixed4a': 508,
            'mixed4b': 512,
            'mixed4c': 512,
            'mixed4d': 528,
            'mixed4e': 832,
            'mixed5a': 832,
            'mixed5b': 1024
        }

        self.ACT_MAP_SIZE = {
            'mixed3a': (28, 28),
            'mixed3b': (28, 28),
            'mixed4a': (14, 14),
            'mixed4b': (14, 14),
            'mixed4c': (14, 14),
            'mixed4d': (14, 14),
            'mixed4e': (14, 14),
            'mixed5a': (7, 7),
            'mixed5b': (7, 7)
        }
        
        self.LAYER_BLK_SIZE = {
            # mixed3a
            'mixed3a_concat0': 64,
            'mixed3a_concat1': 128,
            'mixed3a_concat2': 32,
            'mixed3a_concat3': 32,
            'mixed3a_3x3': 96,
            'mixed3a_5x5': 16,
            # mixed 3b
            'mixed3b_concat0': 128,
            'mixed3b_concat1': 192,
            'mixed3b_concat2': 96,
            'mixed3b_concat3': 64,
            'mixed3b_3x3': 128,
            'mixed3b_5x5': 32,
            # mixed 4a
            'mixed4a_concat0': 192,
            'mixed4a_concat1': 204,
            'mixed4a_concat2': 48,
            'mixed4a_concat3': 64,
            'mixed4a_3x3': 96,
            'mixed4a_5x5': 16,
            # mixed 4b
            'mixed4b_concat0': 160,
            'mixed4b_concat1': 224,
            'mixed4b_concat2': 64,
            'mixed4b_concat3': 64,
            'mixed4b_3x3': 112,
            'mixed4b_5x5': 24,
            # mixed 4c
            'mixed4c_concat0': 128,
            'mixed4c_concat1': 256,
            'mixed4c_concat2': 64,
            'mixed4c_concat3': 64,
            'mixed4c_3x3': 128,
            'mixed4c_5x5': 24,
            # mixed 4d
            'mixed4d_concat0': 112,
            'mixed4d_concat1': 288,
            'mixed4d_concat2': 64,
            'mixed4d_concat3': 64,
            'mixed4d_3x3': 144,
            'mixed4d_5x5': 32,
            # mixed 4e
            'mixed4e_concat0': 256,
            'mixed4e_concat1': 320,
            'mixed4e_concat2': 128,
            'mixed4e_concat3': 128,
            'mixed4e_3x3': 160,
            'mixed4e_5x5': 32,
            # mixed 5a
            'mixed5a_concat0': 256,
            'mixed5a_concat1': 320,
            'mixed5a_concat2': 128,
            'mixed5a_concat3': 128,
            'mixed5a_3x3': 160,
            'mixed5a_5x5': 48,
            # mixed 5b
            'mixed5b_concat0': 384,
            'mixed5b_concat1': 384,
            'mixed5b_concat2': 128,
            'mixed5b_concat3': 128,
            'mixed5b_3x3': 192,
            'mixed5b_5x5': 48
        }
        
        self.BLKS = [
            # mixed3a
            'mixed3a',
            # mixed3b 
            'mixed3b_3x3', 'mixed3b_5x5', 'mixed3b', 
            # mixed4a
            'mixed4a_3x3', 'mixed4a_5x5', 'mixed4a', 
            # mixed4b
            'mixed4b_3x3', 'mixed4b_5x5', 'mixed4b', 
            # mixed4c
            'mixed4c_3x3', 'mixed4c_5x5', 'mixed4c', 
            # mixed4d
            'mixed4d_3x3', 'mixed4d_5x5', 'mixed4d', 
            # mixed4e
            'mixed4e_3x3', 'mixed4e_5x5', 'mixed4e', 
            # mixed5a
            'mixed5a_3x3', 'mixed5a_5x5', 'mixed5a', 
            # mixed5b
            'mixed5b_3x3', 'mixed5b_5x5', 'mixed5b'
        ]
                
        self.BLK_APPENDIXES = [
            'concat0', 'concat1', 'concat2', 
            'concat3', 'conn3x3', 'conn5x5'
        ]

        self.CONCAT_OFFSET = {
            'mixed3b_concat0': 0, 
            'mixed3b_concat1': 128, 
            'mixed3b_concat2': 320, 
            'mixed3b_concat3': 416, 
            'mixed4a_concat0': 0, 
            'mixed4a_concat1': 192, 
            'mixed4a_concat2': 396, 
            'mixed4a_concat3': 444, 
            'mixed4b_concat0': 0, 
            'mixed4b_concat1': 160, 
            'mixed4b_concat2': 384, 
            'mixed4b_concat3': 448, 
            'mixed4c_concat0': 0, 
            'mixed4c_concat1': 128, 
            'mixed4c_concat2': 384, 
            'mixed4c_concat3': 448, 
            'mixed4d_concat0': 0, 
            'mixed4d_concat1': 112, 
            'mixed4d_concat2': 400, 
            'mixed4d_concat3': 464, 
            'mixed4e_concat0': 0, 
            'mixed4e_concat1': 256, 
            'mixed4e_concat2': 576, 
            'mixed4e_concat3': 704, 
            'mixed5a_concat0': 0, 
            'mixed5a_concat1': 256, 
            'mixed5a_concat2': 576, 
            'mixed5a_concat3': 704, 
            'mixed5b_concat0': 0, 
            'mixed5b_concat1': 384, 
            'mixed5b_concat2': 768, 
            'mixed5b_concat3': 896
        }

        self.MAX_POOL_SETTING = {
            'ksize': [1, 3, 3, 1],
            'strides': [1, 2, 2, 1],
            'padding': 'SAME'
        }



    '''
    Load model
    '''

    def load_model(self):
        '''
        Load InceptionV1 model from lucid.modelzoo
        * input
            - N/A
        * output
            - N/A
        '''
        
        model = models.InceptionV1()
        model.load_graphdef()
        self.model = model
        
        

    '''
    Get data or information of the model
    '''

    def get_number_of_input_imgs(self):
        '''
        Get the number of images
        * input
            - N/A
        * output
            - num_imgs: number of input images
        '''
        
        # Read the number of images by synset
        num_imgs_dict, total_num = {}, 0
        filepath = '{}/imagenet-num-imgs.txt'.format(
            self.data_path.base_dir
        )
        with open(filepath, 'r') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if i == 0:
                continue
            synset, name, num_imgs = line.split('\t')
            num_imgs_dict[synset] = int(num_imgs)
            total_num += num_imgs_dict[synset]
        
        # The number of input images
        if 'all' in self.args.synset.lower():
            return total_num
        elif 'sample' in self.args.synset.lower():
            tfrecs = self.data_path.get_data_path('imagenet')
            synsets = [tfrec.split('-')[-1][:-6] for tfrec in tfrecs]
            return np.sum([num_imgs_dict[synset] for synset in synsets])
        else:
            return num_imgs_dict[self.args.synset]
        
        
    def get_prev_layer(self, layer):
        '''
        Get previous layer
        * input
            - layer: current layer
        * output
            - prev_layer: previous layer. Return None if layer is 
                not in layers or layer is the first layer.
        '''
        
        # Return None if layer is not in layers 
        if layer not in self.LAYERS:
            return None
        
        # Return None if layer is the first layer
        layer_idx = self.LAYERS.index(layer)
        if layer_idx == 0:
            return None
        
        # Get prev_layer
        prev_layer = self.LAYERS[layer_idx -1]
        
        return prev_layer


    def get_prev_blk(self, neuron):
        '''
        Get previous block for a neuron's belonging block
        * input
            - neuron: neuron id
        * output
            - previous block
        '''

        blk, n = neuron.split('-')

        if '_3x3' in neuron:
            prev_layer = self.get_prev_layer(blk.split('_')[0])
            return prev_layer
        elif '_5x5' in neuron:
            prev_layer = self.get_prev_layer(blk.split('_')[0])
            return prev_layer
        else:
            concat_i = self.get_concat_blk_from_neuron(neuron)
            if concat_i == 0 or concat_i == 3:
                prev_layer = self.get_prev_layer(blk)
                return prev_layer
            elif concat_i == 1:
                return '{}_3x3'.format(blk)
            else: 
                return '{}_5x5'.format(blk)


    def get_conn_name(self, neuron):
        '''
        Get connection name for an output neuron belonging
        * input
            - neuron: neuron id
        * output
            - connection name
        '''

        blk, n = neuron.split('-')

        if '_3x3' in neuron:
            layer = blk.split('_')[0]
            return '{}_conn3x3'.format(layer)
        elif '_5x5' in neuron:
            layer = blk.split('_')[0]
            return '{}_conn5x5'.format(layer)
        else:
            concat_i = self.get_concat_blk_from_neuron(neuron)
            return '{}_concat{}'.format(blk, concat_i)


    def get_num_neurons(self, blk):
        '''
        Get number of neurons in the block
        '''

        num_neurons = 0
        if ('3x3' in blk) or ('5x5' in blk):
            num_neurons = self.LAYER_BLK_SIZE[blk]
        else:
            for concat_i in range(4):
                num_neurons += self.LAYER_BLK_SIZE[
                    '{}_concat{}'.format(blk, concat_i)
                ]
        return num_neurons


    '''
    Get tensors
    '''
    
    def get_t_blk(self, block):
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


    def get_t_blks(self, prev_layer, layer):
        '''
        Get layer block tensors in a layer gap
        * input
            - prev_layer: the previous layer given in string (e.g., 'mixed3a')
            - layer: the current layer given in string (e.g., 'mixed3b')
        * output
            - t_l_input: the tensor of the previous layer
            - t_l_3x3: the tensor of the first branch block (3x3 bottleneck)
            - t_l_5x5: the tensor for the second branch block (5x5 bottleneck)
        '''

        t_l_input = self.get_t_blk(prev_layer)
        t_l_3x3 = self.get_t_blk('{}_3x3'.format(layer))
        t_l_5x5 = self.get_t_blk('{}_5x5'.format(layer))
        return t_l_input, t_l_3x3, t_l_5x5


    def get_concat_blk_from_neuron(self, neuron):
        '''
        Get concat block from neuron
        * input
            - neuron: neuron id
        * output
            - concat_i: the index of concat block
        '''
        
        layer, n = neuron.split('-')
        n = int(n)
        offset, concat_i = 0, 3
        for i in range(4):
            blk = '{}_concat{}'.format(layer, i)
            offset += self.LAYER_BLK_SIZE[blk]
            if n < offset:
                concat_i = i
                break
        return concat_i


    def get_t_blks_layer_gap(self, prev_layer, layer):
        '''
        Get layer block tensors in a layer gap in the inceptionV1 model
        * input
            - prev_layer: the previous layer given in string (e.g., 'mixed3a')
            - layer: the current layer given in string (e.g., 'mixed3b')
        * output
            - t_l_input: the tensor of the previous layer
            - t_l_3x3: the tensor of the first branch block (3x3 bottleneck)
            - t_l_5x5: the tensor for the second branch block (5x5 bottleneck)
        '''

        t_l_input = self.get_t_blk(prev_layer)
        t_l_3x3 = self.get_t_blk('{}_3x3'.format(layer))
        t_l_5x5 = self.get_t_blk('{}_5x5'.format(layer))
        return t_l_input, t_l_3x3, t_l_5x5
    
    
    def get_t_weights_layer_gap(self, layer):
        '''
        Get weight tensors for the given layer in the inceptionV1 model
        * input
            - layer: the name of the layer in string (e.g., 'mixed3a')
        * output
            - t_w_1x1: the tensor of {layer}_1x1_w:0
            - t_w_3x3_b: the tensor of {layer}_3x3_bottleneck_w:0
            - t_w_3x3: the tensor of {layer}_3x3_w:0
            - t_w_5x5_b: the tensor of {layer}_5x5_bottleneck_w:0
            - t_w_5x5: the tensor of {layer}_5x5_w:0
            - t_w_p_r: the tensor of {layer}_pool_reduce_w:0
        '''
    
        t_w_1x1 = self.get_t_blk('{}_1x1_w'.format(layer))
        t_w_3x3_b = self.get_t_blk('{}_3x3_bottleneck_w'.format(layer))
        t_w_3x3 = self.get_t_blk('{}_3x3_w'.format(layer))
        t_w_5x5_b = self.get_t_blk('{}_5x5_bottleneck_w'.format(layer))
        t_w_5x5 = self.get_t_blk('{}_5x5_w'.format(layer))
        t_w_p_r = self.get_t_blk('{}_pool_reduce_w'.format(layer))

        return t_w_1x1, t_w_3x3_b, t_w_3x3, t_w_5x5_b, t_w_5x5, t_w_p_r


    def _parse_function(self, feature_proto, image_size=224):
        '''
        Parse imagenet data in tf-record format
        * input
            - feature_proto: feature prototype
            - image_size: the image size (width or height)
            - with_input
        * output
            - image: parsed images
            - label: parsed labels of the images
            - synset: parsed synset
        '''

        # Parse bytes features
        def _bytes_feature(value):
            return tf.train.Feature(
                bytes_list=tf.train.BytesList(value=[value]))

        # Parse int64 features
        def _int64_feature(value):
            return tf.train.Feature(
                int64_list=tf.train.Int64List(value=[value]))

        # Features to get from the dataset
        feature_set = {
            'image/encoded': tf.FixedLenFeature([], tf.string),
            'image/class/label': tf.FixedLenFeature([], tf.int64),
            'image/class/synset': tf.FixedLenFeature([], tf.string)
        }

        # Parse features
        parsed_features = tf.parse_single_example(feature_proto, feature_set)

        # Get each parsed feature
        image = parsed_features['image/encoded']
        label = parsed_features['image/class/label']
        synset = parsed_features['image/class/synset']

        # Decode images
        image = tf.image.decode_jpeg(image, channels=3)
        image = tf.image.resize_images(
            image, 
            tf.constant([image_size, image_size])
        )

        return image, label, synset
 


    '''
    Compute tensor and data
    '''

    def compute_data(self, compute_tensors, t_args, parse_data, p_args):
        '''
        Compute data
        * input
            - compute_tensors: a function that computes tensor data
            - t_args: arguments for compute_tensors()
            - parse_data: a function that parses computed tensor data
            - p_args: arguments for parse_data()
        * output
            - data: computed data in the dictionary format
            - time_log: running time log
        '''

        # Imagenet path
        input_path = self.data_path.get_data_path('imagenet')
        
        # Time checker
        tic, time_log, cpu_time = time(), '', 0
        
        # Initialize data
        data = {}
        
        # Compute data
        with tf.Graph().as_default():

            # Parse datasets of a certain batch size
            dataset = tf.data.TFRecordDataset(input_path)
            dataset = dataset.map(self._parse_function)
            dataset = dataset.map(
                lambda img, lab, syn: (preprocess_input(img), lab, syn)
            )
            dataset = dataset.batch(self.args.batch_size)

            # Define dataset iterator
            iterator = dataset.make_one_shot_iterator()

            # Define tensors to store the dataset
            t_preprocessed_images, t_labels, t_synsets = iterator.get_next()

            # Define actiavtion map render
            T = render.import_model(self.model, t_preprocessed_images, None)
            T('mixed3a')

            # Define tensors to store the dataset
            tensors = compute_tensors(*t_args)

            # Load data and compute the activation range
            with tf.Session() as sess:

                try:
                    with tqdm.tqdm(total=self.num_imgs, unit='imgs') as pbar:
                        while(True):

                            # Run the session
                            sess_data = sess.run(tensors)

                            '''''''''''''''''''''''''''''''''''''''''''''''
                            no sess.run after this!
                            python code here on out
                            '''''''''''''''''''''''''''''''''''''''''''''''
                            
                            # Index our of range
                            if len(sess_data) == 0:
                                break

                            # Check time
                            cpu_tic = time()

                            # Parse the sess_data and update data
                            data = parse_data(data, sess_data, *p_args)

                            # Check time
                            cpu_toc = time()
                            cpu_time += cpu_toc - cpu_tic

                            # Update progress bar
                            pbar.update(self.args.batch_size)
                            

                except tf.errors.OutOfRangeError:
                    pass
                
        # Time log
        toc = time()
        total_time = toc - tic
        time_log += 'total_time: %.2lf\n' % (total_time)
        time_log += 'gpu_time: %.2lf\n' % (total_time - cpu_time)
        time_log += 'cpu_time: %.2lf\n' % (cpu_time)
        
        return data, time_log


    def compute_with_image(self, parse_data, p_args):
        '''
        Compute parse_data with processed image
        * input
            - parse_data: a function that parses computed tensor data
            - p_args: arguments for parse_data()
        * output
            - data: computed data in the dictionary format
            - time_log: running time log
        '''
        
        # Imagenet path
        input_path = self.data_path.get_data_path('imagenet')
        
        # Time checker
        tic, time_log, cpu_time = time(), '', 0
        
        # Initialize data
        data = {}
        
        # Compute data
        with tf.Graph().as_default():

            # Parse datasets of a certain batch size
            dataset = tf.data.TFRecordDataset(input_path)
            dataset = dataset.map(self._parse_function)
            dataset = dataset.map(
                lambda img, lab, syn: (preprocess_input(img), lab, syn, img)
            )
            dataset = dataset.batch(self.args.batch_size)

            # Define dataset iterator
            iterator = dataset.make_one_shot_iterator()

            # Define tensors to store the dataset
            t_preprocessed_images, t_labels, t_synsets, t_input \
                = iterator.get_next()

            # Load data and compute the activation range
            with tf.Session() as sess:

                try:
                    with tqdm.tqdm(total=self.num_imgs, unit='imgs') as pbar:
                        while(True):
                            
                            # Run the session
                            sess_data = sess.run(t_input)

                            '''''''''''''''''''''''''''''''''''''''''''''''
                            no sess.run after this!
                            python code here on out
                            '''''''''''''''''''''''''''''''''''''''''''''''
                            
                            # Index our of range
                            if len(sess_data) == 0:
                                break

                            # Check time
                            cpu_tic = time()

                            # Parse the sess_data and update data
                            data = parse_data(data, sess_data, *p_args)

                            # Check time
                            cpu_toc = time()
                            cpu_time += cpu_toc - cpu_tic

                            # Update progress bar
                            pbar.update(self.args.batch_size)

                except tf.errors.OutOfRangeError:
                    pass
                
        # Time log
        toc = time()
        total_time = toc - tic
        time_log += 'total_time: %.2lf\n' % (total_time)
        time_log += 'gpu_time: %.2lf\n' % (total_time - cpu_time)
        time_log += 'cpu_time: %.2lf\n' % (cpu_time)
        
        return data, time_log
    
    
    