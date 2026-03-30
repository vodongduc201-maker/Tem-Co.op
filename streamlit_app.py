import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Kết nối Google Sheets (Để ghi dữ liệu)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Đọc danh mục Nhân viên từ GitHub (Để làm bộ lọc)
@st.cache_data(ttl=600)
def load_github_data():
    try:
        # Đọc trực tiếp file excel bạn đã up lên GitHub
        df = pd.read_excel("data nhan vien.xlsx")
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except:
        return None

df_master = load_github_data()

st.title("🥤 Báo Cáo Thị Trường Chương Dương")

if df_master is not None:
    # --- PHẦN BỘ LỌC ĐIỀU HƯỚNG ---
    with st.container():
        c1, c2, c3 = st.columns(3)
        
        with c1:
            list_nv = sorted(df_master['NHAN VIEN'].unique())
            sel_nv = st.selectbox("👤 Nhân viên", options=list_nv)
        
        # Lọc Phường theo Nhân viên
        df_nv = df_master[df_master['NHAN VIEN'] == sel_nv]
        with c2:
            list_ph = sorted(df_nv['PHUONG'].unique())
            sel_ph = st.selectbox("📍 Phường/Khu vực", options=list_ph)
            
        # Lọc Siêu thị theo Phường
        df_ph = df_nv[df_nv['PHUONG'] == sel_ph]
        with c3:
            list_st = sorted(df_ph['SIEU THI'].unique())
            sel_st = st.selectbox("🛒 Siêu thị", options=list_st)

    st.divider()

    # --- PHẦN FORM GHI DỮ LIỆU (Giữ nguyên vụ Add vào Sheets của bạn) ---
    with st.form("form_bao_cao", clear_on_submit=True):
        st.subheader(f"Ghi nhận tại: {sel_st}")
        
        # Các trường nhập liệu
        san_pham = st.text_input("Sản phẩm")
        facing = st.number_input("Facing", min_value=0, step=1)
        ton_kho = st.number_input("Tồn kho", min_value=0, step=1)
        hinh_anh = st.text_input("Link hình ảnh")
        ghi_chu = st.text_area("Ghi chú")
        
        if st.form_submit_button("Lưu vào hệ thống"):
            # Tạo dòng dữ liệu để add vào sheet
            new_row = pd.DataFrame([{
                "NGAY": datetime.now().strftime("%d/%m/%Y"),
                "GIO": datetime.now().strftime("%H:%M:%S"),
                "NHAN VIEN": sel_nv,
                "HE THONG": df_ph[df_ph['SIEU THI'] == sel_st]['HE THONG'].values[0],
                "PHUONG": sel_ph,
                "SIEU THI": sel_st,
                "SAN PHAM": san_pham,
                "FACING": facing,
                "TON KHO": ton_kho,
                "GHI CHU": ghi_chu,
                "HINH ANH": hinh_anh
            }])
            
            # Đọc file cũ - Nối file mới - Ghi đè lại (Cách add sheet của bạn)
            try:
                df_cu = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                df_moi = pd.concat([df_cu, new_row], ignore_index=True)
                conn.update(worksheet="Data_Bao_Cao_MT", data=df_moi)
                st.success(f"✅ Đã lưu báo cáo {sel_st} thành công!")
            except Exception as e:
                st.error(f"Lỗi khi lưu: {e}")

# --- PHẦN BẠN THEO DÕI ---
with st.expander("Xem lịch sử báo cáo"):
    df_history = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
    st.dataframe(df_history.tail(10))
