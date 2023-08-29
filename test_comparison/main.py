# main.py

import pandas as pd
import sys
from scala_transformer import *
from java_test_transformation import *


def comparison_producer(build_number, comparison_run):
    """
    This function compares the json file taken from the transformer functions with an external one by doing a diff on the tables and only showing if new Test failures or aborted test groups appear.
    """
    try:

        # Read the output from the transformer functions
        with open(f'results-{build_number}.json', 'r') as json_file:
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
        # Drop columns that we do not compare
        df.drop(columns= ['Succeeded', 'Failed', 'Skipped', 'Pending'], inplace=True)
        # Chenge the column type Aborted_tests to "object"
        df['Aborted_tests'] = df['Aborted_tests'].astype('object')
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
        df_external = pd.DataFrame(records)
        # Drop columns that we do not compare
        df_external.drop(columns= ['Succeeded', 'Failed', 'Skipped', 'Pending'], inplace=True)
        # Chenge the column type Aborted_tests to "object"
        df_external['Aborted_tests'] = df_external['Aborted_tests'].astype('object')
        print(df_external)
        # Merge ancient and new tables
        df = df.merge(df_external, how='left', indicator=True)
        # Checks if there is an aborted test or a test error in the new table
        df_comparison = df[((df['_merge'] == 'left_only') & pd.notna(df['Aborted_tests'])) | ((df['_merge'] == 'left_only') & pd.notna(df['Failed_test']))]
        print("Comparison succeeded")
        print(df_comparison)
        # Produce csv file for comparison and entire dataframe taht we will need later on for the decision making. These are the required outputs of the function.
        return df_comparison.to_csv('comparison.csv', header=False)
            
    except:
        print("Comparison failed")
        sys.exit(1)


if __name__ == "__main__":
    # The build number is the 1st argument after the filename
    build_number = sys.argv[1]
    # If we give a filename as 3rd argument, comparison will be that filename
    if len(sys.argv) == 3:
        comparison_run = sys.argv[2]
    # Otherwise the variable comparison-run will be empty
    else:
        comparison_run = "0"
    # Run the following functions
    java_test_transfomer(build_number)
    scala_transfomer_fy(build_number)
    comparison_producer(build_number, comparison_run)