# scala_transformer.py

import pandas as pd
import sys
import os
import json

def scala_transfomer_fy(build_number):
    """
    This function constructs the table with the scala test data taken from the extraction an concatinates it with the table constrcted by the java_test_transfomer. It then returns the table in json format with all extracted information.
    """
    try:
        # Read the output from the java transformer
        with open('java-test.json', 'r') as json_file:
            json_data = json.load(json_file)

        # Convert the nested dictionary into a DataFrame
        # Create a list called record
            records = []
            # Loop through each element of the json file
            for test_group, values in json_data.items():
                # For each element in the failed_test list
                for failed_test in values['Failed_tests']:
                    # Get the class Test_group and define it as key for value test_group which is the main element of the schema
                    record = {'Test_group': test_group}
                    # Get the attribute values
                    record.update(values['attributes'])
                    # Get the list of failed tests
                    record['Failed_test'] = failed_test
                    # Append all these elements to the list records
                    records.append(record)

        # Define the dataframe
        df = pd.DataFrame(records)

        # Read the scala-end-results.txt file if it has some input in it
        if os.path.getsize('scala-end-results.txt') > 1:
            # Read the scala-end-results.txt file
            df1 = pd.read_csv('scala-end-results.txt', header=None, sep='.txt:', engine='python')
            # Give column names
            df1.columns = ['Test_group','Results']
            # Iliminate the path to SparkTestSuite file and keep only the module name 
            df1['Test_group'] = df1['Test_group'].str.replace("/target/surefire-reports/SparkTestSuite","")
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
            # Join the columns Canceled and Ignored in one signle coulumn
            df1['Skipped'] = df1['Canceled'] + df1['Ignored']
            # Drop the columns which are not needed anymore
            df1 = df1.drop(columns = ['Canceled', 'Ignored'])
            # Reorder the columns
            df1 = df1[['Test_group', 'Succeeded', 'Failed', 'Skipped', 'Pending']]
        else:
            # Exit since no test has run
            columns = ['Test_group', 'Succeeded', 'Failed', 'Skipped', 'Pending']
            df1 = pd.DataFrame(columns = columns)
            print("No module has run")

        # Read the aborted-tests.txt file if it has some input in it
        if os.path.getsize('aborted-tests.txt') > 1:
            df2 = pd.read_csv('aborted-tests.txt', header=None, sep='.txt:', engine='python')
            # Give column names
            df2.columns = ['Test_group','Aborted_tests']
            # Iliminate the path to SparkTestSuite file and keep only the module name 
            df2['Test_group'] = df2['Test_group'].str.replace("/target/surefire-reports/SparkTestSuite","")
            # Merge df1 and df2
            df1 = pd.concat([df1, df2] , ignore_index=True)
        else:
            # Give the dataframe the column Aborted_tests with empty values
            df1["Aborted_tests"] = None
            print("No aborted tests")

        # Read the scala-tests.txt file if it has some input in it
        if os.path.getsize('scala-tests.txt') > 1:
            df3 = pd.read_csv('scala-tests.txt', header=None, sep='.txt:', engine='python')
            # Give column names
            df3.columns = ['Test_group','Failed_test']
            # Iliminate the path to SparkTestSuite file and keep only the module name 
            df3['Test_group'] = df3['Test_group'].str.replace("/target/surefire-reports/SparkTestSuite","")
            # Merge new df1 and df3
            df1 = pd.merge(df1, df3, how='outer')
        else:
            # Give the dataframe the column Failed_test with empty colmun
            df1["Failed_test"] = None
            print("No scala test errors")

        # Concatinate dataframe from the java tests with df1
        df = pd.concat([df, df1] , ignore_index=True)

        # Create a dictionnary
        nested_dict = {}
        # Go through each row
        for _, row in df.iterrows():
            # Define the Test_group which will be a class
            test_group = row['Test_group']
            # If the Test_group is not already in the dictionnary add it to it with its attributes and the list of failed tests
            if test_group not in nested_dict:
                nested_dict[test_group] = {
                    'attributes': {
                        'Succeeded': row['Succeeded'],
                        'Failed': row['Failed'],
                        'Skipped': row['Skipped'],
                        'Pending': row['Pending'],
                        'Aborted_tests' : row['Aborted_tests']
                    },
                    'Failed_tests': []
                }
            # Append individual failed tests
            nested_dict[test_group]['Failed_tests'].append(row['Failed_test'])

        # Write the nested dictionary to a JSON file
        with open(f'results-{build_number}.json', 'w') as json_file:
            json.dump(nested_dict, json_file, indent=2)
        
        #df.to_json(f'results-{build_number}.json', orient= "table")

        print("Scala data transfromation succeeded")

        # The output of this function is the total results file combined with one from the java test function transformer
        #return df4.to_json(f'results-{build_number}.json')

        
    except:
        print("Scala data transformation failed")
        sys.exit(1)