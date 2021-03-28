export var shown_group = {
  'group': 'None'
}

export var mode = {
  'mode': 'normal'
}

export var embedding_setup = {
  'filtering': 'All-neurons', // 'All-neurons', 'Neurons-of-Class', 'Neurons-of-Selected-groups'
  'epoch': 3 // [1, 2, 3, 4, 5, 6]
}

export var selected_class = {
  'synset': 'n02085936'
}

export var selected_groups = {
  'groups': new Set()
}

export var selected_neuron = {
  'selected': ''
}

export var filter_nodes = {
  'max_num_nodes': 5,
  'max_num_neurons': 10,
  'cnt_thr': 2, // means 200
  'cnt_min': 0, // means 0
  'cnt_max': 5 // means 500
}