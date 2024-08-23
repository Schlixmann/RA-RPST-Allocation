# RA-RPST Allocation:

This is the latest version of the code for the RA-PST Project. 
The Project aims to combine possible resource allocations and the control flow of a process in one Resource-Augmented PST (RA-PST)
This project is ongoing and, therefore, under constant development. <br>
Please see the note at the end of this readme.

## Build own RA-PST:
To create an RA-PST yourself, follow these steps: 

1. Create a process that is a valid CPEE-Tree:
("https://cpee.org/flow/?" -> create new instance -> monitor instance -> set "Attributes:theme" => felix)
Now, model a process. Set allowed resource roles on the right under "resources".
Download the finished model via: "save testset"

2. Create a valid resource file in which the resources fit the roles defined for tasks in the process.
Use one of the resource files in ```resource_config/*``` as template

3. Build the RA-PST by running ```create_ra_pst.py``` from command line: 
```
python create_ra_pst.py <process-file> <resource-file> -p
```

5. find the ra_pst as ```ra_pst.xml```

## View a GraphViz visualization of an RA-PST or an allocated RA-PST_instance: 

```
python draw_ra_pst.py <ra_pst_file.xml>
```

## Experiments as described in "Optimizing Resource-Driven Process Configuration through Genetic Algorithms"

All results of the experiments described in "Optimizing Resource-Driven Process Configuration through Genetic Algorithms" can be found in the directory: `results/experiments`. <br>
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


## Please Note:
The original code handed in with the paper: "Optimizing Resource-Driven Process Configuration through Genetic Algorithms" can be found in the branch "RD_Configuration Freeze". 
The current main branch is more user-friendly but has more computational overhead.
