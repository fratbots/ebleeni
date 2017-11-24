#!/usr/bin/env python3

import os
import urllib.parse as parse
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup


def languages_lines() -> List[str]:
    with open('%s/data/languages.txt' % os.path.dirname(os.path.realpath(__file__))) as f:
        for line in f.readlines():
            yield line.rstrip()


def languages_values() -> List[Tuple[str]]:
    for line in languages_lines():
        arr = line.split(':', 1)
        yield (arr[0], arr[1])


def language_url(value: str, page: int = 0) -> str:
    url = 'http://git-awards.com/users?utf8=%E2%9C%93&type=world&language={}'.format(parse.quote_plus(value))
    if page > 1:
        url = '%s&page=%d' % (url, page)
    return url


def lang_dir(value) -> str:
    path = '%s/data/langs/%s' % (os.path.dirname(os.path.realpath(__file__)), value)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def lang_users_pages(value: str):
    result = []
    for page in range(1, 10):
        page_path = '%s/users.%d.html' % (lang_dir(value), page)
        if os.path.exists(page_path):
            with open(page_path) as f:
                page_content = f.read()
        else:
            url = language_url(value, page)
            res = requests.get(url)
            with open(page_path, mode='wb') as f:
                f.write(res.content)
                page_content = str(res.content)
        result.append(page_content)
    return result


def lang_users_parse(value: str) -> List[Tuple[str]]:
    for page in lang_users_pages(value):
        soup = BeautifulSoup(page, 'html.parser')
        for td_tags in soup.find_all('td'):
            username = avatar = None
            for a_tag in td_tags.find_all('a'):
                img = a_tag.find('img', class_='avatar')
                if img:
                    avatar = img.get('src')
                href = a_tag.get('href')
                href_prefix = '/users/'
                if href.startswith(href_prefix):
                    username = href[len(href_prefix):]
                if username and avatar:
                    yield (username, avatar)


def lang_users(value: str) -> List[Tuple[str]]:
    path = '%s/users.txt' % lang_dir(value)
    if os.path.exists(path):
        with open(path) as f:
            for line in f.readlines():
                yield tuple(line.rstrip().split(':', 1))

    users = lang_users_parse(value)
    with open(path, mode='w') as f:
        for user, avatar in users:
            f.write('%s:%s\n' % (user, avatar))
            yield user, avatar


def user_avatar_path(value, user) -> str:
    return '%s/avatar-%s.png' % (lang_dir(value), user)


def sure_avatar(value, user, avatar):
    path = user_avatar_path(value, user)
    if os.path.exists(path):
        return

    res = requests.get(avatar)
    with open(path, mode='wb') as f:
        f.write(res.content)


for value, name in languages_values():
    users = lang_users(value)
    for user, avatar in users:
        sure_avatar(value, user, avatar)
        print(user, avatar)
