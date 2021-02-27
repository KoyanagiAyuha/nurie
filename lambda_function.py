import cv2
import base64
import json
import numpy as np


def convert_b64_string_to_bynary(s):
    """base64をデコードする"""
    return base64.b64decode(s.encode("UTF-8"))

def base64_to_cv2(image_base64):
    """base64 image to cv2"""
    image_bytes = base64.b64decode(image_base64)
    np_array = np.fromstring(image_bytes, np.uint8)
    image_cv2 = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    return image_cv2


def cv2_to_base64(image_cv2):
    """cv2 image to base64"""
    image_bytes = cv2.imencode('.jpg', image_cv2)[1].tostring()
    image_base64 = base64.b64encode(image_bytes).decode()
    return image_base64

def nurie_filter(img):
    neiborhood24 = np.ones((5, 5), dtype=np.uint8)
    dilated = cv2.dilate(img, neiborhood24, iterations=1)
    diff = cv2.absdiff(dilated, img)
    contour = 255 - diff
    return contour

def lambda_handler(event, context):
    # requestbodeyの中のjsonはeventに辞書型に変化されて保存されている
    # なので、eventの中には {"mypng": "base64でエンコードされた文字列"}が入力される想定。
    base_64ed_image = event['mypng']
    # バケット作成を作成してbynary変換して保存する。
    cvimg = base64_to_cv2(base_64ed_image)

    anime = nurie_filter(cvimg)
    
    body = cv2_to_base64(anime)
    # とりあえずOKを返す。
    return body