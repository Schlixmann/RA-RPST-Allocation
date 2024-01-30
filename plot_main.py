import matplotlib.pyplot as plt
import json
import os

# Load JSON data from dir_path folder
dir_path = "results/"
combined_data = []
for file in os.listdir(dir_path):
    if os.path.isdir(file):
        continue
    with open(dir_path+file, "r") as f:
        combined_data.append(json.loads(f.read()))

# Extracting data for plotting
solvers = [item["solver"][0] for item in combined_data]
times = [item["time"][0] for item in combined_data]
items = [item["items"][0] for item in combined_data]
best_values = [item["best"][0] for item in combined_data]

# Plotting the data
fig, ax = plt.subplots(figsize=(10, 6))
box = ax.boxplot(items, labels=solvers, vert=True, patch_artist=True)

# Highlight the best values with a red line
#ax.plot(solvers, best_values, color='red', marker='o', linestyle='None', label='Best')

# Adjust x-values for aligning with the boxplot positions
x_values_best = [i + 1 for i in range(len(solvers))]

# Highlight the best values with a red line
ax.plot(x_values_best, best_values, color='red', marker='o', linestyle='None', label='Best')

# Annotate the time on top of each whisker
for i, (solver, time) in enumerate(zip(solvers, times)):
    ax.text(i + 1, max(items[i]), f'Time: {time:.2f}', ha='center', va='bottom', color='blue')

# Adding labels and title
plt.xlabel("Solver")
plt.ylabel("Items")
plt.title("Whisker Plot for Items with Best Values and Time Annotation")
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
