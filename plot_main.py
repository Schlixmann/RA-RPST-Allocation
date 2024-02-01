import matplotlib.pyplot as plt
import json
import os

# Load JSON data from dir_path folder
dir_path = "results/"
combined_data = []
gen_data = []
for file in os.listdir(dir_path):
    if os.path.isdir(dir_path + file):
        continue

    with open(dir_path+file, "r") as f:
        if file[:3] == "gen":
            gen_data.append(json.loads(f.read()))
        else:    
            combined_data.append(json.loads(f.read()))

# Extracting data for plotting
solvers = [item["solver"][0] for item in combined_data]
times = [item["time"][0] for item in combined_data]
items = [item["items"][0] for item in combined_data]
best_values = [item["best"][0] for item in combined_data]

# Extracting Gen Data:
solvers_g = [item["solver"][0] for item in  gen_data]
times_g = [sum(item["times"])/len(item["times"]) for item in gen_data]
items_g = [min([v for k,v in item.items() if k[:5] == "items"]) for item in gen_data]
best_values_g = [min(item["bests"]) for item in gen_data]

for i in range(len(items_g)):
    items.append(items_g[i][0])
times += times_g
lables =solvers + solvers_g

best_values += (best_values_g)
# Plotting the data
fig, ax = plt.subplots(figsize=(10, 6))
box = ax.boxplot(items, labels=lables, vert=True, patch_artist=True)

# Highlight the best values with a red line
#ax.plot(solvers, best_values, color='red', marker='o', linestyle='None', label='Best')

# Adjust x-values for aligning with the boxplot positions
x_values_best = [i + 1 for i in range(len(lables))]

# Highlight the best values with a red line
ax.plot(x_values_best, best_values, color='red', marker='o', linestyle='None', label='Best')

# Annotate the time on top of each whisker
for i, (solver, time) in enumerate(zip(lables, times)):
    ax.text(i + 1, max(items[i]), f'Time: {time:.2f}', ha='center', va='bottom', color='blue')

# Adding labels and title
plt.xlabel("Solver")
plt.ylabel("Items")
plt.title("Whisker Plot for Items with Best Values and Time Annotation")
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
