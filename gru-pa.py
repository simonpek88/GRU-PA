# coding utf-8
import calendar
import datetime
import os
import time

import nivo_chart as nc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import streamlit_antd_components as sac
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from openpyxl.cell import MergedCell
from openpyxl.styles import Alignment, Border, Font, Side
from plotly.subplots import make_subplots
from pybadges import badge
from streamlit_condition_tree import condition_tree
from streamlit_extras.metric_cards import style_metric_cards
from wcwidth import wcswidth

from commFunc import (execute_sql, execute_sql_and_commit, get_update_content,
                      getUserEDKeys, getVerInfo, updatePyFileinfo)
from gd_weather import get_city_weather
from gen_badges import gen_badge
from hf_weather import get_city_history_weather, get_city_now_weather
from mysql_pool import get_connection

# cSpell:ignoreRegExp /[^\s]{16,}/
# cSpell:ignoreRegExp /\b[A-Z]{3,15}\b/g
# cSpell:ignoreRegExp /\b[A-Z]\b/g

@st.fragment
def login():
    st.set_page_config(layout="centered")
    # 显示应用名称
    st.markdown(f"<font face='微软雅黑' color=purple size=20><center>**{APPNAME_CN}**</center></font>", unsafe_allow_html=True)

    # 登录表单容器
    login = st.empty()
    with login.container(border=True):
        userID, userCName = [], []
        sql = "SELECT DISTINCT(StationCN) from users order by StationCN"
        rows = execute_sql(cur, sql)
        station_type = st.selectbox(label="请选择站点", options=[row[0] for row in rows], index=0)
        sql = f"SELECT userID, userCName, StationCN from users where StationCN = '{station_type}' order by StationCN, userCName"
        rows = execute_sql(cur, sql)
        for row in rows:
            userID.append(row[0])
            userCName.append(row[1])
        query_userCName = st.selectbox("请选择用户", userCName, index=None)
        if query_userCName is not None:
            userID = userID[userCName.index(query_userCName)]
        else:
            userID = None

        # 用户密码输入框
        userPassword = st.text_input("请输入密码", max_chars=8, placeholder="用户初始密码为1234", type="password", autocomplete="off")

        # 登录按钮
        buttonLogin = st.button("登录")

    # 如果点击了登录按钮
    if buttonLogin:
        # 如果用户编码和密码不为空
        if userID and userPassword:
            # 验证用户密码
            verifyUPW = verifyUserPW(userID, userPassword)
            # 如果密码验证成功
            if verifyUPW[0]:
                userPassword = verifyUPW[1]
            sql = f"SELECT userID, userCName, userType, StationCN, clerk_type from users where userID = {userID} and userPassword = '{userPassword}'"
            result = execute_sql(cur, sql)
            if result:
                st.toast(f"用户: {result[0][1]} 登录成功, 欢迎回来")
                login.empty()
                st.session_state.logged_in = True
                st.session_state.userID = result[0][0]
                st.session_state.userCName = result[0][1]
                st.session_state.userType = result[0][2]
                st.session_state.StationCN = result[0][3]
                st.session_state.clerkType = result[0][4]
                st.session_state.userPwRechecked = False
                # 获取城市编码
                get_city_code()
                # 自动获取历史天气, 免得过期后数据无法获取
                auto_get_history_weather()
                # 更新用户设置
                refresh_users_setup()
                # 更新访问次数
                sql = "UPDATE verinfo set pyLM = pyLM + 1 where pyFile = 'visitcounter'"
                execute_sql_and_commit(conn, cur, sql)
                updatePyFileinfo()
                # 更新版本信息
                verinfo, verLM = getVerInfo()
                app_version = f'{int(verinfo / 10000)}.{int((verinfo % 10000) / 100)}.{verinfo}'
                app_lm = time.strftime('%Y-%m-%d %H:%M', time.localtime(verLM))
                gen_badge(conn, cur, [], 'MySQL', APPNAME_EN, app_version, app_lm)
                now = datetime.datetime.now()
                valid_time = now.strftime("%Y-%m-%d")
                sql = f"SELECT notice from notices where StationCN = '{st.session_state.StationCN}' and start_time >= '{valid_time}' and '{valid_time}' <= end_time"
                result = execute_sql(cur, sql)
                if result:
                    st.session_state.menu_index = 0
                else:
                    st.session_state.menu_index = 1
                # 删除超过MAXREVDAYS天的数据
                del_date = cal_date(-MAXREVDAYS)
                sql = f"DELETE from pa_share where pa_date <= '{del_date}'"
                execute_sql_and_commit(conn, cur, sql)
                st.set_page_config(layout="wide")
                st.rerun()
            elif not verifyUPW[0]:
                st.error("登录失败, 请检查用户名和密码, 若忘记密码请联系管理员重置")
        else:
            st.warning("请输入用户编码和密码")


def logout():
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
    st.session_state.userPwRechecked = False
    vUserEncPW = ""
    sql = f"SELECT userPassword from users where userID = {vUserName}"
    pwTable = execute_sql(cur, sql)
    if pwTable:
        vUserEncPW = pwTable[0][0]
        vUserDecPW = getUserEDKeys(vUserEncPW, "dec")
        if vUserPW == vUserDecPW:
            st.session_state.userPwRechecked = True

    return st.session_state.userPwRechecked, vUserEncPW

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
def displayAppInfo(txt_height=300):
    infoStr = open("./MyComponentsScript/glowintext.txt", "r", encoding="utf-8").read()
    infoStr = infoStr.replace("软件名称", APPNAME_CN)
    verinfo, verLM = getVerInfo()
    infoStr = infoStr.replace("软件版本", f"软件版本: {int(verinfo / 10000)}.{int((verinfo % 10000) / 100)}.{verinfo} building {verinfo}")
    infoStr = infoStr.replace("更新时间", f"更新时间: {time.strftime('%Y-%m-%d %H:%M', time.localtime(verLM))}")
    update_type, update_content = get_update_content(f"./CHANGELOG.md")
    infoStr = infoStr.replace("更新内容", f"更新内容: {update_type} - {update_content}")
    components.html(infoStr, height=txt_height)


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
        confirmPassword = st.text_input("请再次输入新密码", max_chars=8, placeholder="请确保和上一步输入的密码一致", type="password", autocomplete="new-password")
        # 确认修改按钮
        buttonSubmit = st.button("确认修改")

    # 检查原密码是否为空
    if oldPassword:
        # 验证用户原密码
        verifyUPW = verifyUserPW(st.session_state.userID, oldPassword)
        if verifyUPW[0]:
            oldPassword = verifyUPW[1]
        # 构造SQL查询语句，验证用户名和密码是否匹配
        sql = f"SELECT ID from users where userID = {st.session_state.userID} and userPassword = '{oldPassword}'"
        if execute_sql(cur, sql):
            # 检查新密码和确认密码是否填写且一致
            if newPassword and confirmPassword and newPassword != "":
                if newPassword == confirmPassword:
                    # 确认修改按钮是否被点击
                    if buttonSubmit:
                        # 加密新密码
                        newPassword = getUserEDKeys(newPassword, "enc")
                        # 构造SQL更新语句，更新用户密码
                        sql = f"UPDATE users set userPassword = '{newPassword}' where userID = {st.session_state.userID}"
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


@st.fragment
def changelog():
    changelogInfo = open("./CHANGELOG.md", "r", encoding="utf-8").read()
    st.markdown(changelogInfo)


def aboutReadme():
    st.markdown(open("./README.md", "r", encoding="utf-8").read(), unsafe_allow_html=True)

def aboutInfo():
    updatePyFileinfo()
    cols_limit = 5
    st.subheader("关于本软件", divider="rainbow")
    st.subheader(":blue[Powered by Python and Streamlit]")
    module_pack = ['Python', 'MySQL', 'Streamlit', 'Pandas', 'NumPy', 'Plotly', 'Openpyxl', 'Python-Docx', 'PyJWT']
    module_img = st.columns(cols_limit)
    for index, value in enumerate(module_pack):
        module_img[index % cols_limit].caption(value)
        module_img[index % cols_limit].image(f'./Images/logos/{value.replace(" ", "_").lower()}.png')
    display_pypi()
    if st.context.theme.type == 'dark':
        st.write("###### :violet[为了获得更好的使用体验, 请使用浅色主题]")
    sac.divider(align="center", color="gray")
    st.caption(":violet[Copyright © 2025 Simon. All rights reserved.]")
    st.image("./Images/logos/simon-logo.png", width=50)


def display_pypi():
    db_type = 'MySQL'
    cols_limit = 5
    pypi = st.columns(cols_limit)
    badge_pack = ['streamlit', 'pandas', 'NumPY', 'plotly', 'openpyxl', 'python-docx', 'PyJWT']
    verinfo, verLM = getVerInfo()
    app_version = f'{int(verinfo / 10000)}.{int((verinfo % 10000) / 100)}.{verinfo}'
    app_lm = time.strftime('%Y-%m-%d %H:%M', time.localtime(verLM))
    gen_badge(conn, cur, badge_pack, db_type, APPNAME_EN, app_version, app_lm)
    badge_pack = ['Python', db_type] + badge_pack
    for index, value in enumerate(badge_pack):
        pypi[index % cols_limit].image(f'./Images/badges/{value}-badge.svg')

    pypi[0].image(f'./Images/badges/{APPNAME_EN}-badge.svg')
    pypi[1].image(f'./Images/badges/{APPNAME_EN}-lm-badge.svg')


def get_md_task_status(task_date, userID, task_content):
    # 获取月份的第一天
    first_day_of_month = task_date.replace(day=1)
    # 使用 calendar.monthrange() 获取该月总天数，即最后一天
    _, last_day = calendar.monthrange(task_date.year, task_date.month)
    last_day_of_month = task_date.replace(day=last_day)

    sql = f"SELECT ID from clerk_work where clerk_work = '{task_content}' and task_date >= '{first_day_of_month}' and task_date <= '{last_day_of_month}' and clerk_id = {userID}"
    if not execute_sql(cur, sql):

        return True

    return False


@st.fragment
def task_input():
    st.markdown("### <font face='微软雅黑' color=red><center>工作量录入</center></font>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.markdown(f"#### 当前用户: {st.session_state.userCName}")
    with col1:
        flag_auto_task = sac.switch("自动带入默认工作", value=True, align="start", on_label="On")
    task_date = col2.date_input('工作时间', value=datetime.date.today(), max_value="today")
    confirm_btn_input = st.button("确认添加")
    ttl_score = 0
    sql = f"SELECT clerk_work, task_score, task_group from clerk_work where clerk_id = {st.session_state.userID} and task_date = '{task_date}'"
    result = execute_sql(cur, sql)
    if result:
        st.markdown("##### 已输入工作量:\n\n")
        for row in result:
            st.write(f':violet[工作类型:] {row[2]} :orange[内容:] {row[0]} :green[分值:] {row[1]}')
            ttl_score += row[1]
        st.markdown(f':red[总分:] {ttl_score}')
    else:
        st.markdown(f'###### :red[无任何记录]')
    sql = f"INSERT INTO pa_share (pa_ID, pa_content, share_score, StationCN, share_date) SELECT ID, pa_content, pa_score, '{st.session_state.StationCN}', '{task_date}' from gru_pa where StationCN = '{st.session_state.StationCN}' and pa_share = 1 and pa_content not in (SELECT pa_content from pa_share where StationCN = '{st.session_state.StationCN}' and share_date = '{task_date}')"
    execute_sql_and_commit(conn, cur, sql)
    with st.expander(f"# :green[常用]", expanded=True):
        sql = f"SELECT ID, pa_content, pa_score, pa_group, multi_score, min_days, default_task, pa_share from gru_pa where StationCN = '{st.session_state.StationCN}' and comm_task = 1 order by ID"
        rows2 = execute_sql(cur, sql)
        for row2 in rows2:
            if row2[5] == MDTASKDAYS:
                display_md_task = get_md_task_status(task_date, st.session_state.userID, row2[1])
            else:
                display_md_task = True
            if row2[6] == st.session_state.clerkType and flag_auto_task:
                auto_task = True
            else:
                auto_task = False
            if row2[5] > 0 and display_md_task:
                st.checkbox(f":red[{row2[1]} 分值:{row2[2]}]", value=auto_task, key=f"task_work_{row2[0]}")
            elif display_md_task:
                st.checkbox(f"{row2[1]} 分值:{row2[2]}", value=auto_task, key=f"task_work_{row2[0]}")
            if row2[4] == 1:
                st.number_input(f"倍数", min_value=1, max_value=10, value=1, step=1, key=f"task_multi_{row2[0]}")
    sql = f"SELECT DISTINCT(task_group) from gru_pa where StationCN = '{st.session_state.StationCN}'"
    rows = execute_sql(cur, sql)
    for row in rows:
        sql = f"SELECT ID, pa_content, pa_score, pa_group, multi_score, min_days, default_task from gru_pa where StationCN = '{st.session_state.StationCN}' and task_group = '{row[0]}' and comm_task = 0 order by ID"
        rows2 = execute_sql(cur, sql)
        if rows2:
            with st.expander(f"# :green[{row[0]}]", expanded=False):
                for row2 in rows2:
                    if row2[5] == MDTASKDAYS:
                        display_md_task = get_md_task_status(task_date, st.session_state.userID, row2[1])
                    else:
                        display_md_task = True
                    if row2[6] == st.session_state.clerkType and flag_auto_task:
                        auto_task = True
                    else:
                        auto_task = False
                    if row2[5] > 0 and display_md_task:
                        st.checkbox(f":red[{row2[1]} 分值:{row2[2]}]", value=auto_task, key=f"task_work_{row2[0]}")
                    elif display_md_task:
                        st.checkbox(f"{row2[1]} 分值:{row2[2]}", value=auto_task, key=f"task_work_{row2[0]}")
                    if row2[4] == 1:
                        st.number_input(f"倍数", min_value=1, max_value=10, value=1, step=1, key=f"task_multi_{row2[0]}")
    if confirm_btn_input:
        for key in st.session_state.keys():
            if key.startswith("task_work_") and st.session_state[key]:
                #st.write(key, st.session_state[key])
                task_id = key[key.rfind("_") + 1:]
                sql = f"SELECT pa_content, pa_score, task_group from gru_pa where ID = {task_id}"
                task_result = execute_sql(cur, sql)
                task_content, task_score, task_group = task_result[0]
                if f'task_multi_{task_id}' in st.session_state.keys():
                    task_score *= st.session_state[f'task_multi_{task_id}']
                    #st.write(f"倍数: {st.session_state[f'task_multi_{task_id}']}")
                sql = f"SELECT ID from clerk_work where task_date = '{task_date}' and clerk_id = {st.session_state.userID} and clerk_work = '{task_content}' and task_group = '{task_group}'"
                if not execute_sql(cur, sql):
                    sql = f"INSERT INTO clerk_work (task_date, clerk_id, clerk_cname, clerk_work, task_score, task_group, StationCN) VALUES ('{task_date}', {st.session_state.userID}, '{st.session_state.userCName}', '{task_content}', {task_score}, '{task_group}', '{st.session_state.StationCN}')"
                    execute_sql_and_commit(conn, cur, sql)
                    st.toast(f"工作量: [{task_content}] 分值: [{task_score}] 添加成功！")
                else:
                    st.warning(f"工作量: [{task_content}] 已存在！")


def query_task():
    st.markdown("### <font face='微软雅黑' color=red><center>工作量查询及导出</center></font>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    if st.session_state.userType == 'admin':
        userID, userCName = [], []
        sql = f"SELECT userID, userCName from users where StationCN = '{st.session_state.StationCN}' and clerk_pa = 1 order by ID"
        rows = execute_sql(cur, sql)
        for row in rows:
            userID.append(row[0])
            userCName.append(row[1])
        query_userCName = col1.selectbox("请选择查询用户", userCName)
        query_userID = userID[userCName.index(query_userCName)]
    elif st.session_state.userType == 'user':
        col1.markdown(f"#### 当前用户: {st.session_state.userCName}")
        query_userCName = st.session_state.userCName
        query_userID = st.session_state.userID
    query_date_start = col2.date_input('查询开始时间', value=datetime.date.today())
    query_date_end = col3.date_input('查询结束时间', value=datetime.date.today())
    col4, col5, col6, col7 = st.columns(4)
    confirm_btn_output = col4.button("导出为Word文件")
    if st.session_state.userType == 'admin':
        confirm_btn_output_excel = col5.button("导出统计报表")
    else:
        confirm_btn_output_excel = False
    with col6:
        flag_approved = sac.switch("仅限已核定工作", value=False, on_label="On")
    with col7:
        flag_combine = sac.switch("合并统计", value=False, on_label="On")
    if flag_combine:
        sql_task = f"SELECT clerk_work, AVG(task_score) AS avg_task_score, task_group, count(clerk_work) FROM clerk_work WHERE task_approved >= {int(flag_approved)} and task_date >= '{query_date_start}' AND task_date <= '{query_date_end}' AND clerk_id = {query_userID} GROUP BY clerk_work, task_group ORDER BY task_group"
        affix_info, color_field, score_num = "(合并统计)", "单项分值", 1
    else:
        sql_task = f"SELECT task_date, clerk_work, task_score, task_group, task_approved from clerk_work where task_approved >= {int(flag_approved)} and task_date >= '{query_date_start}' and task_date <= '{query_date_end}' and clerk_id = {query_userID} order by task_date, task_group, ID, clerk_work"
        affix_info, color_field, score_num = "", "分值", 2
    display_area = st.empty()
    rows = execute_sql(cur, sql_task)
    if rows:
        ttl_score = 0
        for row in rows:
            if flag_combine:
                ttl_score = ttl_score + row[1] * row[3]
            else:
                ttl_score += row[2]
        ttl_score = int(ttl_score)
        df = pd.DataFrame(rows, dtype=str)
        if flag_combine:
            df.columns = ["工作", "单项分值", "工作组别", "工作项数"]
            for index, value in enumerate(rows):
                df.loc[index, "单项分值"] = int(float(df["单项分值"][index]))
        else:
            df.columns = ["日期", "工作", "分值", "工作组别", "核定状态"]
            for index, value in enumerate(rows):
                df.loc[index, "分值"] = int(df["分值"][index])
                df.loc[index, "核定状态"] = "已核定" if int(df["核定状态"][index]) == 1 else "未核定"
        with display_area.container():
            st.dataframe(df.style.apply(highlight_max, subset=[color_field]))
            st.markdown(f':green[共计:] {len(rows)}项工作{affix_info} :red[总分:] {ttl_score}')
    else:
        st.info(f":red[没有查询到符合条件的记录]")
    if flag_approved:
        approved_info = "全部已审核"
    else:
        approved_info = "包含未审核"
    if confirm_btn_output:
        headerFS = 14
        contentFS = 12
        quesDOC = Document()
        quesDOC.styles["Normal"].font.name = "Microsoft YaHei"
        quesDOC.styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        pHeader = quesDOC.add_paragraph()
        pHeader.alignment = WD_ALIGN_PARAGRAPH.CENTER
        textHeader = pHeader.add_run(f"{query_userCName} {query_date_start} 至 {query_date_end} 工作量{affix_info}记录 {approved_info}", 0)
        textHeader.font.size = Pt(headerFS)
        textHeader.font.bold = True
        rows = execute_sql(cur, sql_task)
        if rows:
            i = 1
            for row in rows:
                pContent = quesDOC.add_paragraph()
                if flag_combine:
                    textContent = pContent.add_run(f"第{i}项 - 工作类型: {row[2]} 内容: {row[0]} 单项分值: {int(row[1])} 项数: {row[3]}次")
                else:
                    if row[4] == 1:
                        approved_text = "已核定"
                    else:
                        approved_text = "未核定"
                    textContent = pContent.add_run(f"第{i}项 - 日期: {row[0]} 工作类型: {row[3]} 内容: {row[1]} 分值: {row[2]} 状态: {approved_text}")
                textContent.font.size = Pt(contentFS)
                textContent.font.bold = False
                if row[score_num] < 0:
                    textContent.font.color.rgb = RGBColor(139, 0, 0)
                else:
                    textContent.font.color.rgb = RGBColor(0, 0, 0)
                i += 1
            sql = f"SELECT clerk_work, task_score, task_group from clerk_work where task_date >= '{query_date_start}' and task_date <= '{query_date_end}' and clerk_id = {query_userID} and task_score < 0 order by task_date, task_group, ID, clerk_work"
            deduct_result = execute_sql(cur, sql)
            if deduct_result:
                pContent = quesDOC.add_paragraph()
                textContent = pContent.add_run(f"其中共{len(deduct_result)}个减分项(未合并)")
                textContent.font.size = Pt(contentFS + 2)
                textContent.font.bold = True
                textContent.font.color.rgb = RGBColor(139, 0, 0)
                j = 1
                for deduct_row in deduct_result:
                    pContent = quesDOC.add_paragraph()
                    textContent = pContent.add_run(f"第{j}项 - 工作类型: {deduct_row[2]} 内容: {deduct_row[0]} 分值: {deduct_row[1]}")
                    textContent.font.size = Pt(contentFS)
                    textContent.font.bold = True
                    textContent.font.color.rgb = RGBColor(0, 0, 0)
                    j += 1
            for j in range(1):
                pContent = quesDOC.add_paragraph()
            pContent = quesDOC.add_paragraph()
            textContent = pContent.add_run(f"共计完成{i - 1}项工作{affix_info} 总分: {ttl_score}")
            textContent.font.size = Pt(contentFS + 2)
            textContent.font.bold = True
            textContent.font.color.rgb = RGBColor(155, 17, 30)
            if not flag_approved:
                for j in range(1):
                    pContent = quesDOC.add_paragraph()
                pContent = quesDOC.add_paragraph()
                textContent = pContent.add_run("核定签字:  ________")
            # 加入页码
            footer = quesDOC.sections[0].footer
            paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
            add_page_number(paragraph)
            outputFile = f"./user_pa/{query_userCName}_{query_date_start}至{query_date_end}_{time.strftime('%Y%m%d%H%M%S', time.localtime(int(time.time())))}.docx"
            if os.path.exists(outputFile):
                os.remove(outputFile)
            quesDOC.save(outputFile)
            if os.path.exists(outputFile):
                if os.path.exists(outputFile):
                    with open(outputFile, "rb") as file:
                        content = file.read()
                    file.close()
                    buttonDL = st.download_button("点击下载", content, file_name=outputFile[outputFile.rfind("/") + 1:], icon=":material/download:", type="secondary")
                    st.success(f":green[成功导出至程序目录user_pa下 {outputFile[outputFile.rfind('/') + 1:]}]")
                    if buttonDL:
                        st.toast("文件已下载至你的默认目录")
            else:
                st.error(f":red[文件导出失败]")
        else:
            st.info(f":red[没有查询到符合条件的记录]")
    elif confirm_btn_output_excel:
        display_area.empty()
        sql = f"SELECT clerk_cname, clerk_work, AVG(task_score), COUNT(clerk_work), AVG(task_score) * COUNT(clerk_work), task_group FROM clerk_work WHERE task_approved >= {int(flag_approved)} AND task_date >= '{query_date_start}' AND task_date <= '{query_date_end}' and StationCN = '{st.session_state.StationCN}' GROUP BY clerk_cname, clerk_work, task_group ORDER BY clerk_cname"
        result = execute_sql(cur, sql)
        df = pd.DataFrame(result)
        df.columns = ["姓名", "工作项", "单项分值", "项数", "单项合计", "工作组"]
        for item in ['单项分值', '项数', '单项合计']:
            df[item] = pd.to_numeric(df[item], errors='coerce').astype(int)
        # 指定需要计算小计的列
        sum_columns = ["项数", "单项合计"]
        # 调用函数添加小计行
        df_with_subtotals = add_subtotals(df, "姓名", sum_columns)
        # 修正单项分值列
        df_with_subtotals['单项分值'] = pd.to_numeric(df_with_subtotals['单项分值'], errors='coerce')
        # 显示带有小计行的 DataFrame
        st.dataframe(df_with_subtotals)
        # 导出为 Excel
        outputFile = f"./user_pa/工作量统计表_{query_date_start}至{query_date_end}_{time.strftime('%Y%m%d%H%M%S', time.localtime(int(time.time())))}.xlsx"
        if os.path.exists(outputFile):
            os.remove(outputFile)
        with pd.ExcelWriter(outputFile, engine='openpyxl') as writer:
            df_with_subtotals.to_excel(writer, sheet_name='统计表', index=False, startrow=1)
            # 插入统计时间行
            report_date_range = f"工作量统计 时间：{query_date_start} 至 {query_date_end} {approved_info}"
            # 对excel文件进行格式化
            ws = writer.sheets['统计表']
            # 设置页面为横向
            ws.page_setup.orientation = 'landscape'
            # 添加页眉/页脚（页脚居中显示页码）
            ws.oddFooter.center.text = "&P / &N"
            # 冻结前两行为标题行
            ws.print_title_rows = '1:2'
            # 合并 A1:F1，并设置样式
            ws.merge_cells("A1:F1")
            cell = ws["A1"]
            cell.value = report_date_range
            cell.font = Font(name="微软雅黑", size=14, bold=True)
            # 创建一个通用的对齐设置
            alignment = Alignment(horizontal='center', vertical='center')
            # 设置标题行样式
            for cell in ws[1]:
                cell.font = Font(name="微软雅黑", size=12, bold=True)
            # 将“小计”行设为粗体，并设置字体大小
            for row in ws.iter_rows(min_row=2):  # 跳过标题行
                if isinstance(row[0].value, str) and row[0].value.startswith('小计'):
                    for cell in row:
                        cell.font = Font(name="微软雅黑", size=12, bold=True)
            # 设置正文其他行字体
            for row in ws.iter_rows(min_row=2):
                if not (isinstance(row[0].value, str) and row[0].value.startswith('小计')):
                    for cell in row:
                        cell.font = Font(name="微软雅黑", size=12)
            # 定义边框样式
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            special_columns = {
                "A": 15
            }
            for col in ws.columns:
                max_width = 0
                column = None
                for cell in col:
                    if isinstance(cell, MergedCell):
                        continue
                    column = cell.column_letter
                    value = str(cell.value) if cell.value else ""
                    # 使用 wcswidth 精确计算显示宽度
                    width = wcswidth(value)
                    if width > max_width:
                        max_width = width
                if column:
                    if column in special_columns:
                        ws.column_dimensions[column].width = special_columns[column]
                    else:
                        ws.column_dimensions[column].width = max_width + 2
            # 添加边框到所有单元格
            for row in ws.iter_rows():
                for cell in row:
                    cell.border = thin_border
                    if row[0].row == 1:
                        cell.alignment = alignment
                    else:
                        cell.alignment = Alignment(horizontal='left', vertical='center')
        if os.path.exists(outputFile):
            with open(outputFile, "rb") as file:
                content = file.read()
            file.close()
            buttonDL = st.download_button("点击下载", content, file_name=outputFile[outputFile.rfind("/") + 1:], icon=":material/download:", type="secondary")
            st.success(f":green[成功导出至程序目录user_pa下 {outputFile[outputFile.rfind('/') + 1:]}]")
            if buttonDL:
                st.toast("文件已下载至你的默认目录")
        else:
            st.error(f":red[文件导出失败]")


def add_subtotals(df, group_column, sum_columns):
    # 创建一个空列表用于存储新的行数据
    new_rows = []
    # 遍历每个分组
    for name, group in df.groupby(group_column):
        # 计算当前分组的小计
        subtotal = group[sum_columns].sum()
        # 创建小计行
        subtotal_row = {col: "" for col in df.columns}
        subtotal_row[group_column] = f"小计: {name}"
        for col in sum_columns:
            subtotal_row[col] = subtotal[col]
        # 将小计行添加到列表中
        new_rows.append(subtotal_row)
    # 将小计行转换为 DataFrame
    subtotal_df = pd.DataFrame(new_rows)
    # 将原始 DataFrame 和 小计 DataFrame 合并
    result_df = pd.concat([df, subtotal_df], ignore_index=True)

    return result_df


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = paragraph.add_run()

    # 插入 "第 "
    run.add_text("第 ")
    # 插入 PAGE 字段
    _new_page_field(run, "PAGE")
    run.add_text(" 页 / 共 ")
    # 插入 NUMPAGES 字段
    _new_page_field(run, "NUMPAGES")
    run.add_text(" 页")


def _new_page_field(run, field_code):
    """
    插入 PAGE 或 NUMPAGES 字段到指定 run 中
    :param run: 要插入的 run 对象
    :param field_code: 'PAGE' 或 'NUMPAGES'
    """
    # 创建 fldSimple 元素
    fld_elm = OxmlElement('w:fldSimple')
    # 设置属性
    fld_elm.set(qn('w:instr'), f'{field_code} \\* MERGEFORMAT')
    # 添加到 run
    run._r.append(fld_elm)


def manual_input():
    items = []
    st.markdown("### <font face='微软雅黑' color=red><center>工作量手工录入</center></font>", unsafe_allow_html=True)
    st.markdown(f"#### 当前用户: {st.session_state.userCName}")
    sql = f"SELECT DISTINCT(task_group) from gru_pa where StationCN = '{st.session_state.StationCN}'"
    rows = execute_sql(cur, sql)
    for row in rows:
        items.append(row[0])
    col1, col2, col3 = st.columns(3)
    task_date = col1.date_input('工作时间', value=datetime.date.today(), max_value="today")
    task_group = col2.selectbox('工作组别', items, index=None, accept_new_options=True)
    task_score = col3.number_input("单项分值", min_value=1, max_value=300, value=10, step=1)
    opt1, opt2, opt3 = st.columns(3)
    if st.session_state.userType == 'admin':
        with opt1:
            flag_add_pa = sac.switch("加入固定列表", value=False, align="start", on_label="On")
        with opt2:
            flag_multi_score = sac.switch("多倍计算", value=False, align="start", on_label="On")
        with opt3:
            flag_comm_task = sac.switch("设为常用", value=False, align="start", on_label="On")
    else:
        flag_add_pa, flag_multi_score, flag_comm_task = False, False, False
    task_content = st.text_area("工作内容", height=100)
    confirm_btn_manual = st.button("确认添加")
    if task_group and task_content and confirm_btn_manual:
        sql = f"SELECT ID from clerk_work where task_date = '{task_date}' and clerk_id = {st.session_state.userID} and clerk_work = '{task_content}' and task_group = '{task_group}'"
        if not execute_sql(cur, sql):
            sql = f"INSERT INTO clerk_work (task_date, clerk_id, clerk_cname, clerk_work, task_score, task_group, StationCN) VALUES ('{task_date}', {st.session_state.userID}, '{st.session_state.userCName}', '{task_content}', {task_score}, '{task_group}', '{st.session_state.StationCN}')"
            execute_sql_and_commit(conn, cur, sql)
            st.toast(f"工作量: [{task_content}] 添加成功！")
        else:
            st.warning(f"工作量: [{task_content}] 已存在！")
        if flag_add_pa:
            sql = f"SELECT ID from gru_pa where StationCN = '{st.session_state.StationCN}' and pa_content = '{task_content}' and task_group = '{task_group}' and pa_score = {task_score}"
            if not execute_sql(cur, sql):
                sql = f"INSERT INTO gru_pa (pa_content, pa_score, pa_group, task_group, multi_score, comm_task, StationCN) VALUES ('{task_content}', {task_score}, '全员', '{task_group}', {int(flag_multi_score)}, {int(flag_comm_task)}, '{st.session_state.StationCN}')"
                execute_sql_and_commit(conn, cur, sql)
                reset_table_num(True)
                st.toast(f"工作量: [{task_content}] 添加至列表成功！")
            else:
                st.warning(f"工作量: [{task_content}] 在列表中已存在！")
    elif not task_group:
        st.warning(f"请选择工作组！")
    elif not task_content:
        st.warning(f"请输入工作内容！")

def reset_table_num(flag_force=False):
    if not flag_force:
        confirm_btn_reset = st.button("确认重置")
    else:
        confirm_btn_reset = True
    if confirm_btn_reset:
        for modify_table in ['gru_pa', 'gru_pa_deduct']:
            i, sql = 1, ''
            if modify_table == 'gru_pa':
                sql = f"SELECT ID from {modify_table} order by task_group, ID, pa_num"
            elif modify_table == 'gru_pa_deduct':
                sql = f"SELECT ID from {modify_table} order by ID"
            if sql:
                rows = execute_sql(cur, sql)
                for row in rows:
                    sql = f"UPDATE {modify_table} SET pa_num = {i} where ID = {row[0]}"
                    execute_sql_and_commit(conn, cur, sql)
                    i += 2
        if not flag_force:
            st.success("数据库ID重置成功")


#@st.fragment
def task_modify():
    st.markdown("### <font face='微软雅黑' color=red><center>记录修改</center></font>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    if st.session_state.userType == 'admin':
        userID, userCName = [], []
        sql = f"SELECT userID, userCName from users where StationCN = '{st.session_state.StationCN}' and clerk_pa = 1 order by ID"
        rows = execute_sql(cur, sql)
        for row in rows:
            userID.append(row[0])
            userCName.append(row[1])
        query_userCName = col1.selectbox("请选择查询用户", userCName)
        query_userID = userID[userCName.index(query_userCName)]
    else:
        col1.markdown(f"##### 当前用户: {st.session_state.userCName}")
        query_userID = st.session_state.userID
        query_userCName = st.session_state.userCName
    query_date_start = col2.date_input('查询开始时间', value=datetime.date.today(), max_value="today")
    query_date_end = col3.date_input('查询结束时间', value=datetime.date.today(), max_value="today")
    user_task_id_pack = []
    sql = f"SELECT clerk_work, task_score, task_group, ID from clerk_work where clerk_id = {query_userID} and task_date >= '{query_date_start}' and task_date <= '{query_date_end}'"
    result = execute_sql(cur, sql)
    for row in result:
        user_task_id_pack.append(row[3])
    task_modify_id = col4.selectbox("请选择任务ID", user_task_id_pack, index=None)
    form = st.columns(3)
    confirm_btn_delete = form[0].button("删除", type="primary")
    display_are = st.empty()
    with display_are.container(border=True):
        if result:
            ttl_score = 0
            st.markdown("##### 已输入工作量:\n\n")
            for row in result:
                st.write(f'ID:{row[3]} :violet[工作类型:] {row[2]} :orange[内容:] {row[0]} :green[分值:] {row[1]}')
                ttl_score += row[1]
            st.markdown(f':red[总分:] {ttl_score}')
        else:
            st.markdown(f'###### :red[无任何记录]')
    if task_modify_id:
        if confirm_btn_delete:
            form[1].button("确认删除", type="secondary", on_click=delete_task, args=(task_modify_id, query_userID,))
        if st.session_state.userType == 'admin':
            display_are.empty()
            modify_task(task_modify_id, query_userID)
    else:
        st.info('请选择要处理的记录ID')


def delete_task(task_modify_id, query_userID):
    if st.session_state.userType == 'admin':
        sql = f"DELETE FROM clerk_work where ID = {task_modify_id} and clerk_id = {query_userID}"
    else:
        sql = f"DELETE FROM clerk_work where ID = {task_modify_id} and clerk_id = {query_userID} and task_approved = 0"
    execute_sql_and_commit(conn, cur, sql)
    sql = f"SELECT ID FROM clerk_work where ID = {task_modify_id} and clerk_id = {query_userID}"
    if not execute_sql(cur, sql):
        st.toast(f"ID:{task_modify_id} 删除成功!")
    else:
        st.toast(f"ID:{task_modify_id} 删除失败! 被核定的记录无法删除, 请联系管理员!")


def modify_task(task_modify_id, query_userID):
    sql = f"SELECT clerk_work, task_score, task_group from clerk_work where ID = {task_modify_id} and clerk_id = {query_userID}"
    modify_pack = execute_sql(cur, sql)[0]
    form = st.columns(3)
    modify_content = form[0].text_area("请输入修改后的内容", value=modify_pack[0], height=100)
    modify_score = form[1].number_input("请输入修改后的分数", min_value=MAXDEDUCTSCORE, max_value=1000, value=modify_pack[1], step=1, placeholder="最大1000")
    sql = f"UPDATE clerk_work SET clerk_work = '{modify_content}', task_score = {modify_score} where ID = {task_modify_id} and clerk_id = {query_userID}"
    execute_sql_and_commit(conn, cur, sql)
    sql = f"SELECT ID from clerk_work where clerk_work = '{modify_content}' and task_score = {modify_score} and ID = {task_modify_id} and clerk_id = {query_userID}"
    if execute_sql(cur, sql):
        pass
        #st.toast(f"ID:{task_modify_id} 修改成功!")
    else:
        st.toast(f"ID:{task_modify_id} 修改失败! 被核定的记录无法修改, 请联系管理员!")

@st.fragment
def check_data():
    st.markdown("### <font face='微软雅黑' color=red><center>数据检查与核定</center></font>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    userID, userCName = [], []
    sql = f"SELECT userID, userCName from users where StationCN = '{st.session_state.StationCN}' and clerk_pa = 1 order by ID"
    rows = execute_sql(cur, sql)
    for row in rows:
        userID.append(row[0])
        userCName.append(row[1])
    query_date_start = col1.date_input('查询开始时间', value=datetime.date.today())
    query_date_end = col2.date_input('查询结束时间', value=datetime.date.today())
    dur_time = query_date_end - query_date_start
    st.markdown(f'##### 统计周期: {dur_time.days}天')
    confirm_btn_check = col1.button("检查")
    confirm_btn_approv = col2.button("核定")
    if confirm_btn_check:
        for index, value in enumerate(userID):
            sql = f"SELECT pa_content, min_days from gru_pa where StationCN = '{st.session_state.StationCN}' and min_days > 0 order by min_days DESC"
            rows = execute_sql(cur, sql)
            for row in rows:
                sql = f"SELECT count(ID) from clerk_work where clerk_work = '{row[0]}' and clerk_id = {value} and task_date >= '{query_date_start}' and task_date <= '{query_date_end}'"
                task_count = execute_sql(cur, sql)[0][0]
                if task_count > 1 and task_count > dur_time.days / row[1]:
                    st.warning(f"用户: {userCName[index]} 工作: [{row[0]}] 应该 1次/{row[1]}天, 实际: {task_count}次 已超量, 请检查记录！")
    else:
        task_pack = []
        sql = f"SELECT ID, clerk_cname, task_date, clerk_work, task_score, task_group from clerk_work where StationCN = '{st.session_state.StationCN}' and task_approved = 0 and task_date >= '{query_date_start}' and task_date <= '{query_date_end}' order by task_date, task_group, clerk_work, clerk_cname, task_score"
        result = execute_sql(cur, sql)
        if result:
            for row in result:
                task_pack.append(f'{str(row[2])[5:]} {row[1]} {row[5]} 内容:{row[3]} 分值:{row[4]} ID:{row[0]}')
            approve_pack = sac.transfer(items=task_pack, label='工作量核定', titles=['项目'], reload=True, align='center', search=True, pagination=True, use_container_width=True)
            if confirm_btn_approv and approve_pack:
                for each in approve_pack:
                    approve_id = each[each.find('ID:') + 3:].strip()
                    sql = f"UPDATE clerk_work SET task_approved = 1 where ID = {approve_id}"
                    execute_sql_and_commit(conn, cur, sql)
                    st.success(f"**{each} 工作量已核定**")
        else:
            st.markdown(f'###### :red[无任何记录]')

def resetPassword():
    # 显示副标题和分隔线
    st.subheader(":orange[密码重置]", divider="red")
    if st.session_state.userPwRechecked:
        # 显示重置用户信息提示
        st.write(":red[**重置用户信息**]")
        # 获取用户编码
        userID, userCName = [], []
        sql = f"SELECT userID, userCName from users where StationCN = '{st.session_state.StationCN}' order by ID"
        rows = execute_sql(cur, sql)
        for row in rows:
            userID.append(row[0])
            userCName.append(row[1])
        query_userCName = st.selectbox("请选择用户", userCName, index=None)
        if query_userCName is not None:
            rUserName = userID[userCName.index(query_userCName)]
        if query_userCName is not None:
            # 创建重置按钮
            btnResetUserPW = st.button("重置", type="primary")
            if btnResetUserPW:
                st.button("确认重置", type="secondary", on_click=actionResetUserPW, args=(rUserName,))
                st.session_state.userPwRechecked = False
    else:
        vUserPW = st.text_input("请输入密码", max_chars=8, placeholder="请输入管理员密码, 以验证身份", type="password", autocomplete="off")
        # 检查是否输入了密码
        if vUserPW:
            # 验证密码
            if verifyUserPW(st.session_state.userID, vUserPW)[0]:
                st.session_state.userPwRechecked = True
                st.rerun()
            # 如果密码错误，显示错误提示
            else:
                st.error("密码错误, 请重新输入")
                st.session_state.userPwRechecked = False


def actionResetUserPW(rUserName):
    rInfo = ""

    # 获取用户加密密钥
    resetPW = getUserEDKeys("1234", "enc")
    # 构建 SQL 更新语句
    sql = f"UPDATE users SET userPassword = '{resetPW}' where userID = {rUserName}"
    # 执行 SQL 并提交
    execute_sql_and_commit(conn, cur, sql)
    # 更新信息，表示密码已重置
    rInfo += "密码已重置为: 1234"

    st.success(f"**{rInfo}**")


def deduction_input():
    st.markdown("### <font face='微软雅黑' color=red><center>减分项录入</center></font>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    userID, userCName, pa_deduct, pa_deduct_score = [], [], [], []
    sql = f"SELECT userID, userCName from users where StationCN = '{st.session_state.StationCN}' and clerk_pa = 1 order by ID"
    rows = execute_sql(cur, sql)
    for row in rows:
        userID.append(row[0])
        userCName.append(row[1])
    deduct_userCName = col1.selectbox("请选择用户", userCName)
    deduct_userID = userID[userCName.index(deduct_userCName)]
    deduct_date = col2.date_input("请选择日期", datetime.date.today(), max_value="today")
    sql = f"SELECT pa_content, pa_score from gru_pa_deduct where StationCN = '{st.session_state.StationCN}' order by pa_score, pa_content"
    rows = execute_sql(cur, sql)
    for row in rows:
        pa_deduct.append(row[0])
        pa_deduct_score.append(row[1])
    task_deduct = col1.selectbox("扣分项", pa_deduct, index=None)
    if task_deduct:
        task_score = pa_deduct_score[pa_deduct.index(task_deduct)]
    else:
        task_score = -50
    deduct_score = col2.number_input("扣分", min_value=MAXDEDUCTSCORE, max_value=-10, value=task_score, step=10)
    deduct_content = col1.text_area("自定义扣分项内容", value=task_deduct, placeholder="可选择固定扣分项后修改", height=100)
    confirm_btn_add = st.button("确认添加")
    if confirm_btn_add:
        #st.write(deduct_content, deduct_score, deduct_userID, deduct_userCName, deduct_date)
        if deduct_content:
            sql = f"INSERT INTO clerk_work (task_date, clerk_id, clerk_cname, clerk_work, task_score, task_group, task_approved, StationCN) VALUES ('{deduct_date}', {deduct_userID}, '{deduct_userCName}', '{deduct_content}', {deduct_score}, '扣分', 1, '{st.session_state.StationCN}')"
            execute_sql_and_commit(conn, cur, sql)
            st.success(f"{deduct_userCName} 扣分项添加成功")
            sql = f"SELECT ID from gru_pa_deduct where pa_content = '{deduct_content}' and pa_score = {deduct_score} and StationCN = '{st.session_state.StationCN}'"
            if not execute_sql(cur, sql):
                sql = f"INSERT INTO gru_pa_deduct(pa_content, pa_score, StationCN) VALUES ('{deduct_content}', {deduct_score}, '{st.session_state.StationCN}')"
                execute_sql_and_commit(conn, cur, sql)
                st.success(f"{deduct_content} 扣分项已添加至固定列表")
                reset_table_num(True)
        else:
            st.error("请输入扣分项内容")


def highlight_max(x, forecolor='black', backcolor="#D61919"):
    is_max = x == x.max()

    return [f'color: {forecolor}; background-color: {backcolor}' if v else '' for v in is_max]


def gen_chart():
    st.markdown("### <font face='微软雅黑' color=red><center>趋势图</center></font>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    tab1, tab2 = st.tabs(["📈 图表", "🗃 数据"])
    if st.session_state.userType == 'admin':
        userID, userCName = [], []
        sql = f"SELECT userID, userCName from users where StationCN = '{st.session_state.StationCN}' and clerk_pa = 1 order by ID"
        rows = execute_sql(cur, sql)
        for row in rows:
            userID.append(row[0])
            userCName.append(row[1])
        query_userCName = col1.selectbox("请选择查询用户", userCName)
        query_userID = userID[userCName.index(query_userCName)]
    elif st.session_state.userType == 'user':
        col1.markdown(f"#### 当前用户: {st.session_state.userCName}")
        query_userCName = st.session_state.userCName
        query_userID = st.session_state.userID
    query_date_start = col2.date_input('查询开始时间', value=datetime.date.today())
    query_date_end = col3.date_input('查询结束时间', value=datetime.date.today())
    if st.session_state.userType == 'admin':
        with col1:
            flag_all_user = sac.switch("查询所有用户", value=False, align="start", on_label="On")
    else:
        flag_all_user = False
    with col2:
        flag_approved = sac.switch("仅限已核定工作", value=False, on_label="On")
    if not flag_all_user:
        userID = [query_userID]
        userCName = [query_userCName]
    with col3:
        #dur_time = query_date_end - query_date_start
        chart_type_pack = ['折线图', '中位数图', '旭日图', '矩阵树图', '饼图', '日历热度图']
        if len(userID) == 1:
            chart_type_pack = chart_type_pack + ['柱状图(分组)', '柱状图(堆叠)', '漏斗图']
        chart_type = st.selectbox("图表类型", chart_type_pack, index=1)
    min_value, max_value = 1000, 0
    raws_data, df = [], []
    charArea = tab1.empty()
    if chart_type == '折线图':
        with tab1:
            # 双Y轴折线图
            with charArea.container(border=True):
                fig = go.Figure()
                for index, value in enumerate(userID):
                    hot_value, hot_date, temp_value_pack = [], [], []
                    sql = f"SELECT task_date, sum(task_score) from clerk_work where task_approved >= {int(flag_approved)} and clerk_id = {value} and task_date >= '{query_date_start}' and task_date <= '{query_date_end}' GROUP BY task_date order by task_date"
                    result = execute_sql(cur, sql)
                    for each in result:
                        hot_date.append(each[0])
                        hot_value.append(int(each[1]))
                        raws_data.append([userCName[index], each[0], int(each[1])])
                    temp_value_pack = hot_value
                    if temp_value_pack:
                        temp_value_pack.sort()
                        if temp_value_pack[0] < min_value:
                            min_value = temp_value_pack[0]
                        if temp_value_pack[-1] > max_value:
                            max_value = temp_value_pack[-1]
                        #st.write(min_value, max_value, hot_value)
                        if temp_value_pack[-1] < max_value / 2:
                            yax = 'y2'
                        else:
                            yax = 'y'
                        fig.add_trace(
                            go.Scatter(name=f"{userCName[index]}",
                                        x=hot_date,
                                        y=hot_value,
                                        mode="markers+lines+text",
                                        text=[
                                            format(round(x, 2), ",")
                                            for x in hot_value
                                        ],
                                        yaxis=yax,
                                        textposition="top center"))
                if raws_data:
                    fig.update_layout(
                        title="工作量",
                        xaxis=dict(title="日期"),
                        yaxis=dict(title="主轴",
                                    rangemode="normal"),
                        template="simple_white",
                        font=dict(size=CHARTFONTSIZE),
                        yaxis2=dict(
                            title="",
                            overlaying='y',
                            side='right'))
                    st.plotly_chart(fig)
                    df = pd.DataFrame(raws_data, columns=["姓名", "日期", "合计分值"])
                else:
                    st.info("没有查询到符合条件的记录")
    elif chart_type.startswith("柱状图"):
        if "分组" in chart_type:
            bar_type = "group"
        elif "堆叠" in chart_type:
            bar_type = "stack"
        else:
            bar_type = "relative"
        with tab1:
            with charArea.container(border=True):
                for index, value in enumerate(userID):
                    sql = f"SELECT task_date, task_group, sum(task_score) from clerk_work where task_approved >= {int(flag_approved)} and clerk_id = {value} and task_date >= '{query_date_start}' and task_date <= '{query_date_end}' GROUP BY task_date, task_group order by task_date"
                    result = execute_sql(cur, sql)
                    for each in result:
                        raws_data.append([userCName[index], each[0], each[1], int(each[2])])
                if raws_data:
                    df = pd.DataFrame(raws_data, columns=["姓名", "日期", "工作组别", "合计分值"])
                    # 使用 Plotly Express 生成分组柱状图
                    fig = px.bar(
                        df,
                        x="日期",
                        y="合计分值",
                        color="工作组别",
                        text="合计分值",
                        title="按日期和工作组别统计",
                        labels={"合计分值": "总分", "日期": "工作日期", "工作组别": "任务组"},
                        barmode=bar_type
                    )
                    # 调整样式
                    fig.update_traces(textposition='outside')
                    fig.update_layout(
                        xaxis_tickangle=-45,
                        template="simple_white",
                        font=dict(size=CHARTFONTSIZE)
                    )
                    st.plotly_chart(fig)
                else:
                    st.info("没有查询到符合条件的记录")
    elif chart_type == "日历热度图":
        with tab1:
            with charArea.container(border=True):
                query_date_start = f'{datetime.datetime.now().year}-01-01'
                query_date_end = f'{datetime.datetime.now().year}-12-31'
                cal_data = []
                sql = f"SELECT task_date, sum(task_score) from clerk_work where StationCN = '{st.session_state.StationCN}' and task_date >= '{query_date_start}' and task_date <= '{query_date_end}' group by task_date"
                rows = execute_sql(cur, sql)
                for row in rows:
                    raws_data.append([row[0], int(row[1])])
                    temp = {'value': int(row[1]), 'day': row[0].strftime("%Y-%m-%d")}
                    cal_data.append(temp)
                if raws_data:
                    df = pd.DataFrame(raws_data, columns=["日期", "合计分值"])
                    calendar_chart = {
                        "data": cal_data,
                        "layout": {
                            "title": "日历热度图",
                            "type": "calendar",
                            "height": 500,
                            "from": query_date_start,
                            "to": query_date_end,
                            "emptyColor": "#eeeeee",
                            "colors": ["#61cdbb", "#97e3d5", "#e8c1a0", "#f47560"],
                            "margin": {"top": 40, "right": 40, "bottom": 40, "left": 40},
                            "yearSpacing": 40,
                            "monthBorderColor": "#ffffff",
                            "dayBorderWidth": 2,
                            "dayBorderColor": "#ffffff",
                            "legends": [
                                {
                                    "anchor": "bottom-right",
                                    "direction": "row",
                                    "translateY": 36,
                                    "itemCount": 4,
                                    "itemWidth": 42,
                                    "itemHeight": 36,
                                    "itemsSpacing": 14,
                                    "itemDirection": "right-to-left",
                                }
                            ],
                        },
                    }
                    nc.nivo_chart(data=calendar_chart["data"], layout=calendar_chart["layout"])
                else:
                    st.info("没有查询到符合条件的记录")
    elif chart_type == "漏斗图":
        with tab1:
            with charArea.container(border=True):
                for index, value in enumerate(userID):
                    sql = f"SELECT task_date, task_group, sum(task_score) from clerk_work where task_approved >= {int(flag_approved)} and clerk_id = {value} and task_date >= '{query_date_start}' and task_date <= '{query_date_end}' GROUP BY task_date, task_group order by sum(task_score) DESC"
                    result = execute_sql(cur, sql)
                    for each in result:
                        raws_data.append([userCName[index], each[0], each[1], int(each[2])])
                if raws_data:
                    df = pd.DataFrame(raws_data, columns=["姓名", "日期", "工作组别", "合计分值"])
                    # 按工作组别统计总分并按降序排序
                    funnel_data = df.groupby("工作组别")["合计分值"].sum().reset_index()
                    funnel_data = funnel_data.sort_values(by="合计分值", ascending=False)
                    # 生成漏斗图
                    fig = px.funnel(
                        funnel_data,
                        x="合计分值",
                        y="工作组别",
                        title="工作量(日期合并)",
                        labels={"合计分值": "总分", "工作组别": "任务组别"},
                        color_discrete_sequence=px.colors.qualitative.Prism
                    )
                    # 放大图表整体字体
                    fig.update_layout(font=dict(size=CHARTFONTSIZE))
                    st.plotly_chart(fig)
                else:
                    st.info("没有查询到符合条件的记录")
    elif chart_type == "饼图":
        with tab1:
            with charArea.container(border=True):
                for index, value in enumerate(userID):
                    sql = f"SELECT task_group, sum(task_score) from clerk_work where task_approved >= {int(flag_approved)} and clerk_id = {value} and task_date >= '{query_date_start}' and task_date <= '{query_date_end}' GROUP BY task_group order by sum(task_score) DESC"
                    result = execute_sql(cur, sql)
                    for each in result:
                        raws_data.append([userCName[index], each[0], int(each[1])])
                if raws_data:
                    df = pd.DataFrame(raws_data, columns=["姓名", "工作组别", "合计分值"])
                    if len(userID) > 1:
                        pie_data = df.groupby("工作组别")["合计分值"].sum().reset_index()
                    else:
                        pie_data = df.copy()
                    # 计算总和
                    total = pie_data['合计分值'].sum()
                    # 添加百分比列
                    pie_data['百分比'] = (pie_data['合计分值'] / total) * 100
                    # 保留所有原始条目，不进行合并
                    final_data = pie_data.copy()
                    fig = px.pie(
                        final_data,
                        names="工作组别",
                        values="合计分值",
                        title="工作量(日期合并)",
                        hole=0.2,
                        hover_data=["合计分值"],
                        labels={"合计分值": "总分", "工作组别": "任务组别"},
                        color_discrete_sequence=px.colors.qualitative.Prism
                    )
                    fig.update_traces(textposition='outside', textinfo='percent+label')
                    fig.update_layout(showlegend=False, font=dict(size=12))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("没有查询到符合条件的记录")
    elif chart_type == "旭日图":
        with tab1:
            with charArea.container(border=True):
                for index, value in enumerate(userID):
                    # 查询每个用户的任务分值按工作组别汇总
                    sql = f"SELECT task_group, sum(task_score) from clerk_work where task_approved >= {int(flag_approved)} and clerk_id = {value} and task_date >= '{query_date_start}' and task_date <= '{query_date_end}' GROUP BY task_group order by sum(task_score) DESC"
                    result = execute_sql(cur, sql)
                    for each in result:
                        raws_data.append([userCName[index], each[0], int(each[1])])
                if raws_data:
                    # 构造 DataFrame
                    df = pd.DataFrame(raws_data, columns=["姓名", "工作组别", "合计分值"])
                    if len(userID) > 1:
                        sunburst_data = df.groupby(["工作组别", "姓名"], as_index=False)["合计分值"].sum()
                    else:
                        sunburst_data = df.copy()
                    # 绘制旭日图
                    fig = px.sunburst(
                        sunburst_data,
                        path=['工作组别', '姓名'],
                        values='合计分值',
                        color='合计分值',
                        hover_data=['合计分值'],
                        color_continuous_scale='Plasma',
                        title="工作量（工作组别 → 用户）",
                    )
                    fig.update_layout(margin=dict(t=50, l=0, r=0, b=0), font=dict(size=CHARTFONTSIZE))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("没有查询到符合条件的记录")
    elif chart_type == "矩阵树图":
        with tab1:
            with charArea.container(border=True):
                for index, value in enumerate(userID):
                    # 查询每个用户的任务分值按工作组别汇总
                    sql = f"SELECT task_group, sum(task_score) from clerk_work where task_approved >= {int(flag_approved)} and clerk_id = {value} and task_date >= '{query_date_start}' and task_date <= '{query_date_end}' GROUP BY task_group order by sum(task_score) DESC"
                    result = execute_sql(cur, sql)
                    for each in result:
                        raws_data.append([userCName[index], each[0], int(each[1])])
                if raws_data:
                    df = pd.DataFrame(raws_data, columns=["姓名", "工作组别", "合计分值"])
                    if len(userID) > 1:
                        treemap_data = df.groupby(["工作组别", "姓名"], as_index=False)["合计分值"].sum()
                    else:
                        treemap_data = df.copy()
                    fig = px.treemap(
                        treemap_data,
                        path=['工作组别', '姓名'],
                        values='合计分值',
                        color='合计分值',
                        color_continuous_scale='Plasma',
                        title="工作量（工作组别 → 用户）",
                        hover_data={'合计分值': True}
                    )
                    fig.update_layout(margin=dict(t=50, l=0, r=0, b=0), font=dict(size=CHARTFONTSIZE))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("没有查询到符合条件的记录")
    elif chart_type == "中位数图":
        with tab1:
            with charArea.container(border=True):
                sql = f"SELECT clerk_cname, sum(task_score) from clerk_work where StationCN = '{st.session_state.StationCN}' and task_approved >= {int(flag_approved)} and task_date >= '{query_date_start}' and task_date <= '{query_date_end}' GROUP BY clerk_cname order by clerk_cname"
                result = execute_sql(cur, sql)
                for each in result:
                    raws_data.append([each[0], int(each[1])])
                if raws_data:
                    df = pd.DataFrame(raws_data, columns=["姓名", "合计分值"])
                    # 计算中位数
                    median_score = np.nanmedian(df["合计分值"])
                    # 生成柱状图
                    fig = px.bar(df, x="姓名", y="合计分值", text_auto=True,
                                title="工作量分值", labels={"姓名": "员工姓名", "合计分值": "总分值"})
                    # 添加中位数水平线
                    fig.add_shape(type='line',
                                x0=-0.5, x1=len(df) - 0.5,
                                y0=median_score, y1=median_score,
                                line=dict(color='red', dash='dash'))
                    fig.update_layout(font=dict(size=CHARTFONTSIZE))
                    # 将中位数标注移到线上方，并调整字体大小
                    fig.add_annotation(x=len(df) - 1, y=median_score + 12,  # 向上偏移
                                    text=f'中位数: {median_score:.0f}',
                                    showarrow=False,
                                    font=dict(color='red', size=CHARTFONTSIZE + 2),
                                    xanchor='right',
                                    yanchor='bottom')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("没有查询到符合条件的记录")
    if raws_data:
        tab2.write(df)
    else:
        tab2.info("没有查询到符合条件的记录")


def input_public_notice():
    st.markdown("### <font face='微软雅黑' color=green><center>公告发布</center></font>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    query_date_start = col1.date_input('公告开始时间', value=datetime.date.today(), min_value="today", max_value=datetime.date.today() + datetime.timedelta(days=180))
    query_date_end = col2.date_input('公告结束时间', value=datetime.date.today(), min_value="today", max_value=datetime.date.today() + datetime.timedelta(days=180))
    confirm_btn_public = st.button('发布')
    display_area = st.empty()
    with display_area.container():
        public_text = st.text_area('请输入公告内容')
    if confirm_btn_public:
        now = datetime.datetime.now()
        pub_time = now.strftime("%Y-%m-%d %H:%M:%S")
        if public_text:
            sql = f"SELECT ID from notices where StationCN = '{st.session_state.StationCN}' and notice = '{public_text}' and start_time <= '{query_date_start}' and end_time >= '{query_date_end}'"
            if not execute_sql(cur, sql):
                sql = f"INSERT INTO notices (notice, start_time, end_time, publisher, pub_time, StationCN) VALUES ('{public_text}', '{query_date_start}', '{query_date_end}', '{st.session_state.userCName}', '{pub_time}', '{st.session_state.StationCN}')"
                execute_sql_and_commit(conn, cur, sql)
                display_area.empty()
                st.success('公告添加成功')
        else:
            st.warning('请输入公告内容')


def public_notice():
    st.markdown("### <font face='微软雅黑' color=red><center>站内公告</center></font>", unsafe_allow_html=True)
    now = datetime.datetime.now()
    valid_time = now.strftime("%Y-%m-%d")
    sql = f"SELECT notice from notices where StationCN = '{st.session_state.StationCN}' and start_time >= '{valid_time}' and '{valid_time}' <= end_time"
    result = execute_sql(cur, sql)
    if result:
        for index, row in enumerate(result, start=1):
            st.markdown(f'##### 第{index}条. {row[0]}')
    else:
        st.info("暂无公告")


@st.fragment
def displayBigTime():
    components.html(open("./MyComponentsScript/Clock-Big.txt", "r", encoding="utf-8").read(), height=140)


def aboutLicense():
    st.subheader("License", divider="green")
    st.markdown(open("./LICENSE", "r", encoding="utf-8").read())


def display_weather_gd(city_code):
    weather_info = get_city_weather(city_code)
    if weather_info:
        st.markdown(f"#### {weather_info['city']} - 实时天气")
        #st.markdown(f"<div style='text-align:center; font-family:微软雅黑; color:#008080; font-size:18px;'>地区: {weather_info['city']} 天气: {weather_info['weather_icon']} 温度: {weather_info['temperature']} ℃ {weather_info['temp_icon']}</div>", unsafe_allow_html=True)
        #st.markdown(f"<div style='text-align:center; font-family:微软雅黑; color:#008080; font-size:18px;'>风向: {weather_info['winddirection']} 风力: {weather_info['windpower']} km/h {weather_info['wind_icon']} 湿度: {weather_info['humidity']}% {weather_info['humidity_icon']}</div>", unsafe_allow_html=True)
        wcol = st.columns(3)
        #wcol[0].metric('地区', weather_info['city'])
        wcol[0].metric(label='天气',value=f"{weather_info['weather']} {weather_info['weather_icon']}")
        wcol[1].metric(label='温度', value=f"{weather_info['temperature']} ℃ {weather_info['temp_icon']}")
        wcol[2].metric(label='湿度', value=f"{weather_info['humidity']}% {weather_info['humidity_icon']}")
        wcol[0].metric(label='风向', value=f"{weather_info['winddirection']}风")
        wcol[1].metric(label='风力', value=f"{weather_info['windpower']} km/s {weather_info['wind_icon']}")
        wcol[2].metric(label='数据更新时间', value=f"{weather_info['reporttime'][2:]}")
        # 设置度量卡片的样式
        style_metric_cards(border_left_color="#8581d9")


def display_history_weather():
    st.markdown("### <font face='微软雅黑' color=green><center>历史天气</center></font>", unsafe_allow_html=True)
    city_code = st.session_state.hf_city_code
    city_name = st.session_state.cityname
    sql = f"SELECT MIN(weather_date) from weather_history where city_code = '{city_code}'"
    date_result = execute_sql(cur, sql)
    if date_result:
        query_min_date = date_result[0][0]
    else:
        query_min_date = datetime.datetime.now() - datetime.timedelta(days=10)
        query_min_date = query_min_date.strftime('%Y-%m-%d')
    query_date = st.date_input('查询时间', value=datetime.date.today() - datetime.timedelta(days=1), min_value=query_min_date, max_value=datetime.date.today() - datetime.timedelta(days=1))
    query_date_convert = str(query_date).replace('-', '')
    display_area = st.empty()
    sql = f"SELECT sunrise, sunset, moonrise, moonset, moonPhase, tempMax, tempMin, humidity, pressure, moon_icon, temp_icon, humidity_icon, temp_hourly, windspeed_hourly, humidity_hourly, weather_icon_hourly, precip_hourly, windscale_hourly FROM weather_history WHERE city_code = '{city_code}' and weather_date = '{query_date}'"
    cur.execute(sql)
    result = cur.fetchone()
    if result:
        weather_info = {
                'sunrise': result[0],
                'sunset': result[1],
                'moonrise': result[2],
                'moonset': result[3],
                'moonPhase': result[4],
                'tempMax': result[5],
                'tempMin': result[6],
                'humidity': result[7],
                'pressure': result[8],
                'moon_icon': result[9],
                'temp_icon': result[10],
                'humidity_icon': result[11],
                'temp_hourly': result[12],
                'windspeed_hourly': result[13],
                'humidity_hourly': result[14],
                'weather_icon_hourly': result[15],
                'precip_hourly': result[16],
                'windscale_hourly': result[17]
            }
    else:
        weather_info = get_city_history_weather(city_code, query_date_convert)
        sql = f"INSERT INTO weather_history (weather_date, city_code, city_name, sunrise, sunset, moonrise, moonset, moonPhase, tempMax, tempMin, humidity, pressure, moon_icon, temp_icon, humidity_icon, temp_hourly, weather_hourly, precip_hourly, windir_hourly, windscale_hourly, windspeed_hourly, humidity_hourly, pressure_hourly, weather_icon_hourly) VALUES ('{query_date}', '{city_code}', '{city_name}', '{weather_info['sunrise']}', '{weather_info['sunset']}', '{weather_info['moonrise']}', '{weather_info['moonset']}', '{weather_info['moonPhase']}', '{weather_info['tempMax']}', '{weather_info['tempMin']}', '{weather_info['humidity']}', '{weather_info['pressure']}', '{weather_info['moon_icon']}', '{weather_info['temp_icon']}', '{weather_info['humidity_icon']}', '{weather_info['temp_hourly']}', '{weather_info['weather_hourly']}', '{weather_info['precip_hourly']}', '{weather_info['windir_hourly']}', '{weather_info['windscale_hourly']}', '{weather_info['windspeed_hourly']}', '{weather_info['humidity_hourly']}', '{weather_info['pressure_hourly']}', '{weather_info['weather_icon_hourly']}')"
        execute_sql_and_commit(conn, cur, sql)
    if weather_info:
        with display_area.container(border=True):
            weather_icon_pack, pre_weather_icon, weather_text = weather_info['weather_icon_hourly'].split('/'), '', ''
            precip_pack = [float(value) for value in weather_info['precip_hourly'].split('/')]
            windscale_pack = [int(value) for value in weather_info['windscale_hourly'].split('/')]
            humidity_pack = [int(value) for value in weather_info['humidity_hourly'].split('/')]
            windspeed_pack = [int(value) for value in weather_info['windspeed_hourly'].split('/')]
            for index, value in enumerate(weather_icon_pack):
                if value != pre_weather_icon:
                    weather_text = weather_text + str(index) + '点 ' + value + ' '
                    pre_weather_icon = value
            windscale_pack.sort(reverse=True)
            windspeed_pack.sort(reverse=True)
            humidity_pack.sort(reverse=True)
            st.markdown(f"##### 地区: {city_name} 温度: {weather_info['tempMax']} - {weather_info['tempMin']} ℃ {weather_info['temp_icon']}")
            st.markdown(f"##### 天气: {weather_text.strip()}")
            st.markdown(f"##### 降水: {int(sum(precip_pack))} mm 最大风力: {windscale_pack[0]} kts/ {windspeed_pack[0]} km/h")
            st.markdown(f"##### 湿度: {humidity_pack[0]} - {humidity_pack[-1]}% {weather_info['humidity_icon']} 气压: {weather_info['pressure']} hPa")
            st.markdown(f"##### 日升: {weather_info['sunrise']} 日落: {weather_info['sunset']}")
            st.markdown(f"##### 月升: {weather_info['moonrise']} 月落: {weather_info['moonset']} 月相: {weather_info['moonPhase']} {weather_info['moon_icon']}")
        chart_col = st.columns(2)
        with chart_col[0]:
            plot_wind_speed_curve(weather_info['temp_hourly'].split('/'), weather_info['windspeed_hourly'].split('/'))
        with chart_col[1]:
            plot_data_curve(weather_info['humidity_hourly'].split('/'))
    else:
        st.info("没有查询历史天气记录")

def plot_wind_speed_curve(hourly_data1, hourly_data2):
    df1 = pd.DataFrame({
        '小时': range(len(hourly_data1)),
        '温度': hourly_data1
    })
    df2 = pd.DataFrame({
        '小时': range(len(hourly_data2)),
        '风力': hourly_data2
    })

    # 使用Plotly Express创建双Y轴折线图
    fig = make_subplots(specs=[[{'secondary_y': True}]])

    # 添加第一个数据集到图表
    fig.add_trace(
        go.Scatter(x=df1['小时'], y=df1['温度'], name='温度', line=dict(color='red')),
        secondary_y=False,
    )

    # 添加第二个数据集到图表
    fig.add_trace(
        go.Scatter(x=df2['小时'], y=df2['风力'], name='风力', line=dict(color='green', dash='dash')),
        secondary_y=True,
    )

    # 设置图表标题和标签
    fig.update_layout(title_text='温度/风力曲线')
    fig.update_xaxes(title_text='小时')
    fig.update_yaxes(title_text='温度 (℃)', secondary_y=False)
    fig.update_yaxes(title_text='风力 (m/s)', secondary_y=True)

    # 显示图表
    chart = st.empty()
    with chart.container(border=True):
        st.plotly_chart(fig, use_container_width=True)


def plot_data_curve(hourly_data):
    # 创建一个包含小时和温度的数据框
    df = pd.DataFrame({
        '小时': range(len(hourly_data)),
        '湿度': hourly_data
    })

    # 使用Plotly Express创建折线图
    fig = px.line(df, x='小时', y='湿度', title='湿度曲线')
    fig.update_yaxes(title_text='湿度 (%)')
    # 显示图表
    chart = st.empty()
    with chart.container(border=True):
        st.plotly_chart(fig, use_container_width=True)


def display_weather_hf(city_code):
    weather_info = get_city_now_weather(city_code)
    city_name = st.session_state.cityname
    if weather_info:
        if weather_info['cloud']:
            cloud = weather_info['cloud']
        else:
            cloud = 'N/A'
        if float(weather_info['precip']) > 0.0:
            precip = '☔'
        else:
            precip = '🌂'
        weather_icon_html = f"""
            <html>
            <head>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/qweather-icons@1.7.0/font/qweather-icons.css">
            </head>
                <i class="qi-{weather_info['weather_icon_id']}"></i>
            </html>
        """
        icon_size = 24
        weather_info['winddir_icon_html'] = weather_info['winddir_icon_html'].replace('icon_size', f'{icon_size}')
        #st.markdown(f"<div style='text-align:center; font-family:微软雅黑; color:#008080; font-size:18px;'>地区: {city_name} 天气: {weather_info['weather_icon']} 温度: {weather_info['temp']} ℃ {weather_info['temp_icon']} / 体感温度: {weather_info['feelslike']} ℃ {weather_info['feelslike_icon']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center; font-family:微软雅黑; color:#008080; font-size:18px;'>地区: {city_name} 天气: {weather_info['weather']} {weather_icon_html} 🌡️温度: {weather_info['temp']}℃ / 🧘温度: {weather_info['feelslike']}℃ {weather_info['feelslike_icon']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center; font-family:微软雅黑; color:#008080; font-size:18px;'>降水: {weather_info['precip']} mm {precip} 能见度: {weather_info['vis']} km 云量: {cloud}% 大气压强: {weather_info['pressure']} hPa</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center; font-family:微软雅黑; color:#008080; font-size:18px;'>风向: {weather_info['winddir']} {weather_info['winddir_icon_html']} 风力: {weather_info['windscale']} 级 / {weather_info['windspeed']} km/h {weather_info['wind_icon']} 湿度: {weather_info['humidity']}% {weather_info['humidity_icon']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center; font-family:微软雅黑; color:#000000; font-size:14px;'>数据更新时间: {weather_info['obstime'][2:-6].replace('T', ' ')}</div>", unsafe_allow_html=True)


def display_weather_hf_metric(city_code):
    weather_info = get_city_now_weather(city_code)
    city_name = st.session_state.cityname
    if weather_info:
        if weather_info['cloud']:
            cloud = weather_info['cloud']
        else:
            cloud = 'N/A'
        if float(weather_info['precip']) > 0.0:
            precip = '☔'
        else:
            precip = '🌂'
        st.markdown(f'##### {city_name} - 实时天气')
        wcol = st.columns(4)
        wcol[0].metric(label='天气', value=f"{weather_info['weather']} {weather_info['weather_icon']}")
        wcol[1].metric(label='🌡️温度', value=f"{weather_info['temp']}℃ {weather_info['temp_icon']}")
        wcol[2].metric(label='🧘体感温度', value=f"{weather_info['feelslike']}℃ {weather_info['feelslike_icon']}")
        wcol[3].metric(label='降水', value=f"{weather_info['precip']} mm {precip}")
        wcol[0].metric(label='能见度', value=f"{weather_info['vis']} km")
        wcol[1].metric(label='云量', value=f"{cloud}%")
        wcol[2].metric(label='大气压强', value=f"{weather_info['pressure']} hPa")
        wcol[3].metric(label='湿度', value=f"{weather_info['humidity']}% {weather_info['humidity_icon']}")
        wcol[0].metric(label='风向', value=weather_info['winddir'])
        wcol[1].metric(label='风力', value=f"{weather_info['windspeed']} km/h {weather_info['wind_icon']}")
        wcol[2].metric(label='数据更新时间', value=weather_info['obstime'][5:-6].replace('T', ' '))
        style_metric_cards(border_left_color="#426edd")


@st.fragment
def displayVisitCounter_static():
    sql = "SELECT pyLM from verinfo where pyFile = 'visitcounter'"
    visitcount = execute_sql(cur, sql)[0][0]

    # 生成徽章样式的访问计数器
    badge_svg = badge(left_text='访  问  次  数', right_text=f'{visitcount}', right_color='brightgreen')
    # 将badge_svg包裹在具有居中和缩放样式的<div>标签中
    centered_and_scaled_badge = f"<div style='display: flex; justify-content: center; transform: scale(1.3);'>{badge_svg}</div>"
    st.markdown(centered_and_scaled_badge, unsafe_allow_html=True)


@st.fragment
def displayAppInfo_static():
    st.markdown(f"<font face='微软雅黑' color=purple size=16><center>**{APPNAME_CN}**</center></font>", unsafe_allow_html=True)
    verinfo, verLM = getVerInfo()
    st.markdown(f"<font face='微软雅黑' size=5><center>软件版本: {int(verinfo / 10000)}.{int((verinfo % 10000) / 100)}.{int(verinfo / 10)} building {verinfo}</center></font>", unsafe_allow_html=True)
    st.markdown(f"<font face='微软雅黑' size=3><center>更新时间: {time.strftime('%Y-%m-%d %H:%M', time.localtime(verLM))}</center></font>", unsafe_allow_html=True)
    update_type, update_content = get_update_content(f"./CHANGELOG.md")
    st.markdown(f"<font face='微软雅黑' color=blue size=4><center>更新内容: {update_type} - {update_content}</center></font>", unsafe_allow_html=True)


def combine_query():
    st.markdown("### <font face='微软雅黑' color=tear><center>工作量高级查询</center></font>", unsafe_allow_html=True)
    btn_query = st.button("查询")
    clerk_cname_pack, task_group_pack = [], []
    sql = f"SELECT userCName from users where clerk_pa = 1 and StationCN = '{st.session_state.StationCN}' order by ID"
    result = execute_sql(cur, sql)
    for row in result:
        clerk_cname_pack.append({'value': row[0], 'title': row[0]})
    sql = f"SELECT DISTINCT(task_group) from clerk_work where StationCN = '{st.session_state.StationCN}'"
    result = execute_sql(cur, sql)
    for row in result:
        task_group_pack.append({'value': row[0], 'title': row[0]})
    sql = f"SELECT MIN(task_score), MAX(task_score) from clerk_work where StationCN = '{st.session_state.StationCN}'"
    result = execute_sql(cur, sql)
    min_task_score = result[0][0]
    max_task_score = result[0][1]

    config = {
    'fields': {
        'clerk_cname': {
            'label': '姓名',
            'type': 'select',
            'fieldSettings': {
            'listValues': clerk_cname_pack,
            },
        },
        'task_date': {
            'label': '日期',
            'type': 'date',
            'operators': ['between']
        },
        'task_group': {
            'label': '工作组别',
            'type': 'select',
            'fieldSettings': {
            'listValues': task_group_pack,
            },
        },
        'task_score': {
            'label': '单项分值',
            'type': 'number',
            'fieldSettings': {
            'min': min_task_score,
            'max': max_task_score,
            'step': 1
            },
            'preferWidgets': ['slider', 'rangeslider'],
        },
        'task_approved': {
            'label': '是否已核定',
            'type': 'boolean',
            'operators': ['equal'],
        }
    }
    }

    sql_query = condition_tree(
        config,
        return_type='sql',
        placeholder='暂无查询条件',
    )

    if  sql_query and btn_query:
        sql = f"SELECT ID, task_date, clerk_cname, clerk_work, task_score, task_group, task_approved FROM clerk_work where StationCN = '{st.session_state.StationCN}' and {sql_query}"
        sql = sql.replace('task_approved = true', 'task_approved = 1').replace('task_approved = false', 'task_approved = 0')
        result = execute_sql(cur, sql)
        if result:
            df = pd.DataFrame(result, dtype=str)
            df.columns = ["ID", "日期", "员工姓名", "工作项", "单项分值", "工作组别", "核定状态"]
            for index, value in enumerate(result):
                df.loc[index, "核定状态"] = "已核定" if df["核定状态"][index] == '1' else "未核定"
            st.dataframe(df)
        else:
            st.info("没有查询到符合条件的记录")


def update_users_setup(param_name, param_value, action_type):
    if action_type == 'update':
        sql = f"UPDATE users_setup SET param_value = {int(param_value)} where param_name = '{param_name}'"
        execute_sql_and_commit(conn, cur, sql)
    elif action_type == 'insert':
        sql = f"INSERT INTO users_setup (userID, userCName, param_name, param_value) VALUES ({st.session_state.userID}, '{st.session_state.userCName}', '{param_name}', {int(param_value)})"
        execute_sql_and_commit(conn, cur, sql)


def users_setup():
    st.markdown("### <font face='微软雅黑' color=blue><center>个人设置</center></font>", unsafe_allow_html=True)
    for index, value in enumerate(SETUP_NAME_PACK):
        sql = f"SELECT userID, userCName, param_value from users_setup where userID = {st.session_state.userID} and param_name = '{value}'"
        cur.execute(sql)
        result = cur.fetchone()
        st.markdown(f'##### {SETUP_LABEL_PACK[index]}')
        if result:
            sac.switch(label='', value=bool(int(result[2])), key=f'setup_{value}_{result[0]}', align='start', on_label='On', off_label='Off')
            update_users_setup(value, st.session_state[f'setup_{value}_{result[0]}'], 'update')
        else:
            sac.switch(label='', value=True, key=f'setup_{value}_{st.session_state.userID}', align='start', on_label='On', off_label='Off')
            update_users_setup(value, st.session_state[f'setup_{value}_{st.session_state.userID}'], 'insert')


def refresh_users_setup():
    for index, value in enumerate(SETUP_NAME_PACK):
        sql = f"SELECT userID, userCName, param_value from users_setup where userID = {st.session_state.userID} and param_name = '{value}'"
        result = execute_sql(cur, sql)
        if result:
            st.session_state[value] = bool(result[0][2])
        else:
            st.session_state[value] = True


def get_city_code():
    st.session_state.cityname = STATION_CITYNAME[st.session_state.StationCN]
    sql = f"SELECT location_ID, AD_code from hf_cn_city where Location_Name_ZH = '{st.session_state.cityname}'"
    result = execute_sql(cur, sql)
    if result:
        st.session_state.hf_city_code = result[0][0]
        st.session_state.gd_city_code = result[0][1]
    else:
        st.error("城市编码获取失败")


def auto_get_history_weather():
    city_code = st.session_state.hf_city_code
    city_name = st.session_state.cityname
    for i in range(1, 11):
        #st.progress(value=i / 10, text=f'正在获取 {city_name} 的第{i}天历史天气数据...')
        query_date = datetime.datetime.now() - datetime.timedelta(days=i)
        query_date = query_date.strftime('%Y-%m-%d')
        sql = f"SELECT ID FROM weather_history WHERE city_code = '{city_code}' and weather_date = '{query_date}'"
        cur.execute(sql)
        result = cur.fetchone()
        if not result:
            weather_info = get_city_history_weather(city_code, str(query_date).replace('-', ''))
            sql = f"INSERT INTO weather_history (weather_date, city_code, city_name, sunrise, sunset, moonrise, moonset, moonPhase, tempMax, tempMin, humidity, pressure, moon_icon, temp_icon, humidity_icon, temp_hourly, weather_hourly, precip_hourly, windir_hourly, windscale_hourly, windspeed_hourly, humidity_hourly, pressure_hourly, weather_icon_hourly) VALUES ('{query_date}', '{city_code}', '{city_name}', '{weather_info['sunrise']}', '{weather_info['sunset']}', '{weather_info['moonrise']}', '{weather_info['moonset']}', '{weather_info['moonPhase']}', '{weather_info['tempMax']}', '{weather_info['tempMin']}', '{weather_info['humidity']}', '{weather_info['pressure']}', '{weather_info['moon_icon']}', '{weather_info['temp_icon']}', '{weather_info['humidity_icon']}', '{weather_info['temp_hourly']}', '{weather_info['weather_hourly']}', '{weather_info['precip_hourly']}', '{weather_info['windir_hourly']}', '{weather_info['windscale_hourly']}', '{weather_info['windspeed_hourly']}', '{weather_info['humidity_hourly']}', '{weather_info['pressure_hourly']}', '{weather_info['weather_icon_hourly']}')"
            execute_sql_and_commit(conn, cur, sql)


def cal_date(diff_days):
    if diff_days > 0:
        result_date = datetime.datetime.now() + datetime.timedelta(days=diff_days)
    else:
        result_date = datetime.datetime.now() - datetime.timedelta(days=abs(diff_days))
    result_date = result_date.strftime('%Y-%m-%d')

    return result_date


global APPNAME_CN, APPNAME_EN, MAXDEDUCTSCORE, CHARTFONTSIZE, MDTASKDAYS, WEATHERICON, STATION_CITYNAME, SETUP_NAME_PACK, SETUP_LABEL_PACK, MAXREVDAYS
APPNAME_CN = "站室绩效考核系统KPI-PA"
APPNAME_EN = "GRU-PA"
MAXDEDUCTSCORE = -200
CHARTFONTSIZE = 14
MDTASKDAYS = 28
MAXREVDAYS = 45
STATION_CITYNAME = {'北京站': '顺义', '天津站': '滨海新区', '总控室': '滨海新区', '调控中心': '滨海新区', '武清站': '武清'}
SETUP_NAME_PACK = ['static_show', 'weather_show', 'weather_metric', 'weather_provider']
SETUP_LABEL_PACK = ['主页展示方式: :green[On 静态文字] :orange[Off 特效文字]', '天气展示', '天气展示方式: :green[On 卡片] :orange[Off 文字] :violet[高德只有卡片模式]', '天气数据源: :green[On 和风] :orange[Off 高德]']
conn = get_connection()
cur = conn.cursor()
st.logo(image="./Images/logos/GRU-PA-logo.png", icon_image="./Images/logos/GRU-PA-logo.png", size="large")
weather_provider = 'hf'
selected = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    login()

if st.session_state.logged_in:
    with st.sidebar:
        st.markdown(f"<font face='微软雅黑' color=green size=4><center>**当前用户:{st.session_state.userCName}**</center></font>", unsafe_allow_html=True)
        #st.markdown(f'### :green[当前用户:] :orange[{st.session_state.userCName}]')
        #displaySmallTime()
        #displaySmallClock()
        if st.session_state.userType == "admin":
            selected = sac.menu([
                sac.MenuItem('公告', icon='megaphone'),
                sac.MenuItem('主页', icon='house'),
                sac.MenuItem('功能', icon='grid-3x3-gap', children=[
                    sac.MenuItem('工作量录入', icon='list-task'),
                    sac.MenuItem('工作量手工录入', icon='journal-plus'),
                    sac.MenuItem('工作减分项录入', icon='journal-minus'),
                    sac.MenuItem('记录修改', icon='journal-medical'),
                    sac.MenuItem('统计查询及导出', icon='clipboard-data'),
                    sac.MenuItem('趋势图', icon='bar-chart-line'),
                    sac.MenuItem('数据检查与核定', icon='check2-all'),
                    sac.MenuItem('高级查询', icon='search'),
                    sac.MenuItem('历史天气', icon='cloud-sun'),
                    sac.MenuItem('公告发布', icon='journal-arrow-up'),
                    sac.MenuItem("重置数据库ID", icon="bootstrap-reboot"),
                ]),
                sac.MenuItem('设置', icon='gear', children=[
                    sac.MenuItem('个人设置', icon='sliders'),
                ]),
                sac.MenuItem('账户', icon='person-gear', children=[
                    sac.MenuItem('密码修改', icon='key'),
                    sac.MenuItem('密码重置', icon='person-gear'),
                    sac.MenuItem('登出', icon='box-arrow-right'),
                ]),
                sac.MenuItem('关于', icon='layout-wtf', children=[
                    sac.MenuItem('Changelog', icon='view-list'),
                    sac.MenuItem('Readme', icon='github'),
                    sac.MenuItem('关于...', icon='link-45deg'),
                    sac.MenuItem('LICENSE', icon='card-text'),
                ]),
            ], open_index=[1, 2], index=st.session_state.menu_index)
        elif st.session_state.userType == "user":
            selected = sac.menu([
                sac.MenuItem('公告', icon='megaphone'),
                sac.MenuItem('主页', icon='house'),
                sac.MenuItem('功能', icon='grid-3x3-gap', children=[
                    sac.MenuItem('工作量录入', icon='list-task'),
                    sac.MenuItem('工作量手工录入', icon='journal-plus'),
                    sac.MenuItem('记录修改', icon='journal-medical'),
                    sac.MenuItem('统计查询及导出', icon='clipboard-data'),
                    sac.MenuItem('趋势图', icon='bar-chart-line'),
                    sac.MenuItem('历史天气', icon='cloud-sun'),
                ]),
                sac.MenuItem('设置', icon='gear', children=[
                    sac.MenuItem('个人设置', icon='sliders'),
                ]),
                sac.MenuItem('账户', icon='person-gear', children=[
                    sac.MenuItem('密码修改', icon='key'),
                    sac.MenuItem('登出', icon='box-arrow-right'),
                ]),
                sac.MenuItem('关于', icon='layout-wtf', children=[
                    sac.MenuItem('Changelog', icon='view-list'),
                    sac.MenuItem('Readme', icon='github'),
                    sac.MenuItem('关于...', icon='link-45deg'),
                    sac.MenuItem('LICENSE', icon='card-text'),
                ]),
            ], open_index=[1, 2], index=st.session_state.menu_index)
        st.divider()
        st.image(f'./Images/badges/{APPNAME_EN}-badge.svg')
        st.image(f'./Images/badges/{APPNAME_EN}-lm-badge.svg')
        #st.markdown(f'### :green[当前用户:] :orange[{st.session_state.userCName}]')
    if selected == "公告":
        public_notice()
    elif selected == "主页":
        # 刷新个人设置
        refresh_users_setup()
        # 更新版本信息
        updatePyFileinfo()
        verinfo, verLM = getVerInfo()
        app_version = f'{int(verinfo / 10000)}.{int((verinfo % 10000) / 100)}.{verinfo}'
        app_lm = time.strftime('%Y-%m-%d %H:%M', time.localtime(verLM))
        gen_badge(conn, cur, [], 'MySQL', APPNAME_EN, app_version, app_lm)
        if st.session_state.static_show:
            displayAppInfo_static()
        else:
            displayBigTime()
            displayAppInfo(300)
        if st.session_state.weather_show:
            if st.session_state.weather_provider:
                if st.session_state.weather_metric:
                    display_weather_hf_metric(st.session_state.hf_city_code)
                    # 手动测试
                    #display_weather_hf_metric('101010900')
                else:
                    display_weather_hf(st.session_state.hf_city_code)
                    st.header(' ')
            else:
                display_weather_gd(st.session_state.gd_city_code)
        else:
            st.header(' ')
            st.header(' ')
        sac.divider(label='', icon=sac.BsIcon(name='boxes', size=20), align='center')
        if st.session_state.static_show:
            displayVisitCounter_static()
        else:
            displayVisitCounter()
    elif selected == "工作量录入":
        task_input()
    elif selected == "工作量手工录入":
        manual_input()
    elif selected == "工作减分项录入":
        deduction_input()
    elif selected == "记录修改":
        task_modify()
    elif selected == "统计查询及导出":
        query_task()
    elif selected == "趋势图":
        gen_chart()
    elif selected == "数据检查与核定":
        check_data()
    elif selected == "高级查询":
        combine_query()
    elif selected == "公告发布":
        input_public_notice()
    elif selected == "历史天气":
        display_history_weather()
    elif selected == "重置数据库ID":
        reset_table_num()
    elif selected == "个人设置":
        users_setup()
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
    elif selected == "LICENSE":
        aboutLicense()
