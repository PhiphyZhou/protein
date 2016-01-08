# protein
Protein simulation and data analysis 

## Dependencies
cython-0.23.4

mdtraj-1.5.1

numpy-1.10.2

scipy-0.13.3

Using docker container: 
```
docker run -it --name protein -v /home/bdslss15-xpjs/simple-examples:/simple-examples -v /home/bdslss15-xpjs/protein:/protein -v /damsl/projects/MD/Simulations/bpti:/protein-data -v /output phiphy/tensorflow-adv
```
