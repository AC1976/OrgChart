import pandas as pd
import duckdb

## load the org tree in the excel file as a pandas dataframe 
chart = pd.read_excel('tree.xlsx')

## function to recursively walk the org chart, from child_id up to topco
def get_owners(child_id):
 
    # recursive sql statement to get, recursive, all LEs below 'goldid'
    recursive_sql = f"""
                        WITH RECURSIVE org_chart AS (
                        SELECT CHILD_ID, CHILD_NAME, CHILD_COUNTRY, OWNER_ID, OWNERSHIP, 0 AS level
                        FROM chart
                        WHERE CHILD_ID = '{child_id}'
 
                        UNION ALL
 
                        SELECT r.CHILD_ID, r.CHILD_NAME, r.CHILD_COUNTRY, r.OWNER_ID, r.OWNERSHIP, level + 1
                        FROM chart r, org_chart oc
                        WHERE r.CHILD_ID = oc.OWNER_ID
                        )
 
                        SELECT * FROM org_chart
                       
                        """
       
    query = duckdb.sql(recursive_sql).show() ## change .show() to e.g. .df() to export a dataframe
 
    return query

## statement to execute the function
get_owners('D0009')