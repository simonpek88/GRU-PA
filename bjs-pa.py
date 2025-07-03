# coding utf-8
import datetime
import re
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit_antd_components as sac
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from st_keyup import st_keyup

from mysql_pool import get_connection

conn = get_connection()
cur = conn.cursor()
