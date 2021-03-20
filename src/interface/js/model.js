export class InceptionV1 {
  
  constructor() {
    this.LAYERS = this.get_InceptionV1_layers()
    this.REV_LAYERS = this.LAYERS.slice().reverse()
    this.BLKS = this.get_InceptionV1_blocks()
  }

  get_InceptionV1_layers() {
    let layers = [
      'mixed3a', 'mixed3b',
      'mixed4a', 'mixed4b', 'mixed4c', 'mixed4d', 'mixed4e',
      'mixed5a', 'mixed5b'
    ]
    return layers
  }

  get_InceptionV1_blocks() {
    let blks = []
    for (let layer of this.LAYERS) {
      blks.push(layer)
      if (layer == 'mixed3a') {
        continue
      }
      for (let apdx of ['_3x3', '_5x5']) {
        blks.push(layer + apdx)
      }
    }
    return blks
  }

}