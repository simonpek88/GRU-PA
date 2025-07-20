import hashlib
import os
import time

import cv2
import face_recognition
import numpy as np

from commFunc import execute_sql, execute_sql_and_commit
from mysql_pool import get_connection

# cSpell:ignoreRegExp /[^\s]{16,}/
# cSpell:ignoreRegExp /\b[A-Z]{3,15}\b/g
# cSpell:ignoreRegExp /\b[A-Z]\b/g


def face_login_cv(StationCN):
    known_encoding, userID_Pack = load_face_data(StationCN)
    userID = None
    # 获取摄像头
    cap = cv2.VideoCapture(0)
    # 检查摄像头是否成功打开
    flag = cap.isOpened()
    i = 0

    while flag:
        # 读取一帧图像
        ret, frame = cap.read()

        # 显示图像
        #cv2.imshow("Face Recognize", frame)

        #filename = f"./ID_Photos/snapshot_{index}.jpg"
        #cv2.imwrite(filename, frame)
        result = face_compare(known_encoding, frame)
        if result[1] or i > 30:
            if result[1]:
                userID = userID_Pack[result[0]]
                if debug:
                    for index, value in enumerate(result[2]):
                        if value:
                            print(f"用户ID: {userID_Pack[index]} 识别: {value}")
            break
        else:
            i += 1
            time.sleep(0.5)

    # 释放摄像头
    cap.release()
    # 关闭所有窗口
    #cv2.destroyAllWindows()

    if userID:
        sql = f"SELECT userID, userCName, userType, StationCN, clerk_type from users where userID = {userID}"
        result = execute_sql(cur, sql)
        return result

    return None


def clean_snapshot():
    for root, dirs, files in os.walk('./ID_Photos'):
        for file in files:
            if os.path.splitext(file)[1].lower() == '.jpg' and os.path.splitext(file)[0].startswith('snapshot_'):
                pathIn = os.path.join(root, file)
                os.remove(pathIn)


def face_compare(known_faces, face_image, pathIn=None, toleranceValue=0.5):
    if pathIn:
        face_image = face_recognition.load_image_file(pathIn)
    #clean_snapshot()
    face_locations = face_recognition.face_locations(face_image)
    tmp_encodings = face_recognition.face_encodings(face_image, face_locations, num_jitters=10, model='large')
    if tmp_encodings:
        unknown_encoding = tmp_encodings[0]
        results = face_recognition.compare_faces(known_faces, unknown_encoding, tolerance=toleranceValue)
        for index, is_match in enumerate(results):
            if is_match:
                return index, is_match, results

    return None, False, None


def update_face_data():
    for root, dirs, files in os.walk('./ID_Photos'):
        for file in files:
            if os.path.splitext(file)[1].lower() == '.jpg' and not os.path.splitext(file)[0].startswith('snapshot_'):
                face_data = ''
                userID = os.path.splitext(file)[0]
                if userID.find('_') != -1:
                    userID = userID[:userID.find('_')]
                pathIn = os.path.join(root, file)
                with open(pathIn, 'rb') as f:
                    sha1obj = hashlib.sha256()
                    sha1obj.update(f.read())
                    file_hash = sha1obj.hexdigest()
                sql = f"SELECT ID from users_face_data where userID = {userID} and file_hash = '{file_hash}'"
                if not execute_sql(cur, sql):
                    face_image = face_recognition.load_image_file(pathIn)
                    face_locations = face_recognition.face_locations(face_image)
                    tmp_encodings = face_recognition.face_encodings(face_image, face_locations, num_jitters=10, model='large')
                    if tmp_encodings:
                        face_data = ' '.join([str(item) for item in tmp_encodings[0].flatten()])
                        sql = f"SELECT userCName, StationCN from users where userID = {userID}"
                        result = execute_sql(cur, sql)
                        if result:
                            sql = f"INSERT INTO users_face_data(userID, userCName, face_data, StationCN, file_hash) VALUES ({userID}, '{result[0][0]}', '{face_data}', '{result[0][1]}', '{file_hash}')"
                            execute_sql_and_commit(conn, cur, sql)
                        else:
                            print('获取用户信息失败!')
                    else:
                        print('面部数据获取失败!')


def load_face_data(StationCN):
    face_data_pack, userID_pack = [], []
    sql = f"SELECT userID, face_data FROM users_face_data where StationCN = '{StationCN}'"
    rows = execute_sql(cur, sql)
    for row in rows:
        face_data_pack.append(np.array(row[1].split(), dtype=float))
        userID_pack.append(row[0])

    return face_data_pack, userID_pack


def face_login_webrtc(StationCN, frame, tolerance=0.5):
    known_encoding, userID_Pack = load_face_data(StationCN)
    userID = None
    result = face_compare(known_encoding, frame, pathIn=frame, toleranceValue=tolerance)
    if result[1]:
        userID = userID_Pack[result[0]]

    if userID:
        sql = f"SELECT userID, userCName, userType, StationCN, clerk_type from users where userID = {userID}"
        result = execute_sql(cur, sql)
        return result

    return None


def face_recognize_webrtc(StationCN, frame, tolerance=0.5):
    known_encoding, userID_Pack = load_face_data(StationCN)
    userID = []
    result = face_compare(known_encoding, frame, pathIn=frame, toleranceValue=tolerance)
    if result[2]:
        for index, value in enumerate(result[2]):
            if value:
                userID.append(userID_Pack[index])

    return userID


conn = get_connection()
cur = conn.cursor()
cmd = 'setx OPENCV_VIDEOIO_PRIORITY_MSMF 0'
debug = False
