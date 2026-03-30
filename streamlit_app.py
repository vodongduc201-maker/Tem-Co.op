import pytz  # Thêm thư viện này ở đầu file

# Thiết lập múi giờ Việt Nam
tz = pytz.timezone('Asia/Ho_Chi_Minh')
now = datetime.now(tz)

# Lấy Ngày và Giờ chuẩn Việt Nam
now_date = now.strftime("%d/%m/%Y")
now_time = now.strftime("%H:%M:%S")import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. KẾT NỐI SHEETS (Lõi thành công của bạn)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ĐỌC DANH MỤC TỪ GITHUB (NV, HT, PH, ST)
@st.cache_data(ttl=600)
def load_master_data():
    try:
        # header=None vì file Excel của bạn bắt đầu bằng dữ liệu ngay dòng 1
        df = pd.read_excel("data nhan vien.xlsx", header=None)
        # Gán tên cột theo thứ tự A, B, C, D
        df.columns = ['NHAN VIEN', 'HE THONG', 'PHUONG', 'SIEU THI']
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file danh mục từ GitHub: {e}")
        return None

df_master = load_master_data()

st.title("🥤 Báo Cáo Thị Trường Chương Dương")

if df_master is not None:
    # --- BỘ LỌC ĐIỀU HƯỚNG 4 CẤP (Lọc đuổi nhau) ---
    st.subheader("📍 Thông tin tuyến đường")
    
    # Cấp 1: Chọn Nhân viên
    list_nv = sorted(df_master['NHAN VIEN'].dropna().unique())
    sel_nv = st.selectbox("👤 1. Chọn Nhân viên", options=list_nv)
    df_f1 = df_master[df_master['NHAN VIEN'] == sel_nv]

    # Cấp 2: Chọn Hệ thống (Lọc theo Nhân viên đã chọn)
    list_ht = sorted(df_f1['HE THONG'].dropna().unique())
    sel_ht = st.selectbox("🏢 2. Chọn Hệ thống", options=list_ht)
    df_f2 = df_f1[df_f1['HE THONG'] == sel_ht]

    # Cấp 3: Chọn Phường (Lọc theo Hệ thống đã chọn)
    list_ph = sorted(df_f2['PHUONG'].dropna().unique())
    sel_ph = st.selectbox("🏘️ 3. Chọn Phường", options=list_ph)
    df_f3 = df_f2[df_f2['PHUONG'] == sel_ph]

    # Cấp 4: Chọn Siêu thị (Lọc theo Phường và Hệ thống đã chọn)
    list_st = sorted(df_f3['SIEU THI'].dropna().unique())
    sel_st = st.selectbox("🛒 4. Chọn Siêu thị", options=list_st)

    st.divider()

    # --- DANH SÁCH SẢN PHẨM LIỆT KÊ SẴN ---
    st.subheader(f"📝 Báo cáo: {sel_st}")
    
    list_sp = [
        "Sa Xi Lon", "Sa Xi Zero Lon", "Xi Pet 390", 
        "Xi Pet 1.5L", "Soda Kem Lon", "Suoi 500mL", "Soda Lon"
    ]

    data_inputs = {}

    with st.form("form_multi_sp", clear_on_submit=True):
        # Tiêu đề cột
        h1, h2, h3 = st.columns([2, 1, 1])
        h1.write("**Tên Sản Phẩm**")
        h2.write("**Facing**")
        h3.write("**Tồn kho**")

        for sp in list_sp:
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"✅ {sp}")
            # Dùng key duy nhất cho mỗi input để tránh lỗi
            f_val = col2.number_input("", min_value=0, step=1, key=f"fc_{sp}", label_visibility="collapsed")
            t_val = col3.number_input("", min_value=0, step=1, key=f"tk_{sp}", label_visibility="collapsed")
            data_inputs[sp] = {"fc": f_val, "tk": t_val}

        st.write("---")
        hinh_anh = st.text_input("🔗 Link hình ảnh (Nếu có)")
        ghi_chu = st.text_area("💬 Ghi chú")

        if st.form_submit_button("🚀 Gửi tất cả báo cáo"):
            rows_to_add = []
            now_date = datetime.now().strftime("%d/%m/%Y")
            now_time = datetime.now().strftime("%H:%M:%S")

            for sp, values in data_inputs.items():
                # Chỉ lưu những sản phẩm có nhập số liệu
                if values['fc'] > 0 or values['tk'] > 0: 
                    rows_to_add.append({
                        "NGAY": now_date, "GIO": now_time,
                        "NHAN VIEN": sel_nv, "HE THONG": sel_ht,
                        "PHUONG": sel_ph, "SIEU THI": sel_st,
                        "SAN PHAM": sp, "FACING": values['fc'],
                        "TON KHO": values['tk'], "GHI CHU": ghi_chu,
                        "HINH ANH": hinh_anh
                    })

            if rows_to_add:
                try:
                    df_new = pd.DataFrame(rows_to_add)
                    df_old = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                    df_final = pd.concat([df_old, df_new], ignore_index=True)
                    conn.update(worksheet="Data_Bao_Cao_MT", data=df_final)
                    st.success(f"✅ Đã gửi thành công báo cáo cho {len(rows_to_add)} mã hàng!")
                except Exception as e:
                    st.error(f"❌ Lỗi ghi Sheets: {e}")
            else:
                st.warning("Bạn chưa nhập số liệu cho sản phẩm nào.")

