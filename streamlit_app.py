import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Cấu hình trang
st.set_page_config(page_title="Báo cáo MT", layout="wide")

# Kết nối dữ liệu
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)

st.title("📊 Quản lý siêu thị theo phân cấp")

# --- BỘ LỌC PHÂN CẤP ---
with st.expander("🔍 Bộ lọc tìm kiếm", expanded=True):
    col1, col2, col3, col4 = st.columns(4)

    # Lọc Nhân viên
    with col1:
        nv_list = sorted(df['Tên nhân viên'].dropna().unique())
        sel_nv = st.multiselect("👤 Nhân viên", nv_list)
    
    # Lọc Hệ thống dựa trên Nhân viên
    df_step1 = df[df['Tên nhân viên'].isin(sel_nv)] if sel_nv else df
    with col2:
        ht_list = sorted(df_step1['Hệ thống'].dropna().unique())
        sel_ht = st.multiselect("🏢 Hệ thống", ht_list)

    # Lọc Phường dựa trên Hệ thống
    df_step2 = df_step1[df_step1['Hệ thống'].isin(sel_ht)] if sel_ht else df_step1
    with col3:
        ph_list = sorted(df_step2['Phường'].dropna().unique())
        sel_ph = st.multiselect("📍 Phường", ph_list)

    # Lọc Tên siêu thị dựa trên Phường
    df_step3 = df_step2[df_step2['Phường'].isin(sel_ph)] if sel_ph else df_step2
    with col4:
        st_list = sorted(df_step3['Tên siêu thị'].dropna().unique())
        sel_st = st.multiselect("🛒 Tên siêu thị", st_list)

# Kết quả lọc cuối cùng
df_final = df_step3[df_step3['Tên siêu thị'].isin(sel_st)] if sel_st else df_step3

# --- HIỂN THỊ ---
st.divider()
st.metric("Tổng số siêu thị", len(df_final))

# Hiển thị bảng với tính năng sắp xếp và tìm kiếm của Streamlit mới
st.dataframe(
    df_final, 
    use_container_width=True,
    column_config={
        "Tên nhân viên": "Nhân viên",
        "Hệ thống": "Hệ thống",
        "Phường": "Phường",
        "Tên siêu thị": "Siêu thị"
    }
)
