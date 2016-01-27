# protein
Protein simulation and data analysis 

## Dependencies
Tensorflow
cython-0.23.4
mdtraj-1.5.1
numpy-1.10.2
scipy-0.13.3
MDAnalysis-0.12.1

Run a docker container from the image built by the Dockerfile: 
```
docker build -t phiphy/protein . 
docker run -it --name protein -v /home/bdslss15-xpjs/simple-examples:/simple-examples -v /home/bdslss15-xpjs/protein:/protein -v /damsl/projects/MD/Simulations/bpti:/protein-data phiphy/protein
```
