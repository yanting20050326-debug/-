import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime, timedelta

# ==========================================
# 網頁基本設定
# ==========================================
st.set_page_config(page_title="班聚訂餐系統 - 已截止", page_icon="🍔", layout="centered")

st.title("🍔 班聚訂餐系統")

# ==========================================
# 📢 截止狀態顯示區
# ==========================================
# 取得現在時間 (台灣時間 UTC+8)
now = datetime.utcnow() + timedelta(hours=8)
st.info(f"📅 目前時間：{now.strftime('%Y-%m-%d %H:%M:%S')}")

st.error("""
### 🛑 訂餐已截止
本系統已於 **2026/03/31 23:59** 停止接收新訂單。
感謝大家的配合與參與！如有任何訂單修改需求，請直接聯繫主揪 **彥廷**。
""")

# 原本的注意事項改為唯讀提醒
st.warning("""
**⚠️ 歷史注意事項回顧：**
1. 每人金額上限$129
2. 不參加的人不填寫
3. 禁止重複填寫
""")

# ==========================================
# Google Sheets 連線設定 (保留以供後續查詢或備用)
# ==========================================
def connect_to_sheets():
    try:
        creds_dict = json.loads(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception:
        return None

# ==========================================
# 狀態初始化
# ==========================================
if 'show_success_dialog' not in st.session_state: st.session_state.show_success_dialog = False

# ==========================================
# 前台 UI 區 (移除菜單輸入，僅保留結尾資訊)
# ==========================================

st.markdown("---")

# 這裡可以放一張感謝圖或是單純文字
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJmZzR6NHR3Z3R3Z3R3Z3R3Z3R3Z3R3Z3R3Z3R3Z3R3Z3ImZXA9djFfaW50ZXJuYWxfZ2lmX2J5X2lkJmN0PWc/3o7TKMGpxP5Oq8q9q0/giphy.gif", caption="訂單整理中...", use_container_width=True)
    except:
        st.write("✨ 彥廷感謝大家的配合！")

st.markdown("""
<div style="text-align: center;">
    <p style="color: gray;">系統狀態：唯讀 (ReadOnly)</p>
</div>
""", unsafe_allow_html=True)

# 移除原本的 submit_order 邏輯與所有 input widgets
# 這樣使用者進入網頁只會看到截止訊息，無法點餐
