# We Walk the Org Chart

Once a multinational has determined which jurisdictions in the org chart are subject to 'Jurisdictional Top Up Tax' -- i.e. in 2024, in any jurisdiction that flunks any of the three temporary Safe Harbor provisions and which does not itself apply a QDMTT (yet) -- the tax team is faced with the not insignificant challenge of 'walking the org chart' to identify the shareholders of all Constituent Entities in such a jurisdiction. 

Scrutiny of that ownership is then required to determine whether the IIR applies at a higher tier of ownership and, if so, for what share in the Jurisdictional Top Up Tax pie. For multinationals with a global footprint and 100s of subsidiaries, standard Excel based approaches may fall fall short in documenting the ownership chains for all but the most organized of tax professionals. 

A better approach is needed. This repo provides the Python code and explanations to make a first step / attempt to that better approach. 

## The General Idea

> *The assumption is that you have already figured out which jurisdictions are (likely going to be) low taxed in 2024, so that you know which legal entities are in scope of being subject to an IIR. It is those entities we start with.*

Regardless of the breadth and width of an org chart and regardless whether it prints on A4, A3 or A1 sized rolls of paper - it is nothing but a list of nodes with edges and a root. Probably a long list, but nonetheless.

In columnar Excel style, the list comprises of a column headed **Child_ID** with row upon row of legal entity identifiers, a column headed **Parent_ID** with the matching shareholder for the adjacent Child_ID and finally a column **Ownership** with the ownership percentage. Like so:

| Child_ID | Child_Country | Parent_ID | Ownership
|-|-|-|-|
| ChartWalk |US |NASDAQ |100%
| HoldCo |NL |ChartWalk |100%
| IPCo | N/A | HoldCo |100%
| DistriCo | SG |HoldCo |25%
| DistriCo | SG |ChartWalk |75%

This is a *hierachical tree* with root *NASDAQ* and we can code a routine that allows to extract the path from any **Child_ID** we take an interest in, to the ultimate parent or the root i.e. the top of the tree. For example, we want to be able to tell the script to get us the ownership for DistriCo and the routine then should give us something like:

- DistriCo in Singapore is 25% held by HoldCo in NL;
- HoldCo in NL is 100% held by ChartWalk, Inc in US;
- DistriCo in Singapore is 75% held by ChartWalk in US.

Clearly such a *walk through the org chart* for any **Child_ID** we care about is awesome. It allows us to identify interim owners that may, or may not, apply an IIR rule. If the org chart is massive and 10 tiers deep, the *org chart walk* greatly simplifies the IIR analysis. Perhaps we can even design an algo to autoflag whether an IIR applies, or not, for any given **Child_ID**. 

And of course, if we have the org chart in the table as set forth above, we don't need to manually identify the legal entities in any low taxed jurisdiction. We should be able to just tell the machine, simply, *give me all the org chart walks for all legal entities in jurisdiction A*  where A is the ISO code for some jurisdiction where the top up tax applies. 

## Before we Get to the Code

> This repo contains a chunky synthetic org chart that can be used to toy with. It is an *.xlsx file because despite what the tax software vendors like to tell us, there's no substitute for Microsoft's Excel for doing tax.*

### Who's Python

The next steps walk through the implementation of all the above in Python. If you have never worked with Python before, fear not. All you need to do is:

- Install Python 3 ->  https://www.python.org/downloads/
- Install VS Code -> https://code.visualstudio.com/download

*For Python, I like to work with 3.10. For VS Code, best to download the 'User Install' version, and not the System install. This keeps the instal local for your user, and should give least fuss with Corporate IT controlled locked down PCs.*

Installing Python 3 will make the Python runtime available on your computer so you can run the code we will be building. VS Code is a text editor -- think of it like Word for software developers. It is the program we'll use to write our code in or, if you're lazy, use to open the files in this repo. VS Code is awesome. It also allows to execute the Python code without the need to leave the editor. It's free and brilliant and one more reason you should buy some more MS stock.

Okay. On the desktop of your computer, create a new folder called 'ChartWalker'. Now open VS Code and 'open project folder'. Pick the folder 'ChartWalker' you just created on the desktop. Below is the link to the beginner tutorial for VS Code by MS which you are going to follow to set up a 'virtual environment'.

https://code.visualstudio.com/docs/python/python-tutorial

Pay attention to setting up the 'virtual environment' as explained in the tutorial (use 'venv'). Now, follow the instructions and create a 'virtual environment'. Make sure that the environment is active and install the following packages into it:

- pandas
- openpyxl
- duckdb

These packages extent the core capabilities that come standard with Python. Don't worry about installing these on your machine -- they are de facto standards in the data science world. And hey, duckdb is from Amsterdam. Good guys.

Everything installed?

Next, create a new file hello.py (just as the VS Code Tutorial is suggesting). VS Code, when it sees the .py file being created, will assume you are coding in Python and will start looking for the 'Python Interpreter' it will use. Check the right bottom of VS Code screen. Click and fiddle with it - what you want to see here is the name of the virtual environment which you created earlier AND IN WHICH YOU INSTALLED PANDAS AND DUCKDB.

(You can also forget about the virtual environments and just install pandas and duckdb in your global Python space. That works as well. However, on the notion of better learned right to begin with... I am setting a higher bar here.)

Okay, with the file hello.py open in editor tab, type the following two lines on the first two lines:

```python
import pandas as pd
import duckdb
```
When we 'run' our code later on, this tells the Python interpreter that it needs to include the pandas package, as well as the duckdb package, in whatever it does to figure out how to execute our code. (We don't need to import openpyxl -- pandas used that under the hood to open the *.xlsx file only). See here the importance of making sure you install these packages in the virtual environment that VS Code has enabled. If you get red squigly lines underneath 'pandas' and 'duckdb' something is wrong -- the interpreter can't find the packages. You are likely using the wrong interpreter, or installed the packaged in the wrong environment. Fiddle with the interpreter options in the low right bottom of the VS Code screen if that happens or just reinstall the packages.

We import pandas as 'pd'. That's an alias. We'll use pandas so often we like to abbreviate it to just two letters. This is the standard alias for pandas but you could pick something else if you fancy.

## Now we Get to the Code

So, so far we have a file hello.py open in the editor with just the above two statements importing the two packages we'll depend on. The first step now is to 'load'  the org chart. That org chart is included the excel file 'tree.xlsx' and follows the table design I laid out above. Of course, you can just replace this with your own company data. However, it's important to keep the order of the columns, and the column names, identical to the example provided. If you change these, the code needs to be updated accordingly. How do we open an *.xlsx file in Python and read the content? Pandas!

```python
chart = pd.read_excel('tree.xlsx')
```
Here we tell Python to create a new variable *chart* that is comprised of the data in the Excel file  'tree.xlsx'. This is done using the Pandas method *read_excel* which we invoke with the *pd.read_excel* statement. Pandas is brilliant and automagically interprets the first row of the spreadsheet as the names of the columns. 

With the data loaded in the variable *chart*, let's see what it looks like. Add the following statement on the next line:
```python
print(chart)
```
and then 'run'  the program. To 'run'  the code, press the 90 degree rotated triangle in the right top corner of the screen where you are editing the code. In the terminal window of VS Code, you now should see something like this:

```console
   CHILD_ID                CHILD_NAME   CHILD_COUNTRY OWNER_ID  OWNERSHIP
0     A0001               Chart, Inc.   United States   NASDAQ        NaN
1     A0002          Charts EMEA B.V.     Netherlands    A0001       1.00
2     X0099            Charts IP B.V.     Netherlands    A0002       1.00
3     Y0001    Charts PanAsia Pty Ltd       Singapore    A0002       1.00
4     Z0001      EMEA Distributor Ltd         Ireland    A0002       1.00
5     B0004  Dublin Employment Co Ltd         Ireland    Z0001       1.00
6     C0002   Unlimited Financing LLC   United States    A0001       1.00
7     X0090        Chart Ventures Ltd  United Kingdom    X0002       0.50
8     D0004          Australia Rep Co       Australia    Y0001       1.00
9     D0005          Bali Home Office       Indonesia    Y0001       0.99
10    D0006       Bangkok Home Office        Thailand    Y0001       0.51
11    D0007         Angkor Snack Shop        Cambodia    Y0001       0.49
12    D0008       Phi Phi Beach Shack        Thailand    Y0001       0.51
13    D0009            Lanta Cook Ops        Thailand    Y0001       0.51
```

What happened? The 'read_excel' method of the pandas package read the file 'tree.xlsx' (using the package openpyxl that you installed under the hood) into the variable we called 'chart', and then we printed the content of 'chart' to the terminal. We can confirm it all got copy/pasted quite nicely. One thing to note is the index on the left, starting from 0 and running through the end of the rows. That's an index that we get from pandas for free. We'll not use it here but more about it later.

Experienced spreadsheet users may want to verify for themselves here that the values shown in the 'Ownership' column indeed are values, and not strings. Pandas handles the data types automatically and generally does an awesome job. We can use the following command to confirm the data types of the various fields in our table:
```python
x = chart.dtypes
print(x)
```
Which gives us:
```python
CHILD_ID          object
CHILD_NAME        object
CHILD_COUNTRY     object
OWNER_ID          object
OWNERSHIP        float64
dtype: object
```
The first four columns have 'object'  as datatype -- which is pandas slang for text strings. The ownership column has 'float' as datatype. So, should we desire or need it, we can run arethmetics with the 'ownership' column. We'll get to that later. (Just to say it here: if the source xlsx file has dates and time fields, pandas generally converts those to Python datatime objects as well flawlessly).

So, we have succeeded in loading the context of the tree.xlsx file into a variable that we can toy with. Now, before we go on, it is probably good to mention that the variable 'chart'  that we created here is what is called a 'dataframe' -- a 2 dimensional set of values (just as out Excel spreadsheets). Pandas is the leading tool to create dataframes from external data, and then manipulate as needed and/or run calculations on. The possibilities are endless -- see https://pandas.pydata.org/docs/getting_started/overview.html 

Whilst in the past I used pandas to query the data in my dataframes, and build a lot of logic and algos using the pandas API to manipulate dataframes, I have come to use more and more the functionality of DuckDb in the last months. DuckDb is, I think, I hybrid of a database query engine and a database -- we'll be jsut using the query engine piece of DuckDb. We'll apply that DuckDb functionality directly to the dataframe we created above -- without the need to setting up an actual database. We'll use raw SQL statements to query our dataframe, as I feel SQL is the most accessible tech for querying data and resources on the web when support is needed is enormous. 

Okay, so we continue in VS Code. Delete the 'print(chart)' line and replace with the following:

```python
chart = pd.read_excel('tree.xlsx')
results = duckdb.sql("SELECT * from chart").show()
```
And run the script. We now see the following being printed to the terminal:

```console

 ──────────┬──────────────────────────┬────────────────┬──────────┬───────────┐
│ CHILD_ID │        CHILD_NAME        │ CHILD_COUNTRY  │ OWNER_ID │ OWNERSHIP │
│ varchar  │         varchar          │    varchar     │ varchar  │  double   │
├──────────┼──────────────────────────┼────────────────┼──────────┼───────────┤
│ A0001    │ Chart, Inc.              │ United States  │ NASDAQ   │      NULL │
│ A0002    │ Charts EMEA B.V.         │ Netherlands    │ A0001    │       1.0 │
│ X0099    │ Charts IP B.V.           │ Netherlands    │ A0002    │       1.0 │
│ Y0001    │ Charts PanAsia Pty Ltd   │ Singapore      │ A0002    │       1.0 │
│ Z0001    │ EMEA Distributor Ltd     │ Ireland        │ A0002    │       1.0 │
│ B0004    │ Dublin Employment Co Ltd │ Ireland        │ Z0001    │       1.0 │
│ C0002    │ Unlimited Financing LLC  │ United States  │ A0001    │       1.0 │
│ X0090    │ Chart Ventures Ltd       │ United Kingdom │ X0002    │       0.5 │
│ D0004    │ Australia Rep Co         │ Australia      │ Y0001    │       1.0 │
│ D0005    │ Bali Home Office         │ Indonesia      │ Y0001    │      0.99 │
│ D0006    │ Bangkok Home Office      │ Thailand       │ Y0001    │      0.51 │
│ D0007    │ Angkor Snack Shop        │ Cambodia       │ Y0001    │      0.49 │
│ D0008    │ Phi Phi Beach Shack      │ Thailand       │ Y0001    │      0.51 │
│ D0009    │ Lanta Cook Ops           │ Thailand       │ Y0001    │      0.51 │
├──────────┴──────────────────────────┴────────────────┴──────────┴───────────┤
│ 14 rows                                                           5 columns │
└─────────────────────────────────────────────────────────────────────────────┘
```
It is -- again -- our dataframe, but now represented as the output of the sql query we executed on the pandas dataframe. Huh? Okay, when we issued the statement:
```python
results = duckdb.sql("SELECT * FROM chart").show()
```
We told the machine to create a variable 'results' from the sql query (which we invoked with the duckdb.sql method) 'SELECT * FROM chart'. Of course, 'chart' in this statement references the dataframe 'chart' we created in the earlier line and 'SELECT *' is the standard SQL statement to 'select all column and row values from the table 'chart' (our dataframe). So think of DuckDb is a tool to run SQL statements on our dataframe. Note the '.show()' at the end of the line. That tells the system to 'show'  the result and print same to the terminal. We'll used different output functions later on. So let's give it another try. We want to query all **Childs** that reside in, say, the Netherlands. How we go about that?

We could simply do this:

```python
chart = pd.read_excel('tree.xlsx')
results = duckdb.sql("SELECT * from chart WHERE CHILD_COUNTRY = 'Netherlands").show()
```
and we indeed would just get back to the Dutch legal entities:

```console
┌──────────┬──────────────────┬───────────────┬──────────┬───────────┐
│ CHILD_ID │    CHILD_NAME    │ CHILD_COUNTRY │ OWNER_ID │ OWNERSHIP │
│ varchar  │     varchar      │    varchar    │ varchar  │  double   │
├──────────┼──────────────────┼───────────────┼──────────┼───────────┤
│ A0002    │ Charts EMEA B.V. │ Netherlands   │ A0001    │       1.0 │
│ X0099    │ Charts IP B.V.   │ Netherlands   │ A0002    │       1.0 │
└──────────┴──────────────────┴───────────────┴──────────┴───────────┘
```
But this is anathema. Our final piece of code needs to be able to find all Childs in low taxed jurisdictions, which we'll provide to the code as a list of country names. Hardtyping it defeats the purpose of automation. So, we'll tweak the code as follows. Same result, for now, but loopable:

```python
chart = pd.read_excel('tree.xlsx')
low_taxed_jurisdiction = 'Ireland'
results = duckdb.sql(f"""SELECT * from chart WHERE CHILD_COUNTRY = '{low_taxed_jurisdiction}' """).show()
```
The changes in the last line are as follows. The WHERE CHILD_COUNTRY is a selector in the sql statement that tells the interpreter to take all values from all columns and all rows, but only where the value for the Child_Country column is equal to the variable that we labelled 'low_taxed_jurisdiction'. We create that variable in line 2 ("Ireland") and insert that using the parenthesis in line 3. Note the single quotes that go before and after the curly braces -- they are essential, just like the triple quotes """ before and after the statement. The 'f' before the first triple quote tells Python to expect a variable later on in the statement, that needs to be parsed. 

So what's in Ireland?
```console
┌──────────┬──────────────────────────┬───────────────┬──────────┬───────────┐
│ CHILD_ID │        CHILD_NAME        │ CHILD_COUNTRY │ OWNER_ID │ OWNERSHIP │
│ varchar  │         varchar          │    varchar    │ varchar  │  double   │
├──────────┼──────────────────────────┼───────────────┼──────────┼───────────┤
│ Z0001    │ EMEA Distributor Ltd     │ Ireland       │ A0002    │       1.0 │
│ B0004    │ Dublin Employment Co Ltd │ Ireland       │ Z0001    │       1.0 │
└──────────┴──────────────────────────┴───────────────┴──────────┴───────────┘
```
With the basic concept laid down, let's have a look how we can 'loop' through the dataframe. Let's say we know from the CbCr Safe Harbor exercise we have four low taxed jurisdictions to care for - Singapore, Ireland, Thailand and Cambodia. How to find the **CHILD_IDs** for those countries, only? Introducing the ~~hi hat~~ loop. As follows:
```python
chart = pd.read_excel('tree.xlsx')
low_taxed_jurisdictions = ['Ireland', 'Singapore', 'Thailand', 'Cambodia']

for country in low_taxed_jurisdictions:
    results = duckdb.sql(f"""SELECT * from chart WHERE CHILD_COUNTRY = '{country}' """).show()
```
Run the code and experience the joy and wonder of the code repeating the sql statement for each country mentioned in the variable 'low_taxed_jurisdictions' and printing four tables! What's happening here? First, we create a 'list' -- that's is the 'low_taxed_jurisdictions' item. Lists in Python are created by putting items between [square brackets]. In the list, we have the 4 country names. Then we create a 'for' loop where we tell Python to run the results query for every item in the list. The reference to 'country' in the for loop could be anything, but it is good practice to have something meaningful. 

Now, showing off with looped printing of table to the terminal is pretty cool but not very useful. Remember we are on a quest to find the paths from TopCo to each of the **CHILD_IDs** we are now able to find. How to take this further? Next step -- figure out how to consolidate these 4 tables into one. As is common is Python, there's a few ways to do this. The 'best' way, going by Stack Overflow, is to expand our SQL query with an 'IN' statement. That however requires some code wrenching which I want to avoid. So here's my plan B instead -- we'll have the loop create the 4 dataframes, we then stack the 4 frames together, and merge them into 1 big happy frame. As follows:
```python
chart = pd.read_excel('tree.xlsx')
low_taxed_jurisdictions = ['Ireland', 'Singapore', 'Thailand', 'Cambodia']

temporary_holding_list = []

for country in low_taxed_jurisdictions:
    results = duckdb.sql(f"""SELECT * from chart WHERE CHILD_COUNTRY = '{country}' """).df()
    temporary_holding_list.append(results)

output = pd.concat(temporary_holding_list)
print(output)
```
What's happening here? First, we create an new list, 'temporary_holding_list', which for now is empty. We then run our loop, same as prior. Note however that we have replaced the outputter and the end of line from .show() to .df() - this tells duckdb to not show the query on screen, but instead convert it in memory to a pandas dataframe. In the next line, we append that newly created dataframe called 'results' to the list 'temporary_holding_list'. Because we have 4 low taxed countries, the loop does this sequence 4 times. So, at the end of the loop, the 'temporary_holding_list'  contains 4 dataframes as 4 separate items. Then, we create a new dataframe 'output' which is the concatenation of the four separate ones -- we use the pandas function 'concat' for that. We finalize by printing the final result 'output' to the terminal as a dataframe. And we get:

```console
  CHILD_ID                CHILD_NAME CHILD_COUNTRY OWNER_ID  OWNERSHIP
0    Z0001      EMEA Distributor Ltd       Ireland    A0002       1.00
1    B0004  Dublin Employment Co Ltd       Ireland    Z0001       1.00
0    Y0001    Charts PanAsia Pty Ltd     Singapore    A0002       1.00
0    D0006       Bangkok Home Office      Thailand    Y0001       0.51
1    D0008       Phi Phi Beach Shack      Thailand    Y0001       0.51
2    D0009            Lanta Cook Ops      Thailand    Y0001       0.51
0    D0007         Angkor Snack Shop      Cambodia    Y0001       0.49
```
So there you have it -- all low taxed jurisdictions, in one dataframe. Next -- are all **Child_IDs** in the low taxed countries Constituent Entities? We'd need more info, but let's just assume for now that the snack shop @ Angkor Wat in Siem Reap is not a consolidated subsidiary because of the ownership. How to filter for this? There's two easy routes and I'll explain both. 

**First** we can simply use the pandas API to filter the values. That looks as follows:
```python
chart = pd.read_excel('tree.xlsx')
low_taxed_jurisdictions = ['Ireland', 'Singapore', 'Thailand', 'Cambodia']

temporary_holding_list = []

for country in low_taxed_jurisdictions:
    results = duckdb.sql(f"""SELECT * from chart WHERE CHILD_COUNTRY = '{country}' """).df()
    temporary_holding_list.append(results)

output = pd.concat(temporary_holding_list)
output_ce_only = output.loc[output['OWNERSHIP'] > 0.5]

print(output_ce_only)
```
The sole change here is the new dataframe 'output_ce_only'. We create a new dataframe with this name by selecting from the dataframe 'output' just those rows for which the value in the column 'OWNERSHIP' is larger than 50%. If we print it, we get the same table as before but now without the Angkor Snack Shop.

**Alternatively** we use the DuckDB filter option. That works as follows:
```python
output = pd.concat(temporary_holding_list)
results = duckdb.sql("""SELECT * from output WHERE OWNERSHIP > 0.5 """).show()
```
This of course is slightly odd -- we throw the dataframe back into DuckDb to slice the query. With hindsight, perhaps we should have amended the original query and just eliminate any <50% ownership positions to begin with? It all depends on your data. Ideally, the original org tree we start with indicates for each **Child_ID** whether it is part of the consolidated financials. If not, and ownership less than 50% (so we escape the JV rules) we could indeed filter out early on. The above gives you options to design your own workflow.

## Walk the Chart

With our CHILD_IDs in the low taxed jurisdictions in one single dataframe, we can now turn to figuring out how to trace the path from the CHILD_ID to the ultimate parent. Recall that with that path in hand, we can then identify intermediaries that may apply an Income Inclusion Rule. 

We begin with loading the entire org tree as a dataframe, so:
```python
chart = pd.read_excel('tree.xlsx')
results = duckdb.sql("SELECT * from chart").df()
```
Next, we define the Python function 'get_owners' which we denote with the 'def' reference and that takes a 'child_id' as an argument. We then use a lengthy SQL statement to first, find us the child_id in the org_chart dataframe 'results'  that we pass it and get us the Child_Name, Child_Country, Owner_ID and Ownership (i.e. the column header of the dataframe 'results' in which we loaded the org tree) for that Child_ID. Next, we run a second query, where we look for the same column values for the Owner_ID of the Child_ID that we started with. This keeps running until we are done -- i.e. until we are the top of the org chart.

```python
def get_owners(child_id):
 
    # recursive sql statement to get, recursive, all LEs above 'child_id'
    recursive_sql = f"""
                        WITH RECURSIVE org_chart AS (
                        SELECT CHILD_ID, CHILD_NAME, CHILD_COUNTRY, OWNER_ID, OWNERSHIP, 0 AS level
                        FROM results
                        WHERE CHILD_ID = '{child_id}'
 
                        UNION ALL
 
                        SELECT r.CHILD_ID, r.CHILD_NAME, r.CHILD_COUNTRY, r.OWNER_ID, r.OWNERSHIP, level + 1
                        FROM results r, org_chart oc
                        WHERE r.CHILD_ID = oc.OWNER_ID
                        )
 
                        SELECT * FROM org_chart
                       
                        """
       
    query = duckdb.sql(recursive_sql).show()
 
    return query
```
You'll find a better explanation here https://www.mssqltips.com/sqlservertip/1520/recursive-queries-using-common-table-expressions-cte-in-sql-server/ and elsewhere on the web.

Now that we have our function, let's run it. Simple type the function name, get_owners, and pass it a parameter -- here, I am using the **Child_Id** of Lanta Cook Ops, our Thai cooking holiday experience business. Run it.
```python
get_owners('D0009')
```
This will print in the terminal:
```console
┌──────────┬────────────────────────┬───────────────┬──────────┬───────────┬───────┐
│ CHILD_ID │       CHILD_NAME       │ CHILD_COUNTRY │ OWNER_ID │ OWNERSHIP │ level │
│ varchar  │        varchar         │    varchar    │ varchar  │  double   │ int32 │
├──────────┼────────────────────────┼───────────────┼──────────┼───────────┼───────┤
│ D0009    │ Lanta Cook Ops         │ Thailand      │ Y0001    │      0.51 │     0 │
│ Y0001    │ Charts PanAsia Pty Ltd │ Singapore     │ A0002    │       1.0 │     1 │
│ A0002    │ Charts EMEA B.V.       │ Netherlands   │ A0001    │       1.0 │     2 │
│ A0001    │ Chart, Inc.            │ United States │ NASDAQ   │      NULL │     3 │
└──────────┴────────────────────────┴───────────────┴──────────┴───────────┴───────┘
```
That is the full path of ownership from D0009 up, tier for tier, to our TopCo, A0001.

## Next bits

If in popular demand, I'll walk through a few more steps to produce 'org chart walks' for every legal entity in a low taxed jurisdiction -- and export it all to an Excel file for further handling. 

## License

Copyright 2024 A.C. van der Linde

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.