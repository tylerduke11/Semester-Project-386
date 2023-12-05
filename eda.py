# %%
# import libraries for EDA
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# read file
basketball = pd.read_csv("nba_data.csv", index_col=0)

# %% Find all the relavent information we need
avg_points = basketball.groupby('Team')['PTS'].mean().sort_values()
avg_salary = basketball.groupby('Team')['Salary'].mean()
team_wins = basketball.groupby('Team')['TW'].mean()


# %% EDA 1
# Find the average salary per team
sns.barplot(x=avg_salary.values / 1e6, y=avg_salary.index, palette='viridis')
plt.title('Average Salary of Players on a Team')
plt.xlabel('Salary (in Millions)')
plt.ylabel('Frequency')
#plt.savefig('bar_salary_by_team.png')


# %% EDA 2
# Plot the average salary per team and the average points per team next to each other
bar_width = 0.35
index = np.arange(len(avg_points))
plt.figure(figsize=(12, 10))

# Plotting average points per team
plt.bar(index, avg_points, bar_width, color='skyblue', label='Average Points')
# Plotting average salary per team next to the previous bars
plt.bar(index + bar_width, avg_salary / 1e6, bar_width, color='orange', alpha=0.7, label='Average Salary')

plt.xlabel('Team')
plt.ylabel('Values (Scaled Points and Salary to be on the same scale)')
plt.title('Average Points and Salary of Players on a Team')
plt.xticks(index + bar_width / 2, avg_points.index, rotation=90)
plt.tick_params(axis='y', which='both', left=False, labelleft=False)
plt.legend()
#plt.savefig('bar_pts_vs_salary.png')


# %% EDA 3
# Scatter plot of total wins vs. average salary
plt.figure(figsize=(10, 8))
plt.scatter(x=avg_salary / 1e6, y=team_wins, color='deepskyblue')
sns.regplot(x=avg_salary / 1e6, y=team_wins, color='deepskyblue')
# Label the points with their corresponding team
for i, team in enumerate(team_wins.index): 
    plt.text(avg_salary[i] / 1e6, team_wins[i], team, ha='right', va='bottom')
plt.xlabel('Average Salary (in Millions)')
plt.ylabel('Total Wins')
plt.title('Total Wins vs. Average Salary')
#plt.savefig('point_teamwins_vs_salary.png')


# %% EDA 4
# Define the list of metrics for the y-axis
metrics = ['Age', 'GP', 'FG%', '3P%', 'FT%', 'PTS', 'REB', 'AST', 'DD2', 'TD3']
metric_labels = ['Age', 'Games Played', 'Field Goal %', '3 Point %', 'Free Throw %', 'Points', 'Rebounds',
                 'Assists', 'Double Doubles', 'Triple Doubles']

# Set up subplots in a 2x5 grid for 10 different graphs
fig, axes = plt.subplots(2, 5, figsize=(18, 8))
fig.suptitle('Relationship between Salary and Various Metrics for Players in the 2022-2023 NBA Season', fontsize=16)

# Iterate through metrics and create individual subplots
for i, metric in enumerate(metrics):
    row = i // 5  # Calculate the row index
    col = i % 5   # Calculate the column index

    # Plot each metric on its corresponding subplot
    axes[row, col].scatter(basketball['Salary'] / 1e6, basketball[metric], color=plt.cm.tab10(i), label=metric)
    sns.regplot(x=basketball['Salary'] / 1e6, y=basketball[metric], ax=axes[row, col], scatter=False, color=plt.cm.tab10(i))
    axes[row, col].set_xlabel('Salary (in Millions)')
    axes[row, col].set_ylabel(metric_labels[i])
    axes[row, col].legend()

#plt.savefig('multi_salary_vs_metrics.png')


# %% EDA 5
# Extract top 5 and bottom 5 teams by average points per game
top_teams = avg_points.tail(3).index.tolist()
bottom_teams = avg_points.head(3).index.tolist()
selected_teams = top_teams + bottom_teams
filtered_data = basketball[basketball['Team'].isin(selected_teams)]

plt.figure(figsize=(10, 6))
sns.lmplot(data=filtered_data, x="Salary", y="PTS", hue="Team", lowess=True)
plt.title("Salary vs. Points per Game for Top 3 and Bottom 3 Teams by Points")
plt.xlabel('Salary (in Millions)')
plt.ylabel('Average Points per Game')
plt.grid(True)
#plt.savefig("top3_bottom3_score.png")

# %% EDA 6
# boxplot for points among teams
plt.figure(figsize=(10, 6))
sns.boxplot(x='Team', y='PTS', data=basketball, palette='Set2')
plt.xlabel('Team')
plt.ylabel('Points (PTS)')
plt.title('Distribution of Points among NBA Teams')
plt.xticks(rotation=45)
#plt.savefig("boxplot_team_points.png")
# %%
