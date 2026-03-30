import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. KẾT NỐI SHEETS (Mốc thành công của bạn)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ĐỌC DANH MỤC TỪ GITHUB (Để nhân viên chọn cho nhanh)
@st.cache_data(ttl=600)
def load_master_data():
    try:
        # header=None vì file Excel của bạn bắt đầu bằng dữ liệu ngay dòng 1
        df = pd.read_excel("data nhan vien.xlsx", header=None)
        # Gán tên cột theo đúng thứ tự A, B, C, D trong file của bạn
        df.columns = ['NHAN VIEN', 'HE THONG', 'PHUONG', 'SIEU THI']
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file danh mục từ GitHub: {e}")
        return None

df_master = load_master_data()

st.title("🥤 App Báo Cáo Thị Trường Chương Dương")

if df_master is not None:
    # --- PHẦN BỘ LỌC 4 CẤP (Điều hướng thông minh) ---
    st.subheader("📍 Chọn điểm bán")
    
    # Cấp 1: Nhân viên (Cột A)
    list_nv = sorted(df_master['NHAN VIEN'].dropna().unique())
    sel_nv = st.selectbox("👤 1. Chọn Nhân viên", options=list_nv)
    df_f1 = df_master[df_master['NHAN VIEN'] == sel_nv]

    # Cấp 2: Hệ thống (Cột B)
    list_ht = sorted(df_f1['HE THONG'].dropna().unique())
    sel_ht = st.selectbox("🏢 2. Chọn Hệ thống", options=list_ht)
    df_f2 = df_f1[df_f1['HE THONG'] == sel_ht]

    # Cấp 3: Phường (Cột C)
    list_ph = sorted(df_f2['PHUONG'].dropna().unique())
    sel_ph = st.selectbox("🏘️ 3. Chọn Phường", options=list_ph)
    df_f3 = df_f2[df_f2['PHUONG'] == sel_ph]

    # Cấp 4: Siêu thị (Cột D)
    list_st = sorted(df_f3['SIEU THI'].dropna().unique())
    sel_st = st.selectbox("🛒 4. Chọn Siêu thị", options=list_st)

    st.divider()

    # --- PHẦN GHI DỮ LIỆU (Giữ nguyên logic bạn đã thành công) ---
    with st.form("form_bao_cao", clear_on_submit=True):
        st.subheader(f"📝 Nhập báo cáo cho: {sel_st}")
        
        # Các ô nhập liệu
        san_pham = st.text_input("📦 Sản phẩm", value="Sá Xị")
        facing = st.number_input("📊 Facing", min_value=0, step=1)
        ton_kho = st.number_input("📉 Tồn kho", min_value=0, step=1)
        hinh_anh = st.text_input("🔗 Link hình ảnh (Google Drive/Lark)")
        ghi_chu = st.text_area("💬 Ghi chú thêm")
        
        # NÚT BẤM QUAN TRỌNG NHẤT
        if st.form_submit_button("🚀 Gửi báo cáo về Sheets"):
            # 1. Tạo dòng dữ liệu mới (Gồm cả thông tin lọc và thông tin nhập)
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
            
            # 2. Thực hiện ghi vào Sheets (Logic Đọc cũ -> Nối mới -> Update)
            try:
                df_cu = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                df_moi = pd.concat([df_cu, new_data], ignore_index=True)
                conn.update(worksheet="Data_Bao_Cao_MT", data=df_moi)
                st.success(f"✅ Đã ghi thành công dữ liệu tại {sel_st}!")
            except Exception as e:
                st.error(f"❌ Lỗi khi ghi vào Sheets: {e}")


