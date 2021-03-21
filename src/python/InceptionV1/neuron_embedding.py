'''
* Project:
    Neuro-Cartography: Drawing Concept-based Neural Maps to Interpret 
    Deep Neural Networks by Automatically Discovering and Visualizing 
    Cell Assemblies
* File name:
    neuron_embedding.py
* Description:
    Make vector of neurons in InceptionV1
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Jan 30, 2020
'''


import tqdm
import json
import umap
import random
import numpy as np
import tensorflow as tf
from time import time


class NeuralEmbedding:

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Class for learning neuron embedding
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def __init__(self, args, data_path, model_wrapper):
        
        # Hyperparameters
        self.D = args.embedding_dimension
        self.epoch = args.epoch
        self.N = args.num_negative_samples
        self.lr = args.learning_rate
        # self.batch_size = args.batch_size
        # self.coeff = args.coeff

        # Fine tuning
        self.version = args.emb_version

        # Data paths
        self.data_path = data_path
        
        # Model
        self.model = model_wrapper.model
        self.BLKS = self.model.BLKS

        # Data
        self.emb = {}
        self.emb2d = {}
        self.top_imgs = {}
        self.co_act_neurons = {}


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Pair of co-activated neurons
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def gen_pair_dict(self):
        '''
        Generate dictionary of pair of co-activated neurons
        * input
            - N/A
        * output
            - N/A
        '''

        # Check time
        tic = time()

        # Load top images
        self.load_top_imgs()

        # Find co-activated neurons
        for blk in self.BLKS:
            imgs = self.top_imgs[blk]
            num_neurons = imgs.shape[-1]
            for n in range(num_neurons):
                neuron = '{}-{}'.format(blk, n)
                imgs_n = imgs[:, n]
                for img in imgs_n:
                    if img not in self.co_act_neurons:
                        self.co_act_neurons[img] = []
                    self.co_act_neurons[img].append(neuron)

        # Save co_activated neurons
        co_act_data = [
            self.co_act_neurons[img]
            for img in self.co_act_neurons
            if len(self.co_act_neurons[img]) > 1
        ]
        self.save_co_act(co_act_data)
            
        # Time check
        toc = time()
        time_log = 'Find co-activated neurons\n'
        time_log += '%.2lf sec\n' % (toc - tic)
        self.save_time_log(time_log, 'co_activation')


    def gen_pair_dict_old(self):
        '''
        Generate dictionary of pair of co-activated neurons 
        * input
            - N/A
        * output
            - N/A
        '''

        # Load activation threshold of neurons
        act_thr = self.load_act_thr()

        # Define a function for highly activated neurons
        def compute_high_act_neurons_tensors():

            tensors = []
            for blk in self.BLKS:

                t_blk = self.model.get_t_blk(blk)
                t_max = tf.math.reduce_max(
                    t_blk, axis=[1, 2]
                )
                t_high_act_neurons = tf.where(
                    t_max > (act_thr[blk] * self.coeff)
                )
                tensors.append(t_high_act_neurons)

            return tensors

        # Define a function to find co-occurring neurons
        def compute_co_act_neurons(data, sess_data):

            # Find co-activated neurons by images
            for i, blk in enumerate(self.BLKS):
                high_act_neurons = sess_data[i]
                for img_i, n in high_act_neurons:

                    # img key
                    img_k = self.img_idx + img_i

                    # Initialize co_act pairs
                    if img_k not in data:
                        data[img_k] = {}

                    # Add neuron into co_act_by_imgs
                    neuron = '{}-{}'.format(blk, n)
                    data[img_k][neuron] = True

            self.img_idx += self.batch_size
            
            return data

        data, time_log = self.model.compute_data(
            compute_high_act_neurons_tensors,
            [],
            compute_co_act_neurons,
            []
        )
        data = {str(img_k): list(data[img_k].keys()) for img_k in data}
        self.img_idx = 0

        self.save_co_act(data)
        self.save_time_log(time_log, 'co_activation')



    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Learn neuron embedding
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def learn_embedding(self):
        '''
        Learn neuron embedding
        '''

        # Check time
        tic = time()

        # Get ready
        self.init_embedding()
        co_act = self.load_co_act()
        neurons = list(self.emb.keys())
        
        # Learn embedding
        for i in range(self.epoch):
            self.learn_embedding_one_epoch(co_act, neurons)

        # Save embedding
        self.save_embedding()

        # Check time
        toc = time()
        time_log = 'Learn embedding\n'
        time_log += '%.2lf sec\n' % (toc - tic)
        time_log += 'Umap\n'
        self.save_time_log(time_log, 'embedding')

        
    def init_embedding(self):
        '''
        Initialize neurons' embedding
        '''

        if self.version == 0:
            for blk in self.BLKS:
                num_neurons = self.model.get_num_neurons(blk)
                for n in range(num_neurons):
                    self.emb['{}-{}'.format(blk, n)] = \
                        np.random.random(self.D) - 0.5
        else:
            self.emb = self.load_embedding(self.version - 1)


    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))


    def learn_embedding_one_epoch(self, co_act, all_neurons):
        '''
        Learn neuron embedding for one epoch
        * input
            - co_act: co-activation data
            - all_neurons: list of all neurons
        * output
            - N/A
        '''

        total_num_neurons = len(all_neurons)
        tic = time()
        T = len(co_act)
                
        with tqdm.tqdm(total=T) as pbar:

            for neurons in co_act:

                random.shuffle(neurons)
                for i, u in enumerate(neurons[:-1]):
                    
                    # Neighbor neurons
                    v = neurons[i + 1]

                    # 1 - sigma(V_u \dot V_v)
                    coeff = 1 - self.sigmoid(
                        self.emb[u].dot(self.emb[v])
                    )
                        
                    # Gradient of emb_u
                    g_u = -coeff * self.emb[v]
                    for neg in range(self.N):
                        n = np.random.randint(total_num_neurons)
                        neuron = all_neurons[n]
                        dot_p = self.emb[neuron].dot(self.emb[neuron])
                        g_u += self.sigmoid(dot_p) * self.emb[neuron]

                    # Gradient of emb_v
                    g_v = -coeff * self.emb[u]
                    for neg in range(self.N):
                        n = np.random.randint(total_num_neurons)
                        neuron = all_neurons[n]
                        dot_p = self.emb[neuron].dot(self.emb[v])
                        g_v += self.sigmoid(dot_p) * self.emb[neuron]

                    # Update
                    self.emb[u] -= self.lr * g_u
                    self.emb[v] -= self.lr * g_v

                pbar.update(1)


    def learn_embedding_one_epoch_old(self, co_act, neurons):
        '''
        Learn neuron embedding for one epoch
        * input
            - co_act: co-activation data
            - neurons: list of all neurons
        * output
            - N/A
        '''

        total_num_neurons = len(neurons)
        tic = time()
        T = len(co_act)
                
        for ii, img_k in enumerate(co_act):
            # if ii % 100 == 0:
            #     toc = time()
            #     print('%d/%d=%.2lf, %.2lf sec' % (ii, T, img_k / T, toc - tic))
            pairs = {}
            co_act_neurons = np.random.choice(co_act[img_k], 100)
            for u in co_act_neurons:
                for v in co_act_neurons:
                    if u == v:
                        continue
                    pair_key = tuple(sorted([u, v]))
                    if pair_key in pairs:
                        continue
                    pairs[pair_key] = True

                    # Gradient of emb_u
                    coeff = 1 - self.sigmoid(
                        self.emb[u].dot(self.emb[v])
                    )
                    g_u = -coeff * self.emb[v]
                    for neg in range(self.N):

                        n = np.random.randint(total_num_neurons)
                        n = neurons[n]
                        dot_p = self.emb[n].dot(self.emb[u])
                        g_u += self.sigmoid(dot_p) * self.emb[n]

                    # Gradient of emb_v
                    g_v = coeff * self.emb[u]

                    # Update
                    self.emb[u] -= self.lr * g_u
                    self.emb[v] -= self.lr * g_v




    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Reduce embedding size
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def reduce_embedding_size_umap(self):
        '''
        Reduce the embedding size to 2D by using umap
        * input
            - N/A
        * output
            - N/A
        '''

        # Load embeding
        self.emb = self.load_embedding(self.version)

        # Convert embedding dict to np arrays
        idx_dict = {}
        num_neurons = len(self.emb)
        X = np.zeros((num_neurons, self.D))
        for i, neuron in enumerate(self.emb):
            idx_dict[i] = neuron
            X[i] = self.emb[neuron]

        # Reduce the dimension
        reducer = umap.UMAP(n_components=2, verbose=True)
        emb2d = reducer.fit_transform(X)
        
        # Convert np array 2d embedding into embedding dict
        for i, emb_i in enumerate(emb2d):
            neuron = idx_dict[i]
            self.emb2d[neuron] = emb_i

        # Save self.emb2d
        self.save_2d_embedding()


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Load and save data
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


    def load_top_imgs(self):
        '''
        Load top images for the groups
        '''

        for blk in self.BLKS:
            # File path
            dir_path = self.data_path.get_data_path(
                'top_imgs', data_or_time='data'
            )
            file_path = '{}/top_imgs-{}.txt'.format(
                dir_path, blk
            )

            # Load top imgs
            self.top_imgs[blk] = np.loadtxt(file_path, dtype=int)
            

    def load_act_thr(self):
        '''
        Load activation threshold of neurons
        * input
            - N/A
        * output
            - act_thr: threshold data
        '''
        file_path = self.data_path.get_data_path(
            'act_thr', 
            target='neuron',
            data_or_time='data'
        )
        with open(file_path, 'r') as f:
            act_thr = json.load(f)
        
        act_thr = {blk: float(act_thr[blk]) for blk in act_thr}
        return act_thr


    def save_co_act(self, data):
        '''
        Save co-activation data
        * input
            - data: co-activation data
        * output
            - N/A
        '''

        file_path = self.data_path.get_data_path(
            'co_activation', data_or_time='data'
        )
        file_path = file_path + '.json'
        with open(file_path, 'w') as f:
            f.write(json.dumps(data))


    def load_co_act(self):
        '''
        Load co-activation data
        * input
            - N/A
        * output
            - co_act: threshold data
        '''

        file_path = self.data_path.get_data_path(
            'co_activation', data_or_time='data'
        )
        file_path = file_path + '.json'
        with open(file_path, 'r') as f:
            co_act = json.load(f)

        return co_act


    def save_embedding(self):
        '''
        Save neuron embedding
        * input
            - N/A
        * output
            s- N/A
        '''

        emb = {
            n:
            ','.join(list(map(lambda x: '%.2lf' % x, self.emb[n]))) 
            for n in self.emb
        }
        file_path = self.data_path.get_data_path(
            'embedding', data_or_time='data'
        )
        file_path += '-{}.json'.format(self.version)
        with open(file_path, 'w') as f:
            f.write(json.dumps(emb))


    def save_2d_embedding(self):
        '''
        Save 2D embedding
        * input
            - N/A
        * output
            - N/A
        '''
        
        emb2d = {
            n:
            ','.join(list(map(lambda x: '%.2lf' % x, self.emb2d[n]))) 
            for n in self.emb2d
        }
        file_path = self.data_path.get_data_path(
            'embedding_2d', data_or_time='data'
        )
        file_path += '-{}.json'.format(self.version)
        with open(file_path, 'w') as f:
            f.write(json.dumps(emb2d))
        


    def load_embedding(self, version=0):
        '''
        Load embeddibg
        '''
    
        file_path = self.data_path.get_data_path(
            'embedding', data_or_time='data'
        )
        file_path += '-{}.json'.format(version)
        with open(file_path, 'r') as f:
            emb = json.load(f)

        emb = {
            n:
            np.array(list(map(float, emb[n].split(','))))
            for n in emb
        }
        return emb


    def save_time_log(self, time_log, data_item):
        '''
        Save activation data
        * input
            - time_log: Time log
            - data_item: what type of data to save
        * output
            - N/A
        '''
        
        data_path = self.data_path.get_data_path(
            data_item, data_or_time='time'
        )
        with open(data_path, 'w') as f:
            f.write(time_log)

