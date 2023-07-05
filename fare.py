import requests
from bs4 import BeautifulSoup
import pandas as pd

# Create an URL object
url = 'https://www.sbstransit.com.sg/fares-and-concessions'
# Create object page
page = requests.get(url)

# parser-lxml = Change html to Python friendly format
# Obtain page's information
soup = BeautifulSoup(page.text, 'lxml')

# Obtain information from tag <table>
results = soup.find(id='accordion')

# Select the first child from the results
table1 = results.find('table')
headers = []
added_titles = set()
for i in table1.find('tbody').find('tr'):
    title = i.text.replace('\n', '').replace('\t', '').strip()
    if title:
        if title in added_titles:
            headers.append(title + ' (Cash Fare)')
        else:
            headers.append(title)
            added_titles.add(title)

fares = pd.DataFrame(columns=headers)
for j in table1.find('tbody').find_all('tr'):
    row_data = j.find_all('td')
    row = [i.text.strip() for i in row_data]  # Retrieve only the text
    # Convert the first column to only the last number
    if len(row) > 0:
        range_values = row[0].split(" - ")
        if len(range_values) == 2:
            last_number = range_values[1].split()[-1]
            if last_number:
                row[0] = last_number
        else:
            over_value = row[0].split("Over ")
            up_to_value = row[0].split("Up to ")
            if len(over_value) == 2:
                row[0] = str(10000)
            elif len(up_to_value) == 2:
                last_number = up_to_value[1].split()[-1]
                if last_number:
                    row[0] = last_number
    length = len(fares)
    length = len(fares)
    fares.loc[length] = row

fares.to_json('fares.json', orient='records')
