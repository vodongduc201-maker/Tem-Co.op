import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Cấu hình trang
st.set_page_config(page_title="Chương Dương - Check Thị Trường", layout="wide")

st.title("🥤 Công cụ Hỗ trợ Check Thị Trường")
st.markdown("Chọn thông tin để tìm nhanh siêu thị bạn đang ghé thăm:")

# 2. ĐỌC DỮ LIỆU DANH MỤC TỪ FILE EXCEL TRÊN GITHUB
# Vì file nằm cùng thư mục với streamlit_app.py, ta đọc trực tiếp
@st.cache_data(ttl=600)
def load_master_data():
    try:
        # Đọc file Excel bạn đã up lên GitHub
        df = pd.read_excel("data nhan vien.xlsx")
        # Xóa khoảng trắng thừa trong tên cột
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Không tìm thấy file 'data nhan vien.xlsx' trên GitHub: {e}")
        return None

df_master = load_master_data()

# 3. KẾT NỐI GOOGLE SHEETS (Để bạn theo dõi kết quả báo cáo)
conn = st.connection("gsheets", type=GSheetsConnection)
df_report = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)

# 4. GIAO DIỆN BỘ LỌC PHÂN CẤP (Lấy từ file Excel GitHub)
if df_master is not None:
    # Định nghĩa các cột (Bạn đảm bảo file Excel có đúng các cột này nhé)
    COL_NV = 'NHAN VIEN'
    COL_HT = 'HE THONG'
    COL_PH = 'PHUONG'
    COL_ST = 'SIEU THI'

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        list_nv = sorted([x for x in df_master[COL_NV].unique() if x])
        sel_nv = st.selectbox(f"👤 1. {COL_NV}", options=["-- Chọn NV --"] + list_nv)

    # Lọc đuổi cấp 1
    df_step1 = df_master[df_master[COL_NV] == sel_nv] if sel_nv != "-- Chọn NV --" else df_master

    with c2:
        list_ht = sorted([x for x in df_step1[COL_HT].unique() if x])
        sel_ht = st.selectbox(f"🏢 2. {COL_HT}", options=["-- Tất cả --"] + list_ht)

    # Lọc đuổi cấp 2
    df_step2 = df_step1[df_step1[COL_HT] == sel_ht] if sel_ht != "-- Tất cả --" else df_step1

    with c3:
        list_ph = sorted([x for x in df_step2[COL_PH].unique() if x])
        sel_ph = st.selectbox(f"📍 3. {COL_PH}", options=["-- Tất cả --"] + list_ph)

    # Lọc đuổi cấp 3
    df_step3 = df_step2[df_step2[COL_PH] == sel_ph] if sel_ph != "-- Tất cả --" else df_step2

    with c4:
        list_st = sorted([x for x in df_step3[COL_ST].unique() if x])
        sel_st = st.selectbox(f"🛒 4. {COL_ST}", options=["-- Chọn siêu thị --"] + list_st)

    # 5. HIỂN THỊ KẾT QUẢ & THEO DÕI
    st.divider()
    if sel_st != "-- Chọn siêu thị --":
        st.success(f"✅ Đã chọn: **{sel_st}**")
        st.info(f"Phụ trách: {sel_nv} | {sel_ht} | {sel_ph}")
        
        if st.button(f"Bắt đầu ghi nhận cho {sel_st}"):
            st.write("Dữ liệu sau khi bạn nhập sẽ được lưu vào Google Sheets 'Data_Bao_Cao_MT'")

    # Bảng hiển thị dữ liệu báo cáo (Dành cho bạn theo dõi)
    st.subheader("📊 Dữ liệu báo cáo hiện có (Từ Google Sheets)")
    st.dataframe(df_report, use_container_width=True, hide_index=True)
