import requests
import json

headers = {"Content-Type": "application/json"}
data = {
    "sub_folder_path": "employment_contracts",
    "filename": "ArbeitsvertragZÄAssistentin.pdf",
}
url = "http://localhost:5001/v1/process_contract"

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.text)
