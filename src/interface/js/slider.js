export class Slider {

  constructor(id, class_name, slider_range, default_val, fn) {

    this.id = id
    this.class_name = class_name
    this.slider_range = slider_range
    this.default_val = default_val
    this.fn = fn
    this.slider_wrap = null
    this.slider = null

    this.gen_slider()
    this.slider_action()

  }

  get_slider() {
    return this.slider_wrap
  }

  gen_slider() {

    this.slider_wrap = document.createElement('div')
    this.slider_wrap.id = `${this.id}-wrap`
    this.slider_wrap.className = this.class_name

    this.slider = document.createElement('input')
    this.slider.id = this.id
    this.slider.type = 'range'
    this.slider.min = this.slider_range[0]
    this.slider.max = this.slider_range[1]
    this.slider.value = this.default_val
    this.slider_wrap.appendChild(this.slider)

  }

  slider_action() {
    let this_class = this
    this.slider.oninput = function() {
      let selected_val = parseInt(this.value)
      this_class.fn(selected_val)
    }
  }

}