import streamlit as st
import pandas as pd
import os

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
4. **填寫截止日期：2026/3/29 20:00**
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

# 飲料選單拆分
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

CSV_FILE = "orders.csv"

# ==========================================
# 狀態初始化與處理邏輯
# ==========================================
if 'student_name' not in st.session_state: st.session_state.student_name = ""
if 'meal_id' not in st.session_state: st.session_state.meal_id = 0
if 'alacarte_food_opts' not in st.session_state: st.session_state.alacarte_food_opts = []
if 'alacarte_drink_opts' not in st.session_state: st.session_state.alacarte_drink_opts = []
if 'sys_msg' not in st.session_state: st.session_state.sys_msg = None
if 'show_success_dialog' not in st.session_state: st.session_state.show_success_dialog = False

# 定義彈出視窗
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
    
    new_order = {
        "姓名": st.session_state.student_name,
        "套餐": meal_name,
        "套餐飲料": final_drink,
        "單點加購": alacarte_str,
        "總金額": total_price
    }
    
    # 寫入 CSV
    df_new = pd.DataFrame([new_order])
    if not os.path.exists(CSV_FILE):
        df_new.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(CSV_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')

    print(f"🔔 [後台通知] 收到新訂單！ {st.session_state.student_name} | 金額: ${total_price}")

    # 觸發彈出視窗，並清空表單
    st.session_state.show_success_dialog = True
    st.session_state.student_name = ""
    st.session_state.meal_id = 0
    st.session_state.alacarte_food_opts = []
    st.session_state.alacarte_drink_opts = []

# ==========================================
# 前台 UI 區
# ==========================================
# 觸發彈出視窗的判斷
if st.session_state.show_success_dialog:
    success_dialog()

# 顯示錯誤訊息 (姓名未填等)
if st.session_state.sys_msg:
    msg_type, msg_text = st.session_state.sys_msg
    if msg_type == "error": 
        st.error(msg_text)
    st.session_state.sys_msg = None 

st.subheader("📋 填寫訂單")

st.text_input("姓名* ", key="student_name", max_chars=3, placeholder="例如：徐明龍大帥哥")

st.markdown("#### 🍔 套餐區")

col_left, col_right = st.columns([2, 1])

with col_left:
    selected_meal_id = st.selectbox("選擇套餐 (不含129元以上品項)", 
                 options=list(combo_items.keys()), 
                 format_func=lambda x: f"{combo_items[x]['name']} (${combo_items[x]['price']})",
                 key="meal_id")

    # 動態決定飲料選單
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

# ==========================================
# 即時金額計算與阻擋邏輯
# ==========================================
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