import requests
import json
import time
import pandas as pd

import sys

sys.path.append("../")

# My Modules
from data.FileReader import FileReader

headers = {"Content-Type": "application/json"}
url = "http://localhost:5001/v1/process_contract"

# Get list of filenames
data_folder = "/home/ec2-user/project/data"
contract_folder = "employment_contracts"
filereader = FileReader(data_folder)
contract_filenames = filereader.get_all_filenames(contract_folder)

result = []
for contract_filename in contract_filenames:
    data = {"sub_folder_path": contract_folder, "filename": contract_filename}
    # Make the POST request
    start_time = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(data))
    end_time = time.time()
    elapsed_time = end_time - start_time
    result.append(
        {
            "contract_filename": contract_filename,
            "elapsed_time": elapsed_time,
            "response": response.text,
        }
    )

pd.DataFrame(result).to_csv("output/performance_test.csv")
