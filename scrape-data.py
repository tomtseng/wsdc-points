import json
import pickle
from pathlib import Path

import requests
from tqdm import tqdm

# Max ID as of 4/28/2024, which I found by manual trial and error, i.e., by
# typing numbers into the WSDC points registry until I consistently got no hits.
MAX_ID = 23454

# This URL and the data format were found by inspecting the network traffic when
# I manually searched for a dancer's points on the WSDC points registry.
url = "https://points.worldsdc.com/lookup2020/find"

# If there's partial data from an interrupted scraping attempt, load it to
# restart from where we left off.
tmp_file_path = Path("data-partial.pkl")
try:
    responses = pickle.load(open("data-partial.pkl", "rb"))
except FileNotFoundError:
    responses = []
last_id = responses[-1]["dancer_wsdcid"] if len(responses) > 0 else 0

# This runs at a rate of 4–5 requests per second on my laptop. Maybe try
# firing multiple requests in parallel if you want to speed this up.
for i in tqdm(range(last_id, MAX_ID + 1)):
    data = {"num": i}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        responses.append(json.loads(response.text))
    # Periodically save the responses just in case.
    if i % 100 == 0:
        pickle.dump(responses, open("data-partial.pkl", "wb"))
pickle.dump(responses, open("data.pkl", "wb"))
tmp_file_path.unlink()
