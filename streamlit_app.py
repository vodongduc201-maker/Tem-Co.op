import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Team MT - Báo Cáo", layout="wide")

@st.cache_data
def load_master_data():
    try:
        # 1. Đọc file không header để dò tìm dữ liệu thực
        df_raw = pd.read_excel("data nhân viên.xlsx", header=None)
        
        # 2. Tìm dòng chứa tiêu đề (Dòng có chữ NHÂN VIÊN hoặc HỆ THỐNG)
        header_row = 0
        for i in range(len(df_raw)):
            row_str = " ".join([str(x).upper() for x in df_raw.iloc[i].values])
            if "NHÂN VIÊN" in row_str or "HỆ THỐNG" in row_str:
                header_row = i
                break
        
        # 3. Đọc lại với header chuẩn từ dòng tìm được
        df = pd.read_excel("data nhân viên.xlsx", header=header_row)
        
        # 4. ÉP TÊN CỘT THEO VỊ TRÍ (Để không bao giờ bị KeyError)
        # Bất kể bạn đặt tên gì, code sẽ lấy cột 1 là NV, cột 2 là HT, cột 3 là Phường, cột 4 là ST
        new_cols = ["NHÂN VIÊN", "HỆ THỐNG", "PHƯỜNG", "TÊN SIÊU THỊ"]
        # Chỉ lấy 4 cột đầu tiên và đặt tên lại cho chắc chắn
        df = df.iloc[:, :4] 
        df.columns = new_cols
        
        # 5. Làm sạch dữ liệu (Xóa khoảng trống, xóa dòng trống)
        df = df.dropna(subset=["TÊN SIÊU THỊ"]) # Xóa dòng nếu không có tên siêu thị
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else x)
        
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
        return None

df_master = load_master_data()

# Danh mục sản phẩm (Đã cập nhật Sá Xị PET 390)
DS_SAN_PHAM = [
    "Sá Xị Chương Dương (Lon 330ml)",
    "Sá Xị Zero (Lon 330ml)",
    "Sá Xị Chương Dương (Chai PET 390ml)",
    "Soda Kem (Lon 330ml)",
    "Sá Xị Chương Dương (Chai 1.5L)",
    "Nước Tinh Khiết CD (Chai 500ml)"
]

if df_master is not None:
    # Gán tên cột cố định theo bước ép tên ở trên
    col_nv, col_ht, col_ph, col_st = "NHÂN VIÊN", "HỆ THỐNG", "PHƯỜNG", "TÊN SIÊU THỊ"

    # --- SIDEBAR 4 TẦNG ---
    with st.sidebar:
        st.header("👤 Định danh công tác")
        
        # Lọc Nhân viên
        list_nv = sorted([x for x in df_master[col_nv].unique() if x not in ['nan', 'None']])
        nv_selected = st.selectbox("1. Chọn Nhân viên:", list_nv)
        df_f1 = df_master[df_master[col_nv] == nv_selected]

        # Lọc Hệ thống
        list_ht = sorted([x for x in df_f1[col_ht].unique() if x not in ['nan', 'None']])
        ht_selected = st.selectbox("2. Chọn Hệ thống:", list_ht)
        df_f2 = df_f1[df_f1[col_ht] == ht_selected]

        # Lọc Phường
        list_ph = sorted([x for x in df_f2[col_ph].unique() if x not in ['nan', 'None']])
        ph_selected = st.selectbox("3. Chọn Phường:", list_ph)
        df_f3 = df_f2[df_f2[col_ph] == ph_selected]

        # Lọc Siêu thị
        list_st = sorted([x for x in df_f3[col_st].unique() if x not in ['nan', 'None']])
        st_selected = st.selectbox("4. Chọn Siêu thị:", list_st)

    # --- GIAO DIỆN NHẬP LIỆU ---
    st.title(f"🥤 {st_selected}")
    st.caption(f"Khu vực: {ph_selected} | Hệ thống: {ht_selected} | NV: {nv_selected}")

    with st.form("entry_form", clear_on_submit=True):
        data_rows = []
        for sp in DS_SAN_PHAM:
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1: st.write(f"**{sp}**")
            with c2: f = st.number_input("Facing", min_value=0, step=1, key=f"f_{sp}")
            with c3: s = st.number_input("Tồn kho", min_value=0, step=1
