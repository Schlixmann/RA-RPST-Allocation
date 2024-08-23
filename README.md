# RA-RPST Allocation:

All results of the experiments can be found in the directory: `results/experiments`. <br>
The table and aggregations can be found in the Jupyternotebook: `results_presentation/results.ipynb`

To reproduce the experiments from Optimizing Resource-Driven Process Configuration through Genetic Algorithms (2024):

**Please note:** <br> Rerunning the solution search is time and resource-consuming, especially if you want to brute-force the search of the full solution space (>24h, >10GB RAM). <br>
The results for the genetic algorithms might differ slightly from our results since the genetic algorithm is non-deterministic.

To run only heuristic search and genetic algorithm:
```
pip install -r requirements.txt
python main.py
```

If you also want to run the iterative search of the full solution space for optimization:
```
python main.py -b
```
## View Process Models in BPM Like representation: 
To view a BPM-like representation of the process models, use the following command:
`python3 open_model.py path_to_model`

e.g.:
```
python3 open_model.py results/experiments/fully_synthetic/proc/brute.xml
```
To show the plain process model: 
```
python3 open_model.py processes/offer_process_paper.xml
```
To look at the other best process models, change the folder accordingly, e.g.:
`../fully_synthetic/proc/..`
All results can be found in `results/experiments`.
