import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# 1. THIẾT LẬP MÚI GIỜ VIỆT NAM
tz = pytz.timezone('Asia/Ho_Chi_Minh')

# 2. KẾT NỐI GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ĐỌC DỮ LIỆU TỪ GITHUB
@st.cache_data(ttl=600)
def load_data():
    try:
        # Đọc danh mục Nhân viên/Siêu thị (4 cột: NV, HT, PH, ST)
        df_master = pd.read_excel("data nhan vien.xlsx", header=None)
        df_master.columns = ['NHAN VIEN', 'HE THONG', 'PHUONG', 'SIEU THI']
        
        # Đọc danh mục Sản phẩm theo Hệ thống (2 cột: Hệ thống, Sản phẩm)
        df_sp_master = pd.read_excel("danh muc san pham.xlsx", header=None)
        df_sp_master.columns = ['HE THONG', 'SAN PHAM']
        
        return df_master, df_sp_master
    except Exception as e:
        st.error(f"Lỗi đọc file từ GitHub: {e}")
        return None, None

df_master, df_sp_master = load_data()

st.title("🥤 Báo Cáo Chương Dương (Smart Edition)")

if df_master is not None:
    # --- BỘ LỌC 3 CẤP ---
    st.subheader("📍 Chọn điểm bán")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        sel_nv = st.selectbox("1. Nhân viên", options=sorted(df_master['NHAN VIEN'].dropna().unique()))
        df_f1 = df_master[df_master['NHAN VIEN'] == sel_nv]

    with c2:
        sel_ht = st.selectbox("2. Hệ thống", options=sorted(df_f1['HE THONG'].dropna().unique()))
        df_f2 = df_f1[df_f1['HE THONG'] == sel_ht]

    with c3:
        sel_st = st.selectbox("3. Siêu thị", options=sorted(df_f2['SIEU THI'].dropna().unique()))

    st.divider()

    # --- XỬ LÝ DANH SÁCH SẢN PHẨM THÔNG MINH ---
    # Lấy danh sách SP tương ứng với Hệ thống đã chọn từ file 'danh muc san pham.xlsx'
    list_sp_dynamic = df_sp_master[df_sp_master['HE THONG'] == sel_ht]['SAN PHAM'].tolist()
    
    # Dự phòng: Nếu hệ thống chưa có trong file SP, hiện mặc định 7 món
    if not list_sp_dynamic:
        list_sp_dynamic = ["Sa Xi Lon", "Sa Xi Zero Lon", "Xi Pet 390", "Xi Pet 1.5L", "Soda Kem Lon", "Suoi 500mL", "Soda Lon"]

    st.subheader(f"📝 Nhập số liệu: {sel_st}")
    data_inputs = {}

    with st.form("form_report", clear_on_submit=True):
        h1, h2, h3 = st.columns([2, 1, 1])
        h1.write("**Sản Phẩm**"); h2.write("**Facing**"); h3.write("**Tồn kho**")

        for sp in list_sp_dynamic:
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"✅ {sp}")
            f_val = col2.number_input("", min_value=0, step=1, key=f"fc_{sp}", label_visibility="collapsed")
            t_val = col3.number_input("", min_value=0, step=1, key=f"tk_{sp}", label_visibility="collapsed")
            data_inputs[sp] = {"fc": f_val, "tk": t_val}

        hinh_anh = st.text_input("🔗 Link hình ảnh")
        ghi_chu = st.text_area("💬 Ghi chú")

        if st.form_submit_button("🚀 Gửi báo cáo"):
            now = datetime.now(tz)
            now_date = now.strftime("%d/%m/%Y")
            now_time = now.strftime("%H:%M:%S")

            rows_to_add = []
            for sp, values in data_inputs.items():
                if values['fc'] > 0 or values['tk'] > 0: 
                    rows_to_add.append({
                        "NGAY": now_date, "GIO": now_time,
                        "NHAN VIEN": sel_nv, "HE THONG": sel_ht,
                        "PHUONG": "N/A",
                        "SIEU THI": sel_st,
                        "SAN PHAM": sp, "FACING": values['fc'],
                        "TON KHO": values['tk'], "GHI CHU": ghi_chu, "HINH ANH": hinh_anh
                    })

            if rows_to_add:
                df_new = pd.DataFrame(rows_to_add)
                df_old = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                df_final = pd.concat([df_old, df_new], ignore_index=True)
                conn.update(worksheet="Data_Bao_Cao_MT", data=df_final)
                st.success(f"✅ Đã gửi thành công lúc {now_time}!")
            else:
                st.warning("Bạn Có Quên Gì Không.")
