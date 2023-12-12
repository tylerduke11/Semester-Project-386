# %% import libraries
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go
st.set_option('deprecation.showPyplotGlobalUse', False)

# Load data
basketball = pd.read_csv("nba_data.csv", index_col=0)

# Show team codes to make it easier to visualize and select the desired team
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

# %%
st.title('NBA Data Analysis Dashboard')
st.write('I have compiled some information about NBA team data, including player game stats from the 2022-2023 NBA season, team wins, and player salary. Take a look at some of my graphs I compiled based on the data!')

# Create a sidebar with navigation links
st.sidebar.title('Links for my Blog Page and GitHub Repository')
blog_link = st.sidebar.button('https://tylerduke11.github.io/my-blog/2023/11/30/project-eda-findings.html')
github_link = st.sidebar.button('https://github.com/tylerduke11/Semester-Project-386')

# Create hyperlinks based on user selections
if blog_link:
    st.write('Redirecting to your blog post...')
    # Use st.markdown to create a hyperlink to your blog post
    st.markdown('[Link to Blog Post](https://www.example.com/blog_post)')
elif github_link:
    st.write('Redirecting to your GitHub repository...')
    # Use st.markdown to create a hyperlink to your GitHub repository
    st.markdown('[Link to GitHub Repository](https://github.com/your_username/your_repository)')


# %%
st.header('Average Salary of Players on a Team')
st.write('Select a few NBA teams to compare their average salary that they pay their players. It will be ordered by the highest average salary on top and the lowest average salary on bottom.')

# Create a list of team names from the dictionary
team_names = list(team_name_to_code.keys())

# Map team codes to team names
code_to_team_name = {v: k for k, v in team_name_to_code.items()}

# Allow users to select multiple teams using team names
selected_teams = st.multiselect('Select Teams', team_names)

# Convert selected team names back to team codes for filtering data
selected_team_codes = [team_name_to_code[name] for name in selected_teams]

# Filter data based on selected team codes
team_df = basketball[basketball['Team'].isin(selected_team_codes)]

if team_df.empty:
    st.write('No data available for the selected teams')
else:
    avg_salary = team_df.groupby('Team')['Salary'].mean().reset_index()

    # Create a Plotly bar chart with custom bar color
    custom_colors = ['#FF5733', '#33FF57', '#3366FF', '#FF33A8']
    
    # Map team codes back to team names for displaying in tooltips
    avg_salary['Team'] = avg_salary['Team'].map(code_to_team_name)

    # Create a Plotly bar chart with hover data
    fig = px.bar(avg_salary, x='Salary', y='Team', text='Salary',
                 labels={'Salary': 'Average Salary (in Millions)', 'Team': 'Team'},
                 title='Average Salary of Players on Selected Teams',
                 hover_data={'Team': True, 'Salary': ':$.2f'}, # Format tooltip as currency
                 color='Salary', color_discrete_sequence=custom_colors)  

    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})

    st.plotly_chart(fig)
# %%
st.header('Average Points of Top Players on Selected Teams')
st.write('Here we can look at the same information as above, but it also has the value for the avg points for that team.')

# Find all the relevant information we need
avg_points = basketball.groupby('Team')['PTS'].mean().sort_values()
avg_salary = basketball.groupby('Team')['Salary'].mean()

# Create DataFrames for average points and salary separately
avg_points_df = pd.DataFrame({'Team': avg_points.index, 'Average Points': avg_points.values})
avg_salary_df = pd.DataFrame({'Team': avg_salary.index, 'Average Salary (Millions)': avg_salary.values / 1e6})

# Merge both DataFrames on 'Team' to ensure correct alignment
avg_df = pd.merge(avg_points_df, avg_salary_df, on='Team')

# Allow users to select multiple teams using multiselect
selected_teams = st.multiselect('Select Teams', avg_df['Team'])

# Filter data based on selected teams
filtered_avg_df = avg_df[avg_df['Team'].isin(selected_teams)]

if not filtered_avg_df.empty:
    # Create an interactive bar chart using Plotly Express for selected teams
    fig = px.bar(filtered_avg_df, x='Team', y=['Average Points', 'Average Salary (Millions)'],
                 labels={'value': 'Values', 'variable': 'Metric', 'Team': 'Team'},
                 title='Average Points and Salary of Players on Selected Teams',
                 barmode='group')

    fig.update_layout(xaxis={'categoryorder': 'total ascending', 'tickangle': 45})  # Rotate x-axis labels by 45 degrees

    # Display the interactive plot in Streamlit
    st.plotly_chart(fig)
else:
    st.write('No data available for the selected teams')
# %%

st.header('Scatterplot of Total Wins vs. Average Salary of a Team')
st.write('Here I fit a model that shows a scatterplot of the Total Wins of a team on the y-axis and the Average Salary of a team on the x-axis. I also included the linear regression line of best fit to show the positive linear trend of the data. Hover over the team for more information!')

# Find all the relevant information we need
avg_salary = basketball.groupby('Team')['Salary'].mean()
team_wins = basketball.groupby('Team')['TW'].mean()

# Create a DataFrame for average salary and total wins of teams
team_stats = pd.DataFrame({'Team': team_wins.index, 'Average Salary (Millions)': avg_salary.values / 1e6, 'Total Wins': team_wins.values})

# Create an interactive scatterplot using Plotly Express
fig = px.scatter(team_stats, x='Average Salary (Millions)', y='Total Wins', text='Team',
                 hover_data={'Average Salary (Millions)': ':.2f', 'Total Wins': ':.2f'},
                 labels={'Average Salary (Millions)': 'Average Salary (in Millions)', 'Total Wins': 'Total Wins'},
                 title='Total Wins vs. Average Salary',
                 trendline='ols', # Add trendline
                 color_discrete_sequence=['limegreen'])  

fig.update_traces(textposition='top center')  # Set text position in the center

# Update layout for tooltips and axis labels
fig.update_layout(hovermode='closest', xaxis_title='Average Salary (in Millions)', yaxis_title='Total Wins')

# Display the interactive plot in Streamlit
st.plotly_chart(fig)

# %%
st.header("Basketball Team Performance Dashboard")
st.write("In this dashboard, you can explore the relationship between team salaries and average points per game for selected basketball teams. The scatterplot displays the data points, which is each player on the selected team, while the lowess curve provides insight into the trend. Choose your favorite teams and visualize their performance.")

# Team selection widget
team_list = basketball['Team'].unique().tolist()
selected_teams = st.multiselect('Select Teams', team_list)

# Filter data based on selection
if selected_teams:
    filtered_data = basketball[basketball['Team'].isin(selected_teams)]

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.lmplot(data=filtered_data, x="Salary", y="PTS", hue="Team", lowess=True, aspect=2)
    plt.title("Salary vs. Points for Selected Teams")
    plt.xlabel('Salary (in Millions)')
    plt.ylabel('Average Points per Game')
    st.pyplot(plt)

else:
     st.write("Please select at least one team to display the graph.")

# %%
st.header("NBA Teams Points Distribution Dashboard")

# Team selection widget
team_list = basketball['Team'].unique().tolist()
selected_teams = st.multiselect('Select Teams to Compare', team_list, default=team_list)

# Palette selection
palette = st.radio('Select Color Palette', ['Set2', 'viridis', 'plasma', 'inferno', 'magma', 'cividis'])

# Filter data based on selection
filtered_data = basketball[basketball['Team'].isin(selected_teams)]

# Plotting
plt.figure(figsize=(10, 6))
sns.boxplot(x='Team', y='PTS', data=filtered_data, palette=palette)
plt.xticks(rotation=45)


plt.xlabel('Team')
plt.ylabel('Points (PTS)')
plt.title('Distribution of Points among NBA Teams')

# Display the plot
st.pyplot(plt)

# %%
st.header('Relationship between Salary and Various Metrics')
st.write('Explore the NBA player performance in the 2022-2023 based on up to 10 various metrics. Select and compare various player metrics, such as age, points, rebounds, and more, against their salaries. Each metric is represented by a unique color, making it easy to spot trends and correlations in player performance and compensation. Each dot represents a player, and you can hover over the dot to see which player it is.')
# Define the list of metrics for the y-axis
metrics = ['Age', 'GP', 'FG%', '3P%', 'FT%', 'PTS', 'REB', 'AST', 'DD2', 'TD3']
metric_labels = ['Age', 'Games Played', 'Field Goal %', '3 Point %', 'Free Throw %', 'Points', 'Rebounds',
                 'Assists', 'Double Doubles', 'Triple Doubles']

# Define a list of colors for the graphs
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Streamlit widget for metric selection
selected_metrics = st.multiselect('Select Metrics to Compare with Salary', metrics, default=metrics)

# Creating subplots for selected metrics
if selected_metrics:
    fig = sp.make_subplots(rows=2, cols=5, subplot_titles=[metric_labels[metrics.index(m)] for m in selected_metrics])

    for i, metric in enumerate(selected_metrics):
        row = i // 5 + 1  # Calculate the row index
        col = i % 5 + 1   # Calculate the column index

        subset = basketball[['Salary', metric, 'Player']].dropna()

         # Scatter plot
        scatter_trace = go.Scatter(x=subset['Salary'] / 1e6, y=subset[metric], mode='markers', name=metric,
                       customdata=subset['Player'],
                       hovertemplate='Player: %{customdata}<br>Salary: %{x}M<br>' + metric + ': %{y}<extra></extra>',
                       marker=dict(color=colors[i]))
        fig.add_trace(scatter_trace, row=row, col=col)

        # Add line of best fit
        slope, intercept = np.polyfit(subset['Salary'], subset[metric], 1)
        line_trace = go.Scatter(x=subset['Salary'] / 1e6, y=slope * subset['Salary'] + intercept, mode='lines',
                       line=dict(color='blue'), showlegend=False)
        fig.add_trace(line_trace, row=row, col=col)

        # Update x and y-axis labels for the subplot
        fig.update_xaxes(title_text="Salary (in Millions)", row=row, col=col)

    fig.update_layout(height=800, width=1000, title_text="Relationship between Salary and Various Metrics for Players in the 2022-2023 NBA Season")

    # Display the plot
    st.plotly_chart(fig)
else:
    st.write("Please select at least one metric to display the graph.")