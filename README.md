# RA-RPST Allocation:

All results of of the experiments can be found in folder: `results/experiments`. <br>
The table and aggregations can be found in the notebook: `results_presentation/results.ipynb`

To reproduce the experiments from Schumann & Rinderle-Ma (2024): Optimizing Resource-Driven Process
configuration through Genetic Algorithms:

**Please be aware:** <br> Rerunning the iterative solution search is time and resource-consuming (>10h, >10GB Ram). <br>
The results for the genetic algorithms might differ slightly from our results, since the genetic algorithm is non-deterministic.

To rerun heuristic search and genetic algorithm:
```
pip install -r requirements.txt
python main.py
```

If you also want to rerun calculation of the iterative optimization search:
```
python main.py -b
```
## View Process Models BPM Like: 
To view a BPM-like representation of the resulting process models, use the following command:
```
python3 open_model.py path_to_model
```
e.g.:
```
python3 open_model.py results/experiments/fully_synthetic/proc/brute.xml
```
To show the plain process model: 
```
python3 open_model.py processes/offer_process_paper.xml
```
To look at the other best process models, change the folder accordingly e.g.:
```
../fully_synthetic/proc/..
```
All results can be found in results/experiments
