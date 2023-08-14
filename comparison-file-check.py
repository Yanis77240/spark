import pandas as pd
import sys


# define file


if len(sys.argv) == 2:
    # define file
    comparison_file = sys.argv[1]
    # Check if file is of a valid json and if it is the case load the dataframe
    try:
        dataframe = pd.read_json(comparison_file)
        print("json file is readable")
    except:
        print("file does not exist, is not of json format or incompatible with pandas json reader")
        sys.exit(1)

    # Check if the columns of the loaded dataframe matches the one used later on
    # The type of the columns can vary it will still work for the comparison.
    if dataframe.columns.tolist()==['Module', 'Succeeded', 'Failed', 'Canceled', 'Ignored', 'Pending', 'Aborted_tests', 'Test_name']:
        print("Compatible schema")
    else:
        print("Wrong schema")
        sys.exit(1)
    
else:
    print("no comparison needed")
    