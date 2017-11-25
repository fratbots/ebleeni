#!/usr/bin/env python3
import random

import requests
import json
from functools import lru_cache


def get_jobs(langs, limit):
    """
    Returns jobs appropriate for specified programming languages.

    Tries to find jobs on github, then gives up and returns static stubs.
    """
    githubJobs = _get_jobs_all_langs(langs, limit)
    
    if not githubJobs:
        return _get_stubs(langs, limit)
    
    return githubJobs


def _get_stubs(langs, limit):
    """
    Returns jobs stub.

    Should be replaces with github-jobs or stackoverflow-jobs API calls.
    Returns jobs for the first lang only for testing purpose.
    """
    tplTitle = '{} job title {}'
    tplDescription = '{} job description {}'
    tplUrl = 'http://example.org/job/{}'
    locations = ['helsinki', 'moscow', 'saint petersburg']
    lang = next(iter(langs or []), None)
    
    if not lang:
        return []
    
    result = []
    for i in range(limit):
        result.append({
            'title': tplTitle.format(lang, i),
            'description': tplDescription.format(lang, i),
            'location': random.choice(locations),
            'url': tplUrl.format(i),
        })
    
    return result


def _get_jobs_all_langs(langs, limit):
    jobs = []
    for lang in langs:
        jobs = jobs + _get_jobs_by_lang(lang)
        if len(jobs) >= limit:
            break
    return jobs[:limit]


@lru_cache(5)
def _get_jobs_by_lang(lang):
    params = {'search': lang}
    res = requests.get('https://jobs.github.com/positions.json', params=params)
    jobs = json.loads(res.text)
    result = []
    for job in jobs:
        result.append({
            'title': job['title'],
            'location': job['location'],
            'url': job['url'],
        })
    return result
