import { Icon } from './icon.js'
import { 
  data_path, graph_style, cascade_style, emb_style 
} from './constant.js'
import {
  shown_group, mode, selected_groups, selected_class, filter_nodes
} from './variable.js'
import { Dropdown } from './dropdown.js'
import { get_css_var } from './utils.js'
import { ExampleView } from './example_view.js'
import { SearchBar } from './search_bar.js'
import { Slider } from './slider.js'


export class GraphViewHeader {

  constructor(node_range, model, node_data, graph_view) {
    this.model = model
    this.BLKS = model.BLKS
    this.graph_view = graph_view
    this.node_range = node_range
    this.node_data = node_data
    this.num_nodes = {}
    this.blk_x = {}
    this.blk_y = {}
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

    // Dropdown
    let dropdown = new Dropdown('model-selection')
    dropdown.gen_dropdown('InceptionV1')
    for (let item of ['InceptionV1', 'Compressed-InceptionV1']) {
      dropdown.add_dropdown_menu_item(
        item,
        item.replace('-', ' '),
        {
          'mouseover': function() {  },
          'mouseout': function() {  },
          'click': function() {  }
        }
      )
    }
    
    model.appendChild(dropdown.get_dropdown()) 

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

      // TODO: Make this a search bar
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

        // Background color
        d3.select('#graph_view-header')
          .style('background', get_css_var('--gray'))
        graph_view.style.background = get_css_var('--gray')

        // Font color
        d3.select('#graph_view-header')
          .style('color', get_css_var('--bright_yellow_text'))
        d3.select('#normal-mode')
          .style('color', 'gray')
        d3.select('#cascade-mode')
          .style('color', get_css_var('--bright_yellow_text'))

        // Model dropdown color
        d3.select('#model-selection')
          .style('color', get_css_var('--bright_yellow_text'))
          .style('border-bottom', 
            `solid 0.5px ${get_css_var('--bright_yellow_text')}`)
        d3.select('#dropdown-menu-model-selection')
          .style('color', get_css_var('--gray_text'))
  
        // Class dropdown color
        d3.select('#class-selection')
          .style('color', get_css_var('--bright_yellow_text'))
          .style('border-bottom', 
            `solid 0.5px ${get_css_var('--bright_yellow_text')}`)
        d3.select('#dropdown-menu-class-selection')
          .style('color', get_css_var('--gray_text'))

        // Icon 
        icon_i.style.transform = 'rotateY(0deg)'

      } else {

        // Update mode
        mode['mode'] = 'normal'

        // Background color
        d3.select('#graph_view-header')
          .style('background', 'white')
        graph_view.style.background = 'white'

        // Font color
        d3.select('#graph_view-header')
          .style('color', get_css_var('--gray_text'))
        d3.select('#class-selection')
          .style('color', get_css_var('--gray_text'))
          .style('border-bottom', 
            `solid 0.5px ${get_css_var('--gray_text')}`)
        d3.select('#model-selection')
          .style('color', get_css_var('--gray_text'))
          .style('border-bottom', 
            `solid 0.5px ${get_css_var('--gray_text')}`)
        d3.select('#normal-mode')
          .style('color', get_css_var('--gray_text'))
        d3.select('#cascade-mode')
        .style('color', get_css_var('--bright_gray_text'))

        // Icon 
        icon_i.style.transform = 'rotateY(180deg)'
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
    title.innerText = 'Filter Nodes'
    title.id = 'graph_view-header-filter-text'
    title.className = 'graph_view-header-title'
    filter_div.appendChild(title)

    // Filter slider
    let this_class = this
    let range = this.node_range[selected_class['synset']]
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
        let x = this_class.blk_x[blk]
        return x + i * W
      })
      .style('display', d => {
        let blk = d[0].split('-')[1]
        let i = parseInt(d[0].split('-')[2])
        let n = this_class.num_nodes[blk]
        if (i < n) {
          return 'inline-block'
        } else {
          return 'none'
        }
      })

    // Update wrapper size and location
    this.update_block_wrap()

    // TODO: Update connection location

  }

  update_num_nodes() {

    let thr = filter_nodes['cnt_thr'] * 100
    
    for (let blk of this.BLKS) {
      let blk_groups = this.node_data[selected_class['synset']][blk]
      let blk_i = 0
      for (let g in blk_groups) {
        let cnt = blk_groups[g]['cnt']
        if (cnt > thr) {
          blk_i = blk_i + 1
        }
      }
      this.num_nodes[blk] = blk_i
    }

  }

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

}


export class GraphView {

  constructor(node_data, node_range, model) {

    // Model
    this.model = model
    this.BLKS = model.BLKS

    // Data
    this.node_data = node_data
    this.node_range = node_range
    this.num_nodes = {}
    this.update_num_nodes()
    
    // Layout
    this.blk_x = {}
    this.blk_y = {}

  }

  ///////////////////////////////////////////////////////
  // Parse data
  ///////////////////////////////////////////////////////

  update_num_nodes() {

    let thr = filter_nodes['cnt_thr'] * 100
    let this_class = this
    
    for (let blk of this.BLKS) {
      let blk_groups = this.node_data[selected_class['synset']][blk]
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

  }

  reload_graph() {

    console.log(this.node_data[selected_class['synset']])

    // Refresh views
    d3.selectAll('.node').remove()
    d3.selectAll('.edge').remove()
    selected_groups['groups'] = new Set()
    d3.selectAll('.emb-dot')
      .style('fill', get_css_var('--gray'))

    this.update_num_nodes()
    this.set_group_layout_x()
    this.draw_nodes()
    this.update_block_wrap()

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
            d3.select('#graph_view-g')
              .attr('transform', d3.event.transform)
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
        d3.select('#graph_view-g')
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

  ///////////////////////////////////////////////////////
  // Layer block styling
  ///////////////////////////////////////////////////////

  add_block_wrap() {

    let this_class = this
    let H = graph_style['blk_bg']['height']
    let h = graph_style['node_h']

    for (let blk of this.model.BLKS) {

      // Add block bg-rect
      d3.select('#graph_view-g')
        .append('rect')
        .attr('id', `blk-bg-${blk}`)
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
        .style('rx', 30)
        .style('ry', 30)

      // Add block name
      d3.select('#graph_view-g')
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
    d3.select('#graph_view-g')
      .selectAll('nodes')
      .data(
        Object.entries(
          this.node_data[selected_class['synset']][blk]
        )
      )
      .enter()
        .append('rect')
        .attr('id', function(d) {
          return `${blk}-${d[0]}`
        })
        .attr('class', 'node')
        .attr('rx', 10)
        .attr('ry', 10)
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

  mouseenter_node(node) {   

    // Generate example view
    let [blk, group] = node.id.split('-g-')
    group = 'g-' + group
    let neurons = this.node_data
      [selected_class['synset']][blk][group]['group']
    let view_id = `ex-${blk}-${group}`
    if (document.getElementById(view_id) == null) {
      let ex_view = new ExampleView(
        'example_view', blk, group, 'example-view', neurons
      )
      ex_view.gen_example_view()
    }

    // Example view size
    if (this.len(neurons) > 1) {
      d3.select(`#ex-${node.id}`)
        .style('height', '240px')
    } 

    // Turn off all others first
    d3.selectAll('.example-view-wrapper')
      .style('display', 'none')
    d3.selectAll('.node')
      .attr('fill', get_css_var('--gray'))

    // Example view scale
    let curr_scale = d3.select('#graph_view-g').attr('transform')
    curr_scale = parseFloat(curr_scale.split('scale(')[1].slice(0, -1)) 

    // Show example patches of neurons
    d3.select(`#ex-${blk}-${group}`)
      .style('display', 'block')
      .style('left', () => {
        let x = d3.event.pageX
        let w = 240
        let mv_x = -w * (1 - 5 * curr_scale) / 2
        return (x + mv_x) + 'px'
      })
      .style('top', () => {
        let y = d3.event.pageY
        let h = 280
        if (neurons.length > 1) {
          h = 240
        }
        let mv_y = -h * (1 - 5 * curr_scale) / 2 + 50 * curr_scale
        return (y + mv_y) + 'px'
      })
      .style('transform', `scale(${5 * curr_scale})`)
    shown_group['group'] = `${blk}-${group}`

    // Turn off other embeddings first
    d3.selectAll('.emb-dot')
      .attr('fill', get_css_var('--gray'))
      .attr('r', emb_style['normal-r'])

    // Highlight embedding
    for (let neuron of neurons) {
      d3.select('#dot-' + neuron)
        .attr('fill', get_css_var('--hotpink'))
        .attr('r', emb_style['hover-r'])
    }

    // Highlight node
    d3.select(`#${blk}-${group}`)
      .attr('fill', get_css_var('--hotpink'))

  }

  mouseleave_node(node) {

    let [blk, group] = node.id.split('-g-')
    group = `g-` + group
    let group_id = `${blk}-${group}`
    shown_group['group'] = 'None'

    setTimeout(function() {
      if (shown_group['group'] != group_id) {

        // Display off example view 
        d3.select(`#ex-${blk}-${group}`)
          .style('display', 'none')

        // Dehighlight node
        d3.select(`#${blk}-${group}`)
          .attr('fill', get_css_var('--gray'))

        // Dehighlight embedding
        d3.selectAll('.emb-dot')
          .attr('fill', get_css_var('--gray'))
          .attr('r', emb_style['normal-r'])

      } 
    }, 800)

  }

  click_node(node) {

    if (selected_groups['groups'].has(node.id)) {

      // Remove group from the selected groups
      selected_groups['groups'].delete(node.id)

      // Dehighlight node
      d3.select(`#${node.id}`)
        .style('fill', get_css_var('--gray'))

      // Turn off embedding
      d3.selectAll(`.emb-dot-group-${node.id}`)
        .style('display', 'none')

    } else {

      // Add group to the selected groups
      selected_groups['groups'].add(node.id)

      // Highlight node
      d3.select(`#${node.id}`)
        .style('fill', get_css_var('--hotpink'))

      // Show embedding
      d3.selectAll('.emb-dot-group-' + node.id)
        .style('display', 'block')
        .style('fill', get_css_var('--hotpink'))

    }

    

    // console.log('click', this)
    // TODO: Remove this
    // 
    // d3.select(`#ex-${blk}-${group}`)
    //   .style('display', 'block')
  }

  ///////////////////////////////////////////////////////
  // Draw connection
  ///////////////////////////////////////////////////////

  draw_connections() {

    // Get ready
    let this_class = this
    this.gen_edge_width_scale()

    // Draw connections
    for (let blk in this.group_level_conn_data) {
      for (let group in this.group_level_conn_data[blk]) {

        // Connection data
        let conn = this.group_level_conn_data[blk][group]
        let conn_d = conn['connection']
        let prev_blk = conn['prev_blk']

        // Add edge path
        d3.select('#graph_view-g')
          .selectAll('edges')
          .data(Object.entries(conn_d))
          .enter()
            .append('path')
            .attr('id', function(d) { 
              return gen_edge_id(d, blk, group, prev_blk)
            })
            .attr('class', 'edge-path')
            .attr('d', function(d) {               
              return gen_path(d, blk, group, prev_blk) 
            })
            .attr('stroke-width', function(d) {
              return this_class.edge_stroke_width_scale(d[1])
            })
            .attr('stroke', graph_style['edge_color'])
      }
    }

    function gen_edge_id(d, blk, group, prev_blk) {
      let prev_group = d[0]
      return `conn-${blk}_${group}-${prev_blk}_${prev_group}`
    }

    function gen_path(d, blk, group, prev_blk) {
      let prev_group = parseInt(d[0])
      let W = graph_style['node_w'] + graph_style['x_gap']
      let H = graph_style['node_h'] 
      let x1 = this_class.blk_x[prev_blk] + prev_group * W
      //  - 0.05 * W
      let y1 = this_class.blk_y[prev_blk] + 0.05 * H 
      let x2 = this_class.blk_x[blk] + parseInt(group) * W
      //  + 0.05 * W
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

    let c1_x = (3 * x1 + x2) / 4
    let c1_y = (3 * y1 + y2) / 4 - (y1 - y2) * 0.6
    let c2_x = (x1 + 3 * x2) / 4
    let c2_y = (y1 + 3 * y2) / 4 + (y1 - y2) * 0.6
  
    let path = 'M ' + x1 + ',' + y1
    path += ' C ' + c1_x + ' ' + c1_y
    path += ' ' + c2_x + ' ' + c2_y + ','
    path += ' ' + x2 + ' ' + y2
    return path

  }

  gen_group_level_conn() {

    for (let blk in this.conn_data) {

      this.group_level_conn_data[blk] = {}

      for (let group in this.conn_data[blk]) {
  
        let [conn_d, prev_blk] = this.gen_group_level_conn_one_group(
          this.conn_data[blk][group]
        )

        this.group_level_conn_data[blk][group] = {
          'prev_blk': prev_blk,
          'connection': conn_d
        }

      }

    }
  }

  gen_group_level_conn_one_group(group_conn_data) {
    let group_conn = {}
    let prev_blk = ''
    for (let neuron in group_conn_data) {
      for (let prev_group in group_conn_data[neuron]) {
        if (!(prev_group in group_conn)) {
          group_conn[prev_group] = 0
        }
        let prev_data = group_conn_data[neuron][prev_group]
        for (let prev_neuron_info of prev_data) {
          group_conn[prev_group] += prev_neuron_info['cnt']
          if (prev_blk == '') {
            prev_blk = prev_neuron_info['prev'].split('-')[0]
          }
        } 
      }
    }
    return [group_conn, prev_blk]
  }

  gen_edge_width_scale() {

    // Maximum edge cnt
    let max_edge_cnt = 0
    for (let blk in this.group_level_conn_data) {
      for (let group in this.group_level_conn_data[blk]) {
        let d = this.group_level_conn_data[blk][group]['connection']        
        if (this.len(d) > 0) {
          let max_cnt = d3.max(Object.values(d))
          max_edge_cnt = d3.max([max_edge_cnt, max_cnt])
        }
      }
    }

    this.edge_stroke_width_scale = d3.scaleLinear()
      .domain([0, max_edge_cnt])
      .range([0, 10])
  }

}
