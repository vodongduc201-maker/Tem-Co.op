import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. KẾT NỐI SHEETS (Lõi thành công của bạn)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ĐỌC DANH MỤC TỪ GITHUB (Nhân viên, Hệ thống, Phường, Siêu thị)
@st.cache_data(ttl=600)
def load_master_data():
    try:
        # header=None vì file Excel của bạn bắt đầu bằng dữ liệu ngay dòng 1
        df = pd.read_excel("data nhan vien.xlsx", header=None)
        df.columns = ['NHAN VIEN', 'HE THONG', 'PHUONG', 'SIEU THI']
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file danh mục từ GitHub: {e}")
        return None

df_master = load_master_data()

st.title("🥤 Báo Cáo Thị Trường Chương Dương")

if df_master is not None:
    # --- BỘ LỌC 4 CẤP ---
    st.subheader("📍 Thông tin điểm bán")
    c1, c2 = st.columns(2)
    
    with c1:
        list_nv = sorted(df_master['NHAN VIEN'].dropna().unique())
        sel_nv = st.selectbox("👤 1. Nhân viên", options=list_nv)
        df_f1 = df_master[df_master['NHAN VIEN'] == sel_nv]

        list_ht = sorted(df_f1['HE THONG'].dropna().unique())
        sel_ht = st.selectbox("🏢 2. Hệ thống", options=list_ht)
        df_f2 = df_f1[df_f1['HE THONG'] == sel_ht]

    with c2:
        list_ph = sorted(df_f2['PHUONG'].dropna().unique())
        sel_ph = st.selectbox("🏘️ 3. Phường", options=list_ph)
        df_f3 = df_f2[df_f2['PHUONG'] == sel_ph]

        list_st = sorted(df_f3['SIEU THI'].dropna().unique())
        sel_st = st.selectbox("🛒 4. Siêu thị", options=list_st)

    st.divider()

    # --- FORM GHI DỮ LIỆU ---
    with st.form("form_bao_cao", clear_on_submit=True):
        st.subheader(f"📝 Báo cáo: {sel_st}")
        
        # DANH SÁCH SẢN PHẨM MỚI CẬP NHẬT
        list_sp = [
            "Sa Xi Lon", "Sa Xi Zero Lon", "Xi Pet 390", 
            "Xi Pet 1.5L", "Soda Kem Lon", "Suoi 500mL", "Soda Lon"
        ]
        
        col1, col2 = st.columns(2)
        with col1:
            san_pham = st.selectbox("📦 Chọn Sản phẩm", options=list_sp)
            facing = st.number_input("📊 Facing", min_value=0, step=1)
            ton_kho = st.number_input("📉 Tồn kho", min_value=0, step=1)
        
        with col2:
            hinh_anh = st.text_input("🔗 Link hình ảnh")
            ghi_chu = st.text_area("💬 Ghi chú")
        
        if st.form_submit_button("🚀 Gửi báo cáo về Sheets"):
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
                # Logic ghi Sheets: Đọc -> Nối -> Update
                df_cu = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                df_moi = pd.concat([df_cu, new_row], ignore_index=True)
                conn.update(worksheet="Data_Bao_Cao_MT", data=df_moi)
                st.success(f"✅ Đã ghi thành công sản phẩm {san_pham} tại {sel_st}!")
            except Exception as e:
                st.error(f"❌ Lỗi khi lưu: {e}")

