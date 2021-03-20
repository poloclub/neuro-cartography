import { 
  data_path
} from './constant.js'
import {
  InceptionV1
} from './model.js'
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
    this.neuron_data = {}
    this.emb_data = {}

    // Views
    this.embedding = null

  }

  ///////////////////////////////////////////////////////
  // Generate views
  ///////////////////////////////////////////////////////

  generate_view() {

    let this_class = this

    Promise.all(this.paths.map(file => d3.json(file))).then(
      function(data) {

        // Load and parse data
        this_class.parse_neuron_data(data.slice(1))

        // Generate embebdding header
        this_class.gen_embedding_header()
        
        // Generate embedding view
        this_class.emb_data = data[0]
        this_class.generate_embedding_view()

        // Generate graph view header
        this_class.generate_graph_view_header()

        // Generate graph view
        this_class.generate_graph_view()

      }
    )
  }

  gen_embedding_header() {
    let emb_header = new EmbeddingHeader(
      'embedding_header'
    )
    emb_header.gen_filtering()
  }

  generate_embedding_view() {
    this.embedding = new EmbeddingView(
      'embedding_view', this.emb_data, this.neuron_data
    )
    this.embedding.draw_dots()
  }

  generate_graph_view_header() {
    let graph_view_header = new GraphViewHeader()
    graph_view_header.gen_header()
  }

  generate_graph_view() {
    this.graph_view = new GraphView(
      this.neuron_data, this.model
    )
    this.graph_view.draw_graph()
  }


  ///////////////////////////////////////////////////////
  // Data path
  ///////////////////////////////////////////////////////

  get_neuron_file_path() {
    let neuron_paths = []
    let dir_path = data_path['neuron_group_path']
    for (let blk of this.model.BLKS) {
      neuron_paths.push(
        `${dir_path}/buckets-${blk}.json`
      )
    }
    return neuron_paths
  }

  get_data_path_list() {
    let path_list = []
    path_list = path_list.concat(
      data_path['emb_path']
    )
    path_list = path_list.concat(
      this.get_neuron_file_path()
    )
    return path_list
  }

  parse_neuron_data(data) {
    let i = 0
    for (let blk_data of data) {
      let blk = this.model.BLKS[i]
      this.neuron_data[blk] = blk_data
      i += 1
    }
  }

}

main()