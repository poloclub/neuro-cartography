import { 
  data_path
} from './constant.js'
import {
  selected_class
} from './variable.js'
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

    // Views
    this.embedding_view = null
    this.graph_view = null

  }


  ///////////////////////////////////////////////////////
  // Data path
  ///////////////////////////////////////////////////////

  get_node_file_path() {
    let dir_path = `${data_path['graph_dir']}/node`
    let synset = selected_class['synset']
    let node_path = `${dir_path}/node-${synset}.json`
    return [node_path]
  }

  get_edge_file_path() {
    let dir_path = `${data_path['graph_dir']}/edge`
    let synset = selected_class['synset']
    let edge_path = `${dir_path}/edge-${synset}.json`
    return [edge_path]
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
    path_list = path_list.concat(
      this.get_edge_file_path()
    )
    return path_list
  }


  ///////////////////////////////////////////////////////
  // Generate views
  ///////////////////////////////////////////////////////

  generate_view() {

    let this_class = this

    Promise.all(this.paths.map(file => d3.json(file))).then(
      function(data) {

        // Generate graph view
        this_class.generate_graph_view(
          data[6], data[7]
        )

        // Generate embedding view
        this_class.generate_embedding_view(
          data.slice(0, 6)
        )
        this_class.gen_embedding_header()

        // Generate graph view header
        this_class.generate_graph_view_header()

        // Turn off "Loading data" text
        d3.select('#loading_data')
          .style('display', 'none')

      }
    )
  }

  gen_embedding_header() {
    let emb_header = new EmbeddingHeader(
      'embedding_header',
      this.embedding_view
    )
    emb_header.gen_filtering()
    emb_header.gen_epoch()
  }

  generate_embedding_view(data) {
    this.embedding_view = new EmbeddingView(
      'embedding_view', 
      data,
      this.graph_view
    )
    this.embedding_view.draw_dots()
  }

  generate_graph_view(node_data, edge_data) {
    this.graph_view = new GraphView(
      node_data, 
      edge_data,
      this.model
    )
    this.graph_view.draw_graph()
  }

  generate_graph_view_header() {
    let graph_view_header = new GraphViewHeader(
      this.model,
      this.graph_view
    )
    graph_view_header.gen_header()
  }

}

main()