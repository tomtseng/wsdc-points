import json
import pickle

import requests
from tqdm import tqdm

# This URL and the data format were found by inspecting the network traffic when
# I manually searched for a dancer's points on the WSDC points registry.
url = "https://points.worldsdc.com/lookup2020/find"

try:
    responses = pickle.load(open("data.pkl", "rb"))
except FileNotFoundError:
    responses = []
last_id = responses[-1]["dancer_wsdcid"] if len(responses) > 0 else 0
# Max ID is 23454 as of 4/28/2024, which I found by manual trial and error,
# i.e., by typing numbers into the WSDC points registry until I consistently got
# no hits.
# This runs at a rate of 4–5 requests per second on my laptop, maybe can speed
# this up by firing multiple requests in parallel.
for i in tqdm(range(last_id, 23455)):
    data = {"num": i}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        responses.append(json.loads(response.text))
    # Periodically save the responses just in case.
    if i % 100 == 0:
        pickle.dump(responses, open("data.pkl", "wb"))
pickle.dump(responses, open("data.pkl", "wb"))
