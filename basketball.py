# %%
# import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import os

# %%
# initialize the web driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# %% scrape the stats data
stats_url = 'https://www.nba.com/stats/players/traditional?Season=2022-23'
 
# select the 'All' option to grab the stats for all players
stats_response = driver.get(stats_url)
dropdown = driver.find_element(By.CLASS_NAME,'DropDown_dropdown__TMlAR')
dropdown.click()
all_option = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select/option[1]')
all_option.click()

# grab the page elements
page_source = driver.page_source
time.sleep(3)
stats_soup = BeautifulSoup(page_source, 'html.parser')
stats_table = stats_soup.select_one('#__next > div.Layout_base__6IeUC.Layout_justNav__2H4H0.Layout_withSubNav__ByKRF > div.Layout_mainContent__jXliI > div.MaxWidthContainer_mwc__ID5AG > section.Block_block__62M07.nba-stats-content-block > div > div.Crom_base__f0niE > div.Crom_container__C45Ti.crom-container > table')
stats = []

# scrape to each row of the table
for row in stats_table.find_all('tr'):
    # scrape each cell within the row
    row_data = [cell.text.strip() for cell in row.find_all(['th', 'td'])]
    stats.append(row_data)

# clean the stats data frame and store the csv (I will not use this csv file)
stats_df = pd.DataFrame(stats)
stats_df = stats_df.iloc[:, 1:30]
stats_df.columns = stats_df.iloc[0]
stats_df = stats_df[1:]
#stats_df.to_csv("nba_stats_2022_2023.csv", index=False)




# %% scrape the salary data
salary_url = "https://hoopshype.com/salaries/players/2022-2023/"

# find the table on the page
salary_response = requests.get(salary_url)
salary_soup = BeautifulSoup(salary_response.text, 'html.parser')
salary_element = salary_soup.find('table')
salary = []

# scrape to each row of the table
for row in salary_element.find_all('tr'):
    # scrape each cell within the row
    salary_row_data = [cell.text.strip() for cell in row.find_all(['th', 'td'])]
    salary.append(salary_row_data)

# clean the salary data frame and store the csv (I will not use this csv file)
salary_df = pd.DataFrame(salary[1:], columns=salary[0])
salary_df.drop(salary_df.columns[[0, 3]], axis=1, inplace=True)
salary_df.rename(columns={'2022/23': 'Salary'}, inplace=True)
#salary_df.to_csv("nba_salary_2022_2023.csv")


# %% merge the salary and stats info to make one data set and store the csv
basketball_data = pd.merge(stats_df, salary_df, on='Player', how='left')
basketball_data = basketball_data[1:]
basketball_data['Salary'] = basketball_data['Salary'].replace('[\$,]', '', regex=True).astype(float)
numeric_columns = ['Age', 'GP', 'W', 'L', 'Min', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PF', 'FP', 'DD2', 'TD3', '+/-']
basketball_data[numeric_columns] = basketball_data[numeric_columns].astype(float)


# %%
teams_url = "https://champsorchumps.us/summary/nba/2023"

# find the table on the page
teams_response = requests.get(teams_url)
teams_soup = BeautifulSoup(teams_response.text, 'html.parser')
teams_element = teams_soup.find_all('table')[1]
teams = []

# scrape to each row of the table
for row in teams_element.find_all('tr'):
    # scrape each cell within the row
    teams_row_data = [cell.text.strip() for cell in row.find_all(['th', 'td'])]
    teams.append(teams_row_data)

# clean the data
teams_df = pd.DataFrame(teams[1:], columns=teams[0])
teams_df[['Wins', 'Losses']] = teams_df['Record'].str.split('-', expand=True)
teams_df = teams_df.iloc[:,[1,8,9]]

team_name_to_code = {
    'Milwaukee Bucks': 'MIL', 
    'Boston Celtics': 'BOS',
    'Philadelphia 76ers': 'PHI',
    'Denver Nuggets': 'DEN',
    'Cleveland Cavaliers': 'CLE',
    'Memphis Grizzlies': 'MEM',
    'Sacramento Kings': 'SAC',
    'New York Knicks': 'NYK',
    'Phoenix Suns': 'PHX',
    'Brooklyn Nets': 'BKN',
    'Golden State Warriors': 'GSW',
    'Los Angeles Clippers': 'LAC',
    'Miami Heat': 'MIA',
    'Los Angeles Lakers': 'LAL',
    'New Orleans Pelicans': 'NOP',
    'Minnesota Timberwolves': 'MIN',
    'Toronto Raptors': 'TOR',
    'Atlanta Hawks': 'ATL',
    'Chicago Bulls': 'CHI',
    'Oklahoma City Thunder': 'OKC',
    'Dallas Mavericks': 'DAL',
    'Utah Jazz': 'UTA',
    'Washington Wizards': 'WAS',
    'Indiana Pacers': 'IND',
    'Orlando Magic': 'ORL',
    'Portland Trail Blazers': 'POR',
    'Charlotte Hornets': 'CHA',
    'Houston Rockets': 'HOU',
    'San Antonio Spurs': 'SAS',
    'Detroit Pistons': 'DET'
}

teams_df['Team Code'] = teams_df['Team'].map(team_name_to_code)
teams_df = teams_df.iloc[:,[3,1,2]]
teams_df.rename(columns={'Team Code': 'Team'}, inplace=True)

# %% Merge the final data frame together
basketball = basketball_data.merge(teams_df, left_on='Team', right_on='Team', how='left')
basketball = basketball.loc[:, ['Player', 'Team', 'Wins', 'Losses', 'Age', 'Salary', 'PTS', 'GP', 'FG%', '3P%', 'FT%', 'REB', 'AST', 'STL', 'BLK', 'DD2', 'TD3']]
basketball = basketball.rename(columns={'Wins': 'TW', 'Losses': 'TL'})
basketball.to_csv("nba_data.csv")





# %% EDA !!!!!!!!
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


# %%
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
plt.savefig("top3_bottom3_score.png")

# %%
plt.figure(figsize=(10, 6))
sns.boxplot(x='Team', y='PTS', data=basketball, palette='Set2')
plt.xlabel('Team')
plt.ylabel('Points (PTS)')
plt.title('Distribution of Points among NBA Teams')
plt.xticks(rotation=45)
plt.savefig("boxplot_team_points.png")
# %%
