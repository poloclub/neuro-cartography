import { Icon } from './icon.js'
import { get_css_var } from './utils.js'
import { ExampleViewNeuron } from './example_view.js'
import { Dropdown } from './dropdown.js'
import { Slider } from './slider.js'
import { emb_style } from './constant.js'
import { embedding_setup, selected_class, selected_groups } from './variable.js'

////////////////////////////////////////////////////////////
// Embedding
////////////////////////////////////////////////////////////

export class EmbeddingView {
  
  constructor(parent_id, emb_data, emb_range, node_data) {

    // Embeddng view size
    this.emb_H = 467
    this.emb_W = 400

    // Embedding view parent
    this.parent = d3.select(`#${parent_id}`)

    // Data
    this.node_data = node_data
    this.emb_data = emb_data
    this.emb_range = emb_range
    this.neuron_to_group = this.get_neuron_group_mapping()

    // XY Scale
    this.x_scale = {}
    this.y_scale = {}

  }


  ///////////////////////////////////////////////////////
  // Parse data
  ///////////////////////////////////////////////////////

  get_neuron_group_mapping() {
    let n2g = {}
    let nodes_of_class = this.node_data[
      selected_class['synset']
    ]
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
  }

  
}

////////////////////////////////////////////////////////////
// Embedding header
////////////////////////////////////////////////////////////

export class EmbeddingHeader {

  constructor(id, emb_range) {
    this.view = document.getElementById(id)
    this.id = id
    this.emb_range = emb_range
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
    title.innerText = 'Epoch to Learn Embedding'
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