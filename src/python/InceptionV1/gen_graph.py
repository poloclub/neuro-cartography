'''
* Project:
    Neuro-Cartography: Drawing Concept-based Neural Maps to Interpret 
    Deep Neural Networks by Automatically Discovering and Visualizing 
    Cell Assemblies
* File name:
    lsh.py
* Description:
    Generate clustered graph
* Author:
    Haekyu Park (haekyu@gatech.edu)
* Date:
    Jan 30, 2020
'''

import json


class ClusteredGraph:

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Class for generating clustered graph
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def __init__(self, args, data_path, model_wrapper):

        # Objects of other classes
        self.neuron_groups = {}
        self.connections = {}

        # Model
        self.model = model_wrapper.model

        # Data path
        self.data_path = data_path

        # Hyperparameters


    def update_data_path(self, layer):
        '''
        Update data path for gen_graph. Update layer.
        * input
            - data_path: data_path before updated
        * ouput
            - data_path: updated data_path
        '''

        # Update layer in data_path
        self.data_path.args.layer = layer
        self.data_path.HYPER_PARAMETERS \
            ['lsh']['bucket']['neuron'][1] = layer
        self.data_path.HYPER_PARAMETERS \
            ['lsh']['bucket']['connection'][1] = layer

        # Update paths
        self.data_path.gen_data_path('lsh')        


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for generating clustered graph
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def gen_graph(self):
        '''
        Generate graph
        '''

        # Generate neuron groups
        self.gen_neuron_groups()

        # Generate connections among the groups
        self.gen_group_connections()


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for generating neuron groups
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def gen_neuron_groups(self):
        '''
        Find neuron groups of all blocks
        '''

        # Initialize neuron_groups
        for blk in self.model.BLKS:
            self.neuron_groups[blk] = {}

        # Load buckets
        self.neuron_groups = self.load_neuron_buckets()

        # Save buckets
        dir_path = self.data_path.get_data_path(
            'graph',
            target='neuron',
            data_or_time='data'
        )
        file_path = '{}/graph-neuron.json'.format(dir_path)
        with open(file_path, 'w') as f:
            json.dump(self.neuron_groups, f)


    def load_neuron_buckets(self):
        '''
        Load neuron buckets of all blocks
        * input
            - N/A
        * output
            - buckets: loaded buckets of all blocks
        '''

        buckets_all_blk = {}
        for layer in self.model.LAYERS:
            
            # Update data path with the given layer
            self.update_data_path(layer)
            dir_path = self.data_path.get_data_path(
                'bucket',
                target='neuron',
                data_or_time='data'
            )

            for apdx in ['', '_3x3', '_5x5']:

                if (layer == 'mixed3a') and ('_' in apdx):
                    continue

                blk = layer + apdx
                buckets_all_blk[blk] = {}
                file_path = '{}/bucket-{}.json'.format(dir_path, blk)
                with open(file_path, 'r') as f:
                    buckets = json.load(f)

                for key in buckets:
                    buckets_all_blk[blk][key] = buckets[key]

        return buckets_all_blk


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Functions for generating connections among groups
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def gen_group_connections(self): 
        '''
        Generate connections among groups
        * input
            - N/A
        * output
            - N/A
        '''

        # Load all connections
        connections_all_blk = self.load_all_connections()

        # Connections among groups
        for blk in self.neuron_groups:
            self.connections[blk] = {}
            if blk == 'mixed3a':
                continue
            for cluster in self.neuron_groups[blk]:
                self.connections[blk][cluster] = {}
                for neuron in self.neuron_groups[blk][cluster]:
                    self.connections[blk][cluster][neuron] = {}
                    for conn_info in connections_all_blk[blk][neuron]:
                        prev_neuron = conn_info['prev']
                        cnt = conn_info['cnt']
                        prev_cluster = self.find_prev_cluster(neuron, prev_neuron)
                        if prev_cluster is not None:
                            if prev_cluster not in self.connections[blk][cluster][neuron]:
                                self.connections[blk][cluster][neuron][prev_cluster] = []
                            self.connections[blk][cluster][neuron][prev_cluster].append(
                                {
                                    'prev': prev_neuron,
                                    'cnt': cnt
                                }
                            )

        # Save the connection information
        dir_path = self.data_path.get_data_path(
            'graph',
            target='connection',
            data_or_time='data'
        )
        file_path = '{}/graph-connection.json'.format(dir_path)
        with open(file_path, 'w') as f:
            json.dump(self.connections, f)
        
                    
                    
    def find_prev_cluster(self, neuron, prev_neuron):
        '''
        Find previous cluster number
        '''

        prev_blk = self.model.get_prev_blk(neuron)

        for cluster in self.neuron_groups[prev_blk]:
            for prev_candidate in self.neuron_groups[prev_blk][cluster]:
                if prev_candidate == prev_neuron:
                    return cluster
        
        return None


    def load_all_connections(self):
        '''
        Load all connections of all layers
        * input
            - N/A
        * output
            - connections_all_blk: connection info of all blocks
        '''

        connections_all_blk = {}

        for layer in self.model.LAYERS:

            if layer == 'mixed3a':
                continue
            
            # Update data path with the given layer
            self.update_data_path(layer)
            dir_path = self.data_path.get_data_path(
                'bucket',
                target='connection',
                data_or_time='data'
            )
            file_path = '{}/bucket.json'.format(dir_path)
            with open(file_path, 'r') as f:
                buckets = json.load(f)

            for blk in buckets:
                connections_all_blk[blk] = {}
                for cluster in buckets[blk]:
                    for neuron in buckets[blk][cluster]:
                        conn_info = sorted(
                            buckets[blk][cluster][neuron].items(),
                            key=lambda x: x[1],
                            reverse=True
                        )
                        top_conn_info = conn_info[:10]
                        connections_all_blk[blk][neuron] = []
                        for prev_neuron, cnt in conn_info:
                            connections_all_blk[blk][neuron].append({
                                'prev': prev_neuron,
                                'cnt': cnt
                            })

        return connections_all_blk
                    