import { Icon } from './icon.js'
import { get_css_var } from './utils.js'
import { ExampleViewCard, ExampleViewNeuron } from './example_view.js'
import { Dropdown } from './dropdown.js'
import { Slider } from './slider.js'
import { emb_style } from './constant.js'
import { 
  embedding_setup, 
  selected_class, 
  selected_groups,
  selected_neuron
} from './variable.js'

////////////////////////////////////////////////////////////
// Embedding
////////////////////////////////////////////////////////////

export class EmbeddingView {
  
  constructor(parent_id, emb_data, graph_view, nei_view) {

    // Embeddng view size
    this.emb_H = 467
    this.emb_W = 400

    // Embedding view parent
    this.parent = d3.select(`#${parent_id}`)
    this.nei_view = nei_view

    // Node Data
    this.node_data = graph_view.node_data
    this.neuron_to_group = this.get_neuron_group_mapping()

    // Embedding data
    this.emb_data = []
    this.emb_range = {}
    this.parse_emb_data(emb_data)

    // XY Scale
    this.x_scale = {}
    this.y_scale = {}

  }


  ///////////////////////////////////////////////////////
  // Parse data
  ///////////////////////////////////////////////////////

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
    return n2g
  }

  ///////////////////////////////////////////////////////
  // Generate view layout
  ///////////////////////////////////////////////////////

  gen_embedding_svg_g() {

    let emb_svg = this.parent
      .append('svg')
      .attr('id', 'embedding-svg')
      .attr('width', this.emb_W)
      .attr('height', this.emb_H)
      .style('pointer-events', 'all')
      .call(
        d3.zoom()
          .on('zoom', function(){
            d3.select('#embedding-g')
              .attr('transform', d3.event.transform)
          })
      )

    let emb_g = emb_svg
      .append('g')
      .attr('id', 'embedding-g')
  }

  embedding_view_auto_zoomout() {
    
    let H = this.emb_H
    let W = this.emb_W

    let zoom = d3.zoom()
      .scaleExtent([.1, 3.5])
      .extent([[0, 0], [W, H]])
      .on('zoom', function() {
        d3.select('#embedding-g')
          .attr('transform', d3.event.transform)
      })

    d3.select('#embedding-svg')
      .transition()
      .duration(750)
      .call(
        zoom.transform,
        d3.zoomIdentity.translate(W * 0.1, H * 0.45).scale(0.75)
      )
  }

  ///////////////////////////////////////////////////////
  // Draw embeddings
  ///////////////////////////////////////////////////////

  draw_dots() {
  
    this.gen_embedding_svg_g()
    this.embedding_view_auto_zoomout()
    this.gen_xy_scale()
    this.add_embedding_dots()
    
  }

  gen_xy_scale() {

    let min_x = this.emb_range[embedding_setup['epoch']]['x'][0]
    let max_x = this.emb_range[embedding_setup['epoch']]['x'][1]
    let min_y = this.emb_range[embedding_setup['epoch']]['y'][0]
    let max_y = this.emb_range[embedding_setup['epoch']]['y'][1]

    this.x_scale = d3.scaleLinear()
      .domain([min_x, max_x])
      .range([0, this.emb_W])

    this.y_scale = d3.scaleLinear()
      .domain([min_y, max_y])
      .range([0, this.emb_H])

  }

  add_embedding_dots() {

    let x_scale = this.x_scale
    let y_scale = this.y_scale
    let n2g = this.neuron_to_group
    let this_class = this

    d3.select('#embedding-g')
      .selectAll('circle')
      .data(this.emb_data)
      .enter()
      .append('circle')
        .attr('id', d => { 
          return 'dot-' + d['neuron'] 
        })
        .attr('class', d => {
          let neuron = d['neuron'] 
          let class1 = 'emb-dot'
          let class2 = 'emb-dot-group-' + n2g[neuron]
          let class3 = 'emb-dot-' + neuron.split('-')[0]
          return [class1, class2, class3].join(' ')
        })
        .attr('r', emb_style['normal-r'])
        .attr('cx', d => { 
          let e = embedding_setup['epoch']
          return x_scale(d[e][0]) 
        })
        .attr('cy', d => { 
          let e = embedding_setup['epoch']
          return y_scale(d[e][1]) 
        })
        .on('mouseover', d => { 
          return this_class.dot_mouseover(d['neuron']) 
        })
        .on('mouseout', d => { 
          return this_class.dot_mouseout(d['neuron']) 
        })
        .on('click', d => {
          return this_class.dot_click(d['neuron'])
        })
        .attr('fill', get_css_var('--gray'))

  }

  dot_mouseover(neuron) {

    // Highlight dot
    d3.select(`#dot-${neuron}`)
      .attr('fill', get_css_var('--hotpink'))
      .attr('r', emb_style['highlight-r'])

    // Highlight group
    let group = this.neuron_to_group[neuron]
    d3.select(`#${group}`)
      .attr('fill', get_css_var('--hotpink'))

    // Highlight dots of the group
    if (neuron in this.neuron_to_group) {
      d3.selectAll('.emb-dot-group-' + group)
        .attr('fill', get_css_var('--hotpink'))
    }

    // Generate example view
    let view_id = `ex-neuron-${neuron}`
    if (document.getElementById(view_id) == null) {
      let ex_view = new ExampleViewNeuron(
        'example_view', neuron, 'example-view-neuron'
      )
      ex_view.gen_example_view()  
    }

    // Show example view
    d3.select(`#${view_id}`)
      .style('display', 'block')
      .style('left', (d3.event.pageX + 50) + 'px')		
      .style('top', (d3.event.pageY - 30) + 'px')

  }

  dot_mouseout(neuron) {

    // Dehighlight dot
    d3.selectAll('.emb-dot')
      .attr('fill', get_css_var('--gray'))
      .attr('r', emb_style['normal-r'])

    // Dehighlight group
    let group = this.neuron_to_group[neuron]
    d3.select(`#${group}`)
      .attr('fill', get_css_var('--gray'))

    // Turn off example view
    let view_id = `ex-neuron-${neuron}`
    d3.select(`#${view_id}`)
      .style('display', 'none')

    // Highlight embedding of clicked groups
    for (let g of selected_groups['groups']) {
      d3.selectAll(`.emb-dot-group-${g}`)
        .attr('fill', get_css_var('--hotpink'))
        .attr('r', emb_style['highlight-r'])
        .raise()
    }
  }

  dot_click(neuron) {

    if (selected_neuron['selected'] != neuron) {

      // Update selected neuron
      selected_neuron['selected'] = neuron

      // Update neighbor view
      this.nei_view.update_nn_view()

    }
    
    
  }

}

////////////////////////////////////////////////////////////
// Embedding headers
////////////////////////////////////////////////////////////

export class EmbeddingHeader {

  constructor(id, embedding_view) {
    this.view = document.getElementById(id)
    this.id = id
    this.embedding_view = embedding_view
    this.emb_range = embedding_view.emb_range
    this.emb_H = 467
    this.emb_W = 400
    this.x_scale = null
    this.y_scale = null
  }

  gen_filtering() {

    // Filtering div
    let filtering = document.createElement('div')
    filtering.id = `${this.id}-filtering`
    filtering.className = 'embedding-header-component'
    this.view.appendChild(filtering)

    // Title
    let title = document.createElement('div')
    title.className = 'embedding-header-title'
    title.innerText = 'Filter Neurons'
    filtering.appendChild(title)

    // Dropdown
    let this_class = this
    let dropdown = new Dropdown('embedding-filtering')
    dropdown.gen_dropdown('All neurons')
    for (let item of ['All-neurons', 'Neurons-of-class', 'Neurons-of-selected-groups']) {
      dropdown.add_dropdown_menu_item(
        item,
        item.replace(/-/g, ' '),
        {
          'mouseover': function() {  },
          'mouseout': function() {  },
          'click': function() { 
            this_class.emb_filtering_item_click(item)
           }
        }
      )
    }
    filtering.appendChild(dropdown.get_dropdown())

  }

  gen_epoch() {

    // Epoch div
    let epoch = document.createElement('div')
    epoch.id = `${this.id}-epoch`
    epoch.className = 'embedding-header-component'
    this.view.appendChild(epoch)

    // Title
    let title = document.createElement('div')
    title.className = 'embedding-header-title'
    title.innerText = 'Epoch to Learn Emb.'
    title.style.display = 'inline-block'
    epoch.appendChild(title)

    // Slider
    let this_class = this
    let slider = new Slider(
      'epoch-slider', 
      'slider',
      [1, 5],
      embedding_setup['epoch'],
      function(selected_epoch) {

        // Update epoch number
        let epoch_number = document.getElementById('epoch')
        epoch_number.innerText = selected_epoch * 5
        embedding_setup['epoch'] = selected_epoch
        this_class.update_embedding()

      }
    )
    let slider_wrap = slider.get_slider()
    epoch.appendChild(slider_wrap)

    // Epoch number
    let number = document.createElement('div')
    number.id = 'epoch'
    number.innerText = embedding_setup['epoch'] * 5
    number.style.display = 'inline-block'
    slider_wrap.appendChild(number)

  }

  update_embedding() {

    // Update xy scale
    this.update_xy_scale()

    // Update embedding location
    let this_class = this
    d3.selectAll('.emb-dot')
      .transition()
      .duration(1000)
      .attr('cx', d => {
        return this_class.x_scale(d[embedding_setup['epoch']][0])
      })
      .attr('cy', d => {
        return this_class.y_scale(d[embedding_setup['epoch']][1])
      })

  }

  update_xy_scale() {

    let min_x = this.emb_range[embedding_setup['epoch']]['x'][0]
    let max_x = this.emb_range[embedding_setup['epoch']]['x'][1]
    let min_y = this.emb_range[embedding_setup['epoch']]['y'][0]
    let max_y = this.emb_range[embedding_setup['epoch']]['y'][1]

    this.x_scale = d3.scaleLinear()
      .domain([min_x, max_x])
      .range([0, this.emb_W])

    this.y_scale = d3.scaleLinear()
      .domain([min_y, max_y])
      .range([0, this.emb_H])

  }

  emb_filtering_item_click(item) {

    // Update filtering mode
    embedding_setup['filtering'] = item

    // Selected neurons
    if (item.toLowerCase().includes('selected')) {

      d3.selectAll('.emb-dot')
        .style('display', 'none')

      for(let group of selected_groups['groups']) {
        d3.selectAll('.emb-dot-group-' + group)
          .style('display', 'block')
      }
    }
    
    // All neurons
    if (item == 'All-neurons') {
      d3.selectAll('.emb-dot')
        .style('display', 'block')
    }

    // Neurons of selected class
    // TODO:

  }

}

////////////////////////////////////////////////////////////
// Nearest Neighbor view
////////////////////////////////////////////////////////////

export class NNView {

  constructor(parent_id, emb_data) {
    this.parent_id = parent_id
    this.emb_data = []
    this.selected_view = null
    this.nei_view = null
    this.parse_emb_data(emb_data)
  }

  gen_neighbor_view() {
    this.gen_layout()
    this.gen_selected()
    this.gen_neighbors()
  }

  gen_layout() {

    let parent = document.getElementById(this.parent_id)

    let selected_neuron_view = document.createElement('div')
    selected_neuron_view.id = 'NNView-selected-neuron'
    parent.appendChild(selected_neuron_view)
    this.selected_view = selected_neuron_view

    let neighbor_view = document.createElement('div')
    neighbor_view.id = 'NNView-neighbors'
    parent.appendChild(neighbor_view)
    this.nei_view = neighbor_view

  }

  gen_selected() {

    let title = document.createElement('div')
    title.id = 'NNView-selected-neuron-title'
    title.className = 'NNView-title'
    title.innerText = 'Selected Neuron'
    this.selected_view.appendChild(title)

    if (selected_neuron['selected'] != null) {

      this.gen_card(
        'NNView-selected-neuron-card',
        selected_neuron['selected'], 
        this.selected_view
      )

    }

  }

  gen_neighbors() {

    // Title
    let title = document.createElement('div')
    title.id = 'NNView-nei-neuron-title'
    title.className = 'NNView-title'
    title.innerText = 'Most Related Neurons'
    this.nei_view.appendChild(title)

    // Find neighbors
    let neighbors = []
    if (selected_neuron['selected'] != null) {
      let epoch = embedding_setup['epoch']
      let [x, y] = this.emb_data[epoch][selected_neuron['selected']]
      neighbors = Object.entries(this.emb_data[epoch])
        .sort((a, b) => {
          let [x_a, y_a] = a[1]
          let [x_b, y_b] = b[1]
          let d_a_sq = (x - x_a) ** 2 + (y - y_a) ** 2
          let d_b_sq = (x - x_b) ** 2 + (y - y_b) ** 2
          return d_a_sq - d_b_sq
        })
        .map(x => x[0])
        .filter(x => {
          if (x == selected_neuron['selected']) {
            return false
          } else {
            return true
          }
        })
        .slice(0, 10)
    }

    // Show neighbors
    let nei_list_view = document.createElement('div')
    nei_list_view.id = 'NNView-nei-list'
    this.nei_view.appendChild(nei_list_view)
    for (let nei of neighbors) {
      this.gen_card(
        `NNView-neighbors-${nei}`,
        nei, 
        nei_list_view
      )  
    }
    

  }

  gen_card(id, neuron, parent) {
    
    let card = new ExampleViewCard(
      parent.id, id, neuron, 'NNView-neuron-card'
    )
    card.gen_example_view()

  }

  update_nn_view() {

    // Refresh the view
    d3.select('#NNView-selected-neuron').remove()
    d3.select('#NNView-neighbors').remove()
    d3.select('#NNView-nei-neuron-title').remove()
    this.gen_layout()

    // Add selected neuron
    this.gen_selected()

    // Add neighbor neurons
    this.gen_neighbors()

  }

  parse_emb_data(data) {

    for (let i of [0, 1, 2, 3, 4, 5]) {

      let neurons = Object.keys(data[i])
      let emb_d = {}
      for (let neuron of neurons) {
        let x = parseFloat(data[i][neuron].split(',')[0])
        let y = parseFloat(data[i][neuron].split(',')[1])
        emb_d[neuron] = [x, y]
      }

      this.emb_data.push(emb_d)

    }

  }

}