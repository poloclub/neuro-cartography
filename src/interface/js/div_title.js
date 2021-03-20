export class DivTitle {

  constructor(id, title, class_name) {
    this.title = document.createElement('div')
    this.title.id = id
    this.title.className = class_name
    this.title.innerText = title
  }

  get_title_div() {
    return this.title
  }

}