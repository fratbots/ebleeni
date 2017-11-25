#!/usr/bin/env python3

import os
import urllib.parse as parse
from typing import List, Tuple

import sys
from PIL import Image
import requests
from bs4 import BeautifulSoup
import glob
import opencv


root = os.path.dirname(os.path.realpath(__file__))
path = '%s/data/noclass/' % root
res = glob.glob(path + '/*')

for img_path in glob.glob(path + '/*'):
    basename = os.path.basename(img_path)
    learn_path = '%s/data/learn/noclass/%s' % (root, basename)
    if os.path.exists(learn_path):
        continue

    face = opencv.detect_face(img_path)
    if face is not None:
        if not os.path.exists(os.path.dirname(learn_path)):
            os.mkdir(os.path.dirname(learn_path))
        img = Image.open(img_path)
        img2 = img.crop((face[0], face[1], face[0]+face[2], face[1]+face[3]))
        img2.save(learn_path)
        del img
        del img2
        print(img_path)

