#!/usr/bin/env python3

import os
import urllib.parse as parse
from typing import List, Tuple
from PIL import Image
import requests
from bs4 import BeautifulSoup

import opencv


def languages_lines() -> List[str]:
    with open('%s/data/languages.txt' % os.path.dirname(os.path.realpath(__file__))) as f:
        for line in f.readlines():
            yield line.rstrip()


def languages_values() -> List[Tuple[str]]:
    for line in languages_lines():
        arr = line.split(':', 1)
        yield (arr[0], arr[1])


def language_url(lang: str, page: int = 0) -> str:
    url = 'http://git-awards.com/users?utf8=%E2%9C%93&type=world&language={}'.format(parse.quote_plus(lang))
    if page > 1:
        url = '%s&page=%d' % (url, page)
    return url


def lang_dir(lang) -> str:
    path = '%s/data/langs/%s' % (os.path.dirname(os.path.realpath(__file__)), lang)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def learn_dir(lang) -> str:
    path = '%s/data/learn/%s' % (os.path.dirname(os.path.realpath(__file__)), lang)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def lang_users_pages(lang: str):
    result = []
    for page in range(1, 10):
        page_path = '%s/users.%d.html' % (lang_dir(lang), page)
        if os.path.exists(page_path):
            with open(page_path) as f:
                page_content = f.read()
        else:
            url = language_url(lang, page)
            res = requests.get(url)
            with open(page_path, mode='wb') as f:
                f.write(res.content)
                page_content = str(res.content)
        result.append(page_content)
    return result


def lang_users_parse(lang: str) -> List[Tuple[str]]:
    for page in lang_users_pages(lang):
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


def lang_users(lang: str) -> List[Tuple[str]]:
    path = '%s/users.txt' % lang_dir(lang)
    if os.path.exists(path):
        with open(path) as f:
            for line in f.readlines():
                yield tuple(line.rstrip().split(':', 1))

    users = lang_users_parse(lang)
    with open(path, mode='w') as f:
        for user, avatar in users:
            f.write('%s:%s\n' % (user, avatar))
            yield user, avatar


def user_avatar_path(lang, user) -> str:
    return '%s/avatar-%s.png' % (lang_dir(lang), user)


def learn_face_path(lang, user) -> str:
    return '%s/face-%s.jpg' % (learn_dir(lang), user)


def sure_avatar(lang, user, avatar):
    path = user_avatar_path(lang, user)
    if os.path.exists(path):
        return

    res = requests.get(avatar)
    with open(path, mode='wb') as f:
        f.write(res.content)


def sure_learn_face(lang, user):
    learn_path = learn_face_path(lang, user)
    if os.path.exists(learn_path):
        return

    avatar_path = user_avatar_path(lang, user)
    face = opencv.detect_face(avatar_path)
    if face is not None:
        img = Image.open(avatar_path)
        img2 = img.crop((face[0], face[1], face[0]+face[2], face[1]+face[3]))
        img2.save(learn_path)
        del img
        del img2


for lang, name in languages_values():
    users = lang_users(lang)
    for user, avatar in users:
        sure_avatar(lang, user, avatar)
        sure_learn_face(lang, user)
        print(user, avatar)
