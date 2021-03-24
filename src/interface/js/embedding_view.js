import { Icon } from './icon.js'
import { get_css_var } from './utils.js'
import { ExampleViewNeuron } from './example_view.js'
import { Dropdown } from './dropdown.js'
import { emb_style } from './constant.js'
import { embedding_setup, selected_class, selected_groups } from './variable.js'

////////////////////////////////////////////////////////////
// Embedding
////////////////////////////////////////////////////////////

export class EmbeddingView {
  
  constructor(parent_id, emb_data, node_data) {

    // Embeddng view size
    this.emb_H = 467
    this.emb_W = 400

    // Embedding view parent
    this.parent = d3.select(`#${parent_id}`)

    // Data
    this.node_data = node_data
    this.emb_data = emb_data
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

  parse_embedding(data) {

    // Parse embedding data
    let [min_x, min_y, max_x, max_y] = [0, 0, 0, 0]
    for (let neuron in data) {
      data[neuron] = data[neuron].split(',').map(parseFloat)
      let x = data[neuron][0]
      let y = data[neuron][1]
      min_x = d3.min([x, min_x])
      min_y = d3.min([y, min_y])
      max_x = d3.max([x, max_x])
      max_y = d3.max([y, max_y])
    }
    this.emb_data[embedding_setup['epoch']] = data

    // Set x, y scale
    this.gen_xy_scale(min_x, min_y, max_x, max_y)

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
        d3.zoomIdentity.translate(W * 0.1, H * 0.2).scale(0.75)
      )
  }

  ///////////////////////////////////////////////////////
  // Draw embeddings
  ///////////////////////////////////////////////////////

  draw_dots() {
  
    this.gen_embedding_svg_g()
    this.embedding_view_auto_zoomout()
    this.parse_embedding(this.emb_data[embedding_setup['epoch']])
    this.add_embedding_dots()
    
  }

  gen_xy_scale(min_x, min_y, max_x, max_y) {

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
      .data(Object.entries(this.emb_data[embedding_setup['epoch']]))
      .enter()
      .append('circle')
        .attr('id', d => { return 'dot-' + d[0] })
        .attr('class', d => {
          let neuron = d[0]
          let class1 = 'emb-dot'
          let class2 = 'emb-dot-group-' + n2g[neuron]
          let class3 = 'emb-dot-' + neuron.split('-')[0]
          return [class1, class2, class3].join(' ')
        })
        .attr('r', emb_style['normal-r'])
        .attr('cx', d => { return x_scale(d[1][0]) })
        .attr('cy', d => { return y_scale(d[1][1]) })
        .on('mouseover', d => { 
          return this_class.dot_mouseover(d[0]) 
        })
        .on('mouseout', d => { 
          return this_class.dot_mouseout(d[0]) 
        })
        .style('opacity', 0.5)
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
        .style('opacity', 1)
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

    // Highlight group
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

  constructor(id) {
    this.view = document.getElementById(id)
    this.id = id
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
    title.innerText = 'Filtering'
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
    title.innerText = 'Epoch'
    title.style.display = 'inline-block'
    epoch.appendChild(title)

    // Epoch number
    let number = document.createElement('div')
    number.id = 'epoch'
    number.innerText = '3'
    number.style.display = 'inline-block'
    epoch.appendChild(number)

    // Slider
    let slider_wrap = document.createElement('div')
    let slider = document.createElement('input')
    slider.id = 'epoch-slider'
    slider_wrap.className = 'slider'
    slider.type = 'range'
    slider.min = 1
    slider.max = 5
    slider.value = 3
    epoch.appendChild(slider_wrap)
    slider_wrap.appendChild(slider)

    // Slider action
    slider.oninput = function() {
      // TODO: Update embedding view according to the selected epoch
      let selected_epoch = this.value
      let epoch_number = document.getElementById('epoch')
      epoch_number.innerText = selected_epoch
      embedding_setup['epoch'] = parseInt(selected_epoch)
    }

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

  }

}