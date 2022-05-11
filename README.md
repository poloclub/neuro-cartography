# NeuroCartography

NeuroCartography is an interactive visualization system for scalable automatic visual summarization of concepts in deep neural networks. 

- 📄 [Our manuscript][paper]
- 🎥 [Video][youtube]
- 💛 [Demo][demo]

## Set up conda environment

Run the followng command to create a conda environment for our method:
```
conda env create -f environment.yml
```
This will generate a conda environment called `neuro-cartography`. Run the following command to activate th conda environment.
```
conda activate neuro-cartography
```


## Live Demo
For a live demo, visit: [https://poloclub.github.io/neuro-cartography/][demo]


## Running Bluff user interface Locally
- Download or clone this repository:
  ```bash
  git clone https://github.com/poloclub/neuro-cartography.git
  ```

- Within `neuro-cartography` repo, run:
  ```
  python -m http.server <PORT>
  ```
  For example,
  ```bash
  python -m http.server 8080
  ```
  To run this command, python 3 is needed.
  
- Open any web browser and go to `http://localhost:<PORT>`. For example, `http://localhost:8080` if you used port 8080.
- You can find the frontend code in `neuro-cartography/src/interface`.

## Generate data for NeuroCartography

### ImageNet Dataset
- We used tfrecord [ImageNet](http://www.image-net.org/) Datasete.

### Code Structure
The codes to generate data are in `neuro-cartography/src/python`.




[demo]: https://poloclub.github.io/neuro-cartography/
[src]: https://github.com/poloclub/neuro-cartography
[youtube]: https://youtu.be/gx0dDNXFJA0
[paper]: https://arxiv.org/abs/2108.12931
