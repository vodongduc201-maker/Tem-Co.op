import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Team MT - Báo Cáo", layout="wide")

# 1. ĐỌC DỮ LIỆU VỚI CƠ CHẾ DÒ TÌM TIÊU ĐỀ
@st.cache_data
def load_master_data():
    try:
        # Đọc file không lấy header trước để kiểm tra
        df = pd.read_excel("data nhân viên.xlsx", header=None)
        
        # Tìm dòng nào chứa chữ "NHÂN VIÊN" hoặc "HỆ THỐNG" để làm Header
        header_row = 0
        for i in range(len(df)):
            row_values = [str(x).upper() for x in df.iloc[i].values]
            if "NHÂN VIÊN" in row_values or "HỆ THỐNG" in row_values:
                header_row = i
                break
        
        # Đọc lại file với đúng dòng header đã tìm thấy
        df = pd.read_excel("data nhân viên.xlsx", header=header_row)
        
        # Làm sạch tên cột: Viết hoa hết và xóa khoảng trắng
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Xóa dòng trống và làm sạch dữ liệu trong ô
        df = df.dropna(how='all')
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else x)
        
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
        return None

df_master = load_master_data()

# Danh mục sản phẩm
DS_SAN_PHAM = [
    "Sá Xị Chương Dương (Lon 330ml)",
    "Sá Xị Zero (Lon 330ml)",
    "Sá Xị Chương Dương (PET 390ml)",
    "Soda Kem (Lon 330ml)",
    "Sá Xị Chương Dương (Chai 1.5L)",
    "Nước Tinh Khiết CD (Chai 500ml)"
]

if df_master is not None:
    # --- KIỂM TRA TÊN CỘT THỰC TẾ ---
    # Gán tên cột chuẩn sau khi đã viết hoa ở bước load_data
    col_nv = "NHÂN VIÊN"
    col_ht = "HỆ THỐNG"
    col_ph = "PHƯỜNG"
    col_st = "TÊN SIÊU THỊ"

    # Kiểm tra xem các cột có tồn tại không để tránh lỗi đỏ màn hình
    required_cols = [col_nv, col_ht, col_ph, col_st]
    missing_cols = [c for c in required_cols if c not in df_master.columns]

    if missing_cols:
        st.error(f"⚠️ File Excel thiếu (hoặc sai tên) các cột: {', '.join(missing_cols)}")
        st.write("Các cột hiện có trong file của bạn là:", list(df_master.columns))
    else:
        # --- PHẦN SIDEBAR: CẤU TRÚC 4 TẦNG ---
        with st.sidebar:
            st.header("👤 Định danh công tác")
            
            # Tầng 1: Nhân viên
            list_nv = sorted([x for x in df_master[col_nv].unique() if x != 'nan'])
            nv_selected = st.selectbox("1. Chọn Nhân viên:", list_nv)
            df_f1 = df_master[df_master[col_nv] == nv_selected]

            # Tầng 2: Hệ thống
            list_ht = sorted([x for x in df_f1[col_ht].unique() if x != 'nan'])
            ht_selected = st.selectbox("2. Chọn Hệ thống:", list_ht)
            df_f2 = df_f1[df_f1[col_ht] == ht_selected]

            # Tầng 3: Phường
            list_ph = sorted([x for x in df_f2[col_ph].unique() if x != 'nan'])
            ph_selected = st.selectbox("3. Chọn Phường:", list_ph)
            df_f3 = df_f2[df_f2[col_ph] == ph_selected]

            # Tầng 4: Siêu thị
            list_st = sorted([x for x in df_f3[col_st].unique() if x != 'nan'])
            st_selected = st.selectbox("4. Chọn Siêu thị:", list_st)

        # --- GIAO DIỆN NHẬP LIỆU CHÍNH ---
        st.title(f"🥤 {st_selected}")
        st.caption(f"Khu vực: {ph_selected} | Hệ thống: {ht_selected} | NV: {nv_selected}")

        with st.form("entry_form", clear_on_submit=True):
            st.subheader("Số liệu trưng bày & Tồn kho")
            data_rows = []
            
            for sp in DS_SAN_PHAM:
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1: st.write(f"**{sp}**")
                with c2: f = st.number_input("Facing", min_value=0, step=1, key=f"f_{sp}")
                with c3: s = st.number_input("Tồn kho", min_value=0, step=1, key=f"s_{sp}")
                data_rows.append({"Sản phẩm": sp, "Facing": f, "Tồn kho": s})
            
            st.divider()
            ghi_chu = st.text_area("🗒️ Ghi chú:")
            submit = st.form_submit_button("🚀 XUẤT BÁO CÁO")

        if submit:
            df_report = pd.DataFrame(data_rows)
            df_report.insert(0, "Ngày", datetime.now().strftime("%d/%m/%Y"))
            df_report.insert
