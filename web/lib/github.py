#!/usr/bin/env python3

import requests
import json
from functools import lru_cache


@lru_cache()
def get_jobs(query: str):
    params = {'description': query}
    res_raw = requests.get('https://jobs.github.com/positions.json', params)
    res = json.loads(res_raw.text)
    return res
