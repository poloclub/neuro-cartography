import { 
  data_path, 
  patch_style,
} from './constant.js'
import {
  shown_group
} from './variable.js'
import {
  get_css_var
} from './utils.js'

export class ExampleView {

  constructor(parent_id, blk, group, class_name, neurons) {
    this.view = document.getElementById(parent_id)
    this.blk = blk
    this.group = group
    this.class_name = class_name
    this.neurons = neurons
  }

  gen_example_view() {

    // Block and group
    let blk = this.blk
    let group = this.group
    let neurons = this.neurons

    // Generate group wrapper and inner wrapper
    this.gen_group_wrapper(blk, group)
    let inner_wrapper = d3.select(`#inner-wrapper-${blk}-${group}`)

    for (let [neuron_i, neuron] of neurons.entries()) {

      // Neuon wrapper
      let neuron_wrapper = inner_wrapper
        .append('svg')
        .attr('id', `neuron-${neuron}`)
        .attr('class', `neuron-wrapper`)
        .style('transform', function () {
          let num_col = patch_style['num_col'] 
          let y = neuron_i * patch_style['height'] * num_col
          y += neuron_i * 35
          return `translate(0px, ${y}px)`
        })
        .on('mouseover', function() {
          d3.selectAll('.example-view-wrapper')
            .style('display', 'none')
          let group_id = `${blk}-${group}`
          shown_group['group'] = group_id
          d3.select(`#ex-${group_id}`)
            .style('display', 'block')
          d3.select(`#${group_id}`)
            .attr('fill', get_css_var('--hotpink'))

          // Highlight embedding
          for (let neuron of neurons) {
            d3.select('#dot-' + neuron)
              .attr('fill', get_css_var('--hotpink'))
              .attr('r', 8)
              .style('opacity', 1)
          }
        })
        .on('mouseout', function() {
          d3.selectAll('.example-view-wrapper')
            .style('display', 'none')
          d3.selectAll('.node')
            .attr('fill', get_css_var('--gray'))
          d3.selectAll('.emb-dot')
            .attr('fill', get_css_var('--gray'))
            .attr('r', 3)
            .style('opacity', 0.5)
        })

      // Add neuron id
      let neuron_number = neuron.split('-')[1]
      neuron_wrapper
        .append('text')
        .attr('id', `neuron-id-${neuron}`)
        .attr('class', 'neuron-id')
        .text(neuron_number)

      // Add images
      let img_paths = this.get_image_paths(neuron)
      let examples = neuron_wrapper
        .selectAll('imgs')
        .data(img_paths)
        .enter()
        .append('image')
          .attr('xlink:href', d => d)
          .attr('x', function (d, i) {
            let W = patch_style['width']
            return (i % patch_style['num_col']) * W
          })
          .attr('y', function (d, i) {
            let H = patch_style['height']
            let row = parseInt(i / patch_style['num_col'])
            return H * row + 30
          })
          .attr('width', patch_style['width'])
          .attr('height', patch_style['height'])
          .attr('preserveAspectRatio', 'none')
        
    }

  }

  gen_group_wrapper(blk, group) {

    let wrapper = document.createElement('div')
    wrapper.id = `ex-${blk}-${group}`
    wrapper.className = `${this.class_name}-wrapper`
    this.view.appendChild(wrapper)

    let neuron_wrapper = document.createElement('svg')
    neuron_wrapper.id = `inner-wrapper-${blk}-${group}`
    neuron_wrapper.className = `${this.class_name}-inner-wrapper`
    wrapper.append(neuron_wrapper)

  }

  get_image_paths(neuron) {

    let idxs = Array.from(Array(patch_style['num_exs']).keys())
    let paths = idxs.map(x => 
      `${data_path['image_dir']}/${neuron}-dataset-p-${x}.jpg`
    )
    return paths
  }

}

export class ExampleViewNeuron {

  constructor(parent_id, neuron, class_name) {
    this.view = document.getElementById(parent_id)
    this.neuron = neuron
    this.class_name = class_name
  }

  gen_example_view() {

    let neuron = this.neuron
    let inner_wrapper = this.gen_group_wrapper(neuron)

    // Neuon wrapper
    let neuron_wrapper = d3.select(inner_wrapper)
      .append('svg')
      .attr('id', `emb-ex-neuron-${neuron}`)
      .attr('class', `neuron-wrapper`)
      .on('mouseover', function() {})
      .on('mouseout', function() {})

    // Add neuron id
    neuron_wrapper
      .append('text')
      .attr('id', `emb-ex-neuron-id-${neuron}`)
      .attr('class', 'neuron-id')
      .text(neuron)

    // Add images
    let img_paths = this.get_image_paths(neuron)
    let examples = neuron_wrapper
      .selectAll('imgs')
      .data(img_paths)
      .enter()
      .append('image')
        .attr('xlink:href', d => d)
        .attr('x', function (d, i) {
          let W = patch_style['width']
          return (i % patch_style['num_col']) * W
        })
        .attr('y', function (d, i) {
          let H = patch_style['height']
          let row = parseInt(i / patch_style['num_col'])
          return H * row + 30
        })
        .attr('width', patch_style['width'])
        .attr('height', patch_style['height'])
        .attr('preserveAspectRatio', 'none')

  }

  gen_group_wrapper(neuron) {

    let wrapper = document.createElement('div')
    wrapper.id = `ex-neuron-${neuron}`
    wrapper.className = `${this.class_name}-wrapper`
    this.view.appendChild(wrapper)

    return wrapper

  }

  get_image_paths(neuron) {

    let idxs = Array.from(Array(patch_style['num_exs']).keys())
    let paths = idxs.map(x => 
      `${data_path['image_dir']}/${neuron}-dataset-p-${x}.jpg`
    )
    return paths
  }

}