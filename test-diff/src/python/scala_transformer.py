# scala_transformer.py

import pandas as pd
import numpy as np
import sys
import os
import json
import math

def scala_transfomer_fy(build_number):
    """
    This function constructs the table with the scala test data taken from the extraction an concatinates it with the table constrcted by the java_test_transfomer. It then returns the table in json format with all extracted information.
    """
    try:
        # If there are scalatests the following file should exist
        if os.path.exists('scala-end-results.txt'):

            # Read the output from the java transformer
            with open(f'results-{build_number}.json', 'r') as json_file:
                json_data = json.load(json_file)
            # Convert the dictionary into a DataFrame
            # Create a list called record
            records = []
            # Loop through each element of the json file
            for test_group, values in json_data.items():
                # If the list of failed test is not empty
                if len(values['failed_list']) > 0:
                    # For each element in the failed_list list
                    for failed_test in values['failed_list']:
                        # Get the class Test_group and define it as key for value test_group which is the main element of the schema
                        record = {'test_group': test_group}
                        # Get the attribute values
                        record.update(values['test_stats'])
                        # Get the list of failed tests
                        record['failed_list'] = failed_test
                        # Append all these elements to the list records
                        records.append(record)
                else:
                    record = {'test_group': test_group}
                    # Get the attribute values
                    record.update(values['test_stats'])
                    # Put the value of failed_list to None
                    record['failed_list'] = None
                    # Append all these elements to the list records
                    records.append(record)

            # Define the dataframe
            df = pd.DataFrame(records)

            # Read the scala-end-results.txt file if it has some input in it
            if os.path.getsize('scala-end-results.txt') > 1:
                # Read the scala-end-results.txt file
                df1 = pd.read_csv('scala-end-results.txt', header=None, sep='.txt:', engine='python')
                # Give column names
                df1.columns = ['test_group','Results']
                # Iliminate the path to SparkTestSuite file and keep only the module name 
                df1['test_group'] = df1['test_group'].str.replace("/target/surefire-reports/SparkTestSuite","")
                # Iliminate all strings in Results column
                df1['Results'] = df1['Results'].str.replace("Tests: succeeded","").str.replace("failed","").str.replace("canceled","").str.replace("ignored","").str.replace("pending","")
                # Split the Results column into sevral columns
                splitted_columns = df1['Results'].str.split(',', expand=True)
                # Give column names
                splitted_columns.columns = ['succeeded', 'failed', 'canceled', 'ignored', 'pending']
                # Transform string to integers
                splitted_columns = splitted_columns.astype(int)
                # Concatinate new df
                df1 = pd.concat([df1, splitted_columns], axis = 1).drop(columns = ['Results'])
                # Join the columns canceled and ignored in one signle coulumn
                df1['skipped'] = df1['canceled'] + df1['ignored']
                # Drop the columns which are not needed anymore
                df1 = df1.drop(columns = ['canceled', 'ignored'])
                # Reorder the columns
                df1 = df1[['test_group', 'succeeded', 'failed', 'skipped', 'pending']]
            else:
                # Exit since no test has run
                columns = ['test_group', 'succeeded', 'failed', 'skipped', 'pending']
                df1 = pd.DataFrame(columns = columns)
                print("No module has run")

            # Read the aborted-tests.txt file if it has some input in it
            if os.path.getsize('aborted-tests.txt') > 1:
                df2 = pd.read_csv('aborted-tests.txt', header=None, sep='.txt:', engine='python')
                # Give column names
                df2.columns = ['test_group','aborted']
                # Iliminate the path to SparkTestSuite file and keep only the module name 
                df2['test_group'] = df2['test_group'].str.replace("/target/surefire-reports/SparkTestSuite","")
                # Merge df1 and df2
                df1 = pd.concat([df1, df2] , ignore_index = True)
            else:
                # Give the dataframe the column aborted with empty values
                df1["aborted"] = False
                print("No aborted tests")

            # Read the scala-tests.txt file if it has some input in it
            if os.path.getsize('scala-tests.txt') > 1:
                df3 = pd.read_csv('scala-tests.txt', header = None, sep ='.txt:', engine ='python')
                # Give column names
                df3.columns = ['test_group','failed_list']
                # Iliminate the path to SparkTestSuite file and keep only the module name 
                df3['test_group'] = df3['test_group'].str.replace("/target/surefire-reports/SparkTestSuite","")
                # Merge new df1 and df3
                df1 = pd.merge(df1, df3, how='outer')
            else:
                # Give the dataframe the column failed_list with empty colmun
                df1["failed_list"] = None
                print("No scala test errors")

            # Concatinate dataframe from the java tests with df1
            df = pd.concat([df, df1] , ignore_index=True)

            # For Python >= 3.9 
            # Replace all NaN None in the dataframe
            #df.replace(np.nan, None, inplace=True)
            # Make sure aborted column is of type boolean after the merge
            #df['aborted'] = df['aborted'].astype(bool)

            # For Python == 3.6
            # Replace all NaN None in the dataframe
            df = df.where(pd.notna(df), None)
            # Make sure aborted column is of type boolean after the merge
            df['aborted'] = df['aborted'].apply(lambda x: True if x=="*** RUN ABORTED ***" else False)
            
            # Create a dictionnary
            nested_dict = {}
            # Go through each row
            for _, row in df.iterrows():
                # Define the test_group which will be a class
                test_group = row['test_group']
                # If the test_group is not already in the dictionnary add it to it with its attributes and the list of failed tests
                if test_group not in nested_dict:
                    nested_dict[test_group] = {
                        'test_stats': {
                            'succeeded': row['succeeded'],
                            'failed': row['failed'],
                            'skipped': row['skipped'],
                            'pending': row['pending'],
                            'aborted' : row['aborted']
                        },
                        'failed_list': []
                    }
                # Append the test_group element comprising the attributes to the dictionnary as well as the failed tests
                if row['failed_list'] is not None:
                    nested_dict[test_group]['failed_list'].append(row['failed_list'])


            # Write the nested dictionary to a JSON file
            with open(f'results-{build_number}.json', 'w') as json_file:
                json.dump(nested_dict, json_file, indent=2)

            print("Scala data transfromation succeeded")

        else:
            print("No scala tests")
        
    except Exception as error:
        print("Scala data transformation failed:", error)
        sys.exit(1)