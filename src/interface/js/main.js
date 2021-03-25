import { 
  data_path
} from './constant.js'
import {
  InceptionV1
} from './model.js'
import {
  synsets
} from './synsets.js'
import {
  EmbeddingHeader,
  EmbeddingView
} from './embedding_view.js'
import { 
  GraphView,
  GraphViewHeader 
} from './graph_view.js'


function main() {
  let main_view = new Main()
  main_view.generate_view()
}

class Main {

  constructor() {

    // Model
    this.model = new InceptionV1()

    // Data path
    this.paths = this.get_data_path_list()

    // Data
    this.node_data = {}
    this.node_range = {}
    this.emb_data = []
    this.emb_range = {}

    // Views
    this.embedding = null
    this.graph_view = null

  }


  ///////////////////////////////////////////////////////
  // Data path
  ///////////////////////////////////////////////////////

  get_node_file_path() {
    let node_paths = []
    let dir_path = `${data_path['graph_dir']}/node/`
    for (let synset of synsets) {
      node_paths.push(
        `${dir_path}/node-${synset}.json`
      )
    }
    return node_paths
  }

  get_emb_file_path() {
    let emb_paths = []
    for (let i of [0, 1, 2, 3, 4, 5]) {
      let file_path = `${data_path['emb_path']}/embedding_2d-30-5-10-0.01-${i}.json`
      emb_paths.push(file_path)
    }
    return emb_paths
  }

  get_data_path_list() {
    let path_list = []
    path_list = path_list.concat(
      this.get_emb_file_path()
    )
    path_list = path_list.concat(
      this.get_node_file_path()
    )
    return path_list
  }


  ///////////////////////////////////////////////////////
  // Parse data
  ///////////////////////////////////////////////////////

  parse_node_data(data) {

    let this_class = this

    for (let i in synsets) {

      // Node data
      let synset = synsets[i]
      this.node_data[synset] = data[i]

      // Minimum count (A-mat) of nodes
      let blk_min_cnt = Object.values(data[i]).map(        
        (x) => {
          let blk_nodes = Object.values(x)
          let blk_cnts = blk_nodes.map(y => y['cnt'])
          let blk_min = this_class.reduce_min(blk_cnts)
          return blk_min
        }
      )

      // Maximum count (A-mat) of nodes
      let blk_max_cnt = Object.values(data[i]).map(        
        (x) => {
          let blk_nodes = Object.values(x)
          let blk_cnts = blk_nodes.map(y => y['cnt'])
          let blk_max = this_class.reduce_max(blk_cnts)
          return blk_max
        }
      )

      // Node count range
      this.node_range[synset] = [
        this_class.reduce_min(blk_min_cnt),
        this_class.reduce_max(blk_max_cnt)
      ]
    }

  }

  reduce_min(arr) {
    return arr.reduce((a, b) => {
      if (a < b) {
        return a
      } else {
        return b
      }
    })
  }

  reduce_max(arr) {
    return arr.reduce((a, b) => {
      if (a > b) {
        return a
      } else {
        return b
      }
    })
  }

  parse_emb_data(data) {

    // Initialize embedding range
    let min_xy = {}
    let max_xy = {}
    for (let i of [0, 1, 2, 3, 4, 5]) {
      min_xy[i] = {'x': 1000, 'y': 1000}
      max_xy[i] = {'x': 0, 'y': 0}
    }

    // Parse embedding data and get embedding range
    let neurons = Object.keys(data[0])
    for (let neuron of neurons) {
      let d = {}
      d['neuron'] = neuron
      for (let i of [0, 1, 2, 3, 4, 5]) {
        d[i + 1] = data[i][neuron].split(',').map(x => parseFloat(x))
        min_xy[i]['x'] = d3.min([min_xy[i]['x'], d[i + 1][0]])
        min_xy[i]['y'] = d3.min([min_xy[i]['y'], d[i + 1][1]])
        max_xy[i]['x'] = d3.max([max_xy[i]['x'], d[i + 1][0]])
        max_xy[i]['y'] = d3.max([max_xy[i]['x'], d[i + 1][1]])
      }
      this.emb_data.push(d)
    }

    // Parse embedding range
    for (let i of [0, 1, 2, 3, 4, 5]) {
      this.emb_range[i] = {
        'x': [min_xy[i]['x'], max_xy[i]['x']],
        'y': [min_xy[i]['y'], max_xy[i]['x']],
      }
    }

  }

  ///////////////////////////////////////////////////////
  // Generate views
  ///////////////////////////////////////////////////////

  generate_view() {

    let this_class = this

    Promise.all(this.paths.map(file => d3.json(file))).then(
      function(data) {

        // Load and parse data
        this_class.parse_node_data(data.slice(6))

        // Generate embedding view
        this_class.parse_emb_data(data.slice(0, 6))
        this_class.gen_embedding_header()
        this_class.generate_embedding_view()

        // Generate graph view
        this_class.generate_graph_view()

        // Generate graph view header
        this_class.generate_graph_view_header()

      }
    )
  }

  gen_embedding_header() {
    let emb_header = new EmbeddingHeader(
      'embedding_header',
      this.emb_range
    )
    emb_header.gen_filtering()
    emb_header.gen_epoch()
  }

  generate_embedding_view() {
    this.embedding = new EmbeddingView(
      'embedding_view', 
      this.emb_data, 
      this.emb_range,
      this.node_data
    )
    this.embedding.draw_dots()
  }

  generate_graph_view() {
    this.graph_view = new GraphView(
      this.node_data, 
      this.node_range,
      this.model
    )
    this.graph_view.draw_graph()
  }

  generate_graph_view_header() {
    let graph_view_header = new GraphViewHeader(
      this.node_range, 
      this.model,
      this.node_data,
      this.graph_view
    )
    graph_view_header.gen_header()
  }

}

main()