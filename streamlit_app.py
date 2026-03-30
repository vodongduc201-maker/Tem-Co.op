import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Chương Dương - Check Thị Trường", layout="wide")

st.title("🥤 Công cụ Báo cáo Thị Trường MT")

# --- 2. ĐỌC DANH MỤC TỪ GITHUB (FILE EXCEL) ---
@st.cache_data(ttl=600)
def load_master_data():
    try:
        # Đọc file excel nằm cùng thư mục trên GitHub
        df = pd.read_excel("data nhan vien.xlsx")
        # Chuẩn hóa tên cột: Viết hoa, bỏ khoảng trắng
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"❌ Không tìm thấy file danh mục trên GitHub: {e}")
        return None

df_master = load_master_data()

# --- 3. KẾT NỐI GOOGLE SHEETS ĐỂ GHI DỮ LIỆU ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. GIAO DIỆN ĐIỀU HƯỚNG (BỘ LỌC) ---
if df_master is not None:
    st.subheader("🔍 Bước 1: Chọn Thông Tin Điểm Bán")
    
    # Định nghĩa các cột chuẩn
    C_NV = 'NHAN VIEN'
    C_HT = 'HE THONG'
    C_PH = 'PHUONG'
    C_ST = 'SIEU THI'

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        list_nv = sorted(df_master[C_NV].dropna().unique())
        sel_nv = st.selectbox(f"👤 Nhân viên", options=["-- Chọn NV --"] + list_nv)

    df_nv = df_master[df_master[C_NV] == sel_nv] if sel_nv != "-- Chọn NV --" else df_master

    with c2:
        list_ht = sorted(df_nv[C_HT].dropna().unique())
        sel_ht = st.selectbox(f"🏢 Hệ thống", options=["-- Tất cả --"] + list_ht)

    df_ht = df_nv[df_nv[C_HT] == sel_ht] if sel_ht != "-- Tất cả --" else df_nv

    with c3:
        list_ph = sorted(df_ht[C_PH].dropna().unique())
        sel_ph = st.selectbox(f"📍 Phường", options=["-- Tất cả --"] + list_ph)

    df_ph = df_ht[df_ht[C_PH] == sel_ph] if sel_ph != "-- Tất cả --" else df_ht

    with c4:
        list_st = sorted(df_ph[C_ST].dropna().unique())
        sel_st = st.selectbox(f"🛒 Siêu thị", options=["-- Chọn siêu thị --"] + list_st)

    # --- 5. GIAO DIỆN NHẬP BÁO CÁO ---
    if sel_st != "-- Chọn siêu thị --":
        st.divider()
        st.subheader(f"📝 Bước 2: Nhập báo cáo cho {sel_st}")
        
        with st.form("form_report", clear_on_submit=True):
            col_in1, col_in2 = st.columns(2)
            
            with col_in1:
                san_pham = st.text_input("📦 Sản phẩm", placeholder="VD: Sá Xị Chương Dương")
                facing = st.number_input("📊 Facing (Mặt trưng bày)", min_value=0, step=1)
                ton_kho = st.number_input("📉 Tồn kho (Thùng/Lon)", min_value=0, step=1)
            
            with col_in2:
                hinh_anh = st.text_input("🔗 Link Hình Ảnh", placeholder="Dán link ảnh tại đây")
                ghi_chu = st.text_area("💬 Ghi chú", placeholder="Tình trạng quầy kệ, đối thủ...")
            
            submit_button = st.form_submit_button("🚀 Gửi Báo Cáo")

            if submit_button:
                # Tạo dòng dữ liệu mới
                new_data = pd.DataFrame([{
                    "NGAY": datetime.now().strftime("%d/%m/%Y"),
                    "GIO": datetime.now().strftime("%H:%M:%S"),
                    "NHAN VIEN": sel_nv,
                    "HE THONG": sel_ht,
                    "PHUONG": sel_ph,
                    "SIEU THI": sel_st,
                    "SAN PHAM": san_pham,
                    "FACING": facing,
                    "TON KHO": ton_kho,
                    "GHI CHU": ghi_chu,
                    "HINH ANH": hinh_anh
                }])

                try:
                    # Ghi dữ liệu vào Google Sheets
                    df_existing = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                    updated_df = pd.concat([df_existing, new_data], ignore_index=True)
                    conn.update(worksheet="Data_Bao_Cao_MT", data=updated_df)
                    st.success("✅ Đã gửi báo cáo thành công!")
                except Exception as e:
                    st.error(f"❌ Lỗi khi lưu dữ liệu: {e}")

# --- 6. PHẦN DÀNH CHO BẠN THEO DÕI (ADMIN) ---
with st.expander("📊 Xem lịch sử báo cáo thị trường"):
    try:
        df_view = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
        st.dataframe(df_view.tail(20), use_container_width=True)
    except:
        st.write("Chưa có dữ liệu báo cáo.")
