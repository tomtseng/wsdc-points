# Sends POST request to https://points.worldsdc.com/lookup2020/find
# with data "num: 23137" and prints the response.

import json
import pickle

import requests
from tqdm import tqdm

url = "https://points.worldsdc.com/lookup2020/find"

responses = []
# Max ID is 23454 as of 4/28/2024, which I found by trial and error
for i in tqdm(range(1, 23455)):
    data = {"num": i}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        responses.append(json.loads(response.text))
    # Periodically save the responses just in case things break or I get
    # rate-limited.
    if i % 100 == 0:
        pickle.dump(responses, open("data-partial.pkl", "wb"))
pickle.dump(responses, open("data.pkl", "wb"))
