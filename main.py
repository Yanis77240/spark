import numpy as np
import pandas as pd
import sys
import os


def comparison_producer(build_number, comparison_run):
    """
    This function constructs the table with th test data taken from the extraction and compares it with a table that the user has chosen. It then returns the table in json format with all extracted information and the comparison table showing the diff only on the new table if a new test or an aborted test has appeared in the run.
    """
    try:
        # Read the scala-end-results.txt file
        df1 = pd.read_csv('scala-end-results.txt', header=None, sep='.txt:', engine='python')
        # Give column names
        df1.columns = ['Module','Results']
        # Iliminate the path to SparkTestSuite file and keep only the module name 
        df1['Module'] = df1['Module'].str.replace("/target/surefire-reports/SparkTestSuite","")
        # Iliminate all strings in Results column
        df1['Results'] = df1['Results'].str.replace("Tests: succeeded","").str.replace("failed","").str.replace("canceled","").str.replace("ignored","").str.replace("pending","")
        # Split the Results column into sevral columns
        splitted_columns = df1['Results'].str.split(',', expand=True)
        # Give column names
        splitted_columns.columns = ['Succeeded', 'Failed', 'Canceled', 'Ignored', 'Pending']
        # Transform string to integers
        splitted_columns = splitted_columns.astype(int)
        # Concatinate new df
        df1 = pd.concat([df1, splitted_columns], axis = 1).drop(columns = ['Results'])

        # Read the aborted-tests.txt file if it has some input in it
        if os.path.getsize('aborted-tests.txt') > 1:
            df2 = pd.read_csv('aborted-tests.txt', header=None, sep='.txt:', engine='python')
            # Give column names
            df2.columns = ['Module','Aborted_tests']
            # Iliminate the path to SparkTestSuite file and keep only the module name 
            df2['Module'] = df2['Module'].str.replace("/target/surefire-reports/SparkTestSuite","")
            # Merge df1 and df2
            df1 = pd.merge(df1, df2, on = 'Module', how='outer')
        else:
            df1["Aborted_tests"] = None
            print("No aborted tests")

        # Read the scala-tests.txt file if it has some input in it
        if os.path.getsize('scala-tests.txt') > 1:
            df3 = pd.read_csv('scala-tests.txt', header=None, sep='.txt:', engine='python')
            # Give column names
            df3.columns = ['Module','Test_name']
            # Iliminate the path to SparkTestSuite file and keep only the module name 
            df3['Module'] = df3['Module'].str.replace("/target/surefire-reports/SparkTestSuite","")
            # Merge new df1 and df3
            df1 = pd.merge(df1, df3, on = 'Module', how='outer')
        else:
            df1["Test_name"] = None
            print("No test errors")

        # Load the external dataframe which we want to compare
        # If We do not give a comparison run, we compare it with the same dataset which will not give any difference
        if comparison_run == "0":
            df_external = df1
        # Otherwise we compare it with the dataset we give for comparison
        else:
            df_external = pd.read_json(f'{comparison_run}')

        # Drop the columns which can hinder the comparison
        df4 = df1.drop(columns=['Succeeded', 'Failed', 'Canceled', 'Ignored', 'Pending'])
        df_external = df_external.drop(columns=['Succeeded', 'Failed', 'Canceled', 'Ignored', 'Pending'])

        # Merge ancient and new tables
        df = df4.merge(df_external, how='left', indicator=True)
        # Checks if there is an aborted test or a test error in the new table
        df_comparison = df_comparison = df[((df['_merge'] == 'left_only') & pd.notna(df['Aborted_tests'])) | ((df['_merge'] == 'left_only') & pd.notna(df['Test_name']))]
        
        print("Data transformation succeeded")

        # Produce csv file for comparison and entire dataframe
        return df_comparison.to_csv('comparison.csv', header=False), df1.to_json(f'results-{build_number}.json')
        
    except:
        print("Data transformation failed")
        sys.exit(1)


if __name__ == "__main__":
    # The build number is the 1st argument after the filename
    build_number = sys.argv[1]
    # If we give a filename as 3rd argument, comparison will be that filename
    if len(sys.argv) == 3:
        comparison_run = sys.argv[2]
    # Otherwise the variable comparison-run will be empty
    else:
        comparison_run = None
    comparison_producer(build_number, comparison_run)