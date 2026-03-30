import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import unicodedata

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="MT Report - Chuong Duong", layout="wide")

def clean_text(text):
    if not isinstance(text, str): text = str(text) if text else ""
    text = text.replace("'", "").replace("’", "").replace('"', "")
    nfkd_form = unicodedata.normalize('NFKD', text)
    clean = "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')
    return clean.encode('ascii', 'ignore').decode('ascii').strip()

# --- 2. KẾT NỐI (KÍCH HOẠT CHẾ ĐỘ GHI) ---
# Thêm ttl=0 để luôn làm mới dữ liệu và kích hoạt Service Account
conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)

@st.cache_data(ttl=600)
def load_master():
    try:
        df = pd.read_excel("data nhan vien.xlsx", engine='openpyxl')
        return df
    except: return None

df_master = load_master()

# --- 3. GIAO DIỆN ---
if df_master is not None:
    st.title("🥤 BÁO CÁO MT - CHƯƠNG DƯƠNG")
    
    with st.sidebar:
        nv = st.selectbox("Nhân viên:", sorted(df_master.iloc[:, 0].unique()))
        ht = st.selectbox("Hệ thống:", sorted(df_master.iloc[:, 1].unique()))
        st_list = df_master[df_master.iloc[:, 1] == ht].iloc[:, 3].unique()
        st_name = st.selectbox("Siêu thị:", sorted(st_list))

    with st.form("my_form", clear_on_submit=True):
        products = ["SA XI LON", "SA XI ZERO", "SA XI PET", "SODA KEM", "SA XI 1.5L", "NUOC SUOI"]
        results = []
        c1, c2 = st.columns(2)
        for i, p in enumerate(products):
            with c1 if i % 2 == 0 else c2:
                f = st.number_input(f"{p} - Facing", min_value=0, step=1)
                s = st.number_input(f"{p} - Tồn", min_value=0, step=1)
                results.append({"P": p, "F": f, "S": s})
        
        note = st.text_input("Ghi chú:")
        submit = st.form_submit_button("GỬI BÁO CÁO")

    # --- 4. XỬ LÝ GỬI (Ghi vào Sheets) ---
    if submit:
        new_data = []
        for r in results:
            if r["F"] > 0 or r["S"] > 0:
                new_data.append({
                    "NGAY": datetime.now().strftime("%d/%m/%Y"),
                    "NHAN VIEN": clean_text(nv),
                    "HE THONG": clean_text(ht),
                    "SIEU THI": clean_text(st_name),
                    "SAN PHAM": r["P"],
                    "FACING": str(r["F"]),
                    "TON KHO": str(r["S"]),
                    "GHI CHU": clean_text(note).upper()
                })
        
        if new_data:
            try:
                # Đọc file hiện tại
                existing = conn.read(worksheet="Data_Bao_Cao_MT")
                df_new = pd.DataFrame(new_data)
                
                if existing is not None and not existing.empty:
                    final_df = pd.concat([existing, df_new], ignore_index=True)
                else:
                    final_df = df_new
                
                # Ghi đè lại file Sheets với dữ liệu mới
                conn.update(worksheet="Data_Bao_Cao_MT", data=final_df)
                st.success("✅ ĐÃ GỬI THÀNH CÔNG!")
                st.balloons()
            except Exception as e:
                st.error(f"Lỗi: {e}")
