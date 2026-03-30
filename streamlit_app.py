import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Cấu hình giao diện rộng
st.set_page_config(page_title="Báo cáo Chương Dương MT", layout="wide")

st.title("📊 Quản lý siêu thị theo phân cấp")
st.markdown("---")

# 2. Kết nối Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
    
    # Làm sạch tên cột (xóa khoảng trắng thừa)
    df.columns = df.columns.str.strip()
    
except Exception as e:
    st.error(f"❌ Lỗi kết nối: {e}")
    st.stop()

# 3. Định nghĩa tên cột chuẩn theo file của bạn
COL_NV = 'NHAN VIEN'
COL_HT = 'HE THONG'
COL_PH = 'PHUONG'
COL_ST = 'SIEU THI'

# 4. Bộ lọc phân cấp (Cascading Filters)
with st.container():
    c1, c2, c3, c4 = st.columns(4)

    # Cấp 1: Nhân viên
    with c1:
        list_nv = sorted(df[COL_NV].dropna().unique())
        sel_nv = st.multiselect(f"👤 {COL_NV}", list_nv)
    
    # Cấp 2: Hệ thống (Lọc theo NV)
    df_step1 = df[df[COL_NV].isin(sel_nv)] if sel_nv else df
    with c2:
        list_ht = sorted(df_step1[COL_HT].dropna().unique())
        sel_ht = st.multiselect(f"🏢 {COL_HT}", list_ht)

    # Cấp 3: Phường (Lọc theo Hệ thống)
    df_step2 = df_step1[df_step1[COL_HT].isin(sel_ht)] if sel_ht else df_step1
    with c3:
        list_ph = sorted(df_step2[COL_PH].dropna().unique())
        sel_ph = st.multiselect(f"📍 {COL_PH}", list_ph)

    # Cấp 4: Siêu thị (Lọc theo Phường)
    df_step3 = df_step2[df_step2[COL_PH].isin(sel_ph)] if sel_ph else df_step2
    with c4:
        list_st = sorted(df_step3[COL_ST].dropna().unique())
        sel_st = st.multiselect(f"🛒 {COL_ST}", list_st)

# 5. Kết quả lọc cuối cùng
df_final = df_step3[df_step3[COL_ST].isin(sel_st)] if sel_st else df_step3

# 6. Hiển thị thông số và Bảng dữ liệu
st.markdown("---")
m1, m2 = st.columns(2)
m1.metric("Tổng số dòng", len(df))
m2.metric("Kết quả sau lọc", len(df_final))

st.dataframe(
    df_final, 
    use_container_width=True,
    hide_index=True
)

st.caption(f"Cập nhật dữ liệu từ Sheets | Streamlit v{st.__version__}")
