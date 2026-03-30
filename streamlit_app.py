import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Cấu hình giao diện rộng để dễ nhìn bảng
st.set_page_config(page_title="Báo cáo Hệ Thống MT", layout="wide")

st.title("📊 Quản lý siêu thị theo phân cấp")
st.markdown("---")

# 2. Kết nối Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
    
    # Xử lý làm sạch tên cột (xóa khoảng trắng thừa)
    df.columns = df.columns.str.strip()
    
except Exception as e:
    st.error(f"❌ Lỗi kết nối Sheets: {e}")
    st.stop()

# 3. Định nghĩa tên cột chính xác (Bạn hãy sửa chữ trong ngoặc '' nếu Sheets đổi tên)
COL_NV = 'NHAN VIEN'
COL_HT = 'HE THONG'
COL_PH = 'PHUONG'
COL_ST = 'TEN SIEU THI'

# Kiểm tra xem các cột có tồn tại không để tránh lỗi KeyError
missing_cols = [c for c in [COL_NV, COL_HT, COL_PH, COL_ST] if c not in df.columns]

if missing_cols:
    st.warning(f"⚠️ Cảnh báo: Không tìm thấy các cột {missing_cols} trong file Sheets.")
    st.write("Danh sách cột thực tế đang có:", df.columns.tolist())
    st.stop()

# 4. Thiết lập Bộ lọc Phân cấp (Cascading Filters)
with st.container():
    c1, c2, c3, c4 = st.columns(4)

    # Cấp 1: Nhân viên
    with c1:
        list_nv = sorted(df[COL_NV].dropna().unique())
        sel_nv = st.multiselect(f"👤 {COL_NV}", list_nv)
    
    # Cấp 2: Hệ thống (Lọc theo Nhân viên)
    df_step1 = df[df[COL_NV].isin(sel_nv)] if sel_nv else df
    with c2:
        list_ht = sorted(df_step1[COL_HT].dropna().unique())
        sel_ht = st.multiselect(f"🏢 {COL_HT}", list_ht)

    # Cấp 3: Phường (Lọc theo Hệ thống)
    df_step2 = df_step1[df_step1[COL_HT].isin(sel_ht)] if sel_ht else df_step1
    with c3:
        list_ph = sorted(df_step2[COL_PH].dropna().unique())
        sel_ph = st.multiselect(f"📍 {COL_PH}", list_ph)

    # Cấp 4: Tên siêu thị (Lọc theo Phường)
    df_step3 = df_step2[df_step2[COL_PH].isin(sel_ph)] if sel_ph else df_step2
    with c4:
        list_st = sorted(df_step3[COL_ST].dropna().unique())
        sel_st = st.multiselect(f"🛒 {COL_ST}", list_st)

# 5. Kết quả lọc cuối cùng
df_final = df_step3[df_step3[COL_ST].isin(sel_st)] if sel_st else df_step3

# 6. Hiển thị thông số và Bảng dữ liệu
st.markdown("---")
col_m1, col_m2 = st.columns(2)
col_m1.metric("Tổng số dòng", len(df))
col_m2.metric("Kết quả sau lọc", len(df_final))

st.dataframe(
    df_final, 
    use_container_width=True,
    hide_index=True # Ẩn cột số thứ tự cho gọn
)

# Chân trang hiện phiên bản (Tùy chọn)
st.caption(f"Đã cập nhật dữ liệu mới nhất | Streamlit v{st.__version__}")
