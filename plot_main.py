import matplotlib.pyplot as plt
import json

# Load JSON data from the first file
with open("results/heur_results_paper.json", "r") as f:
    data1 = json.loads(f.read())

# Load JSON data from the second file
with open("results/gen_results_paper.json", "r") as f:
    data2 = json.loads(f.read())

# Combine data for plotting
combined_data = [data1, data2]

# Extracting data for plotting
solvers = [item["solver"][0] for item in combined_data]
times = [item["time"][0] for item in combined_data]
items = [item["items"][0] for item in combined_data]
best_values = [item["best"][0] for item in combined_data]

# Plotting the data
fig, ax = plt.subplots(figsize=(10, 6))
box = ax.boxplot(items, labels=solvers, vert=True, patch_artist=True)

# Highlight the best values with a red line
ax.plot(solvers, best_values, color='red', marker='o', linestyle='None', label='Best')

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
