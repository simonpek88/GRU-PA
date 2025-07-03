# coding utf-8
import datetime
import re
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import streamlit_antd_components as sac
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from st_keyup import st_keyup

from commFunc import (execute_sql, execute_sql_and_commit, getUserEDKeys,
                      updatePyFileinfo)
from commModules import (get_update_content, get_userCName, get_userName,
                         getVerInfo)
from mysql_pool import get_connection

# cSpell:ignoreRegExp /[^\s]{16,}/
# cSpell:ignoreRegExp /\b[A-Z]{3,15}\b/g
# cSpell:ignoreRegExp /\b[A-Z]\b/g

@st.fragment
def login():
    # 显示应用名称
    st.markdown(f"<font face='微软雅黑' color=purple size=20><center>**{APPNAME}**</center></font>", unsafe_allow_html=True)

    # 登录表单容器
    login = st.empty()
    with login.container(border=True):
        # 用户编码输入框
        userName = st_keyup("请输入用户编码", placeholder="请输入纯数字用户编码, 非站室名称, 如果不知编码, 请在下方输入姓名查询", max_chars=8)
        # 初始化用户姓名
        st.session_state.userCName = ""

        # 如果输入了用户编码
        if userName:
            filtered = get_userName(userName)
            # 如果未找到对应的用户
            if filtered == "":
                # 根据用户编码获取用户姓名和站室
                getUserCName(userName, "Digit")
                # 显示用户姓名和站室
                st.caption(f"用户名: :blue[{st.session_state.userCName}] 站室: :orange[{st.session_state.StationCN}]")
        else:
            filtered = ""

        # 如果用户姓名未找到或存在过滤结果
        if st.session_state.userCName == "未找到" or filtered:
            st.caption(filtered)

        # 如果用户编码为空或用户姓名未找到
        if userName == "" or st.session_state.userCName == "未找到":
            # 用户姓名输入框
            userCName = st_keyup("请输入用户姓名", placeholder="请输入用户姓名, 至少2个字, 用于查询, 非必填项", max_chars=8)
            st.session_state.userCName = ""

            # 如果输入了用户姓名
            if userCName:
                filtered = get_userCName(userCName)
                # 如果未找到对应的用户
                if filtered == "":
                    # 根据用户姓名获取用户姓名和站室
                    getUserCName(userCName, "Str")
                    # 显示用户姓名和站室
                    st.caption(f"用户名: :blue[{st.session_state.userCName}] 站室: :orange[{st.session_state.StationCN}]")
            else:
                filtered = ""

            # 如果用户姓名未找到或存在过滤结果
            if st.session_state.userCName == "未找到" or filtered:
                # 提示区域容器
                promptArea = st.empty()
                with promptArea.container():
                    # 显示过滤结果
                    st.caption(filtered)
                # 如果用户编码存在但过滤结果为空
                if userName and filtered == "":
                    promptArea.empty()

        # 用户密码输入框
        userPassword = st.text_input("请输入密码", max_chars=8, placeholder="用户初始密码为1234", type="password", autocomplete="off")

        # 登录按钮
        buttonLogin = st.button("登录")

    # 如果点击了登录按钮
    if buttonLogin:
        # 如果用户编码和密码不为空
        if userName != "" and userPassword != "":
            # 验证用户密码
            verifyUPW = verifyUserPW(userName, userPassword)
            # 如果密码验证成功
            if verifyUPW[0]:
                userPassword = verifyUPW[1]
            sql = f"SELECT userName, userCName, userType, StationCN from users where userName = {userName} and userPassword = '{userPassword}'"
            result = execute_sql(cur, sql)
            if result:
                st.toast(f"用户: {result[0][0]} 姓名: {result[0][1]} 登录成功, 欢迎回来")
                login.empty()
                st.session_state.logged_in = True
                st.session_state.userName = result[0][0]
                st.session_state.userCName = result[0][1]
                st.session_state.userType = result[0][2]
                st.session_state.StationCN = result[0][3]
                sql = "UPDATE verinfo set pyLM = pyLM + 1 where pyFile = 'visitcounter'"
                execute_sql_and_commit(conn, cur, sql)
                st.rerun()
            elif not verifyUPW[0]:
                st.error("登录失败, 请检查用户名和密码, 若忘记密码请联系管理员重置")
        else:
            st.warning("请输入用户编码和密码")


def logout():
    try:
        pass

    finally:
        # 关闭游标
        cur.close()
        # 关闭数据库连接
        conn.close()

    # 清除会话状态中的所有键值对
    for key in st.session_state.keys():
        del st.session_state[key]

    # 重新运行当前脚本
    st.rerun()


@st.fragment
def getUserCName(sUserName, sType="Digit"):
    errorInfo = ""

    # 判断sType是否为"Digit"
    if sType.capitalize() == "Digit":
        # 使用正则表达式去除非数字和小数点字符
        cop = re.compile('[^0-9^.]')
        inputStr = cop.sub('', sUserName)
        # 如果原字符串长度与过滤后的字符串长度相等，说明原字符串只包含数字和小数点
        if len(sUserName) == len(inputStr):
            sql = f"SELECT userCName, StationCN from users where userName = {sUserName}"
        else:
            sql = ""
            errorInfo = "请输入纯数字用户编码"

    # 判断sType是否为"Str"
    elif sType.capitalize() == "Str":
        sql = f"SELECT userCName, StationCN from users where userCName = '{sUserName}'"

    # 其他情况
    else:
        sql = ""

    # 如果sql不为空
    if sql != "":
        rows = execute_sql(cur, sql)
        if rows:
            st.session_state.userCName = rows[0][0]
            st.session_state.StationCN = rows[0][1]
        else:
            st.session_state.userCName = "未找到"
            st.session_state.StationCN = "未找到"

    # 如果sql为空
    else:
        if errorInfo != "":
            st.error(errorInfo)
        st.session_state.userCName = ""
        st.session_state.StationCN = ""


def verifyUserPW(vUserName, vUserPW):
    st.session_state.userPwRecheck = False
    vUserEncPW = ""
    sql = f"SELECT userPassword from users where userName = {vUserName}"
    pwTable = execute_sql(cur, sql)
    if pwTable:
        vUserEncPW = pwTable[0][0]
        vUserDecPW = getUserEDKeys(vUserEncPW, "dec")
        if vUserPW == vUserDecPW:
            st.session_state.userPwRecheck = True

    return st.session_state.userPwRecheck, vUserEncPW

@st.fragment
def displayBigTimeCircle():
    components.html(open("./MyComponentsScript/Clock-Big-Circle.txt", "r", encoding="utf-8").read(), height=260)


@st.fragment
def displayVisitCounter():
    sql = "SELECT pyLM from verinfo where pyFile = 'visitcounter'"
    visitcount = execute_sql(cur, sql)[0][0]
    countScript = (open("./MyComponentsScript/FlipNumber.txt", "r", encoding="utf-8").read()).replace("visitcount", str(visitcount))
    components.html(countScript, height=40)


@st.fragment
def displaySmallTime():
    components.html(open("./MyComponentsScript/Clock-Small.txt", "r", encoding="utf-8").read(), height=34)


@st.fragment
def displaySmallClock():
    components.html(open("./MyComponentsScript/Clock-Number.txt", "r", encoding="utf-8").read(), height=30)


@st.fragment
def displayAppInfo():
    infoStr = open("./MyComponentsScript/glowintext.txt", "r", encoding="utf-8").read()
    infoStr = infoStr.replace("软件名称", APPNAME)
    verinfo, verLM = getVerInfo()
    infoStr = infoStr.replace("软件版本", f"软件版本: {int(verinfo / 10000)}.{int((verinfo % 10000) / 100)}.{int(verinfo / 10)} building {verinfo}")
    infoStr = infoStr.replace("更新时间", f"更新时间: {time.strftime('%Y-%m-%d %H:%M', time.localtime(verLM))}")
    update_type, update_content = get_update_content(f"./CHANGELOG.md")
    infoStr = infoStr.replace("更新内容", f"更新内容: {update_type} - {update_content}")
    components.html(infoStr, height=340)


global APPNAME
APPNAME = "北京站绩效考核系统"
conn = get_connection()
cur = conn.cursor()
selected = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    updatePyFileinfo()
    login()

if st.session_state.logged_in:
    with st.sidebar:
        displaySmallTime()
        #displaySmallClock()
        if st.session_state.userType == "admin":
            selected = sac.menu([
                sac.MenuItem('主页', icon='house'),
                sac.MenuItem('功能', icon='grid-3x3-gap', children=[
                    sac.MenuItem('选择考试', icon='list-task'),
                    sac.MenuItem('开始考试', icon='pencil-square'),
                ]),
                sac.MenuItem('账户', icon='person-gear', children=[
                    sac.MenuItem('密码修改', icon='key', disabled=True),
                    sac.MenuItem('登出', icon='box-arrow-right'),
                ]),
                sac.MenuItem('关于', icon='layout-wtf', children=[
                    sac.MenuItem('Readme', icon='github'),
                    sac.MenuItem('关于...', icon='link-45deg'),
                ]),
            ], open_all=True)
        elif st.session_state.userType == "user":
            selected = sac.menu([
                sac.MenuItem('主页', icon='house'),
                sac.MenuItem('功能', icon='grid-3x3-gap', children=[
                    sac.MenuItem('选择考试', icon='list-task'),
                    sac.MenuItem('开始考试', icon='pencil-square'),
                ]),
                sac.MenuItem('账户', icon='person-gear', children=[
                    sac.MenuItem('密码修改', icon='key', disabled=True),
                    sac.MenuItem('登出', icon='box-arrow-right'),
                ]),
                sac.MenuItem('关于', icon='layout-wtf', children=[
                    sac.MenuItem('Readme', icon='github'),
                    sac.MenuItem('关于...', icon='link-45deg'),
                ]),
            ], open_all=True)
    if selected == "主页":
        displayBigTimeCircle()
        displayAppInfo()
        displayVisitCounter()
    elif selected == "生成题库" or selected == "选择考试":
        if st.session_state.examType == "training":
            #st.write("### :red[生成练习题库]")
            #st.markdown("<font face='微软雅黑' color=blue size=20><center>**生成练习题库**</center></font>", unsafe_allow_html=True)
            st.markdown("### <font face='微软雅黑' color=teal><center>生成练习题库</center></font>", unsafe_allow_html=True)
        elif st.session_state.examType == "exam":
            #st.markdown("<font face='微软雅黑' color=red size=20><center>**选择考试**</center></font>", unsafe_allow_html=True)
            st.markdown("### <font face='微软雅黑' color=red><center>选择考试</center></font>", unsafe_allow_html=True)
        if not st.session_state.examChosen or not st.session_state.calcScore:
            sql = "UPDATE verinfo set pyLM = 0 where pyFile = 'chapterChosenType'"
            execute_sql_and_commit(conn, cur, sql)
        else:
            st.error("你不能重复选择考试场次")
    elif selected == "题库练习" or selected == "开始考试":
        pass
