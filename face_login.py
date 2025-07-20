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
    known_encoding, userID_Pack, file_hash_pack = load_face_data(StationCN)
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


def face_compare(known_faces, face_image, pathIn=None, toleranceValue=0.5, use_dyna_tolerance=True):
    if use_dyna_tolerance:
        sql = "SELECT param_value from users_setup where param_name = 'face_tolerance'"
        cur.execute(sql)
        toleranceValue = round(cur.fetchone()[0] / 100, 2)
    #print(round(toleranceValue, 2))
    if pathIn:
        face_image = face_recognition.load_image_file(pathIn)
    #clean_snapshot()
    face_locations = face_recognition.face_locations(face_image)
    tmp_encodings = face_recognition.face_encodings(face_image, face_locations, num_jitters=10, model='large')
    if tmp_encodings:
        unknown_encoding = tmp_encodings[0]
        results = face_recognition.compare_faces(known_faces, unknown_encoding, tolerance=toleranceValue)
        results_dist = face_recognition.face_distance(known_faces, unknown_encoding)
        for index, is_match in enumerate(results):
            if is_match:
                return index, is_match, results, results_dist

    return None, False, None


def update_face_data(filename=None):
    os.system('cls')
    file_pack = []
    for root, dirs, files in os.walk('./ID_Photos'):
        for file in files:
            if os.path.splitext(file)[1].lower() == '.jpg' and not os.path.splitext(file)[0].startswith('snapshot_'):
                pathIn = os.path.join(root, file)
                if filename:
                    if pathIn == filename:
                        file_pack.append(pathIn)
                        break
                else:
                    file_pack.append(pathIn)
    for pathIn in file_pack:
        face_data = ''
        userID = pathIn[pathIn.rfind('\\') + 1:-4]
        if userID.find('_') != -1:
            userID = userID[:userID.find('_')]
        file_hash = get_file_sha256(pathIn)
        with open(pathIn, 'rb') as f:
            photo_data = f.read()
        sql = f"SELECT ID from users_face_data where userID = {userID} and file_hash = '{file_hash}'"
        if not execute_sql(cur, sql):
            face_image = face_recognition.load_image_file(pathIn)
            face_locations = face_recognition.face_locations(face_image)
            tmp_encodings = face_recognition.face_encodings(face_image, face_locations, num_jitters=10, model='large')
            if tmp_encodings:
                face_data = ' '.join([str(item) for item in tmp_encodings[0].flatten()])
                sql = f"SELECT userCName, StationCN from users where userID = {userID}"
                cur.execute(sql)
                result = cur.fetchone()
                if result:
                    sql = """
                        INSERT INTO users_face_data (userID, userCName, face_data, StationCN, file_hash, photo_data)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(sql, (
                        userID,
                        result[0],
                        face_data,
                        result[1],
                        file_hash,
                        photo_data
                    ))
                    conn.commit()
                    #print(userID, result[0], result[1], file_hash)
                else:
                    print(f'{pathIn} 获取用户信息失败! 请核对照片ID')
            else:
                os.remove(pathIn)
                print(f'{pathIn} 面部数据获取失败, 照片已经删除!')


def get_file_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def load_face_data(StationCN):
    userID_pack, face_data_pack, file_hash_pack = [], [], []
    sql = f"SELECT userID, face_data, file_hash, photo_data FROM users_face_data where StationCN = '{StationCN}'"
    rows = execute_sql(cur, sql)
    for row in rows:
        userID_pack.append(row[0])
        face_data_pack.append(np.array(row[1].split(), dtype=float))
        file_hash_pack.append(row[2])

    return face_data_pack, userID_pack, file_hash_pack


def face_login_webrtc(StationCN, frame, tolerance=0.5):
    known_encoding, userID_Pack, file_hash_pack = load_face_data(StationCN)
    userID = None
    result = face_compare(known_encoding, frame, pathIn=frame, toleranceValue=tolerance)
    if result[1]:
        userID = userID_Pack[result[0]]

    if userID:
        sql = f"SELECT userID, userCName, userType, StationCN, clerk_type from users where userID = {userID}"
        result = execute_sql(cur, sql)
        return result

    return None


def face_recognize_webrtc(StationCN, frame, tolerance=0.5, use_dyna_tolerance=False):
    known_encoding, userID_Pack, file_hash_pack = load_face_data(StationCN)
    user_id_distance = []
    result = face_compare(known_encoding, frame, pathIn=frame, toleranceValue=tolerance, use_dyna_tolerance=use_dyna_tolerance)
    if result[2]:
        photo_id = 1
        for index, value in enumerate(result[2]):
            if value:
                user_id_distance.append((round(result[3][index], 3), userID_Pack[index], photo_id, file_hash_pack[index]))
                photo_id += 1
        user_id_distance.sort()

    return user_id_distance


conn = get_connection()
cur = conn.cursor()
cmd = 'setx OPENCV_VIDEOIO_PRIORITY_MSMF 0'
debug = False
