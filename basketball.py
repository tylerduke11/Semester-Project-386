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
merged = pd.merge(stats_df, salary_df, on='Player', how='left')
merged = merged[1:]
#merged.to_csv("nba_data.csv")
# %%
