import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Cấu hình trang (Tối ưu cho thiết bị di động khi đi tuyến)
st.set_page_config(page_title="Chương Dương - Điều Hướng Đi Tuyến", layout="wide")

st.title("🥤 Công cụ Hỗ trợ Check Thị Trường")
st.markdown("Chọn thông tin để tìm nhanh siêu thị bạn đang ghé thăm:")

# 2. Kết nối trực tiếp với file Data_Bao_Cao_MT
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Đọc dữ liệu từ sheet cùng tên
    df = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
    
    # Làm sạch tên cột để tránh lỗi KeyError
    df.columns = df.columns.str.strip()
    
except Exception as e:
    st.error(f"❌ Không thể truy xuất file Data_Bao_Cao_MT: {e}")
    st.stop()

# 3. Định nghĩa các cột dựa trên cấu trúc file của bạn
COL_NV = 'NHAN VIEN'
COL_HT = 'HE THONG'
COL_PH = 'PHUONG'  # Cột này sẽ được dùng để lọc khu vực quản lý
COL_ST = 'SIEU THI'

# 4. Giao diện Bộ lọc Phân cấp (Cascading Filters)
c1, c2, c3, c4 = st.columns(4)

# --- Cấp 1: Nhân viên ---
with c1:
    list_nv = sorted(df[COL_NV].dropna().unique())
    sel_nv = st.selectbox(f"👤 1. Chọn {COL_NV}", options=["-- Chọn NV --"] + list_nv)

df_step1 = df[df[COL_NV] == sel_nv] if sel_nv != "-- Chọn NV --" else df

# --- Cấp 2: Hệ thống (Lọc theo NV đã chọn) ---
with c2:
    list_ht = sorted(df_step1[COL_HT].dropna().unique())
    sel_ht = st.selectbox(f"🏢 2. Hệ thống", options=["-- Tất cả hệ thống --"] + list_ht)

df_step2 = df_step1[df_step1[COL_HT] == sel_ht] if sel_ht != "-- Tất cả hệ thống --" else df_step1

# --- Cấp 3: Phường/Khu vực (Lọc theo Hệ thống) ---
with c3:
    # Nếu trong sheet chưa có cột PHUONG, code sẽ lấy giá trị mặc định để không báo lỗi
    if COL_PH in df_step2.columns:
        list_ph = sorted(df_step2[COL_PH].dropna().unique())
    else:
        list_ph = ["N/A"]
    sel_ph = st.selectbox(f"📍 3. Khu vực (Phường)", options=["-- Tất cả khu vực --"] + list_ph)

df_step3 = df_step2[df_step2[COL_PH] == sel_ph] if (sel_ph != "-- Tất cả khu vực --" and COL_PH in df_step2.columns) else df_step2

# --- Cấp 4: Siêu thị (Kết quả cuối cùng) ---
with c4:
    list_st = sorted(df_step3[COL_ST].dropna().unique())
    sel_st = st.selectbox(f"🛒 4. Chọn Siêu thị cần check", options=["-- Chọn siêu thị --"] + list_st)

# 5. Hiển thị thông tin siêu thị đã chọn để nhân viên bắt đầu check
st.markdown("---")
if sel_st != "-- Chọn siêu thị --":
    selected_data = df_step3[df_step3[COL_ST] == sel_st].iloc[0]
    st.success(f"📌 **Bạn đang thực hiện check tại:** {sel_st}")
    
    # Hiển thị các thông tin liên quan từ file data
    info_col1, info_col2, info_col3 = st.columns(3)
    info_col1.write(f"**Nhân viên:** {selected_data[COL_NV]}")
    info_col2.write(f"**Hệ thống:** {selected_data[COL_HT]}")
    if COL_PH in selected_data:
        info_col3.write(f"**Khu vực:** {selected_data[COL_PH]}")
    
    # Nút bấm giả lập để ghi nhận bắt đầu check
    if st.button(f"🚀 Bắt đầu ghi nhận dữ liệu cho {sel_st}"):
        st.balloons()
        st.write("Vui lòng nhập các thông số: FACING, TON KHO, HINH ANH...")
else:
    st.info("💡 Vui lòng chọn các thông tin trên để tìm nhanh siêu thị cần check.")
