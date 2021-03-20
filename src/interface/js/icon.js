import { icon_class } from './constant.js'

export class Icon {

  constructor(id, icon_name, class_name) {
    this.icon_name = icon_name
    this.icon_wrap = document.createElement('div')
    this.icon_wrap.id = id
    this.icon_wrap.className = class_name
    this.icon = null
  }

  gen_icon() {
    let icon = document.createElement('i')
    icon.className = icon_class[this.icon_name]
    this.icon_wrap.appendChild(icon)
    this.icon = icon
    this.icon.style.cursor = 'pointer'
  }

  get_icon() {
    let num_child = this.icon_wrap.childElementCount
    if (num_child == 0){
      this.gen_icon()
    }
    return this.icon_wrap
  }

  get_icon_i() {
    return this.icon
  }

  set_click(click_fn) {
    this.icon.onclick = click_fn
  }

}

export class IconSvg {

  constructor(parent_id, id, icon_text, class_name) {
    this.icon = d3.select(`#${parent_id}`)
      .append('text')
      .attr('id', id)
      .attr('class', class_name)
      .attr('font-family', 'FontAwesome')
      .text(icon_text)
  }

  get_icon() {
    return this.icon
  }

  set_click(click_fn) {
    this.icon.on('click', click_fn)
  }

}