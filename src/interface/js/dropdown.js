import {
  icon_class
} from './constant.js'

export class Dropdown {

  // Dropdown contructor
  constructor(id) {

    this.id = id
    this.color = {
      // Default color
      'background': 'white',
      'highlight': 'lightgray'
    }
    this.dropdown = document.createElement('div')
    this.dropdown_contents = document.createElement('div')
    this.dropdown_text = document.createElement('div')
    this.dropdown_icon = document.createElement('div')
    this.dropdown_menu = document.createElement('div')

    this.dropdown.appendChild(this.dropdown_contents)
    this.dropdown_contents.appendChild(this.dropdown_text)
    this.dropdown_contents.appendChild(this.dropdown_icon)
    this.gen_dropdown_menu()

  }

  // Get dropdown
  get_dropdown() {
    return this.dropdown
  }

  // Get dropdown menu
  get_dropdown_menu() {
    return this.dropdown_menu
  }

  // Add color info
  add_colors(color_dict) {
    this.color = color_dict
  }

  // Get color
  get_color(key) {
    return (key in this.color) ? this.color[key] : null
  }

  // Generate dropdown box
  gen_dropdown(default_text) {

    // Generate dropdown
    this.dropdown.setAttribute('id', this.id)
    this.dropdown.setAttribute('class', 'dropdown')
    this.dropdown.style.display = 'inline-block'
    this.dropdown.style.cursor = 'pointer'

    // Generate dropdown contents
    this.dropdown_contents.setAttribute('id', 'dropdown-contents-' + this.id)
    this.dropdown_contents.setAttribute('class', 'dropdown-contents')
    
    // Generate dropdown text
    this.dropdown_text.setAttribute('id', 'dropdown-text-' + this.id)
    this.dropdown_text.setAttribute('class', 'dropdown-text')
    this.dropdown_text.style.display = 'inline-block'
    this.dropdown_text.style.paddingRight = '2px'
    this.dropdown_text.innerText = default_text

    // Generate dropdown icon
    this.dropdown_icon.setAttribute('id', 'dropdown-icon-' + this.id)
    this.dropdown_icon.setAttribute('class', 'dropdown-icon ' + icon_class['dropdown-down'])
  
    // Dropdown click function
    var dropdown_id = this.id
    this.dropdown_contents.onclick = function() { 

      // Check if the dropdown menu is already displayed
      var dropdown_menu = document.getElementById('dropdown-menu-' + dropdown_id)
      var already_displayed = dropdown_menu.style.display.includes('block')

      // Turn off all other menu off
      d3.selectAll('.dropdown-menu').style('display', 'none')

      // Menu display setting
      if (already_displayed) {
        dropdown_menu.style.display = 'none'
      } else {
        dropdown_menu.style.display = 'inline-block'
      }

    }

  }

  // Generate dropdown menu
  gen_dropdown_menu() {

    // Generate dropdown menu box
    this.dropdown_menu.setAttribute('id', 'dropdown-menu-' + this.id)
    this.dropdown_menu.setAttribute('class', 'dropdown-menu')
    this.dropdown.appendChild(this.dropdown_menu)
    
  }

  // Add dropdown menu
  add_dropdown_menu_item(menu_item, menu_text, menu_functions) {

    // Generate menu
    var menu = document.createElement('div')
    var menu_id = ['dropdown-menu-item', this.id, menu_item].join('-')
    menu.setAttribute('id', menu_id)
    menu.setAttribute('class', 'dropdown-menu-item')
    menu.innerText = menu_text
    menu.style.cursor = 'pointer'
    this.dropdown_menu.appendChild(menu)

    // Menu mouseover
    var highlight_color = this.get_color('highlight')
    menu.onmouseover = function() { 
      d3.select('#' + menu_id)
        .style('background-color', highlight_color)
      if ('mouseover' in menu_functions) {
        menu_functions['mouseover']()
      }
    }

    // Menu mouseout
    var background_color = this.get_color('background')
    menu.onmouseout = function() { 
      d3.select('#' + menu_id)
        .style('background-color', background_color)
      if ('mouseout' in menu_functions) {
        menu_functions['mouseout']() 
      }
    }

    // Menu click
    var menu_box_id = 'dropdown-menu-' + this.id
    var text_id = 'dropdown-text-' + this.id
    menu.onclick = function() { 
      d3.select('#' + menu_box_id)
        .style('display', 'none')
      d3.select('#' + text_id)
        .text(this.innerText)
      if ('click' in menu_functions) {
        menu_functions['click']()
      }
    }

  }

  // Add mouseover function
  add_mouseover(mouseover_function) {
    var old_function = this.dropdown.onmouseover
    this.dropdown.onmouseover = function() {
      old_function()
      mouseover_function()
    }
  }

  // Link mouseout function
  add_mouseout(mouseout_function) {
    var old_function = this.dropdown.onmouseout
    this.dropdown.onmouseout = function() {
      old_function()
      mouseout_function()
    }
  }

  // Link click function
  add_click(click_function) {
    var old_click_function = this.dropdown.onclick
    this.dropdown.onclick = function() {
      old_click_function()
      click_function()
    }
  }

  // Add class to the dropdown
  add_dropdown_class(class_name) {

    var components = [this.dropdown, this.dropdown_contents, this.dropdown_text, this.dropdown_icon]
    var component_tag = ['dropdown', 'dropdown-contents', 'dropdown-text', 'dropdown-icon']
    components.forEach((component, i) => {
      var old_classes = component.className
      var added_class = component_tag[i] + '-' + class_name
      var new_classes = old_classes + ' ' + added_class
      component.setAttribute('class', new_classes)
    })

  }
}