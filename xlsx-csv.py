import pandas as pd

## load the org tree in the excel file as a pandas dataframe 
chart = pd.read_excel('tree.xlsx')

## csv

chart[['CHILD_ID', 'OWNER_ID']].to_csv('tree.csv', index=None)

