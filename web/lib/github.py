#!/usr/bin/env python3

import requests
import json
from functools import lru_cache


def get_jobs(langs, limit):
    jobs = []
    for lang in langs:
        jobs = jobs + get_jobs_by_lang(lang)
        if len(jobs) >= limit:
            return jobs
    return jobs


@lru_cache()
def get_jobs_by_lang(lang):
    params = {'search': lang}
    res = requests.get('https://jobs.github.com/positions.json', params)
    jobs = json.loads(res.text)
    result = []
    for job in jobs:
        result.append({
            'title': job['title'],
            'location': job['location'],
            'description': job['description'],
            'url': job['url'],
            })
    return result
