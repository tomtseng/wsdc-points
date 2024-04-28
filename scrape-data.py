# Sends POST request to https://points.worldsdc.com/lookup2020/find
# with data "num: 23137" and prints the response.

import json
import pickle

import requests
from tqdm import tqdm

url = "https://points.worldsdc.com/lookup2020/find"

try:
    responses = pickle.load(open("data.pkl", "rb"))
except FileNotFoundError:
    responses = []
last_id = responses[-1]["dancer_wsdcid"] if len(responses) > 0 else 0
print(last_id)
# Max ID is 23454 as of 4/28/2024, which I found by trial and error on the WSDC
# website.
for i in tqdm(range(last_id, 23455)):
    data = {"num": i}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        responses.append(json.loads(response.text))
    # Periodically save the responses just in case things break or I get
    # rate-limited.
    if i % 100 == 0:
        pickle.dump(responses, open("data.pkl", "wb"))
pickle.dump(responses, open("data.pkl", "wb"))
