
export class SearchBar {


  constructor(id, class_name, default_txt, functions, items) {
    this.form = document.createElement('form')
    this.id = id
    this.class_name = class_name
    this.form.id = id
    this.form.className = class_name
    this.search_bar_div = null
    this.search_bar_input = null
    this.search_item_list = null
    this.default_txt = default_txt
    this.functions = functions
    this.items = items

    this.gen_search_bar()
  }

  gen_search_bar() {

    let search_bar = document.createElement('div')
    search_bar.id = `${this.id}-bar`
    search_bar.className = `autocomplete ${this.class_name}`
    this.form.appendChild(search_bar)
    this.search_bar_div = search_bar

    let search_bar_input = document.createElement('input')
    search_bar_input.id = `${this.id}-input`
    search_bar_input.type = 'text'
    search_bar_input.name = `${this.id}-input`
    search_bar_input.paceholder = 'Class'
    search_bar_input.value = this.default_txt
    search_bar.appendChild(search_bar_input)
    this.search_bar_input = search_bar_input

    let submit = document.createElement('input')
    submit.id = `${this.id}-submit`
    submit.className = 'autocomplete-submit'
    this.form.appendChild(submit)

    this.gen_item_list(search_bar)
    this.autocomplete()

  }

  get_search_bar() {
    return this.form
  }

  gen_item_list(search_bar) {

    // Create a div element that will contain all items
    let items = document.createElement('div')
    items.setAttribute('id', `${this.id}-autocomplete-list`)
    items.setAttribute('class', 'autocomplete-items')
    search_bar.appendChild(items)

    // Add each item in the array
    let this_class = this
    for (let item of this.items) {
      let item_div = document.createElement('div')
      item_div.id = item['id']
      item_div.innerHTML = item['text']
      item_div.addEventListener('click', function(e) {
        this_class.search_bar_input.value = item['text']
        this_class.close_item_list()
        // TODO: Update data of the selected class
      })
      items.appendChild(item_div)
    }
    this.search_item_list = items
  }

  autocomplete() {
    
    let this_class = this

    this.search_bar_input.addEventListener('input', function(e) {

      // Get user input value
      let val = this.value.toLowerCase()

      // If no value is given, do nothing
      if (!val) { 
        this_class.search_item_list.style.display = 'none'
        return false
      }
      this_class.search_item_list.style.display = 'block'
      
      // Show items that include the value
      for (let item of this_class.items) {
        let text = item['text'].toLowerCase()
        let id = item['id']
        let item_div = document.getElementById(id)

        if (text.includes(val)) {

          // Highlight the value part
          let idx = text.indexOf(val)
          let inner_html = ''
          if (idx == 0) {
            let hl_text = this_class.fst_letter_capital(text)
            hl_text = hl_text.slice(0, val.length)
            inner_html += `<strong>${hl_text}</strong>`
            inner_html += text.slice(val.length)
          } else {
            let before_hl = this_class.fst_letter_capital(
              text.slice(0, idx)
            )
            let hl_text = text.slice(idx, idx + val.length)
            let after_hl = text.slice(idx + val.length)
            inner_html += `${before_hl}<strong>${hl_text}</strong>${after_hl}`
          }
          item_div.innerHTML = inner_html
          item_div.style = 'block'


        } else {
          item_div.style.display = 'none'
        }

      }

    })
  
    document.addEventListener('click', function (e) {
      this_class.close_item_list(e.target);
    })
  }

  fst_letter_capital(s) {
    return s.charAt(0).toUpperCase() + s.slice(1)
  }

  close_item_list(element) {
    if (element != this.search_item_list) {
      this.search_item_list.style.display = 'none'
    }
  }

}
