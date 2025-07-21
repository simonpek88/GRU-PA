import hashlib
import os
import time

import cv2
import face_recognition
import numpy as np

import dlib
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
        # 保存图片
        #filename = f"./ID_Photos/snapshot_{i}.jpg"
        #cv2.imwrite(filename, frame)
        result = face_compare(known_encoding, frame)
        if result[0] or i > 40:
            if result[0]:
                userID = userID_Pack[result[1]]
            break
        else:
            i += 1
            time.sleep(0.2)

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


def face_compare(known_faces, face_image, pathIn=None, toleranceValue=0.45, use_dyna_tolerance=True):
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
        all_results = []
        for index, is_match in enumerate(results):
            if is_match:
                all_results.append([results_dist[index], index])
        if all_results:
            all_results.sort()
            return True, all_results[0][1], all_results[0][0], results, results_dist
        return False, None, None

    return False, None, None


def update_face_data(filename=None):
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
                        INSERT INTO users_face_data (userID, userCName, face_data, StationCN, file_hash, img_filename)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(sql, (
                        userID,
                        result[0],
                        face_data,
                        result[1],
                        file_hash,
                        pathIn
                    ))
                    conn.commit()
                    #print(userID, result[0], result[1], file_hash)
                else:
                    print(f'{pathIn} 获取用户信息失败! 请核对照片ID')
            else:
                os.remove(pathIn)
                print(f'{pathIn} 人脸数据获取失败, 照片已经删除!')


def get_file_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def load_face_data(StationCN):
    userID_pack, face_data_pack, file_hash_pack = [], [], []
    sql = f"SELECT userID, face_data, file_hash FROM users_face_data where StationCN = '{StationCN}'"
    rows = execute_sql(cur, sql)
    for row in rows:
        userID_pack.append(row[0])
        face_data_pack.append(np.array(row[1].split(), dtype=float))
        file_hash_pack.append(row[2])

    return face_data_pack, userID_pack, file_hash_pack


def face_login_webrtc(StationCN, frame, tolerance=0.45):
    known_encoding, userID_Pack, file_hash_pack = load_face_data(StationCN)
    userID = None
    result = face_compare(known_encoding, frame, pathIn=frame, toleranceValue=tolerance)
    if result[0]:
        userID = userID_Pack[result[1]]

    if userID:
        sql = f"SELECT userID, userCName, userType, StationCN, clerk_type from users where userID = {userID}"
        result = execute_sql(cur, sql)
        return result

    return None


def face_recognize_webrtc(StationCN, frame, tolerance=0.45, use_dyna_tolerance=False):
    known_encoding, userID_Pack, file_hash_pack = load_face_data(StationCN)
    user_id_distance = []
    result = face_compare(known_encoding, frame, pathIn=frame, toleranceValue=tolerance, use_dyna_tolerance=use_dyna_tolerance)
    if result[0]:
        draw_face_point(frame)
        for index, value in enumerate(result[3]):
            if value:
                user_id_distance.append((round(result[4][index], 3), userID_Pack[index], file_hash_pack[index]))
        user_id_distance.sort()

    return user_id_distance


def draw_face_point(img_file):
    # dlib预测器
    detector = dlib.get_frontal_face_detector()
    # 读入68点数据
    predictor = dlib.shape_predictor('./dlib/shape_predictor_68_face_landmarks.dat')

    # cv2读取图像
    img = imread_chinese(img_file)

    # 与人脸检测程序相同,使用detector进行人脸检测 dets为返回的结果
    dets = detector(img, 1)
    # 使用enumerate 函数遍历序列中的元素以及它们的下标
    # 下标k即为人脸序号
    # left：人脸左边距离图片左边界的距离 ；right：人脸右边距离图片左边界的距离
    # top：人脸上边距离图片上边界的距离 ；bottom：人脸下边距离图片上边界的距离
    for k, d in enumerate(dets):
        #print("dets{}".format(d))
        #print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))

        # 使用predictor进行人脸关键点识别 shape为返回的结果
        shape = predictor(img, d)
        # 获取第一个和第二个点的坐标（相对于图片而不是框出来的人脸）
        #print("Part 0: {}, Part 1: {} ...".format(shape.part(0),  shape.part(1)))

        # 绘制特征点
        for index, pt in enumerate(shape.parts()):
            #print('Part {}: {}'.format(index, pt))
            pt_pos = (pt.x, pt.y)
            cv2.circle(img, pt_pos, 2, (255, 0, 0), 1)
        # 在人脸框左上角添加序号
        cv2.putText(img, f"Face {k + 1}", (d.left(), d.top() - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1, lineType=cv2.LINE_AA)
        # 绘制头像框
        cv2.rectangle(img, (d.left(), d.top()), (d.right(), d.bottom()), (139, 134, 0), 2)

    cv2.imwrite(f'{img_file[:-4]}_point.jpg', img)


def imread_chinese(path):
    with open(path, 'rb') as f:
        data = f.read()
    img_array = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    return img


conn = get_connection()
cur = conn.cursor()
cmd = 'setx OPENCV_VIDEOIO_PRIORITY_MSMF 0'
