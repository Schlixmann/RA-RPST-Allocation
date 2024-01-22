import matplotlib.pyplot as plt
import json

# Your JSON data
for i in range(0,4):
    with open(f"findings_{i}.json", "r") as f:
        json_data = json.loads(f.read())


    # Extracting data
    execution_numbers = list(range(1, len(json_data["avg_fit"]) + 1))
    avg_fit = json_data["avg_fit"]
    min_fit = json_data["min_fit"]
    max_fit = json_data["max_fit"]

    # Plotting the data
    plt.figure(figsize=(10, 6))
    plt.plot(execution_numbers, avg_fit, label="Average Fitness", marker='o')
    plt.plot(execution_numbers, min_fit, label="Minimum Fitness", marker='o')
    plt.plot(execution_numbers, max_fit, label="Maximum Fitness", marker='o')

    # Adding labels and title
    plt.xlabel("Execution Number")
    plt.ylabel("Fitness")
    plt.title("Fitness Over Executions")
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.show()

