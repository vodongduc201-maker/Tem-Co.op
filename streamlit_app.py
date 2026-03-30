import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Cấu hình trang chuyên nghiệp
st.set_page_config(page_title="Chương Dương - Checklist Thị Trường", layout="wide")

st.title("🥤 Công cụ Hỗ trợ Check Thị Trường")
st.markdown("Chọn thông tin để tìm nhanh siêu thị bạn đang ghé thăm:")

# 2. Kết nối Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
    
    # Làm sạch tên cột (quan trọng nhất để tránh KeyError)
    df.columns = df.columns.str.strip()
    
except Exception as e:
    st.error(f"❌ Không thể kết nối dữ liệu: {e}")
    st.stop()

# 3. Định nghĩa tên cột (Khớp với dữ liệu lúc bạn ghi thành công)
# Mình dùng biến để nếu sau này bạn đổi tên trong Sheet thì chỉ cần sửa ở đây 1 lần
COL_NV = 'NHAN VIEN'
COL_HT = 'HE THONG'
COL_PH = 'PHUONG'
COL_ST = 'SIEU THI'

# Kiểm tra nhanh xem các cột có tồn tại không
actual_cols = df.columns.tolist()
for c in [COL_NV, COL_HT, COL_PH, COL_ST]:
    if c not in actual_cols:
        st.warning(f"⚠️ Chú ý: Cột '{c}' không tìm thấy. Hệ thống sẽ tự tạo danh sách trống.")
        df[c] = "Chưa có dữ liệu"

# 4. Giao diện Bộ lọc Phân cấp (Cascading)
# Chúng ta dùng 4 cột để tối ưu không gian trên điện thoại/máy tính
c1, c2, c3, c4 = st.columns(4)

with c1:
    list_nv = sorted(df[COL_NV].dropna().unique())
    sel_nv = st.selectbox(f"👤 1. Chọn {COL_NV}", options=["-- Tất cả --"] + list_nv)

# Lọc bước 1
df_filter = df.copy()
if sel_nv != "-- Tất cả --":
    df_filter = df_filter[df_filter[COL_NV] == sel_nv]

with c2:
    list_ht = sorted(df_filter[COL_HT].dropna().unique())
    sel_ht = st.selectbox(f"🏢 2. Hệ thống của {sel_nv if sel_nv != '-- Tất cả --' else ''}", options=["-- Tất cả --"] + list_ht)

# Lọc bước 2
if sel_ht != "-- Tất cả --":
    df_filter = df_filter[df_filter[COL_HT] == sel_ht]

with c3:
    list_ph = sorted(df_filter[COL_PH].dropna().unique())
    sel_ph = st.selectbox(f"📍 3. Khu vực (Phường)", options=["-- Tất cả --"] + list_ph)

# Lọc bước 3
if sel_ph != "-- Tất cả --":
    df_filter = df_filter[df_filter[COL_PH] == sel_ph]

with c4:
    list_st = sorted(df_filter[COL_ST].dropna().unique())
    sel_st = st.selectbox(f"🛒 4. Chọn Siêu thị cần check", options=["-- Tất cả --"] + list_st)

# Lọc bước cuối
if sel_st != "-- Tất cả --":
    df_final = df_filter[df_filter[COL_ST] == sel_st]
else:
    df_final = df_filter

# 5. Hiển thị Kết quả điều hướng
st.markdown("---")
if sel_st != "-- Tất cả --":
    st.success(f"✅ Bạn đang xem dữ liệu của: **{sel_st}**")
else:
    st.info(f"💡 Tìm thấy **{len(df_final)}** siêu thị phù hợp với lựa chọn của bạn.")

# Hiển thị bảng kết quả rút gọn để nhân viên dễ nhìn
st.dataframe(
    df_final[[COL_NV, COL_HT, COL_PH, COL_ST]], 
    use_container_width=True,
    hide_index=True
)

# Thêm nút bấm nhanh (Ví dụ dẫn link đến Form nhập liệu nếu bạn có)
if sel_st != "-- Tất cả --":
    st.button(f"Tiến hành Check-in tại {sel_st}")
