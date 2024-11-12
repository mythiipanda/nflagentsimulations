import matplotlib.pyplot as plt

# Data for the chart
players = ['Drew Brees', 'Tom Brady', 'Peyton', 'Brett']
passing_yards = [89214, 89000, 71000, 71000]

# Create the figure and axis
fig, ax = plt.subplots()

# Create the bar chart
ax.bar(players, passing_yards)

# Set the title and labels
ax.set_title('Top 4 Passing Yards Records')
ax.set_xlabel('Player')
ax.set_ylabel('Passing Yards')

# Show the plot
plt.show()