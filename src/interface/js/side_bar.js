import { Icon } from './icon.js'
import { DivTitle } from './div_title.js'

add_header()

// Add header
function add_header() {

  // Side bar div
  let side_bar = document.getElementById('side_bar')

  // Generate header
  let header = document.createElement('div')
  let icon = gen_icon()
  let title = gen_title()
  header.id = 'side_bar-header'
  header.appendChild(icon)
  header.appendChild(title)
  side_bar.appendChild(header)
  
}

// Add left arrow icon
function gen_icon() {

  // Generate left arrow icon
  let arrow_icon = new Icon('side_bar-icon', 'left-arrow', 'icon')
  let arrow_icon_div = arrow_icon.get_icon()

  // Left arrow icon onclick
  arrow_icon.set_click(
    e => {

      // Hide side bar
      side_bar.className = 'hide'

      // Show setting icon
      d3.select('#layer_slice_view-icon')
        .transition()
        .delay(1000)
        .style('visibility', 'visible')

    }
  )

  return arrow_icon_div

}

// Add title
function gen_title() {

  let title = new DivTitle(
    'side_bar-title', 'Setting', 'component-title'
  )
  let title_div = title.get_title_div()
  return title_div

}