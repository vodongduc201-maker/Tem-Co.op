import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Kết nối Google Sheets (Để ghi báo cáo)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Đọc danh mục từ GitHub (Xử lý file không có tiêu đề)
@st.cache_data(ttl=600)
def load_github_data():
    try:
        # header=None vì ảnh của bạn cho thấy dòng 1 là dữ liệu luôn, không có tiêu đề
        df = pd.read_excel("data nhan vien.xlsx", header=None)
        # Gán tên cột theo thứ tự A, B, C, D trong file của bạn
        df.columns = ['NHAN VIEN', 'HE THONG', 'PHUONG', 'SIEU THI']
        return df
    except Exception as e:
        st.error(f"❌ Lỗi đọc file Excel từ GitHub: {e}")
        return None

df_master = load_github_data()

st.title("🥤 Hệ Thống Báo Cáo Thị Trường MT")

if df_master is not None:
    st.subheader("🔍 Bước 1: Chọn Thông Tin Tuyến")
    
    # --- BỘ LỌC PHÂN CẤP 4 BƯỚC ---
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        list_nv = sorted(df_master['NHAN VIEN'].dropna().unique())
        sel_nv = st.selectbox("👤 1. Nhân viên", options=["-- Chọn NV --"] + list_nv)
    
    # Lọc dữ liệu theo Nhân viên
    df_step1 = df_master[df_master['NHAN VIEN'] == sel_nv] if sel_nv != "-- Chọn NV --" else df_master
    
    with c2:
        list_ht = sorted(df_step1['HE THONG'].dropna().unique())
        sel_ht = st.selectbox("🏢 2. Hệ thống", options=["-- Chọn Hệ thống --"] + list_ht)
        
    # Lọc dữ liệu theo Hệ thống
    df_step2 = df_step1[df_step1['HE THONG'] == sel_ht] if sel_ht != "-- Chọn Hệ thống --" else df_step1

    with c3:
        list_ph = sorted(df_step2['PHUONG'].dropna().unique())
        sel_ph = st.selectbox("📍 3. Phường", options=["-- Chọn Phường --"] + list_ph)
        
    # Lọc dữ liệu theo Phường
    df_step3 = df_step2[df_step2['PHUONG'] == sel_ph] if sel_ph != "-- Chọn Phường --" else df_step2

    with c4:
        list_st = sorted(df_step3['SIEU THI'].dropna().unique())
        sel_st = st.selectbox("🛒 4. Siêu thị", options=["-- Chọn Siêu thị --"] + list_st)

    # --- FORM NHẬP BÁO CÁO ---
    if sel_st != "-- Chọn Siêu thị --":
        st.divider()
        st.success(f"✅ Đang báo cáo cho: **{sel_st}** ({sel_ht} - {sel_ph})")
        
        with st.form("form_report", clear_on_submit=True):
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                san_pham = st.text_input("📦 Sản phẩm", value="Sá Xị Chương Dương")
                facing = st.number_input("📊 Facing", min_value=0, step=1)
                ton_kho = st.number_input("📉 Tồn kho", min_value=0, step=1)
            with col_in2:
                hinh_anh = st.text_input("🔗 Link hình ảnh")
                ghi_chu = st.text_area("💬 Ghi chú")

            if st.form_submit_button("🚀 Gửi báo cáo"):
                # Tạo dòng dữ liệu mới
                new_row = pd.DataFrame([{
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
                    # Đọc - Nối - Cập nhật vào Google Sheets
                    df_old = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                    df_final = pd.concat([df_old, new_row], ignore_index=True)
                    conn.update(worksheet="Data_Bao_Cao_MT", data=df_final)
                    st.success(f"🏁 Đã gửi báo cáo thành công!")
                except Exception as e:
                    st.error(f"❌ Lỗi lưu dữ liệu: {e}")

# --- XEM LẠI DỮ LIỆU ---
with st.expander("📊 Xem 5 dòng báo cáo mới nhất"):
    df_view = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
    st.dataframe(df_view.tail(5), use_container_width=True)
