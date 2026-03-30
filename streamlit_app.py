import streamlit as st            # Dòng 1
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz                       # Thư viện xử lý múi giờ

# 1. THIẾT LẬP MÚI GIỜ VIỆT NAM (Bổ sung)
tz = pytz.timezone('Asia/Ho_Chi_Minh')

# 2. KẾT NỐI SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ĐỌC DANH MỤC TỪ GITHUB
@st.cache_data(ttl=600)
def load_master_data():
    try:
        df = pd.read_excel("data nhan vien.xlsx", header=None)
        df.columns = ['NHAN VIEN', 'HE THONG', 'PHUONG', 'SIEU THI']
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file danh mục: {e}")
        return None

df_master = load_master_data()

st.title("🥤 Báo Cáo Thị Trường Chương Dương")

if df_master is not None:
    # --- BỘ LỌC 4 CẤP ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sel_nv = st.selectbox("Nhân viên", options=sorted(df_master['NHAN VIEN'].unique()))
    with c2:
        sel_ht = st.selectbox("Hệ thống", options=sorted(df_master[df_master['NHAN VIEN']==sel_nv]['HE THONG'].unique()))
    with c3:
        sel_ph = st.selectbox("Phường", options=sorted(df_master[(df_master['NHAN VIEN']==sel_nv) & (df_master['HE THONG']==sel_ht)]['PHUONG'].unique()))
    with c4:
        sel_st = st.selectbox("Siêu thị", options=sorted(df_master[(df_master['NHAN VIEN']==sel_nv) & (df_master['PHUONG']==sel_ph)]['SIEU THI'].unique()))

    st.divider()

    # --- DANH SÁCH SẢN PHẨM ---
    list_sp = ["Sa Xi Lon", "Sa Xi Zero Lon", "Xi Pet 390", "Xi Pet 1.5L", "Soda Kem Lon", "Suoi 500mL", "Soda Lon"]
    data_inputs = {}

    with st.form("form_multi_sp", clear_on_submit=True):
        h1, h2, h3 = st.columns([2, 1, 1])
        h1.write("**Sản Phẩm**"); h2.write("**Facing**"); h3.write("**Tồn kho**")

        for sp in list_sp:
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"✅ {sp}")
            f_val = col2.number_input("", min_value=0, step=1, key=f"fc_{sp}", label_visibility="collapsed")
            t_val = col3.number_input("", min_value=0, step=1, key=f"tk_{sp}", label_visibility="collapsed")
            data_inputs[sp] = {"fc": f_val, "tk": t_val}

        hinh_anh = st.text_input("🔗 Link hình ảnh")
        ghi_chu = st.text_area("💬 Ghi chú")

        if st.form_submit_button("🚀 Gửi báo cáo"):
            # LẤY THỜI GIAN CHUẨN VN TẠI ĐÂY
            now = datetime.now(tz)
            now_date = now.strftime("%d/%m/%Y")
            now_time = now.strftime("%H:%M:%S")

            rows_to_add = []
            for sp, values in data_inputs.items():
                if values['fc'] > 0 or values['tk'] > 0: 
                    rows_to_add.append({
                        "NGAY": now_date, "GIO": now_time,
                        "NHAN VIEN": sel_nv, "HE THONG": sel_ht,
                        "PHUONG": sel_ph, "SIEU THI": sel_st,
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
                st.warning("Chưa nhập số liệu.")
