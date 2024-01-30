import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import numpy as np
import json

# Your JSON data
combined_data = []
for i in range(0,5):
    with open(f"findings_{i}.json", "r") as f:
        json_data = json.loads(f.read())
        combined_data.append(json_data)

items_min = [item["min_fit"] for item in combined_data]
items_max = [item["max_fit"] for item in combined_data]
solvers = [item["solver"] for item in combined_data]

unique_solutions = {item["solver"][0] : item["no_unique_solutions"] for item in combined_data}

# Extracting data
#execution_numbers = list(range(1, len(json_data["avg_fit"]) + 1))
avg_fit = json_data["avg_fit"]
min_fit = json_data["min_fit"]
max_fit = json_data["max_fit"]
print(unique_solutions)
#fig, ax = plt.subplots(figsize=(10, 6))
#plt.plot(items_min)


# Plotting the data
cmap = plt.colormaps["tab20"]
colors = cmap.colors
plt.figure(figsize=(10, 6))
plt.axhline(y=179, color='r', linestyle='--', label='Target')



for i in range(len(items_min)):
    plt.plot(list(range(1, len(items_min[i])+1)), items_min[i], label=solvers[i][0], color=colors[i*2])
    plt.plot(list(range(1, len(items_max[i])+1)), items_max[i], label=solvers[i][0], color=colors[(i*2)+1])
    
#plt.plot(execution_numbers, avg_fit, label="Average Fitness", marker='o')
#plt.plot(execution_numbers, min_fit, label="Minimum Fitness", marker='o')
#plt.plot(execution_numbers, max_fit, label="Maximum Fitness", marker='o')


# Adding labels and title
plt.xlabel("Execution Number")
plt.ylabel("Fitness")
plt.title("Fitness Over Executions")
plt.legend()
plt.grid(True)
#plt.title(f"{json_data['solver']}")

# Show the plot
plt.show()


