# ==========================================
# 前台 UI 區
# ==========================================
# 設定一個開關：True 為開啟，False 為關閉
SYSTEM_OPEN = False 

if not SYSTEM_OPEN:
    st.error("🛑 訂購已截止！感謝大家的參與。")
    st.info("系統目前僅供瀏覽，已不再接收新訂單。")
    
    # 這裡可以選擇要不要顯示原本的菜單資訊供參考，但把 input 元件拿掉
    st.markdown("#### 🍔 菜單參考")
    st.table(pd.DataFrame([{"餐點": v["name"], "價格": v["price"]} for k, v in combo_items.items() if k != 0]))

else:
    # 原本的 UI 程式碼 (包含姓名輸入、下拉選單、送出按鈕等)
    if st.session_state.show_success_dialog:
        success_dialog()
    # ... (中間省略，放你原本的 UI 邏輯) ...
    if total_price > 129:
        # ... 原本的按鈕邏輯 ...
