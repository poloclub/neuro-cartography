import { Icon } from './icon.js'
import { DivTitle } from './div_title.js'
import { data_path } from './constant.js'
import { get_css_var } from './utils.js'
import { ExampleView, ExampleViewNeuron } from './example_view.js'

////////////////////////////////////////////////////////////
// Embedding
////////////////////////////////////////////////////////////

export class EmbeddingView {
  
  constructor(parent_id, emb_data, neuron_data) {

    // Embeddng view size
    this.emb_H = 400
    this.emb_W = 400

    // Embedding view parent
    this.parent = d3.select(`#${parent_id}`)

    // Data
    this.neuron_data = neuron_data
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
    for (let blk in this.neuron_data) {
      for (let g_num in this.neuron_data[blk]) {
        for (let neuron of this.neuron_data[blk][g_num]) {
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
    this.emb_data = data

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
        d3.zoomIdentity.translate(W * 0.1, H * 0.05).scale(0.8)
      )
  }

  ///////////////////////////////////////////////////////
  // Draw embeddings
  ///////////////////////////////////////////////////////

  draw_dots() {
  
    this.gen_embedding_svg_g()
    this.embedding_view_auto_zoomout()
    this.parse_embedding(this.emb_data)
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
      .data(Object.entries(this.emb_data))
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
        .attr('r', 3)
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
      .attr('r', 5)
      .style('opacity', 1)

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
      .attr('r', 3)
      .style('opacity', 0.5)

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



