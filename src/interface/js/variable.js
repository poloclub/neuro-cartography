export var shown_group = {
  'group': 'None'
}

export var mode = {
  'mode': 'normal'
}

export var embedding_setup = {
  'filtering': 'All-neurons', // 'All-neurons', 'Neurons-of-Class', 'Neurons-of-Selected-groups'
  'epoch': 3 // [0, 1, 2, 3, 4, 5]
}

export var selected_class = {
  'synset': 'n02085936',
  // 'synset': 'n02107574',
  // 'synset': 'n02113624'
  // 'synset': 'n04328186'
}

export var selected_groups = {
  'groups': new Set(),
  'neurons': new Set(),
}

export var selected_neuron = {
  'selected': null
}

export var cascade_group = {
  'selected': null
}

export var filter_nodes = {
  'max_num_nodes': 5,
  'max_num_neurons': 10,
  'cnt_unit': 50, 
  'cnt_thr': 3, // means 2 * cnt_unit
  'cnt_min': 0, // means 0
  'cnt_max': 10 // means 5 * cnt_unit
}


export var most_related_neurons = {
  'nei': []
}

export var neuron_to_group = {
  'n2g': {}
}