import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Cấu hình giao diện
st.set_page_config(page_title="Báo cáo Chương Dương MT", layout="wide")

st.title("📊 Quản lý báo cáo MT - Chương Dương")
st.markdown("---")

# 2. Kết nối Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
    
    # Làm sạch dữ liệu: xóa khoảng trắng ở đầu/cuối tên cột
    df.columns = df.columns.str.strip()
    
except Exception as e:
    st.error(f"❌ Không thể kết nối dữ liệu: {e}")
    st.stop()

# 3. Định nghĩa tên cột DỰA THEO ẢNH BẠN GỬI
# Lưu ý: Trong ảnh của bạn cột siêu thị chỉ là 'SIEU THI'
COL_NV = 'NHAN VIEN'
COL_HT = 'HE THONG'
COL_ST = 'SIEU THI'

# --- BỘ LỌC PHÂN CẤP ---
with st.container():
    c1, c2, c3 = st.columns(3)

    # Lọc Nhân viên (Cột C trong ảnh)
    with c1:
        list_nv = sorted(df[COL_NV].dropna().unique())
        sel_nv = st.multiselect(f"👤 Chọn {COL_NV}", list_nv)
    
    # Lọc Hệ thống (Cột D trong ảnh - dựa trên Nhân viên)
    df_filtered = df[df[COL_NV].isin(sel_nv)] if sel_nv else df
    with c2:
        list_ht = sorted(df_filtered[COL_HT].dropna().unique())
        sel_ht = st.multiselect(f"🏢 Chọn {COL_HT}", list_ht)

    # Lọc Siêu thị (Cột E trong ảnh - dựa trên Hệ thống)
    if sel_ht:
        df_filtered = df_filtered[df_filtered[COL_HT].isin(sel_ht)]
    
    with c3:
        list_st = sorted(df_filtered[COL_ST].dropna().unique())
        sel_st = st.multiselect(f"🛒 Chọn {COL_ST}", list_st)

# Kết quả lọc cuối cùng
if sel_st:
    df_final = df_filtered[df_filtered[COL_ST].isin(sel_st)]
else:
    df_final = df_filtered

# --- HIỂN THỊ THỐNG KÊ NHANH ---
st.markdown("---")
m1, m2, m3 = st.columns(3)
m1.metric("Tổng số lượt viếng thăm", len(df))
m2.metric("Số dòng sau khi lọc", len(df_final))
# Tính tổng Facing nếu có dữ liệu
if 'FACING' in df_final.columns:
    total_facing = df_final['FACING'].sum()
    m3.metric("Tổng Facing", int(total_facing))

# --- BẢNG DỮ LIỆU ---
st.dataframe(
    df_final, 
    use_container_width=True,
    hide_index=True
)

st.caption(f"Dữ liệu cập nhật lúc: {df['NGAY'].max()} | Streamlit Engine v{st.__version__}")
