import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Cấu hình chuyên nghiệp cho Mobile/Desktop
st.set_page_config(page_title="Chương Dương - Check Thị Trường", layout="wide")

st.title("🥤 Giám Sát Check Thị Trường MT")
st.info("Dữ liệu ghi nhận từ đội ngũ nhân viên đi tuyến")

# 2. Kết nối Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
    # Làm sạch tên cột
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error(f"Lỗi kết nối dữ liệu: {e}")
    st.stop()

# 3. Định nghĩa cột chuẩn theo ảnh Check-in của bạn
COL_NGAY = 'NGAY'
COL_GIO = 'GIO'
COL_NV = 'NHAN VIEN'
COL_HT = 'HE THONG'
COL_ST = 'SIEU THI'
COL_SP = 'SAN PHAM'
COL_FC = 'FACING'
COL_TK = 'TON KHO'
COL_HA = 'HINH ANH'

# 4. Bộ lọc thông minh cho Giám sát
with st.sidebar:
    st.header("🔍 Bộ Lọc Giám Sát")
    
    # Lọc theo Ngày
    list_ngay = sorted(df[COL_NGAY].unique(), reverse=True)
    sel_ngay = st.multiselect("📅 Chọn Ngày", list_ngay)
    df_f = df[df[COL_NGAY].isin(sel_ngay)] if sel_ngay else df

    # Lọc theo Nhân viên
    list_nv = sorted(df_f[COL_NV].dropna().unique())
    sel_nv = st.multiselect("👤 Nhân viên đi tuyến", list_nv)
    if sel_nv: df_f = df_f[df_f[COL_NV].isin(sel_nv)]

    # Lọc theo Hệ thống
    list_ht = sorted(df_f[COL_HT].dropna().unique())
    sel_ht = st.multiselect("🏢 Hệ thống", list_ht)
    if sel_ht: df_f = df_f[df_f[COL_HT].isin(sel_ht)]

# 5. Hiển thị Chỉ số thị trường (KPIs)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Số lượt Check-in", len(df_f))
m2.metric("Số Siêu thị đã ghé", len(df_f[COL_ST].unique()))
if COL_FC in df_f.columns:
    m3.metric("Tổng Facing", int(df_f[COL_FC].sum()))
if COL_TK in df_f.columns:
    m4.metric("Tổng Tồn kho", int(df_f[COL_TK].sum()))

# 6. Hiển thị Bảng dữ liệu chi tiết
st.subheader("📋 Chi tiết lộ trình check")
st.dataframe(
    df_f[[COL_NGAY, COL_GIO, COL_NV, COL_HT, COL_ST, COL_SP, COL_FC, COL_TK]], 
    use_container_width=True,
    hide_index=True
)

# 7. PHẦN QUAN TRỌNG: XEM ẢNH THỊ TRƯỜNG
st.divider()
st.subheader("📸 Hình ảnh thực tế từ điểm bán")

# Chỉ hiện ảnh khi đã lọc để tránh treo máy nếu dữ liệu quá nhiều
if len(df_f) > 100:
    st.warning("Vui lòng lọc theo Nhân viên hoặc Ngày để xem hình ảnh chi tiết.")
else:
    # Tạo lưới hiển thị ảnh (3 ảnh mỗi hàng)
    img_cols = st.columns(3)
    for idx, row in df_f.iterrows():
        with img_cols[idx % 3]:
            if row[COL_HA] and str(row[COL_HA]).startswith('http'):
                st.image(row[COL_HA], caption=f"{row[COL_ST]} ({row[COL_GIO]})", use_column_width=True)
            else:
                st.caption(f"🚫 {row[COL_ST]}: Không có ảnh")
