import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# 1. THIẾT LẬP MÚI GIỜ VIỆT NAM
tz = pytz.timezone('Asia/Ho_Chi_Minh')

# 2. KẾT NỐI SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ĐỌC DANH MỤC TỪ GITHUB (Cấu trúc 5 cột: NV, HT, PH, ST, MSKH)
@st.cache_data(ttl=600)
def load_master_data():
    try:
        # Đọc file Excel từ GitHub
        df = pd.read_excel("data nhan vien.xlsx", header=None)
        # Gán tên cho 5 cột để App hiểu Cột E là MSKH
        df.columns = ['NHAN VIEN', 'HE THONG', 'PHUONG', 'SIEU THI', 'MSKH']
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file danh mục: {e}")
        return None

df_master = load_master_data()

st.title("🥤 Báo Cáo Thị Trường Chương Dương")

if df_master is not None:
    # --- BỘ LỌC 3 CẤP ---
    st.subheader("📍 Chọn thông tin tuyến")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Tạo danh sách nhân viên có thêm lựa chọn mặc định
        list_nv = ["Chọn nhân viên..."] + sorted(df_master['NHAN VIEN'].dropna().unique().tolist())
        sel_nv = st.selectbox("1. Nhân viên", options=list_nv)
        
    # Chỉ hiển thị các bước tiếp theo khi đã chọn tên nhân viên cụ thể
    if sel_nv != "Chọn nhân viên...":
        df_f1 = df_master[df_master['NHAN VIEN'] == sel_nv]

        with c2:
            list_ht = sorted(df_f1['HE THONG'].dropna().unique())
            sel_ht = st.selectbox("2. Hệ thống", options=list_ht)
            df_f2 = df_f1[df_f1['HE THONG'] == sel_ht]

        with c3:
            list_st = sorted(df_f2['SIEU THI'].dropna().unique())
            sel_st = st.selectbox("3. Siêu thị", options=list_st)

        st.divider()

        # --- LOGIC LỌC SẢN PHẨM THEO HỆ THỐNG ---
        st.subheader(f"📝 Nhập số liệu: {sel_st}")
        ht_check = sel_ht.upper().strip()

        # Phân loại danh sách sản phẩm hiển thị
        if ht_check == "BHX":
            list_sp = ["Sa Xi Lon"]
        elif ht_check in ["CF", "CM", "XTRA"]:
            list_sp = ["Sa Xi Lon", "Sa Xi Zero Lon", "Xi Pet 390", "Xi Pet 1.5L"]
        elif ht_check == "GS25":
            list_sp = ["Sa Xi Lon", "Sa Xi Zero Lon", "Xi Pet 390"]
        else:
            # Danh sách mặc định cho các hệ thống khác (Go!, Lotte, WinMart...)
            list_sp = ["Sa Xi Lon", "Sa Xi Zero Lon", "Xi Pet 390", "Xi Pet 1.5L", "Soda Kem Lon", "Suoi 500mL", "Soda Lon"]
        
        data_inputs = {}

        # --- FORM NHẬP LIỆU ---
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
                now = datetime.now(tz)
                now_date = now.strftime("%d/%m/%Y")
                now_time = now.strftime("%H:%M:%S")

                rows_to_add = []
                for sp, values in data_inputs.items():
                    # Chỉ lưu những dòng có nhập số liệu (tránh lưu rác)
                    if values['fc'] > 0 or values['tk'] > 0: 
                        rows_to_add.append({
                            "NGAY": now_date, "GIO": now_time,
                            "NHAN VIEN": sel_nv, "HE THONG": sel_ht,
                            "PHUONG": "N/A", "SIEU THI": sel_st,
                            "SAN PHAM": sp, "FACING": values['fc'],
                            "TON KHO": values['tk'], "GHI CHU": ghi_chu, "HINH ANH": hinh_anh
                        })

                if rows_to_add:
                    try:
                        # Đọc dữ liệu cũ và ghi đè dữ liệu mới
                        df_old = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                        df_final = pd.concat([df_old, pd.DataFrame(rows_to_add)], ignore_index=True)
                        conn.update(worksheet="Data_Bao_Cao_MT", data=df_final)
                        st.success(f"✅ Đã gửi báo cáo thành công lúc {now_time}!")
                    except Exception as e:
                        st.error(f"Lỗi khi gửi dữ liệu: {e}")
                else:
                    st.warning("Vui lòng nhập số liệu Facing hoặc Tồn kho trước khi gửi.")
    else:
        # Thông báo khi chưa chọn nhân viên
        st.info("👋 Chào bạn! Vui lòng chọn **Tên Nhân Viên** để bắt đầu làm báo cáo.")
