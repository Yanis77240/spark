# java_test_transformation.py

import pandas as pd
import numpy as np
import sys
import os
import json



def java_test_transfomer(surefire_version, build_number):
    """
    This function constructs the table with the java test data taken from the extraction. It then returns the table in json format with all extracted information.
    """
    try:
        # Read output-tests.csv file as dataframe
        df = pd.read_csv('output-tests.csv')

        # If Surefire version output display is like 2.20
        if surefire_version=="2.20":
            print("Surefire plugin displays output as version 2.20")
        
            # Give column names
            df.columns = ['Tests_run', 'Failures', 'Errors', 'Skipped', 'test_group']
            # Erase all unnecessary characters in each column and transform them into type int64
            df['Tests_run'] = df['Tests_run'].str.split(':', n=1).str[1].astype('int')
            df['Failures'] = df['Failures'].str.split(':', n=1).str[1].astype('int')
            df['Errors'] = df['Errors'].str.split(':', n=1).str[1].astype('int')
            df['Skipped'] = df['Skipped'].str.split(':', n=1).str[1].astype('int')
            df['test_group'] = df['test_group'].str.split('-', n=1).str[1].str.replace(' in ','')
            # delete lines where no testname is given which corresponds to the total columns
            df = df.dropna(subset=['test_group'])
            # Add empty columns below to be compatible with schema
            df['Pending'] = [None] * len(df)
            df['Aborted_tests'] = [False] * len(df)
            df['Failed']= df['Failures'] + df['Errors']
            # Succeeded is the nuber of test runs minus failed and skipped test
            df['Succeeded'] = df['Tests_run'] - df['Failed'] - df['Skipped']
            # Select and reorder the columns
            df= df[['test_group', 'Succeeded', 'Failed', 'Skipped', 'Pending', 'Aborted_tests']]

            # Read the java-test-failures.txt file if it has some input in it
            if os.path.getsize('java-test-failures.txt') > 1:
                # Read java-test-failures.txt file as dataframe
                df2 = pd.read_csv('java-test-failures.txt', header = None, delimiter='/t', engine='python')
                # Name the single column Tests
                df2.columns = ['Tests']
                # Extract the Testclass
                df2['test_group'] = df2['Tests'].str.extract(r"\[ERROR\] .*?\(([^()]+)\) *Time elapsed:", expand=True)
                # Extract the Testname
                df2['Failed_test'] = df2['Tests'].str.extract(r'\[ERROR\] (.+?)\(')
                # Drop column test
                df2.drop(columns=['Tests'], inplace= True)
                # Reorder columns
                df2= df2[['test_group', 'Failed_test']]
                # Merge the 2 dataframes on their common column test_group
                df = pd.merge(df, df2, on = 'test_group', how='outer')
            else:
                # Create the column Failed_test with empty values
                df['Failed_test'] = None
                print("No java failed tests")

        # If Surefire version output display is like 3.0.0M
        elif surefire_version=="3.0.0":
            print("Surefire plugin displays output as version 3.0.0M")
            
            # Give column names
            df.columns = ['Tests_run', 'Failures', 'Errors', 'Skipped', 'test_group']
            # Erase all unnecessary characters in each column and transform them into type int64
            df['Tests_run'] = df['Tests_run'].str.split(':', n=1).str[1].astype('int')
            df['Failures'] = df['Failures'].str.split(':', n=1).str[1].astype('int')
            df['Errors'] = df['Errors'].str.split(':', n=1).str[1].astype('int')
            df['Skipped'] = df['Skipped'].str.split(':', n=1).str[1].astype('int')
            df['test_group'] = df['test_group'].str.split('-', n=1).str[1].str.replace(' in ','')
            # delete lines where no testname is given which corresponds to the total columns
            df = df.dropna(subset=['test_group'])
            # Add empty columns below to be compatible with schema
            df['Pending'] = [None] * len(df)
            df['Aborted_tests'] = [False] * len(df)
            df['Failed']= df['Failures'] + df['Errors']
            # Succeeded is the nuber of test runs minus failed and skipped test
            df['Succeeded'] = df['Tests_run'] - df['Failed'] - df['Skipped']
            # Select and reorder the columns
            df= df[['test_group', 'Succeeded', 'Failed', 'Skipped', 'Pending', 'Aborted_tests']]
            
            # Read the java-test-failures.txt file if it has some input in it
            if os.path.getsize('java-test-failures.txt') > 1:
                # Read java-test-failures.txt file as dataframe
                df2 = pd.read_csv('java-test-failures.txt', header = None, delimiter='/t', engine='python')
                # Name the single column Tests
                df2.columns = ['Tests']
                # Extract the testname with testclass
                df2["Tests"]=df2["Tests"].str.extract(r'\[ERROR\] (\S+)\s+Time elapsed')
                # Split the Tests column into test_group and Failed_test
                df2[['test_group', 'Failed_test']] = df2['Tests'].str.rsplit('.', 1, expand=True)
                # Drop column Tests
                df2.drop(columns=["Tests"], inplace=True)
                # Merge the 2 dataframes on their common column test_group
                df = pd.merge(df, df2, on = 'test_group', how='outer')
            else:
                # Create the column Failed_test with empty values
                df['Failed_test'] = None
                print("No java failed tests")

        # If Surefire version output display is like 2.14
        elif surefire_version=="2.14":
            print("Surefire plugin displays output as version 2.14")

            # Give column names
            df.columns = ['Tests_run', 'Failures', 'Errors', 'Skipped', 'test_group']
            # Erase all unnecessary characters in each column and transform them into type integer
            df['Tests_run'] = df['Tests_run'].str.split(':', n=1).str[1].astype('int')
            df['Failures'] = df['Failures'].str.split(':', n=1).str[1].astype('int')
            df['Errors'] = df['Errors'].str.split(':', n=1).str[1].astype('int')
            df['Skipped'] = df['Skipped'].str.split(':', n=1).str[1].astype('int')
            df['test_group'] = df['test_group'].str.split('Running', n=1).str[1].str.replace(' ','')
            # delete lines where no testname is given which corresponds to the total columns
            df = df.dropna(subset=['test_group'])
            # Add empty columns below to be compatible with schema
            df['Pending'] = [None] * len(df)
            df['Aborted_tests'] = [False] * len(df)
            df['Failed']= df['Failures'] + df['Errors']
            # Succeeded is the nuber of test runs minus failed and skipped test
            df['Succeeded'] = df['Tests_run'] - df['Failed'] - df['Skipped']
            # Select and reorder the columns
            df= df[['test_group', 'Succeeded', 'Failed', 'Skipped', 'Pending', 'Aborted_tests']]

            # Read the java-test-failures.txt file if it has some input in it
            if os.path.getsize('java-test-failures.txt') > 1:
                # Read java-test-failures.txt file as dataframe
                df2 = pd.read_csv('java-test-failures.txt', header = None, delimiter='/t', engine='python')
                # Name the single column Tests
                df2.columns = ['Tests']
                # Extract the test_group from the Tests column
                df2['test_group'] = df2['Tests'].str.extract("\((.*\..*)\) *Time elapsed:", expand=True)
                # Extract the Failed Test by spliting the column tests
                df2[['Failed_test', 'unnecsessary']] = df2['Tests'].str.split('(', n=1, expand= True)
                # Remove evrything after the parnetheses
                #df2.drop(columns=['unnecsessary'], inplace= True)
                df2.drop(columns=['unnecsessary', 'Tests'], inplace= True)
                # Reorder columns
                df2= df2[['test_group', 'Failed_test']]
                # Merge the 2 dataframes on their common column test_group
                df = pd.merge(df, df2, on = 'test_group', how='outer')
            else:
                # Create the column Failed_test with empty values
                df['Failed_test'] = None
                print("No java failed tests")
        
        else:
            print("Maven surefire version type for output display unknown")
            sys.exit(1)

        # There shouldn't be any duplicates but if there are we should drop them
        df = df.drop_duplicates()
        # Replace all NaN with None in the dataframe
        df.replace(np.nan, None, inplace=True)

        # Convert DataFrame to a nested dictionary
        # Create a dictionnary
        nested_dict = {}
        # Go through each row
        for _, row in df.iterrows():
            # Define the Test_group which will be a class
            test_group = row['test_group']
            # If the test_group is not already in the dictionnary add it to it with its attributes and the list of failed tests
            if test_group not in nested_dict:
                nested_dict[test_group] = {
                    'test_stats': {
                        'succeeded': row['Succeeded'],
                        'failed': row['Failed'],
                        'skipped': row['Skipped'],
                        'pending': row['Pending'],
                        'aborted' : row['Aborted_tests']
                    },
                    'failed_list': []
                }
            # Append the test_group element comprising the attributes to the dictionnary as well as the failed tests
            if row['Failed_test'] is not None:
                nested_dict[test_group]['failed_list'].append(row['Failed_test'])

        # Write the nested dictionary to a JSON file
        with open(f'results-{build_number}.json', 'w') as json_file:
            json.dump(nested_dict, json_file, indent=2)
        
        print("Java data transformation succeeded")

    except Exception as error:
        print("Java data transformation failed:", error)
        sys.exit(1)
