import { icon_class } from './constant.js'

class Header {

  constructor () {
    this.logo
    this.title = ''
    this.subtitle = ''
    this.paper = ''
    this.youtube = ''
    this.github = ''
    this.header = document.getElementById('header')
  }

  // Layout
  gen_layout() {
    this.logo = this.gen_component('header-logo')
    this.title = this.gen_component('header-title')
    this.subtitle = this.gen_component('header-subtitle')
    this.paper = this.gen_component('header-paper')
    this.youtube = this.gen_component('header-youtube')
    this.github = this.gen_component('header-github')
  }

  // Generate component
  gen_component(id) {
    let component = document.createElement('div')
    component.id = id
    this.header.appendChild(component)
    return component
  }

  // Set logo
  set_logo(logo_path) {
    let logo_img = document.createElement('img')
    logo_img.src = logo_path
    logo_img.className = 'logo-img'
    this.logo.appendChild(logo_img)
  }

  // Set Title
  set_title(title) {
    this.title.innerText = title
  }

  // Set Subtitle 
  set_subtitle(subtitle) {
    this.subtitle.innerText = subtitle
  }

  // Generate button
  gen_href_button(link) {
    let button = document.createElement('a')
    button.target = '_blank'
    button.href = link
    button.style.color = 'inherit'
    return button
  }

  // Generate icon
  gen_icon(icon_name) {
    let icon = document.createElement('i')
    icon.className = icon_class[icon_name]
    return icon
  }

  // Set paper icon
  set_paper(link) {

    // Button
    let button = this.gen_href_button(link)
    this.paper.appendChild(button)
    this.paper.className = 'header-button'
    
    // Icon
    let icon = this.gen_icon('paper')
    button.appendChild(icon)

  }

  // Set youtube icon
  set_youtube(link) {

    // Button
    let button = this.gen_href_button(link)
    this.youtube.appendChild(button)
    this.youtube.className = 'header-button'
    
    // Icon
    let icon = this.gen_icon('youtube')
    button.appendChild(icon)

  }

  // Set github icon
  set_github(link) {

    // Button
    let button = this.gen_href_button(link)
    this.github.appendChild(button)
    this.github.className = 'header-button'
    
    // Icon
    let icon = this.gen_icon('github')
    button.appendChild(icon)

  }

}

let header = new Header()
header.gen_layout()
header.set_logo('./img/logo.png')
header.set_title('NeuroCartography')
header.set_subtitle('Scalable Automatic Visual Summarization of Concepts in Deep Neural Networks')
header.set_paper("https://arxiv.org/abs/2108.12931")
// header.set_youtube("https://youtu.be/gx0dDNXFJA0")
header.set_github("https://github.com/poloclub/neuro-cartography/")
