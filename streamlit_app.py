import streamlit as st            
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz                       

# 1. THIẾT LẬP MÚI GIỜ VIỆT NAM
tz = pytz.timezone('Asia/Ho_Chi_Minh')

# 2. KẾT NỐI SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ĐỌC DANH MỤC TỪ GITHUB (NV, HT, PH, ST)
@st.cache_data(ttl=0)
def load_master_data():
    try:
        df = pd.read_excel("data nhan vien.xlsx", header=None)
        # Vẫn giữ cấu trúc 4 cột A,B,C,D từ file Excel để tránh lỗi đọc data
        df.columns = ['NHAN VIEN', 'HE THONG', 'PHUONG', 'SIEU THI']
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file danh mục: {e}")
        return None

df_master = load_master_data()

st.title("🥤 Báo Cáo Thị Trường Chương Dương")

if df_master is not None:
    # --- BỘ LỌC TỐI GIẢN (BỎ PHƯỜNG) ---
    st.subheader("📍 Chọn điểm bán")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        list_nv = sorted(df_master['NHAN VIEN'].dropna().unique())
        sel_nv = st.selectbox("1. Nhân viên", options=list_nv)
        df_f1 = df_master[df_master['NHAN VIEN'] == sel_nv]

    with c2:
        list_ht = sorted(df_f1['HE THONG'].dropna().unique())
        sel_ht = st.selectbox("2. Hệ thống", options=list_ht)
        df_f2 = df_f1[df_f1['HE THONG'] == sel_ht]

    with c3:
        # Lọc trực tiếp Siêu thị theo Hệ thống (Bỏ qua Phường)
        list_st = sorted(df_f2['SIEU THI'].dropna().unique())
        sel_st = st.selectbox("3. Siêu thị", options=list_st)

    st.divider()

    # --- DANH SÁCH SẢN PHẨM LIỆT KÊ ---
    st.subheader(f"📝 Nhập số liệu: {sel_st}")
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
            # Lấy giờ VN
            now = datetime.now(tz)
            now_date = now.strftime("%d/%m/%Y")
            now_time = now.strftime("%H:%M:%S")

            rows_to_add = []
            for sp, values in data_inputs.items():
                if values['fc'] > 0 or values['tk'] > 0: 
                    rows_to_add.append({
                        "NGAY": now_date, "GIO": now_time,
                        "NHAN VIEN": sel_nv, "HE THONG": sel_ht,
                        "PHUONG": "N/A", # Ghi chú N/A vì không chọn phường
                        "SIEU THI": sel_st,
                        "SAN PHAM": sp, "FACING": values['fc'],
                        "TON KHO": values['tk'], "GHI CHU": ghi_chu, "HINH ANH": hinh_anh
                    })

            if rows_to_add:
                try:
                    df_new = pd.DataFrame(rows_to_add)
                    df_old = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                    df_final = pd.concat([df_old, df_new], ignore_index=True)
                    conn.update(worksheet="Data_Bao_Cao_MT", data=df_final)
                    st.success(f"✅ Đã gửi thành công lúc {now_time}!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
            else:
                st.warning("Vui lòng nhập số liệu.")
