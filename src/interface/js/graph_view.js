import { Icon } from './icon.js'
import { 
  data_path, graph_style, cascade_style, emb_style, patch_style 
} from './constant.js'
import {
  shown_group, mode, selected_groups, selected_class, filter_nodes,
  selected_neuron, most_related_neurons, neuron_to_group, cascade_group,
  embedding_setup
} from './variable.js'
import { Dropdown } from './dropdown.js'
import { get_css_var } from './utils.js'
import { ExampleView } from './example_view.js'
import { SearchBar } from './search_bar.js'
import { Slider } from './slider.js'



export class GraphViewHeader {

  constructor(model, graph_view) {
    this.model = model
    this.BLKS = model.BLKS
    this.graph_view = graph_view
  }

  gen_header() {
    this.gen_header_layout()
    this.add_model() 
    this.add_dataset()
    this.add_class_search_bar()
    this.add_mode()
    this.set_layer_layout_y()
    this.add_filter_slider()
  }

  gen_header_layout() {

    // Header
    let header = document.getElementById('graph_view-header')

    // Model
    let model = document.createElement('div')
    model.id = 'graph_view-header-model'
    model.className = 'graph_view-header-component'
    header.appendChild(model)

    // Dataset
    let dataset = document.createElement('div')
    dataset.id = 'graph_view-header-dataset'
    dataset.className = 'graph_view-header-component'
    header.appendChild(dataset)

    // Class
    let class_selection = document.createElement('div')
    class_selection.id = 'graph_view-header-class'
    class_selection.className = 'graph_view-header-component'
    header.appendChild(class_selection)

    // Mode
    let mode_wrap = document.createElement('div')
    mode_wrap.id = 'graph_view-header-mode'
    mode_wrap.className = 'graph_view-header-component'
    header.appendChild(mode_wrap)

    // Filter
    let filter_wrap = document.createElement('div')
    filter_wrap.id = 'graph_view-header-filter'
    filter_wrap.className = 'graph_view-header-component'
    header.appendChild(filter_wrap)

  }

  add_model() {

    // Model div
    let model = document.getElementById(
      'graph_view-header-model'
    )

    // Title
    let title = document.createElement('div')
    title.className = 'graph_view-header-title'
    title.innerText = 'Model'
    model.appendChild(title)

    // Model name
    let model_name = document.createElement('div')
    model_name.innerText = 'InceptionV1'
    model.appendChild(model_name)

    // TODO: We can add dropdown if we want multiple models
    // let dropdown = new Dropdown('model-selection')
    // dropdown.gen_dropdown('InceptionV1')
    // for (let item of ['InceptionV1', 'Compressed-InceptionV1']) {
    //   dropdown.add_dropdown_menu_item(
    //     item,
    //     item.replace('-', ' '),
    //     {
    //       'mouseover': function() {  },
    //       'mouseout': function() {  },
    //       'click': function() {  }
    //     }
    //   )
    // }
    // model.appendChild(dropdown.get_dropdown()) 

  }

  add_dataset() {

    // Dataset div
    let dataset = document.getElementById(
      'graph_view-header-dataset'
    )

    // Title
    let title = document.createElement('div')
    title.className = 'graph_view-header-title'
    title.innerText = 'Dataset'
    dataset.appendChild(title)

    // Imagenet
    let imagenet = document.createElement('div')
    imagenet.innerText = 'ImageNet'
    dataset.appendChild(imagenet)

  }

  parse_synset_data(data) {
    let synset_data = []
    for (let d of data) {
      synset_data.push(
        {
          'id': d['synset'],
          'text': fst_letter_capital(d['name'].replace(/_/g, ' '))
        }
      )
    }
    return synset_data

    function fst_letter_capital(s) {
      return s.charAt(0).toUpperCase() + s.slice(1)
    }
  }

  add_class_search_bar() {

    let this_class = this

    d3.tsv(data_path['class_label'], function(data) {
      return data
    }).then(function(data) {

      // Add class title
      let class_selection = document.getElementById(
        'graph_view-header-class'
      )
      let class_title = document.createElement('div')
      class_title.innerText = 'Class'
      class_title.id = 'graph_view-header-class-title'
      class_title.className = 'graph_view-header-title'
      class_selection.appendChild(class_title)

      // Search bar
      let search_bar = new SearchBar(
        'class-search',
        'class-search',
        'Maltese dog',
        {
          'mouseover': function() {},
          'mouseout': function() {},
          'click': function(click_id) {
            selected_class['synset'] = click_id
            this_class.graph_view.reload_graph()
          }
        },
        this_class.parse_synset_data(data)
      )
      
      class_selection.appendChild(search_bar.get_search_bar())  
    })

  }

  format_class_label(s) {
    s = s.replace(/_/g, ' ')
    s = s.charAt(0).toUpperCase() + s.slice(1)
    return s
  }

  add_mode() {

    // Define components
    let mode_wrap = document.getElementById(
      'graph_view-header-mode'
    )
    let mode_text = document.createElement('div')
    let mode_normal = document.createElement('div')
    let mode_cascade = document.createElement('div')

    // Mode text
    mode_text.innerText = 'Mode'
    mode_text.id = 'graph_view-header-mode-text'
    mode_text.className = 'graph_view-header-title'
    mode_wrap.appendChild(mode_text)

    // Mode normal
    mode_normal.id = 'normal-mode'
    mode_normal.className = 'mode-component'
    mode_normal.innerText = 'Normal'
    mode_wrap.appendChild(mode_normal)

    // Mode icon
    let this_class = this
    let icon = new Icon(
      'mode-icon', 'toggle-on', 'mode_icon'
    )
    icon.gen_icon()
    mode_wrap.appendChild(icon.get_icon())
    icon.get_icon_i().style.transform = 'rotateY(180deg)'
    icon.set_click(() => {

      let normal_div = document.getElementById('normal-mode')
      let cascade_div = document.getElementById('cascade-mode')
      let icon_i = icon.get_icon_i()
      let graph_view = document.getElementById('graph_view')

      if (mode['mode'] == 'normal') {

        // Update mode
        mode['mode'] = 'cascade'

        // Refresh selection option
        selected_groups['groups'] = new Set()
        d3.selectAll('.emb-dot')
          .style('stroke', (d) => {
            let neuron_id = d['neuron']
            if (neuron_id == selected_neuron) {
              return get_css_var('--dodgerblue')
            } else {
              return 'none'
            }
          })
          .attr('fill', (d) => {
            // TODO:
            let neuron_id = d['neuron']
            let is_in_neighbor = document.getElementById(`NNView-neighbors-${neuron_id}`) != null            
            if (neuron_id == selected_neuron) {
              return get_css_var('--dodgerblue')
            } else {
              if (is_in_neighbor) {
                return get_css_var('--dodgerblue')
              } else {
                return get_css_var('--gray')
              }
            }
          })
          .attr('width', (d) => {
            let neuron_id = d['neuron']
            let is_in_neighbor = document.getElementById(`NNView-neighbors-${neuron_id}`) != null
            let width = d3.select(`#dot-${neuron_id}`).attr('width')
            if (neuron_id == selected_neuron) {
              return width
            } else {
              if (is_in_neighbor) {
                return width
              } else {
                return emb_style['normal-r']
              }
            }
          })
          .attr('height', (d) => {
            let neuron_id = d['neuron']
            let is_in_neighbor = document.getElementById(`NNView-neighbors-${neuron_id}`) != null
            let height = d3.select(`#dot-${neuron_id}`).attr('height')
            if (neuron_id == selected_neuron) {
              return height
            } else {
              if (is_in_neighbor) {
                return height
              } else {
                return emb_style['normal-r']
              }
            }
          })
          .style('opacity', (d) => {
            let neuron_id = d['neuron']
            let is_in_neighbor = document.getElementById(`NNView-neighbors-${neuron_id}`) != null
            if (neuron_id == selected_neuron) {
              return emb_style['highlight-opacity']
            } else {
              if (is_in_neighbor) {
                return emb_style['highlight-opacity']
              } else {
                return emb_style['normal-opacity']
              }
            }
            
          })

        // Mode color
        d3.select('#normal-mode')
        .style('color', get_css_var('--bright_gray_text'))
        d3.select('#cascade-mode')
          .style('color', get_css_var('--gray_text'))

        // Icon 
        icon_i.style.transform = 'rotateY(0deg)'

        // Make all node gray
        d3.selectAll('.node')
          .attr('gill', get_css_var('--gray'))

      } else {

        // Update mode
        mode['mode'] = 'normal'

        // Mode color
        d3.select('#normal-mode')
          .style('color', get_css_var('--gray_text'))
        d3.select('#cascade-mode')
          .style('color', get_css_var('--bright_gray_text'))

        // Icon 
        icon_i.style.transform = 'rotateY(180deg)'

        // Disable cascade mode
        this_class.graph_view.disable_cascade_mode()

      }

    })

    // Mode cascade
    mode_cascade.id = 'cascade-mode'
    mode_cascade.className = 'mode-component'
    mode_cascade.innerText = 'Concept Cascade'
    mode_cascade.style.color = get_css_var('--bright_gray_text')
    mode_wrap.appendChild(mode_cascade)

  }


  add_filter_slider() {

    // Title
    let filter_div = document.getElementById(
      'graph_view-header-filter'
    )
    let title = document.createElement('div')
    title.innerText = 'Filter Graph'
    title.id = 'graph_view-header-filter-text'
    title.className = 'graph_view-header-title'
    filter_div.appendChild(title)

    // Filter slider
    let this_class = this
    let range = this.node_range
    let slider = new Slider(
      'node-filter',
      'slider',
      [filter_nodes['cnt_min'], filter_nodes['cnt_max']],
      filter_nodes['cnt_thr'],
      function(selected_val) {
        this_class.update_node_with_filtering(selected_val)
      }
    )
    filter_div.appendChild(slider.get_slider())
  }

  update_node_with_filtering(selected_val) {

    // Update selected value
    filter_nodes['cnt_thr'] = selected_val

    // Count the number of nodes to show
    this.update_num_nodes()

    // Update x scale
    this.set_group_layout_x()

    // Update node location
    let W = graph_style['node_w'] + graph_style['x_gap']
    let this_class = this
    d3.selectAll('.node')
      .transition()
      .duration(1000)
      .attr('x', d => {
        let blk = d[0].split('-')[1]
        let i = parseInt(d[0].split('-')[2])
        let x = this_class.graph_view.blk_x[blk]
        return x + i * W
      })
      .style('display', d => {
        let blk = d[0].split('-')[1]
        let i = parseInt(d[0].split('-')[2])
        let n = this_class.graph_view.num_nodes[blk]
        if (i < n) {
          return 'inline-block'
        } else {
          return 'none'
        }
      })

    // Update wrapper size and location
    this.update_block_wrap()

    // Update connection location
    this.update_connection()

  }

  update_num_nodes() {

    let thr = filter_nodes['cnt_thr'] * filter_nodes['cnt_unit']
    
    for (let blk of this.BLKS) {
      let blk_groups = this.graph_view.node_data[blk]
      let blk_i = 0
      for (let g in blk_groups) {
        let cnt = blk_groups[g]['cnt']
        if (cnt > thr) {
          blk_i = blk_i + 1
        }
      }
      this.graph_view.num_nodes[blk] = blk_i
    }

  }

  set_group_layout_x() {

    let W = graph_style['node_w'] + graph_style['x_gap']
    let this_class = this

    for (let layer of this.model.LAYERS) {

      // Layer block
      let num_neuron_layer = this_class.graph_view.num_nodes[layer]
      this_class.graph_view.blk_x[layer] = - W * parseInt(num_neuron_layer / 2)

      // Ignore mixed3a, as we do not use mixed_3x3 and mixed_5x5
      if (layer == 'mixed3a') {
        continue
      }

      // 3x3 block
      let blk_3x3 = `${layer}_3x3`
      let num_neuron_3x3 = this_class.graph_view.num_nodes[blk_3x3]
      this_class.graph_view.blk_x[blk_3x3] = 
        this_class.graph_view.blk_x[layer] - W * num_neuron_3x3
        - graph_style['blk_gap']

      // 5x5 block
      let blk_5x5 = `${layer}_5x5`
      this_class.graph_view.blk_x[blk_5x5] = 
        this_class.graph_view.blk_x[layer] + W * num_neuron_layer
        + graph_style['blk_gap']

    }
  }

  set_group_layout_x_cascade() {

    // XXX

  }

  set_layer_layout_y() {
    let y = 0
    for (let layer of this.model.REV_LAYERS) {
      this.graph_view.blk_y[layer] = y
      if (layer == 'mixed3a') {
        continue
      }
      this.graph_view.blk_y[`${layer}_3x3`] = y + graph_style['y_gap']
      this.graph_view.blk_y[`${layer}_5x5`] = y + graph_style['y_gap']
      y += (2 * graph_style['y_gap'])
    }
  }

  update_block_wrap() {

    let this_class = this
    let H = graph_style['blk_bg']['height']
    let h = graph_style['node_h']

    for (let blk of this.model.BLKS) {

      d3.select(`#blk-bg-${blk}`)
        .transition()
        .duration(1000)
        .attr('x', this_class.graph_view.blk_x[blk] - H / 2 + h / 2)
        .attr('width', get_blk_bg_w(blk))

      d3.select(`#blk-${blk}`)
        .transition()
        .duration(1000)
        .attr('x', this_class.graph_view.blk_x[blk])

    }

    function get_blk_bg_w(blk) {
      let W = graph_style['node_w'] + graph_style['x_gap']
      let num_neuron = this_class.graph_view.num_nodes[blk]
      let H = graph_style['blk_bg']['height']
      let h = graph_style['node_h']
      if (num_neuron == 0) {
        return 0
      } else {
        return W * num_neuron + H - h - graph_style['x_gap']
      }
    }
  }

  update_connection() {

    let this_class = this
    this.graph_view.gen_edge_width_scale()

    d3.selectAll('.edge-path')
      .transition()
      .duration(1000)
      .attr('d', function(d) {           
        let group = this.id.split('-conn-')[0] 
        return gen_path(group, d[0]) 
      })
      .style('display', function(d) {

        // Check if prev block is shown
        let prev_blk = d[0].split('-')[1]
        let prev_n = parseInt(d[0].split('-')[2])
        let is_prev_on = 
          prev_n < this_class.graph_view.num_nodes[prev_blk]

        // Check if curr block is shown
        let group = this.id.split('-conn-')[0] 
        let blk = group.split('-')[1]
        let curr_n = parseInt(group.split('-')[2])
        let is_curr_on = 
          curr_n < this_class.graph_view.num_nodes[blk]

        // Display on / off
        if (is_prev_on && is_curr_on) {
          return 'inline-block'
        } else {
          return 'none'
        }

      })

      function gen_path(group, prev_group) {

        let blk = group.split('-')[1]
        let prev_blk = prev_group.split('-')[1]
        let groun_n = group.split('-')[2]
        let prev_group_n = prev_group.split('-')[2]
        groun_n = parseInt(groun_n)
        prev_group_n = parseInt(prev_group_n)
  
        let W = graph_style['node_w'] + graph_style['x_gap']
        let H = graph_style['node_h'] 
        let x1 = this_class.graph_view.blk_x[prev_blk] + prev_group_n * W
        let y1 = this_class.graph_view.blk_y[prev_blk] + 0.05 * H 
        let x2 = this_class.graph_view.blk_x[blk] + groun_n * W
        let y2 = this_class.graph_view.blk_y[blk] - 0.05 * H 
        x1 += graph_style['node_w'] / 2
        x2 += graph_style['node_w'] / 2
        y2 += graph_style['node_h'] 
  
        return this_class.graph_view.gen_curve(x1, y1, x2, y2)
      }
  }

}


export class GraphView {

  constructor(node_data, edge_data, node_cascade, edge_cascade, model) {

    // Model
    this.model = model
    this.BLKS = model.BLKS

    // Node data
    this.node_data = {}
    this.node_range = {}
    this.num_nodes = {}
    this.parse_node_data(node_data)
    this.update_num_nodes()

    // Edge data
    this.edge_data = {}
    this.group_level_conn_data = {}
    this.parse_edge_data(edge_data)

    // Cascade data
    this.node_cascade = node_cascade
    this.edge_cascade = edge_cascade

    // Layout
    this.blk_x = {}
    this.blk_y = {}

  }

  ///////////////////////////////////////////////////////
  // Parse data
  ///////////////////////////////////////////////////////

  parse_node_data(data) {

    let this_class = this
    this.node_data = data
    
    // Minimum count (A-mat) of nodes
    let blk_min_cnt = Object.values(data).map(        
      (x) => {
        let blk_nodes = Object.values(x)
        let blk_cnts = blk_nodes.map(y => y['cnt'])
        let blk_min = this_class.reduce_min(blk_cnts)
        return blk_min
      }
    )

    // Maximum count (A-mat) of nodes
    let blk_max_cnt = Object.values(data).map(        
      (x) => {
        let blk_nodes = Object.values(x)
        let blk_cnts = blk_nodes.map(y => y['cnt'])
        let blk_max = this_class.reduce_max(blk_cnts)
        return blk_max
      }
    )

    // Node count range
    this.node_range = [
      this_class.reduce_min(blk_min_cnt),
      this_class.reduce_max(blk_max_cnt)
    ]

  }

  update_num_nodes() {

    let thr = filter_nodes['cnt_thr'] * filter_nodes['cnt_unit']
    let this_class = this

    for (let blk of this.BLKS) {
      let blk_groups = this.node_data[blk]
      
      let blk_i = 0
      for (let g in blk_groups) {
        let cnt = blk_groups[g]['cnt']
        if (cnt > thr) {
          blk_i = blk_i + 1
        }
      }
      this_class.num_nodes[blk] = blk_i
    }

  }

  parse_edge_data(data) {
    this.edge_data = data
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

  get_cascade_file_path() {
    let synset = selected_class['synset']
    let file_paths = [
      `${data_path['cascade_node']}/cascade-node-${synset}.json`,
      `${data_path['cascade_edge']}/cascade-edge-${synset}.json`
    ]
    return file_paths
  }

  get_data_path_list() {
    let path_list = []
    path_list = path_list.concat(
      this.get_node_file_path()
    )
    path_list = path_list.concat(
      this.get_edge_file_path()
    )
    path_list = path_list.concat(
      this.get_cascade_file_path()
    )
    return path_list
  }


  ///////////////////////////////////////////////////////
  // Draw graph
  ///////////////////////////////////////////////////////

  draw_graph() {  

    // Make graph_view zoomable
    this.make_graph_zoomable()
        
    // Set layout of nodes
    this.set_layer_layout_y()
    this.set_group_layout_x()

    // Add block names
    this.add_block_wrap()
        
    // Draw nodes
    this.draw_nodes()
    this.auto_zoom_out()

    // Draw connections
    this.draw_connections()

  }

  reload_graph() {
    // XXX
    // Turn on "Loading data" text
    d3.select('#loading_data')
      .style('display', 'block')

    // Update graph
    let this_class = this
    Promise.all(this_class.get_data_path_list().map(file => d3.json(file))).then(
      function(data) {

        // Refresh views
        d3.selectAll('.node').remove()
        d3.selectAll('.edge-path').remove()
        d3.selectAll('.example-view-wrapper').remove()
        selected_groups['groups'] = new Set()
        selected_groups['neurons'] = new Set()
        this_class.disable_cascade_mode()

        this_class.parse_node_data(data[0])
        this_class.parse_edge_data(data[1])
        // data[2]
        this_class.node_cascade = data[2]
        this_class.edge_cascade = data[3]

        this_class.refresh_emb()
        this_class.update_num_nodes()
        this_class.set_layer_layout_y()
        this_class.set_group_layout_x()
        this_class.draw_nodes()
        this_class.update_block_wrap()
        this_class.draw_connections()

        // Turn off "Loading data" text
        d3.select('#loading_data')
          .style('display', 'none') 
      }
    )

  }
  
  refresh_emb() {

    let n2g = this.get_neuron_group_mapping()
    d3.selectAll('.emb-dot')
      .attr('class', (d) => {
        let neuron = d['neuron']
        let class1 = 'emb-dot'
        let class2 = 'emb-dot-group-' + n2g[neuron]
        let class3 = 'emb-dot-' + neuron.split('-')[0]
        return [class1, class2, class3].join(' ')
      })
      .attr('width', emb_style['normal-r'])
      .attr('height', emb_style['normal-r'])
      .attr('fill', get_css_var('--gray'))
      .attr('opacity', emb_style['normal-opacity'])
      
    this.highlight_selected_and_nei_embedding()
  }
  
  get_neuron_group_mapping() {
    let n2g = {}
    let nodes_of_class = this.node_data
    for (let blk in nodes_of_class) {
      for (let g_num in nodes_of_class[blk]) {
        for (let neuron of nodes_of_class[blk][g_num]['group']) {
          n2g[neuron] = [blk, g_num].join('-')
        }
      }
    }
    neuron_to_group['n2g'] = n2g
    return n2g
  }

  ///////////////////////////////////////////////////////
  // Make graph_view zoomable
  ///////////////////////////////////////////////////////

  make_graph_zoomable() {
    d3.select('#graph_view-svg')
      .style('pointer-events', 'all')
      .call(
        d3.zoom()
          .on('zoom', function(){
            d3.select('#graph_view-node-g')
              .attr('transform', d3.event.transform)
            d3.select('#graph_view-edge-g')
              .attr('transform', d3.event.transform)
            d3.select('#graph_view-cascade-node-g')
              .attr('transform', d3.event.transform)
            d3.select('#graph_view-cascade-edge-g')
              .attr('transform', d3.event.transform)
            d3.selectAll('.example-view-wrapper')
              .style('display', 'none')
          })
      )
  }

  auto_zoom_out() {

    let W = graph_style['graph_view_W']
    let H = graph_style['graph_view_H']

    let zoom = d3.zoom()
      .scaleExtent([.1, 3.5])
      .extent([[0, 0], [W, H]])
      .on('zoom', function() {
        d3.select('#graph_view-node-g')
          .attr('transform', d3.event.transform)
        d3.select('#graph_view-edge-g')
          .attr('transform', d3.event.transform)
      })

    d3.select('#graph_view-svg')
      .transition()
      .duration(750)
      .call(
        zoom.transform,
        d3.zoomIdentity.translate(W * 0.55, H * 0.35).scale(0.06)
      )
  }
  

  ///////////////////////////////////////////////////////
  // Node layout
  ///////////////////////////////////////////////////////

  set_group_layout_x() {

    let W = graph_style['node_w'] + graph_style['x_gap']
    let this_class = this

    for (let layer of this.model.LAYERS) {

      // Layer block
      let num_neuron_layer = this_class.num_nodes[layer]
      this.blk_x[layer] = - W * parseInt(num_neuron_layer / 2)

      // Ignore mixed3a, as we do not use mixed_3x3 and mixed_5x5
      if (layer == 'mixed3a') {
        continue
      }

      // 3x3 block
      let blk_3x3 = `${layer}_3x3`
      let num_neuron_3x3 = this_class.num_nodes[blk_3x3]
      this.blk_x[blk_3x3] = 
        this.blk_x[layer] - W * num_neuron_3x3
        - graph_style['blk_gap']

      // 5x5 block
      let blk_5x5 = `${layer}_5x5`
      this.blk_x[blk_5x5] = 
        this.blk_x[layer] + W * num_neuron_layer
        + graph_style['blk_gap']

    }
  }

  set_layer_layout_y() {
    let y = 0
    for (let layer of this.model.REV_LAYERS) {
      this.blk_y[layer] = y
      if (layer == 'mixed3a') {
        continue
      }
      this.blk_y[`${layer}_3x3`] = y + graph_style['y_gap']
      this.blk_y[`${layer}_5x5`] = y + graph_style['y_gap']
      y += (2 * graph_style['y_gap'])
    }
  }

  len(item) {
    if (Array.isArray(item)) {
      return item.length
    } else {
      return Object.keys(item).length
    }
  }

  update_block_wrap() {

    let this_class = this
    let H = graph_style['blk_bg']['height']
    let h = graph_style['node_h']

    for (let blk of this.model.BLKS) {

      d3.select(`#blk-bg-${blk}`)
        .transition()
        .duration(1000)
        .attr('x', this_class.blk_x[blk] - H / 2 + h / 2)
        .attr('width', get_blk_bg_w(blk))

      d3.select(`#blk-${blk}`)
        .transition()
        .duration(1000)
        .attr('x', this_class.blk_x[blk])

    }

    function get_blk_bg_w(blk) {
      let W = graph_style['node_w'] + graph_style['x_gap']
      let num_neuron = this_class.num_nodes[blk]
      let H = graph_style['blk_bg']['height']
      let h = graph_style['node_h']
      if (num_neuron == 0) {
        return 0
      } else {
        return W * num_neuron + H - h - graph_style['x_gap']
      }
    }
  }

  set_group_layout_x_cascade() {

    let W = graph_style['node_w'] + graph_style['x_gap']
    let this_class = this

    for (let layer of this.model.LAYERS) {
      
      // layer
      let blk_5x5 = `${layer}_5x5`
      let blk_layer_cascade = `${layer}-cascade`
      let num_node_5x5 = num_new_node(blk_5x5)
      this_class.blk_x[blk_layer_cascade] = 
        this_class.blk_x[blk_5x5] + W * num_node_5x5
        + graph_style['blk_gap'] * 3

      if (layer == '3x3') {
        continue
      }

      // 3x3
      let blk_3x3_cascade = `${layer}_3x3-cascade`
      this_class.blk_x[blk_3x3_cascade] = 
        this_class.blk_x[blk_5x5] + W * num_node_5x5
        + graph_style['blk_gap'] * 2

      // 5x5
      let blk_5x5_cascade = `${layer}_5x5-cascade`
      let num_node_3x3 = num_new_node(`${layer}_3x3`)
      this_class.blk_x[blk_5x5_cascade] = 
        this_class.blk_x[blk_3x3_cascade] + W * num_node_3x3
        + graph_style['blk_gap'] * 2

    }

    function num_new_node(blk) {
      let n = 0
      let selected_group = cascade_group['selected'].split('-g-')[1]
      selected_group = 'g-' + selected_group
      for (let new_group in this_class.node_cascade[selected_group]['new']) {
        let new_group_blk = new_group.split('-g-')[1].split('-')[0]
        if (new_group_blk == blk) {
          n += 1
        }
      }
      return n
    }

  }


  ///////////////////////////////////////////////////////
  // Layer block styling
  ///////////////////////////////////////////////////////

  add_block_wrap() {

    let this_class = this
    let H = graph_style['blk_bg']['height']
    let h = graph_style['node_h']

    for (let blk of this.model.BLKS) {

      // Add block bg-rect
      d3.select('#graph_view-node-g')
        .append('rect')
        .attr('id', `blk-bg-${blk}`)
        .attr('class', 'blk-bg')
        .attr('x', this_class.blk_x[blk] - H / 2 + h / 2)
        .attr('y', this_class.blk_y[blk] - H / 2 + h / 2)
        .attr('width', get_blk_bg_w(blk))
        .attr('height', H)
        .attr('fill', () => {
          if (blk.includes('3x3')) {
            return graph_style['blk_bg']['color']['3x3']
          } else if (blk.includes('5x5')) {
            return graph_style['blk_bg']['color']['5x5']
          } else {
            return graph_style['blk_bg']['color']['normal']
          }
        })
        .style('opacity', graph_style['blk_bg']['opacity'])
        .attr('rx', graph_style['blk_bg']['rx'])
        .attr('ry', graph_style['blk_bg']['ry'])

      // Add block name
      d3.select('#graph_view-node-g')
        .append('text')
        .attr('id', `blk-${blk}`)
        .attr('class', 'layer-name')
        .text(blk)
        .attr('x', this_class.blk_x[blk])
        .attr('y', this_class.blk_y[blk] - H / 2)
        .style('display', () => {
          if (this_class.num_nodes[blk] == 0) {
            return 'none'
          } else {
            return 'inline-block'
          }
        })
        .attr('fill', () => {
          if (blk.includes('3x3')) {
            return graph_style['blk_name']['color']['3x3']
          } else if (blk.includes('5x5')) {
            return graph_style['blk_name']['color']['5x5']
          } else {
            return graph_style['blk_name']['color']['normal']
          }
        })

    }
    
    function get_blk_bg_w(blk) {
      let W = graph_style['node_w'] + graph_style['x_gap']
      let num_neuron = this_class.num_nodes[blk]
      let H = graph_style['blk_bg']['height']
      let h = graph_style['node_h']
      if (num_neuron == 0) {
        return 0
      } else {
        return W * num_neuron + H - h - graph_style['x_gap']
      }
    }

  }

  ///////////////////////////////////////////////////////
  // Draw nodes
  ///////////////////////////////////////////////////////

  draw_nodes() {

    for (let layer of this.model.REV_LAYERS) {

      // Groups in layer block
      this.draw_nodes_blk(layer) 

      // Ignore mixed3a
      if (layer == 'mixed3a') {
        continue
      }

      // Groups in 3x3 and 5x5 block
      this.draw_nodes_blk(`${layer}_3x3`) 
      this.draw_nodes_blk(`${layer}_5x5`)      

    }
  }

  draw_nodes_blk(blk) {

    let W = graph_style['node_w'] + graph_style['x_gap']
    let x = this.blk_x[blk]
    let y = this.blk_y[blk]
    let this_class = this
    d3.select('#graph_view-node-g')
      .selectAll('nodes')
      .data(
        Object.entries(
          this.node_data[blk]
        )
      )
      .enter()
        .append('rect')
        .attr('id', function(d) {
          return `${blk}-${d[0]}`
        })
        .attr('class', 'node')
        .attr('rx', 100)
        .attr('ry', 100)
        .attr('x', d => {
          let i = parseInt(d[0].split('-')[2])
          return x + i * W
        })
        .attr('y', y)
        .attr('fill', get_css_var('--gray'))
        .attr('width', graph_style['node_w'])
        .attr('height', graph_style['node_h'])
        .style('display', d => {
          let blk = d[0].split('-')[1]
          let n = this_class.num_nodes[blk]
          let i = parseInt(d[0].split('-')[2])
          if (i < n) {
            return 'inline-block'
          } else {
            return 'none'
          }
        })
        .on('mouseenter', function() {
          this_class.mouseenter_node(this)
        })
        .on('mouseleave', function() {
          this_class.mouseleave_node(this)
        })
        .on('click', function() {
          this_class.click_node(this)
        })
  }

  highlight_selected_and_nei_embedding() {

    // Turn off other embeddings first
    d3.selectAll('.emb-dot')
      .attr('fill', get_css_var('--gray'))
      .style('stroke', 'none')
      .attr('width', emb_style['normal-r'])
      .attr('height', emb_style['normal-r'])
      .style('opacity', emb_style['normal-opacity'])

    // Highlight most related neurons
    let neighbors = most_related_neurons['nei']
    let this_class = this
    for (let nei of neighbors) {
      d3.select(`#dot-${nei}`)
        .attr('fill', () => {
          if (this_class.is_in_selected_group(nei)) {
            return get_css_var('--hotpink')
          } else {
            return get_css_var('--dodgerblue')
          }
        })
        .attr('width', emb_style['highlight-r'])
        .attr('height', emb_style['highlight-r'])
        .style('opacity', emb_style['highlight-opacity'])
        .raise()
    }

    // Highlight embedding of clicked groups
    for (let g of selected_groups['groups']) {
      d3.selectAll(`.emb-dot-group-${g}`)
        .attr('fill', get_css_var('--hotpink'))
        .attr('width', emb_style['highlight-r'])
        .attr('height', emb_style['highlight-r'])
        .style('opacity', emb_style['highlight-opacity'])
        .raise()
    }

    // Highlight embedding of selected neuron
    d3.select(`#dot-${selected_neuron['selected']}`)
      .attr('fill', 'white')
      .style('stroke', () => {
        let neuron = selected_neuron['selected']
        if (this_class.is_in_selected_group(neuron)) {
          return get_css_var('--hotpink')
        } else {
          return get_css_var('--dodgerblue')
        }
      })
      .attr('width', emb_style['highlight-r'])
      .attr('height', emb_style['highlight-r'])
      .style('opacity', emb_style['highlight-opacity'])
      .raise()

  }

  highlight_nei_dots() {
    let neighbors = most_related_neurons['nei']
    let this_class = this
    for (let nei of neighbors) {
      d3.select(`#dot-${nei}`)
        .attr('fill', () => {
          if (this_class.is_in_selected_group(nei)) {
            return get_css_var('--hotpink')
          } else {
            return get_css_var('--dodgerblue')
          }
        })
        .attr('width', emb_style['highlight-r'])
        .attr('height', emb_style['highlight-r'])
        .raise()
    }
  }

  is_in_selected_group(neuron) {
    if (selected_groups['neurons'].has(neuron)) {
      return true
    } else {
      return false
    }
  }

  show_cluster_popup(node) {

    // Generate example view
    let [blk, group] = node.id.split('-g-')
    group = 'g-' + group
    let neurons = this.node_data[blk][group]['group']
    let view_id = `ex-${blk}-${group}`
    if (document.getElementById(view_id) == null) {
      let ex_view = new ExampleView(
        'example_view', blk, group, 'example-view', neurons
      )
      ex_view.gen_example_view()
    }

    // Example view scale
    let curr_scale = d3.select('#graph_view-node-g').attr('transform')
    curr_scale = parseFloat(curr_scale.split('scale(')[1].slice(0, -1)) 

    // Show example patches of neurons
    d3.select(`#ex-${blk}-${group}`)
      .style('display', 'block')
      .style('left', () => {
        let x = d3.event.pageX
        let w = 550
        let mv_x = -w * (1 - 3 * curr_scale) / 2
        mv_x += (3 * curr_scale) * graph_style['node_w'] * 4.5
        return (x + mv_x) + 'px'
      })
      .style('top', () => {
        let y = d3.event.pageY
        let h = patch_style['one_neuron_wrap_height']
        h = d3.min([
          h * patch_style['max_num_wrap'],
          h * neurons.length
        ])
        let mv_y = -h * (1 - 3 * curr_scale) / 2
        mv_y -= graph_style['node_h'] * curr_scale

        return (y + mv_y) + 'px'
      })
      .style('height', () => {
        let h = patch_style['one_neuron_wrap_height']
        h = d3.min([
          h * patch_style['max_num_wrap'],
          h * neurons.length
        ])
        return h + 'px'
      })
      .style('transform', `scale(${3 * curr_scale})`)
    shown_group['group'] = `${blk}-${group}`
  }

  mouseenter_node(node) {   

    if (mode['mode'] == 'normal') {
      this.mouseenter_normal(node)
    } else {
      this.mouseenter_cascade(node)
    }

  }

  mouseenter_cascade(node) {

    // Highlight node
    d3.select(`#${node.id}`)
      .attr('fill', get_css_var('--hotpink'))

    // Show cluster popup
    this.show_cluster_popup(node)    
  }

  mouseenter_normal(node) {
    // Turn off all others first
    d3.selectAll('.example-view-wrapper')
      .style('display', 'none')
    d3.selectAll('.node')
      .attr('fill', get_css_var('--gray'))

    // Show cluster popup
    this.show_cluster_popup(node)

    // Highlight selected neuon and neighbors' embedding
    this.highlight_selected_and_nei_embedding()

    // Highlight embedding of hovered group
    let [blk, group] = node.id.split('-g-')
    group = 'g-' + group
    let neurons = this.node_data[blk][group]['group']
    let this_class = this
    for (let neuron of neurons) {
      d3.select('#dot-' + neuron)
        .attr('fill', () => {
          if (neuron == selected_neuron['selected']) {
            return 'white'
          } else {
            return get_css_var('--hotpink')
          }
        })
        .attr('width', emb_style['hover-r'])
        .attr('height', emb_style['hover-r'])
        .style('opacity', emb_style['highlight-opacity'])
    }
    
    // Highlight node of selected group
    for (let g of selected_groups['groups']) {
      d3.select(`#${g}`)
        .attr('fill', get_css_var('--hotpink'))
    }

    // Highlight node
    d3.select(`#${blk}-${group}`)
      .attr('fill', get_css_var('--hotpink'))

    // Highlight edge
    d3.selectAll(`.edge-${group}`)
      .classed('flowline', true)
  }

  mouseleave_node(node) {

    if (mode['mode'] == 'normal') {
      this.mouseleave_normal(node)
    } else {
      this.mouseleave_cascade(node)
    }

  }

  mouseleave_cascade(node) {

    let [blk, group] = node.id.split('-g-')
    group = `g-` + group
    let group_id = `${blk}-${group}`
    shown_group['group'] = 'None'

    let this_class = this
    setTimeout(function() {
      if (shown_group['group'] != group_id) {

        // Display off example view 
        d3.select(`#ex-${blk}-${group}`)
          .style('display', 'none')

        // Dehighlight node
        d3.select(`#${blk}-${group}`)
          .attr('fill', get_css_var('--gray'))

        // Highlight node of selected group
        for (let g of selected_groups['groups']) {
          d3.select(`#${g}`)
            .attr('fill', get_css_var('--hotpink'))
        }

        // Highlight embedding of clicked groups
        this_class.highlight_selected_and_nei_embedding()
        
      } 
    }, 700)

    // Dehighlight edge
    d3.selectAll(`.edge-${group}`)
      .classed('flowline', false)

    // Highlight embedding of clicked groups
    this.highlight_selected_and_nei_embedding()

    // Highlight node of selected group
    for (let g of selected_groups['groups']) {
      d3.select(`#${g}`)
        .attr('fill', get_css_var('--hotpink'))
    }

  }

  mouseleave_normal(node) {
    let [blk, group] = node.id.split('-g-')
    group = `g-` + group
    let group_id = `${blk}-${group}`
    shown_group['group'] = 'None'

    let this_class = this
    setTimeout(function() {
      if (shown_group['group'] != group_id) {

        // Display off example view 
        d3.select(`#ex-${blk}-${group}`)
          .style('display', 'none')

        // Dehighlight node
        d3.select(`#${blk}-${group}`)
          .attr('fill', get_css_var('--gray'))

        // Highlight node of selected group
        for (let g of selected_groups['groups']) {
          d3.select(`#${g}`)
            .attr('fill', get_css_var('--hotpink'))
        }

        // Highlight embedding of clicked groups
        this_class.highlight_selected_and_nei_embedding()
        
      } 
    }, 800)

    // Dehighlight edge
    d3.selectAll(`.edge-${group}`)
      .classed('flowline', false)

    // Highlight embedding of clicked groups
    this.highlight_selected_and_nei_embedding()

    // Highlight node of selected group
    for (let g of selected_groups['groups']) {
      d3.select(`#${g}`)
        .attr('fill', get_css_var('--hotpink'))
    }

  }

  click_node(node) {

    if (mode['mode'] == 'normal') {

      this.cilck_node_normal(node)

    } else {
      d3.select('#graph_view-cascade-node-g')
        .selectAll('.node').remove()
      d3.select('#graph_view-cascade-node-g')
        .selectAll('rect').remove()
      d3.select('#graph_view-cascade-node-g')
        .selectAll('text').remove()
      d3.select('#graph_view-cascade-edge-g')
        .selectAll('path').remove()
      cascade_group['selected'] = node.id
      this.set_group_layout_x_cascade()
      this.draw_cascade()
    }    

  }

  cilck_node_normal(node) {
    if (selected_groups['groups'].has(node.id)) {

      // Remove group from the selected groups
      selected_groups['groups'].delete(node.id)

      // Remove neurons of the node from the selected groups
      let blk = node.id.split('-g-')[0]
      let g = 'g-' + node.id.split('-g-')[1]
      for (let neuron of this.node_data[blk][g]['group']) {
        selected_groups['neurons'].delete(neuron)
      }

      // Dehighlight node
      d3.select(`#${node.id}`)
        .attr('fill', get_css_var('--gray'))

      // Dehighlight off embedding
      d3.selectAll(`.emb-dot-group-${node.id}`)
        .attr('fill', get_css_var('--gray'))
        .attr('r', emb_style['normal-r'])

    } else {

      // Add group to the selected groups
      selected_groups['groups'].add(node.id)

      // Add neurons of the node from the selected groups
      let blk = node.id.split('-g-')[0]
      let g = 'g-' + node.id.split('-g-')[1]
      for (let neuron of this.node_data[blk][g]['group']) {
        selected_groups['neurons'].add(neuron)
      }

      // Highlight node
      d3.select(`#${node.id}`)
        .attr('fill', get_css_var('--hotpink'))

      // Highlight embedding
      d3.selectAll(`.emb-dot-group-${node.id}`)
        .attr('fill', get_css_var('--hotpink'))
        .attr('r', emb_style['highlight-r'])

    }
  }

  ///////////////////////////////////////////////////////
  // Draw connection
  ///////////////////////////////////////////////////////

  draw_connections() {

    // Get ready
    let this_class = this
    this.gen_edge_width_scale()

    // Draw connections
    for (let blk in this.edge_data) {
      
      for (let group in this.edge_data[blk]) {

        // Add edges
        d3.select('#graph_view-edge-g')
          .selectAll('edges')
          .data(Object.entries(this.edge_data[blk][group]))
          .enter()
            .append('path')
            .attr('id', function(d) { 
              return gen_edge_id(group, d[0])
            })
            .attr('class', (d) => {
              let class1 = 'edge-path'
              let class2 = `edge-${d[0]}`
              let class3 = `edge-${group}`
              return [class1, class2, class3].join(' ')
            })
            .attr('d', function(d) {               
              return gen_path(group, d[0]) 
            })
            .attr('stroke-width', function(d) {
              return this_class.edge_stroke_width_scale(d[1])
            })
            .attr('stroke', graph_style['edge_color'])
            .style('display', function(d) {

              // Check if prev block is shown
              let prev_blk = d[0].split('-')[1]
              let is_prev_off = d3
                .select(`#${prev_blk}-${d[0]}`)
                .style('display') == 'none'
              if (is_prev_off) {
                return 'none'
              }

              // Check if curr block is shown
              let is_curr_off = d3
                .select(`#${blk}-${group}`)
                .style('display') == 'none'
              if (is_curr_off) {
                return 'none'
              }
              
              return 'inline-block'

            })
      }
    }

    function gen_edge_id(group, prev_group) {
      return `${group}-conn-${prev_group}`
    }

    function gen_path(group, prev_group) {

      let blk = group.split('-')[1]
      let prev_blk = prev_group.split('-')[1]
      let groun_n = group.split('-')[2]
      let prev_group_n = prev_group.split('-')[2]
      groun_n = parseInt(groun_n)
      prev_group_n = parseInt(prev_group_n)

      let W = graph_style['node_w'] + graph_style['x_gap']
      let H = graph_style['node_h'] 
      let x1 = this_class.blk_x[prev_blk] + prev_group_n * W
      let y1 = this_class.blk_y[prev_blk] + 0.05 * H 
      let x2 = this_class.blk_x[blk] + groun_n * W
      let y2 = this_class.blk_y[blk] - 0.05 * H 
      x1 += graph_style['node_w'] / 2
      x2 += graph_style['node_w'] / 2
      y2 += graph_style['node_h'] 

      return this_class.gen_curve(x1, y1, x2, y2)
    }
  }

  gen_curve(x1, y1, x2, y2) {

    if (x1 == x2) {
      x1 = x1 + 0.1
    }

    let c1_x = x1
    let c1_y = (y1 + y2) * 0.5
    let c2_x = x2
    let c2_y = (y1 + y2) * 0.5
  
    let path = 'M ' + x1 + ',' + y1
    path += ' C ' + c1_x + ' ' + c1_y
    path += ' ' + c2_x + ' ' + c2_y + ','
    path += ' ' + x2 + ' ' + y2
    return path

  }

  gen_edge_width_scale() {

    // Maximum edge cnt
    let max_edge_cnt = 0
    for (let blk in this.edge_data) {
      for (let group in this.edge_data[blk]) {
        let d = this.edge_data[blk][group]
        if (this.len(d) > 0) {
          let max_cnt = d3.max(Object.values(d))
          max_edge_cnt = d3.max([max_edge_cnt, max_cnt])
        }
      }
    }

    this.edge_stroke_width_scale = d3.scaleLinear()
      .domain([0, max_edge_cnt])
      .range([
        graph_style['edge_width_min'], 
        graph_style['edge_width_max']
      ])
  }

  ///////////////////////////////////////////////////////
  // Cascade mode
  ///////////////////////////////////////////////////////

  draw_cascade() {

    this.draw_cascade_block_wrap()
    this.draw_cascade_nodes()
    this.draw_cascade_edges()

  }

  draw_cascade_nodes() {
    let this_class = this
    let W = graph_style['node_w'] + graph_style['x_gap']
    let selected_group = cascade_group['selected'].split('-g-')[1]
    selected_group = 'g-' + selected_group
    
    d3.select('#graph_view-cascade-node-g')
      .selectAll('nodes')
      .data(        
        Object.entries(this_class.node_cascade[selected_group]['new'])
      )
      .enter()
        .append('rect')
        .attr('id', d => d[0])
        .attr('class', 'node')
        .attr('rx', 100)
        .attr('ry', 100)
        .attr('x', d => {
          let blk = d[0].split('-g-')[1].split('-')[0]
          let x = this_class.blk_x[`${blk}-cascade`]
          let i = parseInt(d[0].split('-')[3])
          return x + i * W
        })
        .attr('y', d => {
          let blk = d[0].split('-g-')[1].split('-')[0]
          let y = this_class.blk_y[blk]
          return y
        })
        .attr('fill', get_css_var('--hotpink'))
        .attr('width', graph_style['node_w'])
        .attr('height', graph_style['node_h'])
        .style('display', 'block')
        .style('cursor', 'pointer')
        .on('mouseover', (d) => {
          console.log(d)
          this_class.show_cluster_popup_cascade(d)
        })

    for (let item of Object.entries(this_class.node_cascade[selected_group]['existing'])) {
      let g = item[0]
      let blk = g.split('-')[1]
      d3.select(`#${blk}-${g}`)
        .attr('fill', get_css_var('--hotpink'))
    }
  }

  show_cluster_popup_cascade(d) {

    // Generate example view
    let group = d[0]
    let blk = group.split('-')[2]
    // group = 'g-' + group
    let neurons = d[1]['neurons']
    let view_id = `ex-${d[0]}`
    if (document.getElementById(view_id) == null) {
      let ex_view = new ExampleView(
        'example_view', blk, group, 'example-view', neurons
      )
      ex_view.gen_example_view()
    }

    // Example view scale
    let curr_scale = d3.select('#graph_view-node-g').attr('transform')
    curr_scale = parseFloat(curr_scale.split('scale(')[1].slice(0, -1)) 

    console.log(d3.select(`#ex-${blk}-${d[0]}`))

    // Show example patches of neurons
    d3.select(`#ex-${blk}-${d[0]}`)
      .style('display', 'block')
      .style('left', () => {
        let x = d3.event.pageX
        let w = 550
        let mv_x = -w * (1 - 3 * curr_scale) / 2
        mv_x += (3 * curr_scale) * graph_style['node_w'] * 4.5
        return (x + mv_x) + 'px'
      })
      .style('top', () => {
        let y = d3.event.pageY
        let h = patch_style['one_neuron_wrap_height']
        h = d3.min([
          h * patch_style['max_num_wrap'],
          h * neurons.length
        ])
        let mv_y = -h * (1 - 3 * curr_scale) / 2
        mv_y -= graph_style['node_h'] * curr_scale
        return (y + mv_y) + 'px'
      })
      .style('height', () => {
        let h = patch_style['one_neuron_wrap_height']
        h = d3.min([
          h * patch_style['max_num_wrap'],
          h * neurons.length
        ])
        return h + 'px'
      })
      // .style('transform', `translate(-500px, 500px) scale(${3 * curr_scale})`)
      .style('transform', `scale(${3 * curr_scale})`)
    // shown_group['group'] = `${blk}-${group}`
  

  }

  draw_cascade_block_wrap() {

    let this_class = this
    let H = graph_style['blk_bg']['height']
    let h = graph_style['node_h']

    for (let blk of this.model.BLKS) {

      if (blk == 'mixed3a') {
        continue
      }

      // Add block bg-rect
      d3.select('#graph_view-cascade-node-g')
        .append('rect')
        .attr('id', `cascade-blk-bg-${blk}`)
        .attr('class', 'blk-bg cascade-blk-bg')
        .attr('x', () => {
          return this_class.blk_x[`${blk}-cascade`] - H / 2 + h / 2
        })
        .attr('y', () => {
          return this_class.blk_y[blk] - H / 2 + h / 2
        })
        .attr('width', get_blk_bg_w(blk))
        .attr('height', H)
        .attr('fill', () => {
          if (blk.includes('3x3')) {
            return graph_style['blk_bg']['color']['3x3']
          } else if (blk.includes('5x5')) {
            return graph_style['blk_bg']['color']['5x5']
          } else {
            return graph_style['blk_bg']['color']['normal']
          }
        })
        .style('opacity', graph_style['blk_bg']['opacity'])
        .attr('rx', graph_style['blk_bg']['rx'])
        .attr('ry', graph_style['blk_bg']['ry'])

      // Add block name
      d3.select('#graph_view-cascade-node-g')
        .append('text')
        .attr('id', `blk-${blk}`)
        .attr('class', 'layer-name')
        .text(blk)
        .attr('x', () => {
          return this_class.blk_x[`${blk}-cascade`]
        })
        .attr('y', () => {
          return this_class.blk_y[blk] - H / 2
        })
        .style('display', () => {
          if (get_blk_bg_w(blk) == 0) {
            return 'none'
          } else {
            return 'inline-block'
          }
        })
        .attr('fill', () => {
          if (blk.includes('3x3')) {
            return graph_style['blk_name']['color']['3x3']
          } else if (blk.includes('5x5')) {
            return graph_style['blk_name']['color']['5x5']
          } else {
            return graph_style['blk_name']['color']['normal']
          }
        })
    }

    function get_blk_bg_w(blk) {
      let W = graph_style['node_w'] + graph_style['x_gap']
      let num_neuron = num_new_node(blk)
      let H = graph_style['blk_bg']['height']
      let h = graph_style['node_h']
      if (num_neuron == 0) {
        return 0
      } else {
        return W * num_neuron + H - h - graph_style['x_gap']
      }
    }

    function num_new_node(blk) {
      let n = 0
      let selected_group = cascade_group['selected'].split('-g-')[1]
      selected_group = 'g-' + selected_group
      for (let new_group in this_class.node_cascade[selected_group]['new']) {
        let new_group_blk = new_group.split('-g-')[1].split('-')[0]
        if (new_group_blk == blk) {
          n += 1
        }
      }
      return n
    }
  }

  draw_cascade_edges() {

    let this_class = this

    let selected_group = cascade_group['selected']
    let initial_node = 'g-' + selected_group.split('-g-')[1]
    let max_weight = 0
    for (let item of Object.entries(this_class.edge_cascade[initial_node])) {
      let avg_weight = item[1]['weight_sum'] / item[1]['total_num']
      max_weight = d3.max([max_weight, avg_weight])
    }
    let width_scale = d3.scaleLinear()
      .domain([0, max_weight])
      .range([10, 30])

    d3.select('#graph_view-cascade-edge-g')
      .selectAll('edges')
      .data(Object.entries(this_class.edge_cascade[initial_node]))
      .enter()
        .append('path')
        .attr('id', d => {
          let [group, prev_group] = d[0].split(',')
          return gen_edge_id(group, prev_group)
        })
        .attr('class', (d) => {
          let [group, prev_group] = d[0].split(',')
          let class1 = 'edge-path'
          let class2 = `edge-${group}`
          let class3 = `edge-${prev_group}`
          let class4 = 'edge-cascade'
          return [class1, class2, class3, class4].join(' ')
        })
        .attr('d', function(d) {     
          let [prev_group, group] = d[0].split(',')          
          return gen_path(group, prev_group) 
        })
        .attr('stroke-width', function(d) {
          let avg_weight = d[1]['weight_sum'] / d[1]['total_num']
          return width_scale(avg_weight)
        })
        // .attr('stroke', graph_style['edge_color'])
        .attr('stroke', get_css_var('--hotpink'))
        .style('display', function(d) {

          // Node id
          let [prev_group, group] = d[0].split(',')  
          if (!(group.includes('new'))) {
            let b = group.split('-')[1]
            group = b + '-' + group
          }
          if (!(prev_group.includes('new'))) {
            let b = prev_group.split('-')[1]
            prev_group = b + '-' + prev_group
          }

          // Check if the nodes are in the graph
          if (document.getElementById(group) == null) {
            return 'none'
          }
          if (document.getElementById(prev_group) == null) {
            return 'none'
          }

          // Check if prev block is shown
          let is_prev_off = d3
            .select(`#${prev_group}`)
            .style('display') == 'none'
          if (is_prev_off) {
            return 'none'
          }

          // Check if curr block is shown
          let is_curr_off = d3
            .select(`#${group}`)
            .style('display') == 'none'
          if (is_curr_off) {
            return 'none'
          }

          
          return 'inline-block'

        })

    function gen_edge_id(group, prev_group) {
      return `${group}-conn-${prev_group}`
    }

    function gen_path(group, prev_group) {

      // Blk
      let blk = ''
      let groun_n = ''
      if (group.includes('new')) {
        blk = group.split('-')[2] + '-cascade'
        groun_n = parseInt(group.split('-')[3])
      } else {
        blk = group.split('-')[1]
        groun_n = parseInt(group.split('-')[2])
      }
      
      // Prev blk
      let prev_blk = ''
      let prev_group_n = ''
      if (prev_group.includes('new')) {
        prev_blk = prev_group.split('-')[2] + '-cascade'
        prev_group_n = parseInt(prev_group.split('-')[3])
      } else {
        prev_blk = prev_group.split('-')[1]
        prev_group_n = parseInt(prev_group.split('-')[2])
      }

      // Generate curve
      let W = graph_style['node_w'] + graph_style['x_gap']
      let H = graph_style['node_h'] 
      let x1 = this_class.blk_x[prev_blk] + prev_group_n * W
      let y1 = this_class.blk_y[prev_blk.replace('-cascade', '')] + 0.05 * H 
      let x2 = this_class.blk_x[blk] + groun_n * W
      let y2 = this_class.blk_y[blk.replace('-cascade', '')] - 0.05 * H 
      x1 += graph_style['node_w'] / 2
      x2 += graph_style['node_w'] / 2
      y2 += graph_style['node_h'] 

      return this_class.gen_curve(x1, y1, x2, y2)
    }
    
  }

  disable_cascade_mode() {

    mode['mode'] = 'normal'
    cascade_group['selected'] = null
    d3.select('#graph_view-cascade-node-g')
      .selectAll('.node').remove()
    d3.select('#graph_view-cascade-node-g')
      .selectAll('rect').remove()
    d3.select('#graph_view-cascade-node-g')
      .selectAll('text').remove()
    d3.select('#graph_view-cascade-edge-g')
      .selectAll('path').remove()
    d3.selectAll('.example-view-cascade').remove()
  }


}
