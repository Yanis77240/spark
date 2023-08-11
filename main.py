import pandas as pd
import sys


def comparison_producer(build_number, comparison_run) :

    # Read the scala-end-results.txt file
    df1 = pd.read_csv('scala-end-results.txt', header=None, sep='.txt:')
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

    # Read the scala-end-results.txt file
    df2 = pd.read_csv('aborted-tests.txt', header=None, sep='.txt:')
    # Give column names
    df2.columns = ['Module','Aborted_tests']
    # Iliminate the path to SparkTestSuite file and keep only the module name 
    df2['Module'] = df2['Module'].str.replace("/target/surefire-reports/SparkTestSuite","")

    # Merge df1 and df2
    df1 = pd.merge(df1, df2, on = 'Module', how='outer')

    # Read the scala-end-results.txt file
    df3 = pd.read_csv('scala-tests.txt', header=None, sep='.txt:')
    # Give column names
    df3.columns = ['Module','Test_name']
    # Iliminate the path to SparkTestSuite file and keep only the module name 
    df3['Module'] = df3['Module'].str.replace("/target/surefire-reports/SparkTestSuite","")

    # Merge new df1 and df3
    df1 = pd.merge(df1, df3, on = 'Module', how='outer')

    # Load the external dataframe which we want to compare
    df_external = pd.read_json(f'{comparison_run}')

    # Drop the columns which can hinder the comparison
    df4 = df1.drop(columns=['Succeeded', 'Failed', 'Canceled', 'Ignored', 'Pending'])
    df_external = df_external.drop(columns=['Succeeded', 'Failed', 'Canceled', 'Ignored', 'Pending'])

    # Merge ancient and new tables
    df = df1.merge(df_external, how='right', indicator=True)
    df_comparison = df[(df['_merge'] != 'both')]
    # Produce csv file for comparison
    df_comparison.to_csv('comparison.csv', header=False)
    # Produce json file for entire dataframe for this run
    df1.to_json(f'results-{build_number}.json')

    print("Data transformation succeeded")

if __name__ == "__main__":
    build_number = sys.argv[1]
    comparison_run= sys.argv[2]
    comparison_producer(build_number, comparison_run)