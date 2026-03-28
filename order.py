import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime, timedelta

# 網頁基本設定
st.set_page_config(page_title="班聚訂餐系統", page_icon="🍔", layout="centered")

st.title("🍔 班聚訂餐系統")

# ==========================================
# 📢 注意事項醒目區塊
# ==========================================
st.warning("""
**⚠️ 注意事項：**
1. **每人金額上限$129**
2. **不參加的人千萬不要填！**
3. **千萬!千萬!千萬!不要重複填** 
4. **填寫截止日期：2026/3/31 23:59**
""")

# ==========================================
# 菜單資料區
# ==========================================
combo_items = {
    0: {"name": "不點套餐想單點", "price": 0},
    1: {"name": "1號餐 - 赤肉麵線焿 + 脆皮炸雞", "price": 109},
    2: {"name": "2號餐 - 香檸吉司豬排堡 + 蘑菇肉醬可樂餅", "price": 119},
    3: {"name": "3號餐 - 無骨雞塊(5入) + 黃金鮮酥雞", "price": 109},
    4: {"name": "4號餐 - 五穀瘦肉粥 + 脆皮炸雞", "price": 109},
    5: {"name": "5號餐 - 鮮脆雞腿堡 + 玉米濃湯", "price": 104},
    6: {"name": "6號餐 - 鮮酥雞肉焿 + 烤醬雞堡", "price": 99},
    7: {"name": "7號餐 - 烤醬雞堡 + 脆皮炸雞", "price": 112},
    8: {"name": "8號餐 - 香檸吉司豬排堡 + 脆皮炸雞", "price": 119},
    9: {"name": "9號餐 - 赤肉麵線焿 + 鮮脆雞腿堡", "price": 119},
    10: {"name": "10號餐 - 2塊脆皮炸雞(腿、塊任選)", "price": 113},
    11: {"name": "11號餐 - 赤肉麵線焿 + 經典排骨酥", "price": 89},
    12: {"name": "12號餐 - 五穀瘦肉粥 + 蘑菇肉醬可樂餅", "price": 99},
    13: {"name": "13號餐 - 烤醬雞堡 + 玉米濃湯 + 無骨雞塊", "price": 129},
    15: {"name": "15號餐 - 黃金鮮酥雞 + 排骨酥肉焿 + 香酥米糕", "price": 129}
}

alacarte_food = {
    "鮮脆雞腿堡 ($69)": 69, "香檸吉司豬排堡 ($59)": 59, "烤醬雞堡 ($47)": 47,
    "玉米濃湯 ($29)": 29, "麻辣麵線焿 ($48)": 48, "赤肉麵線焿 ($42)": 42,
    "五穀瘦肉粥 ($42)": 42, "排骨酥肉焿 ($42)": 42, "鮮酥雞肉焿 ($42)": 42,
    "脆皮雞腿 ($51)": 51, "脆皮雞塊 ($51)": 51, "無骨雞塊 5入 ($49)": 49,
    "無骨雞塊 9入 ($78)": 78, "麻糬棒 ($29)": 29, "經典排骨酥 ($45)": 45,
    "黃金鮮酥雞 ($49)": 49, "蘑菇肉醬可樂餅 ($49)": 49, "義式紅醬波浪薯 ($44)": 44,
    "地瓜薯條 ($31)": 31, "香酥米糕 ($35)": 35, "超長熱狗 ($29)": 29
}

alacarte_drinks = {
    "可樂(中) ($29)": 29, "可樂(大) ($34)": 34,
    "汽水(中) ($29)": 29, "汽水(大) ($34)": 34,
    "蘋果汁(中) ($29)": 29, "蘋果汁(大) ($34)": 34,
    "檸檬風味紅茶(中) ($29)": 29, "檸檬風味紅茶(大) ($34)": 34,
    "台灣烏龍(中) ($29)": 29, "台灣烏龍(大) ($34)": 34,
    "紅茶牛奶(小) ($29)": 29, "紅茶牛奶(中) ($34)": 34, "紅茶牛奶(大) ($39)": 39,
    "熱桂花烏龍 ($29)": 29, "熱美式咖啡 ($29)": 29
}

combo_drink_options_active = {
    "可樂 (中)": 0, "可樂 (大) [+5元]": 5,
    "汽水 (中)": 0, "汽水 (大) [+5元]": 5,
    "蘋果汁 (中)": 0, "蘋果汁 (大) [+5元]": 5,
    "檸檬風味紅茶 (中)": 0, "檸檬風味紅茶 (大) [+5元]": 5,
    "台灣烏龍 (中)": 0, "台灣烏龍 (大) [+5元]": 5,
    "紅茶牛奶 (小)": 0, "紅茶牛奶 (大) [+7元]": 7 
}

combo_drink_options_none = {
    "無 / 不需飲料": 0
}

# ==========================================
# Google Sheets 連線設定
# ==========================================
def connect_to_sheets():
    # 讀取剛剛藏在 Secrets 裡面的 JSON 鑰匙
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client

# ==========================================
# 狀態初始化與處理邏輯
# ==========================================
if 'student_name' not in st.session_state: st.session_state.student_name = ""
if 'meal_id' not in st.session_state: st.session_state.meal_id = 0
if 'alacarte_food_opts' not in st.session_state: st.session_state.alacarte_food_opts = []
if 'alacarte_drink_opts' not in st.session_state: st.session_state.alacarte_drink_opts = []
if 'sys_msg' not in st.session_state: st.session_state.sys_msg = None
if 'show_success_dialog' not in st.session_state: st.session_state.show_success_dialog = False

@st.dialog("🎉 系統通知")
def success_dialog():
    st.markdown("### 訂單成功送出，彥廷感謝您👻")
    if st.button("關閉"):
        st.session_state.show_success_dialog = False
        st.rerun()

def submit_order(total_price, final_drink):
    if st.session_state.student_name.strip() == "":
        st.session_state.sys_msg = ("error", "⚠️ 請務必輸入姓名喔！")
        return

    meal_name = combo_items[st.session_state.meal_id]["name"] if st.session_state.meal_id != 0 else "無套餐"
    
    # 組合單點字串
    all_alacarte = st.session_state.alacarte_food_opts + st.session_state.alacarte_drink_opts
    alacarte_str = "、".join(all_alacarte) if all_alacarte else "無"
    
    # 取得現在時間 (轉換為台灣時間 UTC+8)
    current_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

    try:
        # 連線並寫入 Google 試算表
        client = connect_to_sheets()
        # 注意：這裡的 "丹丹漢堡訂單總表" 必須跟你雲端硬碟裡的檔名一模一樣！
        sheet = client.open("丹丹漢堡訂單總表").sheet1
        
        row_to_append = [
            current_time,
            st.session_state.student_name,
            meal_name,
            final_drink,
            alacarte_str,
            total_price
        ]
        
        sheet.append_row(row_to_append)
        
        # 成功後清空表單並觸發視窗
        st.session_state.show_success_dialog = True
        st.session_state.student_name = ""
        st.session_state.meal_id = 0
        st.session_state.alacarte_food_opts = []
        st.session_state.alacarte_drink_opts = []
        
    except Exception as e:
        # 如果發生連線錯誤或檔名錯誤，會跳出警告
        st.session_state.sys_msg = ("error", f"⚠️ 寫入雲端失敗，請截圖聯絡主揪！錯誤代碼：{e}")

# ==========================================
# 前台 UI 區
# ==========================================
if st.session_state.show_success_dialog:
    success_dialog()

if st.session_state.sys_msg:
    msg_type, msg_text = st.session_state.sys_msg
    if msg_type == "error": 
        st.error(msg_text)
    st.session_state.sys_msg = None 

st.subheader("📋 填寫訂單")

st.text_input("姓名* ", key="student_name", max_chars=10, placeholder="例如：徐明龍大帥哥")

st.markdown("#### 🍔 套餐區")

col_left, col_right = st.columns([2, 1])

with col_left:
    selected_meal_id = st.selectbox("選擇套餐 (不含129元以上品項)", 
                 options=list(combo_items.keys()), 
                 format_func=lambda x: f"{combo_items[x]['name']} (${combo_items[x]['price']})",
                 key="meal_id")

    if selected_meal_id == 0:
        current_drink_options = combo_drink_options_none
    else:
        current_drink_options = combo_drink_options_active

    selected_drink = st.selectbox("套餐附餐飲料", options=list(current_drink_options.keys()), key="combo_drink")

with col_right:
    st.markdown("##### ✨ 最新活動專區")
    try:
        st.image("紅茶牛奶.png", use_container_width=True)
    except FileNotFoundError:
        st.warning("請確認 '紅茶牛奶.png' 是否放在同一資料夾中。")

st.markdown("#### 🍗 單點區")
st.multiselect("美味丹點 (可複選)", options=list(alacarte_food.keys()), key="alacarte_food_opts")
st.multiselect("單點飲料 (可複選)", options=list(alacarte_drinks.keys()), key="alacarte_drink_opts")

combo_price = combo_items[st.session_state.meal_id]["price"]
upgrade_price = current_drink_options[selected_drink]
food_price = sum(alacarte_food[item] for item in st.session_state.alacarte_food_opts)
drink_price = sum(alacarte_drinks[item] for item in st.session_state.alacarte_drink_opts)
total_price = combo_price + upgrade_price + food_price + drink_price

st.markdown("---")

if total_price > 129:
    st.markdown(f"### 🛒 目前餐點總計：NT$ <span style='color:red;'>**{total_price}**</span>", unsafe_allow_html=True)
    st.error("⚠️ 警告：加總金額已超過班聚預算上限 129 元！點太多了喔，彥廷關心您🫤。")
    st.button("金額超標，無法送出", disabled=True)
elif total_price == 0:
    st.markdown(f"### 🛒 目前餐點總計：NT$ **{total_price}**")
    st.button("請先選擇餐點", disabled=True)
else:
    st.markdown(f"### 🛒 目前餐點總計：NT$ <span style='color:green;'>**{total_price}**</span>", unsafe_allow_html=True)
    st.button("送出訂單", type="primary", on_click=submit_order, args=(total_price, selected_drink))
