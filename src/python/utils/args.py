'''
* Project:
    Neuro-Cartography: Drawing Concept-based Neural Maps to Interpret 
    Deep Neural Networks by Automatically Discovering and Visualizing 
    Cell Assemblies
* File name:
    args.py
* Description:
    Parse input arguments
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Jan 30, 2020
'''


import argparse


def parse_args():
    
    # Generate agrument parser
    parser = argparse.ArgumentParser(description='Neuro-Cartography')
    
    '''
    Basic settings used in all components
    '''
    
    # Model name
    parser.add_argument(
        '--model_name', 
        default='InceptionV1', 
        type=str,                
        help='CNN model name'
    )
    
    # GPU
    parser.add_argument(
        '--gpu', 
        default='1', 
        type=str,
        help='GPU number to be used'
    )
    
    # Synset - a class' synset id in imagenet data
    parser.add_argument(
        '--synset', 
        default='all', # n01843383 toucan
        type=str,
        help='Synset id of a class in the imagenet data. "All", "Samples" available too'
    )
    
    # Batch size
    parser.add_argument(
        '--batch_size', 
        default=500, 
        type=int,
        help='batch size'
    )
    
    # Layer
    parser.add_argument(
        '--layer', 
        default='mixed4e', 
        type=str, 
        help='layer'
    )
    
    
    '''
    Activation threshold
    '''
    parser.add_argument(
        '--nbins', 
        default=100, 
        type=int,
        help='Number of bins for activation histogram'
    )
    parser.add_argument(
        '--thr_neuron', 
        default=0.05, 
        type=float,
        help='Activation threshold k. default: 0.03 (3%)'
    )
    parser.add_argument(
        '--thr_connection', 
        default=0.05, 
        type=float,
        help='Activation threshold k. default: 0.03 (3%)'
    )

    '''
    Preprocessing
    '''
    parser.add_argument(
        '--num_top_imgs', 
        default=100, 
        type=int,
        help='Number of top images'
    )
    parser.add_argument(
        '--band_size_top_imgs', 
        default=2, 
        type=int,
        help='Band size in preprocessing'
    )
    parser.add_argument(
        '--num_bands_top_imgs', 
        default=100, 
        type=int,
        help='Number of bands in preprocessing'
    )

    '''
    Generate hash array
    '''
    parser.add_argument(
        '--H', 
        default=14, 
        type=int, 
        help='Height of activation map'
    )
    parser.add_argument(
        '--W', 
        default=14, 
        type=int, 
        help='Width of activation map'
    )
    
    
    '''
    Compute hash value
    '''
    parser.add_argument(
        '--num_hash_per_img', 
        default=10, 
        type=int,
        help='Number of hash functions per image'
    )
    parser.add_argument(
        '--patch_size', 
        default=1, 
        type=int,
        help='Size of pool patch'
    )
    parser.add_argument(
        '--num_perm_sample', 
        default=5000, 
        type=int,
        help='Number of permutations to make'
    )

    '''
    Hash neurons and connections into buckets
    '''
    parser.add_argument(
        '--band_size', 
        default=10, 
        type=int,
        help='Band size in LSH'
    )
    parser.add_argument(
        '--num_bands', 
        default=20, 
        type=int,
        help='Number of bands in LSH'
    )
    parser.add_argument(
        '--thr_of_non_act', 
        default=0.1, 
        type=float,
        help='Threshold of ratio of -1 (no act.) to ignore'
    )
    parser.add_argument(
        '--thr_co_occur', 
        default=0.0005, 
        type=float,
        help='Threshold of ratio of co-occurence to ignore'
    )
    parser.add_argument(
        '--high_act_patch_size', 
        default=2, 
        type=int,
        help='Patch size for high activation'
    )

    '''
    Generate example patches
    '''
    parser.add_argument(
        '--num_ex_candidates',
        default=20, 
        type=int,
        help='Number of candidate pathes for each neuron'
    )
    parser.add_argument(
        '--ex_patch_thr',
        default=0.2, 
        type=float,
        help='Gradient threshold. default: 0.05 (5%)'
    )
    parser.add_argument(
        '--blk',
        default='None', 
        type=str,
        help='Block'
    )

    '''
    Generate neuron embedding
    '''
    parser.add_argument(
        '--embedding_dimension',
        default=30, 
        type=int,
        help='Embedding dimension'
    )
    parser.add_argument(
        '--epoch',
        default=1, 
        type=int,
        help='Epoch'
    )
    parser.add_argument(
        '--learning_rate',
        default=0.01, 
        type=float,
        help='Learning rate'
    )
    parser.add_argument(
        '--num_negative_samples',
        default=10, 
        type=int,
        help='Number of negative samples per positive sample'
    )
    parser.add_argument(
        '--coeff',
        default=5, 
        type=int,
        help='Threshold coefficient'
    )
    parser.add_argument(
        '--emb_version',
        default=0, 
        type=int,
        help='Fine tuning version'
    )
    
    '''
    Whether to do an action for computing activation threshold
    '''
    parser.add_argument(
        '--act_range_neuron',
        default=False, 
        type=parse_bool_arg,
        help='wheter to compute activation range of neurons'
    )
    parser.add_argument(
        '--act_range_connection',
        default=False, 
        type=parse_bool_arg,
        help='wheter to compute activation range of connections'
    )
    parser.add_argument(
        '--act_hist_neuron',
        default=False, 
        type=parse_bool_arg,
        help='wheter to compute activation histogram of neurons'
    )
    parser.add_argument(
        '--act_hist_connection',
        default=False, 
        type=parse_bool_arg,
        help='wheter to compute activation histogram of connections'
    )
    parser.add_argument(
        '--act_thr_neuron',
        default=False, 
        type=parse_bool_arg,
        help='wheter to compute activation threshold of neurons'
    )
    parser.add_argument(
        '--act_thr_connection',
        default=False, 
        type=parse_bool_arg,
        help='wheter to compute activation threshold of connections'
    )

    '''
    Whether to do preprocessing
    '''
    parser.add_argument(
        '--find_top_imgs',
        default=False, 
        type=parse_bool_arg,
        help='wheter to do preprocessing'
    )
    parser.add_argument(
        '--lsh_top_imgs',
        default=False, 
        type=parse_bool_arg,
        help='wheter to do preprocessing'
    )
    parser.add_argument(
        '--save_top_imgs',
        default=False, 
        type=parse_bool_arg,
        help='wheter to do preprocessing'
    )
    
    
    '''
    Whether to do an action for computing hash value
    '''
    parser.add_argument(
        '--gen_hash_array',
        default=False, 
        type=parse_bool_arg,
        help='wheter to generate hash array'
    )
    parser.add_argument(
        '--gen_hash_order',
        default=False, 
        type=parse_bool_arg,
        help='wheter to generate hash order'
    )
    parser.add_argument(
        '--compute_hash_value_neuron',
        default=False, 
        type=parse_bool_arg,
        help='wheter to compute hash value of neurons'
    )
    parser.add_argument(
        '--compute_hash_value_connection',
        default=False, 
        type=parse_bool_arg,
        help='wheter to compute hash value of connections'
    )

    '''
    Whether to do an action for generating buckets
    '''
    parser.add_argument(
        '--gen_bucket',
        default=False, 
        type=parse_bool_arg,
        help='wheter to generate bucket'
    )
    parser.add_argument(
        '--gen_connection',
        default=False, 
        type=parse_bool_arg,
        help='wheter to generate connections between buckets'
    )
    parser.add_argument(
        '--agg_clusters',
        default=False, 
        type=parse_bool_arg,
        help='wheter to aggregate clusters'
    )

    '''
    Whether to do an action for generating graphs
    '''
    parser.add_argument(
        '--gen_graph',
        default=False, 
        type=parse_bool_arg,
        help='wheter to generate graph of neuron clusters'
    )

    '''
    Whether to generate example patches
    '''
    parser.add_argument(
        '--gen_ex_patch',
        default=False, 
        type=parse_bool_arg,
        help='wheter to generate example patches'
    )

    '''
    Whether to generate neuron embedding
    '''
    parser.add_argument(
        '--gen_co_act',
        default=False, 
        type=parse_bool_arg,
        help='wheter to generate neuron co-activation'
    )
    parser.add_argument(
        '--gen_emb',
        default=False, 
        type=parse_bool_arg,
        help='wheter to generate neuron embedding'
    )
    parser.add_argument(
        '--reduce_emb',
        default=False, 
        type=parse_bool_arg,
        help='wheter to reduce neuron embedding dimension'
    )


    # Parsed arguments
    args = parser.parse_args()

    return args



def parse_bool_arg(arg):
    '''
    Parse boolean argument
    * input
        - arg: argument
    * output
        - parsed bool argument, either True or False
    '''
    
    if isinstance(arg, bool):
        return arg
    if arg.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif arg.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')