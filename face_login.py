import hashlib
import os
import time

import cv2
import face_recognition
import numpy as np

from commFunc import execute_sql, execute_sql_and_commit
from mysql_pool import get_connection


def face_login(face_data_all):
    known_encoding, userID_Pack, userCName_Pack, userID, userCName = [], [], [], None, None
    for each in face_data_all:
        known_encoding.append(each[0])
        userID_Pack.append(each[1])
        userCName_Pack.append(each[2])
    cap = cv2.VideoCapture(0)
    # 检查摄像头是否成功打开
    flag = cap.isOpened()
    index = 0

    while flag:
        # 读取一帧图像
        ret, frame = cap.read()
        # 显示图像
        cv2.imshow("面部识别", frame)

        filename = f"./ID_Photos/snapshot_{index}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Save {filename} successfully!")
        result = face_compare(filename, known_encoding)
        print(result)
        if result[1] or index > 20:
            userID = userID_Pack[result[0]]
            userCName = userCName_Pack[result[0]]
            break
        else:
            index += 1
            time.sleep(0.5)

    # 释放摄像头并关闭所有窗口
    cap.release()
    cv2.destroyAllWindows()

    return userID, userCName


def face_compare(pathIn, known_faces, toleranceValue=0.6):
    face_image = face_recognition.load_image_file(pathIn)
    face_locations = face_recognition.face_locations(face_image)
    tmp_encodings = face_recognition.face_encodings(face_image, face_locations, num_jitters=10, model='large')
    if tmp_encodings:
        unknown_encoding = tmp_encodings[0]
        results = face_recognition.compare_faces(known_faces, unknown_encoding)
        for index, is_match in enumerate(results):
            if is_match:
                return index, is_match
    return None, False


def update_face_data():
    for root, dirs, files in os.walk('./ID_Photos'):
        for file in files:
            if os.path.splitext(file)[1].lower() == '.jpg':
                face_data = ''
                userID = os.path.splitext(file)[0]
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
                else:
                    print('面部数据已存在!')


def load_face_data(StationCN):
    face_data_all = []
    sql = f"SELECT userID, userCName, face_data FROM users_face_data where StationCN = '{StationCN}'"
    rows = execute_sql(cur, sql)
    for row in rows:
        userID, userCName, face_encoding = row
        face_data_all.append((np.array(face_encoding.split(), dtype=float), userID, userCName))

    return face_data_all


conn = get_connection()
cur = conn.cursor()
#update_face_data()
face_login(load_face_data('北京站'))
