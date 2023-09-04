# main.py

import pandas as pd
import sys
from java_test_transformation import *
from scala_transformer import *


def comparison_producer(build_number, comparison_run):
    """
    This function compares the json file taken from the transformer functions with an external one by doing a diff on the tables and only showing if new Test failures or aborted test groups appear.
    """
    try:

        # Read the output from the transformer functions
        with open(f'results-{build_number}.json', 'r') as json_file:
            json_data = json.load(json_file)

        # Convert the dictionary into a DataFrame
        # Create a list called record
        records = []
        # Loop through each element of the json file
        for test_group, values in json_data.items():
            # If the list of failed test is not empty
            if len(values['failed_list']) > 0:
                # For each element in the failed_test list
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
                # Put the value of failed_test to None
                record['failed_list'] = None
                # Append all these elements to the list records
                records.append(record)

        # Define the dataframe
        df = pd.DataFrame(records)


        # Drop columns that we do not compare
        df.drop(columns= ['succeeded', 'failed', 'skipped', 'pending'], inplace=True)
        # Chenge the column type Aborted_tests to "object"
        #df['aborted'] = df['aborted'].astype('object')
        df['aborted'] = df['aborted'].map({True: "Module aborted", False: None})

        #df[df_external['aborted'] == False] = "Aborted Run"
        print(df)

        # Load the external dataframe which we want to compare
        # If We do not give a comparison run, we compare it with the same dataset which will not give any difference
        if comparison_run == "0":
            df_external = df
        # Otherwise we compare it with the dataset we give for comparison
        else:
            # Read the JSON data as a dictionary
            with open(f'{comparison_run}', 'r') as json_file:
                json_data = json.load(json_file)
            
            # Convert the dictionary into a DataFrame
            # Create a list called record
            records = []
            # Loop through each element of the json file
            for test_group, values in json_data.items():
                # If the list of failed test is not empty
                if len(values['failed_list']) > 0:
                    # For each element in the failed_test list
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
                    # Put the value of failed_test to None
                    record['failed_list'] = None
                    # Append all these elements to the list records
                    records.append(record)

        # Define the dataframe
        df_external = pd.DataFrame(records)
        # Drop columns that we do not compare
        df_external.drop(columns= ['succeeded', 'failed', 'skipped', 'pending'], inplace=True)
        # Chenge the column type Aborted_tests to "object"
        #df_external['aborted'] = df_external['aborted'].astype('object')
        df_external['aborted'] = df_external['aborted'].map({True: "Module aborted", False: None})

        print(df_external)

        # Merge ancient and new tables
        df = df.merge(df_external, how='left', indicator=True)
        # Checks if there is an aborted test or a test error in the new table
        df_comparison = df[((df['_merge'] == 'left_only') & pd.notna(df['aborted'])) | ((df['_merge'] == 'left_only') & pd.notna(df['failed_list']))]
        print("Comparison succeeded")
        print(df_comparison)
        # Produce csv file for comparison and entire dataframe taht we will need later on for the decision making. These are the required outputs of the function.
        return df_comparison.to_csv('comparison.csv', header=False)
        
    except Exception as error:
        print("Comparison failed:", error)
        sys.exit(1)


if __name__ == "__main__":
    # Set surefire version
    surefire_version = sys.argv[1]
    # The build number is the 1st argument after the filename
    build_number = sys.argv[2]
    # If we give a filename as 3rd argument, comparison will be that filename
    if len(sys.argv) == 4:
        comparison_run = sys.argv[3]
    # Otherwise the variable comparison-run will be empty
    else:
        comparison_run = "0"
    # Run the following functions
    java_test_transfomer(surefire_version, build_number)
    scala_transfomer_fy(build_number)
    comparison_producer(build_number, comparison_run)