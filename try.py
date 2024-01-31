import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Example data
x = np.random.rand(100)
y = np.random.rand(100)
z = np.random.rand(100)
fourth_dimension = np.random.rand(100)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter(x, y, z, c=fourth_dimension, cmap='viridis')

# Add colorbar
cbar = plt.colorbar(sc)
cbar.set_label('Fourth Dimension')

plt.show()