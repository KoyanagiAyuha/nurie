import cv2
import base64
import json
import numpy as np
import boto3
import uuid
import io

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
    img_gray = cv2.cvtColor(contour, cv2.COLOR_BGR2GRAY)
    return img_gray

def post_s3(img, putname):
    s3 = boto3.client('s3')
    s3.upload_fileobj(
        Fileobj = img,
        Bucket = 'nurie',
        Key = putname,
        ExtraArgs={"ContentType": "image/jpeg", "ACL":"public-read"}
    )



def check_r18(img):
    client=boto3.client('rekognition')
    result, buf = cv2.imencode('.jpg', img)
    response = client.detect_moderation_labels(Image={'Bytes':buf.tobytes()})
    if len(response['ModerationLabels']) == 0:
        return True
    return False

def lambda_handler(event, context):
    # requestbodeyの中のjsonはeventに辞書型に変化されて保存されている
    # なので、eventの中には {"mypng": "base64でエンコードされた文字列"}が入力される想定。
    base_64ed_image = event['mypng']
    save_flag = event['saveflag']

    
    # バケット作成を作成してbynary変換して保存する。
    cvimg = base64_to_cv2(base_64ed_image)
    
    if check_r18(cvimg):
        putname = "Moderation/" + str(uuid.uuid4()) + ".jpg"
    else:
        putname = "NoModeration/" + str(uuid.uuid4()) + ".jpg"
    
    anime = nurie_filter(cvimg)
    
    if save_flag == "True":
        post_s3(io.BytesIO(anime), putname)

    body = cv2_to_base64(anime)
    
    # とりあえずOKを返す。
    return body