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
from streamlit_extras.badges import badge

from commFunc import (execute_sql, execute_sql_and_commit, getUserEDKeys,
                      updatePyFileinfo)
from commModules import get_update_content, getVerInfo
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
        userName = st.text_input("请输入用户编码", placeholder="请输入纯数字用户编码", max_chars=8)
        # 初始化用户姓名
        st.session_state.userCName = ""

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


def changePassword():
    # 显示密码修改页面标题
    st.write("### :red[密码修改]")
    # 创建一个带有边框的容器
    changePW = st.empty()
    with changePW.container(border=True):
        # 输入原密码
        oldPassword = st.text_input("请输入原密码", max_chars=8, type="password", autocomplete="off")
        # 输入新密码
        newPassword = st.text_input("请输入新密码", max_chars=8, type="password", autocomplete="off")
        # 再次输入新密码以确认
        confirmPassword = st.text_input("请再次输入新密码", max_chars=8, placeholder="请与上一步输入的密码一致", type="password", autocomplete="new-password")
        # 确认修改按钮
        buttonSubmit = st.button("确认修改")

    # 检查原密码是否为空
    if oldPassword:
        # 验证用户原密码
        verifyUPW = verifyUserPW(st.session_state.userName, oldPassword)
        if verifyUPW[0]:
            oldPassword = verifyUPW[1]
        # 构造SQL查询语句，验证用户名和密码是否匹配
        sql = f"SELECT ID from users where userName = {st.session_state.userName} and userPassword = '{oldPassword}'"
        if execute_sql(cur, sql):
            # 检查新密码和确认密码是否填写且一致
            if newPassword and confirmPassword and newPassword != "":
                if newPassword == confirmPassword:
                    # 确认修改按钮是否被点击
                    if buttonSubmit:
                        # 加密新密码
                        newPassword = getUserEDKeys(newPassword, "enc")
                        # 构造SQL更新语句，更新用户密码
                        sql = f"UPDATE users set userPassword = '{newPassword}' where userName = {st.session_state.userName}"
                        # 执行SQL语句并提交
                        execute_sql_and_commit(conn, cur, sql)
                        # 显示密码修改成功提示，并要求重新登录
                        st.toast("密码修改成功, 请重新登录")
                        # 登出用户
                        logout()
                else:
                    # 显示密码不一致的错误信息
                    st.error("两次输入的密码不一致")
            else:
                # 显示新密码未填写的警告信息
                st.warning("请检查新密码")
        else:
            # 显示原密码错误的错误信息
            st.error("原密码不正确")
    else:
        st.warning("原密码不能为空")


def resetPassword():
    # 显示副标题和分隔线
    st.subheader(":orange[密码重置及更改账户类型]", divider="red")

    # 检查是否需要重置用户信息
    if st.session_state.userPwRecheck:
        # 显示重置用户信息提示
        st.write(":red[**重置用户信息**]")

        # 创建三列布局
        rCol1, rCol2, rCol3 = st.columns(3)

        # 获取用户编码
        rUserName = rCol1.number_input("用户编码", value=0)

        # 检查用户编码是否不为0
        if rUserName != 0:
            # 执行SQL查询用户信息
            sql = f"SELECT userCName, userType from users where userName = {rUserName}"
            rows = execute_sql(cur, sql)

            # 检查是否查询到用户信息
            if rows:
                # 显示用户姓名
                rCol2.write(f"用户姓名: **{rows[0][0]}**")

                # 在第三列创建布局
                with rCol3:
                    rUserType = False

                    # 根据用户类型设置开关
                    if rows[0][1] == "admin" or rows[0][1] == "supervisor":
                        rUserType = sac.switch(label="管理员", value=True, on_label="On", align='start', size='md')
                    elif rows[0][1] == "user":
                        rUserType = sac.switch(label="管理员", value=False, on_label="On", align='start', size='md')

                # 显示重置类型提示
                st.write("重置类型")

                # 创建重置类型的复选框
                rOption1 = st.checkbox("密码", value=False)
                rOption2 = st.checkbox("账户类型", value=False)

                # 创建重置按钮
                btnResetUserPW = st.button("重置", type="primary")

                # 检查是否点击了重置按钮并选择了重置类型
                if btnResetUserPW and (rOption1 or rOption2):
                    st.button("确认", type="secondary", on_click=actionResetUserPW, args=(rUserName, rOption1, rOption2, rUserType,))
                    st.session_state.userPwRecheck = False
                # 如果未选择任何重置类型，显示警告
                elif not rOption1 and not rOption2:
                    st.warning("请选择重置类型")
            # 如果未查询到用户信息，显示错误
            else:
                st.error("用户不存在")
    # 如果不需要重置用户信息，显示密码输入框
    else:
        vUserPW = st.text_input("请输入密码", max_chars=8, placeholder="请输入管理员密码, 以验证身份", type="password", autocomplete="off")

        # 检查是否输入了密码
        if vUserPW:
            # 验证密码
            if verifyUserPW(st.session_state.userName, vUserPW)[0]:
                st.rerun()
            # 如果密码错误，显示错误提示
            else:
                st.error("密码错误, 请重新输入")

@st.fragment
def changelog():
    changelogInfo = open("./CHANGELOG.md", "r", encoding="utf-8").read()
    st.markdown(changelogInfo)


def aboutReadme():
    st.markdown(open("./README.md", "r", encoding="utf-8").read())


def aboutInfo():
    st.subheader("关于本软件", divider="rainbow")
    st.subheader(":blue[Powered by Python and Streamlit]")
    logo1, logo2, logo3, logo4, logo5, logo6 = st.columns(6)
    with logo1:
        st.caption("Python")
        st.image("./Images/logos/python.png")
    with logo2:
        st.caption("Streamlit")
        st.image("./Images/logos/streamlit.png")
    with logo3:
        st.caption("MySQL")
        st.image("./Images/logos/sqlite.png")
    with logo4:
        st.caption("Ant Comp")
        st.image("./Images/logos/antd.png")
    with logo5:
        st.caption("Pandas")
        st.image("./Images/logos/pandas.png")
    with logo6:
        st.caption("Plotly")
        st.image("./Images/logos/antd.png")
    display_pypi()
    st.write("###### :violet[为了获得更好的使用体验, 请使用浅色主题]")
    verinfo, verLM = getVerInfo()
    st.caption(f"Version: {int(verinfo / 10000)}.{int((verinfo % 10000) / 100)}.{int(verinfo / 10)} building {verinfo} Last Modified: {time.strftime('%Y-%m-%d %H:%M', time.localtime(verLM))}")
    sac.divider(align="center", color="blue")


def display_pypi():
    pypi1, pypi2, pypi3, pypi4, pypi5 = st.columns(5)
    with pypi1:
        badge(type="pypi", name="streamlit")
    with pypi2:
        badge(type="pypi", name="streamlit_antd_components")
    with pypi3:
        badge(type="pypi", name="pandas")
    with pypi4:
        badge(type="pypi", name="plotly")


def actionResetUserPW(rUserName, rOption1, rOption2, rUserType):
    rInfo = ""

    # 如果 rOption1 为真
    if rOption1:
        # 获取用户加密密钥
        resetPW = getUserEDKeys("1234", "enc")
        # 构建 SQL 更新语句
        sql = f"UPDATE users SET userPassword = '{resetPW}' where userName = {rUserName}"
        # 执行 SQL 并提交
        execute_sql_and_commit(conn, cur, sql)
        # 更新信息，表示密码已重置
        rInfo += "密码已重置为: 1234 / "

    # 如果 rOption2 为真
    if rOption2:
        # 如果 rUserType 有值
        if rUserType:
            # 构建 SQL 更新语句，将用户类型更改为管理员
            sql = f"UPDATE users SET userType = 'admin' where userName = {rUserName}"
            # 更新信息，表示账户类型已更改为管理员
            rInfo += "账户类型已更改为: 管理员 / "
        else:
            # 构建 SQL 更新语句，将用户类型更改为普通用户
            sql = f"UPDATE users SET userType = 'user' where userName = {rUserName}"
            # 更新信息，表示账户类型已更改为用户
            rInfo += "账户类型已更改为: 用户 / "
        # 执行 SQL 并提交
        execute_sql_and_commit(conn, cur, sql)

    # 显示操作结果
    st.success(f"**{rInfo[:-3]}**")


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
                    sac.MenuItem('日常工作录入', icon='list-task'),
                    sac.MenuItem('开始考试', icon='pencil-square'),
                ]),
                sac.MenuItem('账户', icon='person-gear', children=[
                    sac.MenuItem('密码修改', icon='key'),
                    sac.MenuItem('登出', icon='box-arrow-right'),
                ]),
                sac.MenuItem('关于', icon='layout-wtf', children=[
                    sac.MenuItem('Changelog', icon='view-list'),
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
                    sac.MenuItem('密码修改', icon='key'),
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
    elif selected == "密码修改":
        changePassword()
    elif selected == "密码重置":
        resetPassword()
    elif selected == "登出":
        logout()
    elif selected == "Changelog":
        changelog()
    elif selected == "Readme":
        aboutReadme()
    elif selected == "关于...":
        aboutInfo()
