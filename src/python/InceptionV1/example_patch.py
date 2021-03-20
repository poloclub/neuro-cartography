'''
* Project:
    Neuro-Cartography: Drawing Concept-based Neural Maps to Interpret 
    Deep Neural Networks by Automatically Discovering and Visualizing 
    Cell Assemblies
* File name:
    example_patch.py
* Description:
    Generate example patches for each neuron in InceptionV1
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Jan 30, 2020
'''

import cv2
import json
import tqdm
import numpy as np
from time import time
import tensorflow as tf
import lucid.optvis.render as render
from keras.applications.inception_v3 import preprocess_input
import matplotlib.pyplot as plt


class ExamplePatch:

    '''
    Class for generating example patches for each neuron
    '''

    def __init__(self, args, data_path, model_wrapper):

        # Data path
        self.data_path = data_path

        # Model
        self.model = model_wrapper.model
        if args.blk == 'None':
            self.BLKS = self.model.BLKS
        else:
            self.BLKS = [args.blk]

        # Hyperparameters
        self.num_candidates = args.num_ex_candidates
        self.batch_size = args.batch_size
        self.ex_patch_thr = args.ex_patch_thr

        # Data
        self.act_max_mat = {}
        self.cand_img_idxs = {}
        self.cand_imgs = {}
        self.num_imgs = self.model.get_number_of_input_imgs()

        # Global variable
        self.img_idx = 0


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for computing max activation matrix
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def gen_act_max_matrix(self):
        '''
        Generate act_max_mat of shape (num neurons, num images).
        Each entry is a maximum value of activation map of the
        corresponding neuron and image. Save the matrix into
        self.act_max_mat.
        * input
            - N/A
        * output
            - N/A
        '''

        data, time_log = self.model.compute_data(
            self.compute_t_act_max,
            [],
            self.parse_t_act_max,
            []
        )
        self.img_idx = 0
        self.act_max_mat = data


    def compute_t_act_max(self):
        '''
        Compute tensor of activation max
        * input
            - N/A
        * output
            - tensors: tensors of max activation
        '''

        tensors = []
        for blk in self.BLKS:
            t_blk = self.model.get_t_blk(blk)
            t_max = tf.math.reduce_max(t_blk, axis=[1, 2])
            tensors.append(t_max)
        return tensors


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

        for i, blk in enumerate(self.BLKS):
            act_max = sess_data[i]
            num_neurons = act_max.shape[-1]

            if blk not in data:
                data[blk] = np.zeros(
                    (self.num_imgs, num_neurons)
                )
            
            data[blk][img_s: img_e] = act_max

        self.img_idx += self.batch_size

        return data


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for finding candidate images
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def pick_candidate_images(self):
        '''
        Pick candidate images for each neuron and save the
        images into self.cand_imgs
        * input
            - N/A
        * output
            - N/A
        '''

        self.find_candidate_image_index()

        data, time_log = self.model.compute_with_image(
            self.get_candidate_images_one_batch,
            []
        )

        self.img_idx = 0
        

    def find_candidate_image_index(self):
        '''
        Find index of candidate images for all neurons
        * input
            - N/A
        * output
            - N/A
        '''

        N = self.num_candidates

        for blk in self.BLKS:
            M = self.act_max_mat[blk]
            num_neurons = M.shape[-1]
            self.cand_img_idxs[blk] = {}
            for n in range(num_neurons):
                top_imgs_idx = np.argsort(-M[:, n])[:N]
                self.cand_img_idxs[blk][n] = top_imgs_idx

    
    def get_candidate_images_one_batch(self, data, sess_data):
        '''
        Get candidate images in numpy array in one batch
        * input
            - data: data before udpated
            - sess_data: data in the current session
        * ouput
            - N/A
        '''

        # Image index
        img_s = self.img_idx
        img_e = self.img_idx + self.batch_size

        # Images
        r_imgs = sess_data
        
        # Find images
        for blk in self.BLKS:

            if blk not in self.cand_imgs:
                self.cand_imgs[blk] = {}

            for n in self.cand_img_idxs[blk]:

                img_idxs = self.cand_img_idxs[blk][n]
                for i in img_idxs:

                    if n not in self.cand_imgs[blk]:
                        img_shape = r_imgs[0].shape
                        self.cand_imgs[blk][n] = \
                            np.zeros((
                                self.num_candidates,
                                *img_shape
                            ))
                        
                    if (i >= img_s) and (i < img_e):
                        j = np.where(img_idxs == i)[0][0]
                        self.cand_imgs[blk][n][j] = \
                            r_imgs[i - img_s]

        self.img_idx += self.batch_size


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for finding candidate images
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def find_example_patches_act_map(self):
        '''
        Find example patches from the candidate images
        for all neurons
        * input
            - N/A
        * output
            - N/A
        '''

        with tf.Graph().as_default(), tf.Session():

            # Define tensors
            t_input = tf.placeholder(
                tf.float32, 
                [None, 224, 224, 3]
            )
            t_p_input = preprocess_input(t_input)
            T = render.import_model(
                self.model.model, t_p_input, t_p_input
            )
            T('mixed3a')

            for blk in self.BLKS:

                print(blk)

                # Activation map for given candidate images
                t_acts = self.model.get_t_blk(blk)
                num_neurons = len(self.cand_imgs[blk])

                # Crop images of the high activation
                with tqdm.tqdm(total=num_neurons) as pbar:

                    # For each neuron n
                    for n in self.cand_imgs[blk]:

                        # Images and activation map
                        r_imgs = self.cand_imgs[blk][n]
                        p_imgs = t_p_input.eval({t_input: r_imgs})
                        acts = t_acts.eval({t_input: r_imgs})
                        d, w, h, num_neurons = acts.shape
                        n_ignore = 0

                        for img_i, p_img in enumerate(p_imgs):

                            # Find patch
                            act_map = acts[img_i, :, :, n]

                            # Coordinates of max activation
                            highest_idx = np.argmax(
                                acts[img_i, :, :, n]
                            )
                            r, c = highest_idx // w, highest_idx % w
                            r1 = np.max([0, r - int(h * 0.15)])
                            c1 = np.max([0, c - int(w * 0.15)])
                            r2 = np.max([0, r + int(h * 0.15)])
                            c2 = np.max([0, c + int(w * 0.15)])
                            # r1, c1, r2, c2 = self.find_patch(act_map)

                            # Relative size
                            r1 = int(r1 * 224 / h)
                            c1 = int(c1 * 224 / w)
                            r2 = int(r2 * 224 / h)
                            c2 = int(c2 * 224 / w)

                            patch = r_imgs[img_i, r1: r2, c1: c2, :]
                            # Save patch
                            if len(patch) == 0:
                                n_ignore += 1
                            else:
                                dir_path = self.data_path.get_data_path(
                                    'example_patch'
                                )
                                file_path = '{}/{}-{}-dataset-p-{}.jpg' \
                                .format(
                                    dir_path, blk, n, img_i - n_ignore
                                )
                                cv2.imwrite(file_path, patch)

                        pbar.update(1)


    def find_example_patches_grad(self):
        '''
        Find example patches from the candidate images
        for all neurons
        * input
            - N/A
        * output
            - N/A
        '''

        with tf.Graph().as_default(), tf.Session():

            # Define tensors
            t_input = tf.placeholder(
                tf.float32, 
                [None, 224, 224, 3]
            )
            t_p_input = preprocess_input(t_input)
            T = render.import_model(
                self.model.model, t_p_input, t_p_input
            )
            T('mixed3a')

            for blk in self.BLKS:

                print(blk)

                # Activation map for given candidate images
                t_acts = self.model.get_t_blk(blk)
                num_neurons = len(self.cand_imgs[blk])

                # Gradient of the max activation cell w.r.t. input
                with tqdm.tqdm(total=num_neurons) as pbar:

                    # For each neuron n
                    for n in self.cand_imgs[blk]:

                        # Images and activation map
                        r_imgs = self.cand_imgs[blk][n]
                        p_imgs = t_p_input.eval({t_input: r_imgs})
                        acts = t_acts.eval({t_input: r_imgs})
                        d, w, h, num_neurons = acts.shape
                        n_ignore = 0

                        for img_i, p_img in enumerate(p_imgs):

                            act_map = acts[img_i, :, :, n]

                            # Coordinates of max activation
                            highest_idx = np.argmax(
                                acts[img_i, :, :, n]
                            )
                            r, c = highest_idx // w, highest_idx % w

                            # Gradient of max act cell w.r.t. input
                            t_g = tf.gradients(
                                t_acts[0, r, c, n], 
                                [t_input]
                            )
                            g_img = t_g[0].eval({t_input: [p_img]})[0]
                            gray_g = np.abs(cv2.cvtColor(
                                g_img, cv2.COLOR_BGR2GRAY
                            ))

                            # Find patch
                            r1, c1, r2, c2 = self.find_patch(gray_g)
                            patch = r_imgs[img_i, r1: r2, c1: c2, :]

                            # Save patch
                            if len(patch) == 0:
                                n_ignore += 1
                            else:
                                # Crop patch to square
                                patch = self.crop_patch(
                                    patch, 
                                    r - r1, 
                                    c - c1
                                )

                                dir_path = self.data_path.get_data_path(
                                    'example_patch'
                                )
                                file_path = '{}/{}-{}-dataset-p-{}.jpg' \
                                .format(
                                    dir_path, blk, n, img_i - n_ignore
                                )
                                cv2.imwrite(file_path, patch)
                                
                        pbar.update(1)


    def crop_patch(self, patch, x, y):
        '''
        Crop patch to make it square
        '''
        H, W, d = patch.shape
        if W > H:
            l = int(H / 2)
            if x < l:
                patch = patch[:, 0: 2 * l, :]
            elif x > W - l:
                patch = patch[:, W - 2 * l: W, :]
        elif W < H:
            l = int(W / 2)
            if y < l:
                patch = patch[0: 2 * l, :, :]
            elif x > W - l:
                patch = patch[H - 2 * l: H, :, :]
        return patch


    def find_patch(self, gray_img):
        '''
        Find patch of high values
        * input
            - gray_img: a gray image (no RGB Channel)
        * output
            - r1: minimum row of high value patch
            - c1: minimum column of high value patch
            - r2: maximum row of high value patch
            - c2: maximum column of high value patch
        '''

        R, C = gray_img.shape
        r1, c1, r2, c2 = R - 1, C - 1, 0, 0
        thr_percentile = int(R * C * (1 - self.ex_patch_thr))
        thr = np.sort(gray_img.reshape(-1))[thr_percentile]
        for r in range(R):
            for c in range(C):
                if gray_img[r, c] > thr:
                    r1 = min(r1, r)
                    c1 = min(c1, c)
                    r2 = max(r2, r)
                    c2 = max(r2, c)

        return r1, c1, r2, c2   
