import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Cấu hình
st.set_page_config(page_title="Báo cáo Chương Dương", layout="wide")

st.title("📊 Quản lý dữ liệu MT Chương Dương")

# 2. Kết nối dữ liệu
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
    # Xử lý làm sạch tên cột
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error(f"Lỗi kết nối: {e}")
    st.stop()

# 3. Định nghĩa các cột CHẮC CHẮN CÓ trong ảnh của bạn
COL_NV = 'NHAN VIEN'
COL_HT = 'HE THONG'
COL_ST = 'SIEU THI'
COL_SP = 'SAN PHAM'

# 4. Bộ lọc 3 cấp: Nhân viên -> Hệ thống -> Siêu thị
st.subheader("🔍 Bộ lọc tìm kiếm")
c1, c2, c3 = st.columns(3)

with c1:
    list_nv = sorted(df[COL_NV].dropna().unique())
    sel_nv = st.multiselect("👤 Nhân viên", list_nv)

# Lọc bước 1
df_filtered = df[df[COL_NV].isin(sel_nv)] if sel_nv else df

with c2:
    list_ht = sorted(df_filtered[COL_HT].dropna().unique())
    sel_ht = st.multiselect("🏢 Hệ thống", list_ht)

# Lọc bước 2
if sel_ht:
    df_filtered = df_filtered[df_filtered[COL_HT].isin(sel_ht)]

with c3:
    list_st = sorted(df_filtered[COL_ST].dropna().unique())
    sel_st = st.multiselect("🛒 Siêu thị", list_st)

# Lọc bước 3
if sel_st:
    df_filtered = df_filtered[df_filtered[COL_ST].isin(sel_st)]

# 5. Hiển thị kết quả
st.divider()

# Thống kê nhanh theo các cột có trong ảnh
m1, m2, m3 = st.columns(3)
m1.metric("Tổng số dòng", len(df_filtered))
if 'FACING' in df_filtered.columns:
    m2.metric("Tổng Facing", int(df_filtered['FACING'].sum()))
if 'TON KHO' in df_filtered.columns:
    m3.metric("Tổng Tồn kho", int(df_filtered['TON KHO'].sum()))

# Bảng dữ liệu chính
st.dataframe(df_filtered, use_container_width=True, hide_index=True)

# Hiển thị ảnh nếu có link trong cột HINH ANH
if sel_st and len(df_filtered) > 0:
    st.subheader("📸 Hình ảnh trưng bày")
    for index, row in df_filtered.iterrows():
        if row['HINH ANH'] and str(row['HINH ANH']).startswith('http'):
            st.image(row['HINH ANH'], caption=f"{row[COL_ST]} - {row[COL_SP]}")
