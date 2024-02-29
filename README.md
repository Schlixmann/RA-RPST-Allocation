# RA-RPST Allocation:

All results of of the experiments can be found in folder: `results/experiments`. <br>
The table and aggregations can be found in the notebook: `results_presentation/results.ipynb`

To reproduce the experiments from Schumann & Rinderle-Ma (2024): Optimizing Resource-Driven Process
configuration through Genetic Algorithms:

**Please be aware:** <br> Rerunning the iterative solution search is time and resource-consuming (approx > 5h). <br>
The results for the genetic algorithms might differ slightly from our results, since the genetic algorithm is non-deterministic.
```
pip install -r requirements.txt
python main.py
```

If you also want to rerun calculation of the iterative optimization search:
```
python main.py -b
```
