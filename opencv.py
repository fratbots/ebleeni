import os
from typing import Optional, Tuple

import cv2

_cascade = cv2.CascadeClassifier('%s/haarcascade_frontalface_default.xml' % os.path.dirname(os.path.realpath(__file__)))


def detect_face(path: str) -> Optional[Tuple[int]]:
    """
    :return: x, y, w, h
    """
    img = cv2.imread(path, 0)
    faces = _cascade.detectMultiScale(img, 1.1, 10)
    if len(faces):
        return sorted(faces, key=lambda f: f[2] * f[3])[0]

    return None
