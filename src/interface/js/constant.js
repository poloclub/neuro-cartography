// For icons in svg: https://fontawesome.com/cheatsheet
export var icon_class = {
  'paper': 'fas fa-file-pdf',
  'youtube': 'fab fa-youtube',
  'github': 'fab fa-github',
  'setting': 'fas fa-cog',
  'left-arrow': 'fas fa-arrow-left',
  'map': '\uf05b',
  'cascade': 'fas fa-sitemap',
  'dropdown-down': 'fas fa-caret-down',
  'toggle-on': 'fas fa-toggle-on',
  'search': 'fas fa-search'
}

export var data_path = {
  'graph_dir': './data/InceptionV1/graph',
  'neuron_group_path': './data/InceptionV1/bucket/bucket-all-10-20',
  'image_dir': './data/InceptionV1-vis/example-patch',
  'class_label': './data/imagenet-labels.txt',
  'emb_path': './data/InceptionV1/embedding_2d'
}

export var graph_style = {
  'graph_view_W': 800,
  'graph_view_H': 800,
  'node_w': 80,
  'node_h': 80,
  'x_gap': 40,
  'y_gap': 400,
  'blk_gap': 600,
  'blk_bg': {
    'height': 200,
    'color': {
      'normal': '#fbb4ae',
      '3x3': '#b3cde3',
      '5x5': '#ccebc5'
    },
    'opacity': 0.5
  },
  'blk_name': {
    '3x3': {
      'mv_x': -320,
      'mv_y': 40
    },
    '5x5': {
      'mv_x': 5,
      'mv_y': 40
    },
    'layer': {
      'mv_x': -230,
      'mv_y': 40
    }
  },
  'edge_color': 'rgb(200, 200, 200)',
}

export var patch_style = {
  'num_exs': 7,
  'num_row': 1,
  'num_col': 7,
  'num_exs_neuron': 9,
  'num_row_neuron': 3,
  'num_col_neuron': 3,
  'width': 80,
  'height': 80,
  'width-gap': 3,
  'one_neuron_wrap_height': 120,
  'max_num_wrap': 4
}

export var cascade_style = {
  // 'bg-color': 'rgb(50, 50, 50)'
}

export var emb_style = {
  'normal-r': 3,
  'highlight-r': 5,
  'hover-r': 8,
  'normal-opacity': 0.5
}