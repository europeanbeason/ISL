import matplotlib.pyplot as plt

# Data
x_values = ['159', '493', '1400', '2152', '2319', '3795']
NN = [1.489739, 1.378249, 1.528204, 1.306748, 1.12415, 1.457246]
opt2 = [1.174314, 1.263494, 1.447539, 1.299334, 1.120791, 1.440053]
opt3 = [1.172008, 1.306734, 1.528204, 1.306748, 1.123321, 1.457246]

# Create scatter plot
plt.scatter(x_values, NN, label='Nearest Neighbour', facecolors='none', edgecolors='black', s=70)
plt.scatter(x_values, opt2, label='2-Opt', facecolors='none', edgecolors='green', s=70)
plt.scatter(x_values, opt3, label='3-Opt', facecolors='none', edgecolors='violet', s=70)

# Add labels and title
plt.xlabel('Size of an instance')
plt.ylabel('Standardized Distance')
plt.title('Distance with respect to lower bound for different heuristics.')
plt.legend()
plt.grid()
# Show plot
plt.savefig('scatter_plot.png')