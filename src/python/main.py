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

import os
from utils.path import *
from utils.args import *
from utils.model import *


def main():
    
    # Parse arguments
    args = parse_args()

    # GPU setting
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu

    # Generate data directories
    data_path = DataPath(args)
    data_path.gen_data_dirs()
    
    # Load CNN model
    model_wrapper = ModelWrapper(args, data_path)
    model_wrapper.load_model()
    
    # # Compute activation threshold for neurons
    # model_wrapper.compute_activation_threshold_for_neurons()
    
    # # Compute activation threshold for connections 
    # model_wrapper.compute_activation_threshold_for_connections()

    # # Preprocessing
    # model_wrapper.preprocessing()

    # # Generate hash array and hash orders
    # model_wrapper.generate_permutation_data()
    
    # # Compute hash values for neurons
    # model_wrapper.compute_hash_values()

    # # Generate hashed buckets
    # model_wrapper.generate_bucket()
    
    # # Generate graph
    # model_wrapper.generate_graph()

    # # Generate example patches
    # model_wrapper.generate_example_patches()

    # # Generate neuron embedding
    # model_wrapper.generate_embedding()

    
if __name__ == '__main__':
    main()