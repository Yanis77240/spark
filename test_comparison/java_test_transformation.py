# java_test_transformation.py

import pandas as pd
import sys
import os
import json



def java_test_transfomer(build_number):
    """
    This function constructs the table with the java test data taken from the extraction. It then returns the table in json format with all extracted information.
    """
    #try:
    # read output-tests.csv file as dataframe
    df = pd.read_csv('output-tests.csv')
    print(df)
    # Give column names
    df.columns = ['Tests_run', 'Failures', 'Errors', 'Skipped', 'Test_group']
    # Erase all unnecessary characters in each column and transform them into type int64
    df['Tests_run'] = df['Tests_run'].str.split(':', n=1).str[1]
    df['Failures'] = df['Failures'].str.split(':', n=1).str[1].astype('int64')
    df['Errors'] = df['Errors'].str.split(':', n=1).str[1].astype('int64')
    df['Skipped'] = df['Skipped'].str.split(':', n=1).str[1].astype('int64')
    df['Test_group'] = df['Test_group'].str.split('-', n=1).str[1].str.replace('in','')
    # delete lines where no testname is given which corresponds to the total columns
    df = df.dropna(subset=['Test_group'])
    # Add empty columns below to be compatible with schema
    df['Pending'] = [None] * len(df)
    df['Aborted_tests'] = [None] * len(df)
    df['Failed']= df['Failures'] + df['Errors']
    # Succeeded is the nuber of test runs minus failed and skipped test
    df['Succeeded'] = df['Tests_run'] - df['Failed'] - df['Skipped']
    # Select and reorder the columns
    df= df[['Test_group', 'Succeeded', 'Failed', 'Skipped', 'Pending', 'Aborted_tests']]

    # Read the java-test-failures.txt file if it has some input in it
    if os.path.getsize('java-test-failures.txt') > 1:
        # Read output-tests.csv file as dataframe
        df2 = pd.read_csv('java-test-failures.txt', header = None, delimiter='/t', engine='python')
        # Name the single column Tests
        df2.columns = ['Tests']
        # Split the columns into two coulumns named Failed_test and Test_group
        df2[['Failed_test', 'Test_group']] = df2['Tests'].str.split('(', n=1, expand= True)
        # Remove the column Tests
        df2.drop(columns=['Tests'], inplace= True)
        # Split the columns Test_group into two after the )
        df2[['Test_group', 'unnecsessary']] = df2['Test_group'].str.split(')', n=1, expand= True)
        # Remove evrything after the parnetheses
        df2.drop(columns=['unnecsessary'], inplace= True)
        # Reorder columns
        df2= df2[['Test_group', 'Failed_test']]
        df = pd.merge(df, df2, on = 'Test_group', how='outer')
    else:
        # Create the column Failed_test with empty values
        df['Failed_test'] = None
        print("No java failed tests")
    
    # There shouldn't be any duplicates but if there are we should drop them
    df = df.drop_duplicates()
    
    # Convert DataFrame to a nested dictionary
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
        # Append the test_group element comprising the attributes to the dictionnary as well as the failed tests
        nested_dict[test_group]['Failed_tests'].append(row['Failed_test'])

    # Write the nested dictionary to a JSON file
    with open('java-test.json', 'w') as json_file:
        json.dump(nested_dict, json_file, indent=2)
    
    print("Java data transformation succeeded")

    #except:
        #print("Java data transformation failed")
        #sys.exit(1)
