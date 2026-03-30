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
        # header=None giúp đọc file không có dòng tiêu đề
        df = pd.read_excel("data nhan vien.xlsx", header=None)
        # Tự đặt tên cột cho chuẩn để code bên dưới sử dụng
        df.columns = ['NHAN VIEN', 'HE THONG', 'PHUONG', 'SIEU THI']
        return df
    except Exception as e:
        st.error(f"❌ Lỗi file Excel trên GitHub: {e}")
        return None

df_master = load_github_data()

st.title("🥤 Báo Cáo Thị Trường Chương Dương")

if df_master is not None:
    # --- BỘ LỌC ĐIỀU HƯỚNG ---
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Lấy danh sách nhân viên từ cột A (đã đặt tên là NHAN VIEN)
        list_nv = sorted(df_master['NHAN VIEN'].unique())
        sel_nv = st.selectbox("👤 1. Chọn NHAN VIEN", options=list_nv)
    
    # Lọc Phường theo Nhân viên
    df_nv = df_master[df_master['NHAN VIEN'] == sel_nv]
    with c2:
        list_ph = sorted(df_nv['PHUONG'].unique())
        sel_ph = st.selectbox("📍 2. Chọn Phường", options=list_ph)
        
    # Lọc Siêu thị theo Phường
    df_ph = df_nv[df_nv['PHUONG'] == sel_ph]
    with c3:
        list_st = sorted(df_ph['SIEU THI'].unique())
        sel_st = st.selectbox("🛒 3. Chọn Siêu thị", options=list_st)

    st.divider()

    # --- FORM GHI DỮ LIỆU ---
    with st.form("form_ghi_du_lieu", clear_on_submit=True):
        st.subheader(f"📝 Ghi nhận: {sel_st}")
        
        # Lấy Hệ thống tự động từ cột B
        he_thong_auto = df_ph[df_ph['SIEU THI'] == sel_st]['HE THONG'].values[0]
        
        c_in1, c_in2 = st.columns(2)
        with c_in1:
            san_pham = st.text_input("📦 Sản phẩm", value="Sá Xị Chương Dương")
            facing = st.number_input("📊 Facing", min_value=0, step=1)
            ton_kho = st.number_input("📉 Tồn kho", min_value=0, step=1)
        with c_in2:
            hinh_anh = st.text_input("🔗 Link hình ảnh")
            ghi_chu = st.text_area("💬 Ghi chú")

        if st.form_submit_button("🚀 Gửi báo cáo"):
            # Tạo dòng mới để add vào sheet
            new_row = pd.DataFrame([{
                "NGAY": datetime.now().strftime("%d/%m/%Y"),
                "GIO": datetime.now().strftime("%H:%M:%S"),
                "NHAN VIEN": sel_nv,
                "HE THONG": str(he_thong_auto).upper(),
                "PHUONG": sel_ph,
                "SIEU THI": sel_st,
                "SAN PHAM": san_pham,
                "FACING": facing,
                "TON KHO": ton_kho,
                "GHI CHU": ghi_chu,
                "HINH ANH": hinh_anh
            }])
            
            try:
                # Đọc dữ liệu cũ và nối dòng mới vào (Add to Sheets)
                df_old = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                df_final = pd.concat([df_old, new_row], ignore_index=True)
                conn.update(worksheet="Data_Bao_Cao_MT", data=df_final)
                st.success(f"✅ Đã ghi nhận thành công cho {sel_st}!")
            except Exception as e:
                st.error(f"❌ Lỗi khi add vào Sheets: {e}")

# --- DÀNH CHO ADMIN THEO DÕI ---
with st.expander("📊 Xem lịch sử báo cáo"):
    df_view = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
    st.dataframe(df_view.tail(10), use_container_width=True)
