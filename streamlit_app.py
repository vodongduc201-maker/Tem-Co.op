import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import unicodedata

# 1. Cau hinh trang
st.set_page_config(page_title="MT Team - Chuong Duong", layout="wide", page_icon="🥤")

# Ham xoa dau tieng Viet (Dung de lam sach moi du lieu nhap vao)
def remove_accents(text):
    if not isinstance(text, str): return str(text)
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')

@st.cache_data
def load_master_data():
    try:
        # Goi file Excel da doi ten thanh khong dau
        df_raw = pd.read_excel("data_nhan_vien.xlsx", header=None)
        header_row = 0
        for i in range(len(df_raw)):
            row_str = " ".join([str(x).upper() for x in df_raw.iloc[i].values])
            # Tim dong tieu de (Nhan vien/He thong)
            if "NHAN VIEN" in row_str or "HE THONG" in row_str:
                header_row = i
                break
        df = pd.read_excel("data_nhan_vien.xlsx", header=header_row)
        df = df.iloc[:, :4] 
        df.columns = ["NHAN VIEN", "HE THONG", "PHUONG", "TEN SIEU THI"]
        df = df.dropna(subset=["TEN SIEU THI"])
        # Chuyen toan bo Master Data sang chu IN HOA khong dau
        df = df.map(lambda x: remove_accents(str(x)).strip().upper() if pd.notnull(x) else x)
        return df
    except Exception as e:
        st.error(f"Loi: Khong tim thay file 'data_nhan_vien.xlsx' tren GitHub.")
        return None

df_master = load_master_data()

# Danh muc san pham (Khong dau)
DS_SAN_PHAM = [
    "SA XI CHUONG DUONG (LON 330ML)",
    "SA XI ZERO (LON 330ML)",
    "SA XI CHUONG DUONG (PET 390ML)",
    "SODA KEM (LON 330ML)",
    "SA XI CHUONG DUONG (CHAI 1.5L)",
    "NUOC TINH KHIET CD (CHAI 500ML)"
]

conn = st.connection("gsheets", type=GSheetsConnection)

if df_master is not None:
    with st.sidebar:
        st.header("👤 THONG TIN")
        list_nv = sorted([x for x in df_master["NHAN VIEN"].unique() if x not in ['NAN', 'NONE']])
        nv_selected = st.selectbox("1. Nhan vien:", list_nv)
        df_f1 = df_master[df_master["NHAN VIEN"] == nv_selected]
        
        list_ht = sorted([x for x in df_f1["HE THONG"].unique() if x not in ['NAN', 'NONE']])
        ht_selected = st.selectbox("2. He thong:", list_ht)
        df_f2 = df_f1[df_f1["HE THONG"] == ht_selected]
        
        list_ph = sorted([x for x in df_f2["PHUONG"].unique() if x not in ['NAN', 'NONE']])
        ph_selected = st.selectbox("3. Phuong:", list_ph)
        
        df_f3 = df_f2[df_f2["PHUONG"] == ph_selected]
        st_selected = st.selectbox("4. Sieu thi:", sorted(df_f3["TEN SIEU THI"].unique()))

    st.title(f"🥤 {st_selected}")
    
    with st.form("entry_form", clear_on_submit=True):
        st.subheader("📊 NHAP SO LIEU")
        all_entries = []
        for sp in DS_SAN_PHAM:
            st.write(f"**{sp}**")
            c1, c2 = st.columns(2)
            with c1: f = st.number_input(f"Facing", min_value=0, step=
