# coding utf-8
from commFunc import execute_sql, execute_sql_and_commit
from mysql_pool import get_connection


def getVerInfo():
    """
    获取版本信息统计和点赞相关的计算结果。

    参数:
        无

    返回值:
        tuple: 包含三个元素的元组:
            - verinfo (int): pyMC字段的总和。
            - verLM (int): pyLM字段的最大值。
            - likeCM (float): 计算后的平均评分，保留一位小数。
    """
    try:
        # 查询pyMC字段总和
        sql = "SELECT SUM(pyMC) FROM verinfo"
        result = execute_sql(cur3, sql)
        verinfo = result[0][0] if result else 0

        # 查询pyLM字段最大值
        sql = "SELECT MAX(pyLM) FROM verinfo"
        result = execute_sql(cur3, sql)
        verLM = result[0][0] if result else 0

        # 查询特定文件记录的pyLM * pyMC总和以及pyMC总和
        sql = "SELECT SUM(pyLM * pyMC), SUM(pyMC) FROM verinfo WHERE pyFile = %s"
        tmpTable = execute_sql(cur3, sql, ('thumbs-up-stars',))

        return verinfo, verLM
    except Exception as e:
        print(f"Database error: {str(e)}")

        return 0, 0


def ClearTables():
    try:
        # 删除 questions 表中的重复记录
        sql_delete_questions = """
            DELETE q1
            FROM questions q1
            JOIN questions q2
            ON q1.Question = q2.Question
            AND q1.qType = q2.qType
            AND q1.StationCN = q2.StationCN
            AND q1.chapterName = q2.chapterName
            WHERE q1.id > q2.id;
        """
        cur3.execute(sql_delete_questions)

        # 删除 commquestions 表中的重复记录
        sql_delete_commquestions = """
            DELETE c1
            FROM commquestions c1
            JOIN commquestions c2
            ON c1.Question = c2.Question AND c1.qType = c2.qType
            WHERE c1.id > c2.id;
        """
        cur3.execute(sql_delete_commquestions)

        # 删除 morepractise 表中的重复记录
        sql_delete_morepractise = """
            DELETE m1
            FROM morepractise m1
            JOIN morepractise m2
            ON m1.Question = m2.Question AND m1.qType = m2.qType AND m1.userName = m2.userName
            WHERE m1.id > m2.id;
        """
        cur3.execute(sql_delete_morepractise)

        # 删除 questionaff 表中的重复记录
        sql_delete_questionaff = """
            DELETE a1
            FROM questionaff a1
            JOIN questionaff a2
            ON a1.chapterName = a2.chapterName AND a1.StationCN = a2.StationCN
            WHERE a1.id > a2.id;
        """
        cur3.execute(sql_delete_questionaff)

        # 删除不在 questions 表中的 chapterName
        sql_delete_invalid_chapters = """
            DELETE FROM questionaff
            WHERE chapterName NOT IN ('公共题库', '错题集', '关注题集')
            AND chapterName NOT IN (SELECT DISTINCT(chapterName) FROM questions);
        """
        cur3.execute(sql_delete_invalid_chapters)

        # 更新 users 表中的用户中文名，去除空格
        sql_update_users = """
            UPDATE users
            SET userCName = REPLACE(userCName, ' ', '')
            WHERE userCName LIKE '% %';
        """
        cur3.execute(sql_update_users)

        # 去除问题字段中的换行符 - questions
        sql_update_questions = """
            UPDATE questions
            SET Question = REPLACE(Question, '\n', '')
            WHERE Question LIKE '%\n%';
        """
        cur3.execute(sql_update_questions)

        # 去除问题字段中的换行符 - commquestions
        sql_update_commquestions = """
            UPDATE commquestions
            SET Question = REPLACE(Question, '\n', '')
            WHERE Question LIKE '%\n%';
        """
        cur3.execute(sql_update_commquestions)

        # 去除问题字段中的换行符 - morepractise
        sql_update_morepractise = """
            UPDATE morepractise
            SET Question = REPLACE(Question, '\n', '')
            WHERE Question LIKE '%\n%';
        """
        cur3.execute(sql_update_morepractise)

        # 提交事务
        conn3.commit()

    except Exception as e:
        conn3.rollback()


def clearModifyQues(quesID, tablename, mRow):
    delTablePack = ["morepractise", "favques"]
    question, qOption, qAnswer, qType = mRow[:4]

    # 使用参数化查询防止SQL注入
    delete_sql_template = "DELETE FROM {table} WHERE Question = %s AND qOption = %s AND qAnswer = %s AND qType = %s"

    try:
        for each in delTablePack:
            # 确保表名安全，避免SQL注入
            if each not in ["morepractise", "favques"]:
                raise ValueError("Invalid table name: {}".format(each))
            sql = delete_sql_template.format(table=each)
            execute_sql_and_commit(conn3, cur3, sql, (question, qOption, qAnswer, qType))

        # 删除studyinfo表中的记录
        studyinfo_sql = "DELETE FROM studyinfo WHERE cid = %s AND quesTable = %s"
        execute_sql_and_commit(conn3, cur3, studyinfo_sql, (quesID, tablename))

    except Exception as e:
        # 记录异常日志
        print(f"Error occurred during database operation: {e}")
        # 根据实际情况选择是否抛出异常或回滚事务


def reviseQues():
    # 替换中文括号为英文括号
    for table_name in ["questions", "commquestions"]:
        # 替换全角括号
        for char_pair in [['（', '('], ['）', ')']]:
            # 使用 CONCAT 匹配包含通配符的模式，并使用 %s 占位符
            sql = f"UPDATE {table_name} SET Question = REPLACE(Question, %s, %s) WHERE qType = '填空题' AND Question LIKE CONCAT('%%', %s, '%%')"
            params = (char_pair[0], char_pair[1], char_pair[0])
            execute_sql_and_commit(conn3, cur3, sql, params)

    # 替换带空格的括号为标准括号
    for table_name in ["questions", "commquestions"]:
        for space_parentheses in ['( )', '(  )', '(   )', '(    )']:
            # 使用 CONCAT 进行模式匹配
            sql = f"UPDATE {table_name} SET Question = REPLACE(Question, %s, '()') WHERE qType = '填空题' AND Question LIKE CONCAT('%%', %s, '%%')"
            params = (space_parentheses, space_parentheses)
            execute_sql_and_commit(conn3, cur3, sql, params)


def getStationCNALL(flagALL=False):
    """
    获取站点中文名称列表

    参数:
        flagALL (bool): 是否包含'全站'选项, 默认不包含

    返回:
        list: 包含所有站点中文名称的列表
    """
    StationCNamePack = []
    if flagALL:
        # 如果flagALL为True，添加'全站'到列表中
        StationCNamePack.append("全站")
    sql = "SELECT Station from stations order by ID"
    rows = execute_sql(cur3, sql)
    for row in rows:
        # 将查询结果中的站点名称添加到列表中
        StationCNamePack.append(row[0])

    return StationCNamePack


def get_userName(searchUserName=""):
    searchUserNameInfo = ""
    if len(searchUserName) > 1:
        # 构建SQL查询语句，使用参数化查询防止SQL注入
        sql = "SELECT userName, userCName, StationCN FROM users WHERE userName LIKE %s"
        params = (f"%{searchUserName}%",)  # MySQL 使用 % 作为通配符，并用 %s 占位符
        rows = execute_sql(cur3, sql, params)
        if rows:
            # 格式化查询结果，使用颜色标记不同字段
            searchUserNameInfo = "\n\n".join(
                f"用户编码: :red[{row[0]}] 姓名: :blue[{row[1]}] 站室: :orange[{row[2]}]" for row in rows
            )

    # 添加最终提示信息
    if searchUserNameInfo:
        searchUserNameInfo += "\n请在用户编码栏中填写查询出的完整编码"

    return searchUserNameInfo

MIN_SEARCH_LENGTH_TIP = ":red[**请输入至少2个字**]"
PLEASE_FILL_FULL_CODE_TIP = "\n请在用户编码栏中填写查询出的完整编码"


def get_userCName(searchUserCName=""):
    """
    根据用户输入的中文名前缀搜索用户信息。

    参数:
    searchUserCName (str): 要搜索的用户中文名前缀，默认为空字符串。

    返回值:
    str: 包含搜索结果的字符串，包含用户编码、姓名和站室信息，
         或提示信息如输入长度不足或请填写完整编码。
    """
    searchUserCNameInfo = ""
    if len(searchUserCName) > 1:
        sql = "SELECT userName, userCName, StationCN FROM users WHERE userCName LIKE %s"
        # 使用 %s 占位符，并在参数中添加通配符 %
        params = (f"%{searchUserCName}%",)
        rows = execute_sql(cur3, sql, params)

        result_lines = [f"用户编码: :red[{row[0]}] 姓名: :blue[{row[1]}] 站室: :orange[{row[2]}]\n\n" for row in rows]
        searchUserCNameInfo = ''.join(result_lines)
    else:
        searchUserCNameInfo = MIN_SEARCH_LENGTH_TIP

    if "请输入至少2个字" not in searchUserCNameInfo:
        searchUserCNameInfo += PLEASE_FILL_FULL_CODE_TIP

    return searchUserCNameInfo


def get_update_content(file_path):
    """
    从指定文件中读取更新类型和更新内容信息。

    参数:
    file_path (str): 需要读取的文件的完整路径

    返回:
    tuple: 包含两个字符串元素的元组 (update_type, update_content)
           update_type: 更新类型描述
           update_content: 具体的更新内容
    """
    update_type, update_content = '', ''
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    file.close()
    flag_proc = False
    # 读取文件前30行，查找版本更新信息
    for line in lines[:30]:
        if line.startswith("### 版本"):
            flag_proc = True
        if flag_proc:
            # 提取更新类型
            if line.startswith("- "):
                update_type = line[2:-1]
            # 提取具体更新内容
            elif line.startswith("  - "):
                update_content = line[4:]
                break

    return update_type, update_content


conn3 = get_connection()
cur3 = conn3.cursor()
