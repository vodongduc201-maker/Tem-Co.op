import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# 1. THIẾT LẬP MÚI GIỜ VIỆT NAM
tz = pytz.timezone('Asia/Ho_Chi_Minh')

# 2. KẾT NỐI SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ĐỌC DANH MỤC TỪ GITHUB
@st.cache_data(ttl=600)
def load_master_data():
    try:
        df = pd.read_excel("data nhan vien.xlsx", header=None)
        num_cols = df.shape[1] 
        if num_cols >= 5:
            df = df.iloc[:, :5] 
            df.columns = ['NHAN VIEN', 'HE THONG', 'PHUONG', 'SIEU THI', 'MSKH']
        else:
            df.columns = ['NHAN VIEN', 'HE THONG', 'PHUONG', 'SIEU THI']
            df['MSKH'] = "N/A" 
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
        return None

df_master = load_master_data()

# --- GIAO DIỆN CHÍNH ---
st.title("🥤 Báo Cáo Thị Trường Chương Dương")

if df_master is not None:
    # --- BỘ LỌC BƯỚC 1 ---
    st.subheader("📍 Chọn thông tin nhân viên")
    
    list_nv = ["Chọn nhân viên..."] + sorted(df_master['NHAN VIEN'].dropna().unique().tolist())
    sel_nv = st.selectbox("1. Nhân viên", options=list_nv)

    # --- Ô GHI CHÚ QUY ĐỊNH (ĐẶT NGAY DƯỚI TÊN NHÂN VIÊN) ---
    st.info("""
    ### 📋 QUY ĐỊNH BÁO CÁO (Đọc kỹ trước khi nhập)
    1. **Tồn kho:** Nếu dưới 1/2 thùng => Nhập **Tồn = 0**. Note số lượng lẻ vào phần **Ghi chú**.
    2. **Hết hàng:** Nhập **Facing**, KHÔNG nhập tồn. Note tình trạng vào phần **Ghi chú**.
    3. **Điểm check-in:** Đóng cửa/Sai khu vực... vui lòng cập nhật lên **Group Báo Cáo MT**.
    """)

    if sel_nv != "Chọn nhân viên...":
        df_f1 = df_master[df_master['NHAN VIEN'] == sel_nv]
        
        st.divider()
        st.subheader("🏢 Chọn tuyến đi")
        c2, c3 = st.columns(2)

        with c2:
            # Thứ tự ưu tiên hệ thống
            priority_order = ['CM', 'EMART', 'XTRA', 'CF', 'SM', 'MM', 'SF', 'GS25', 'BHX', 'MIO']
            raw_list_ht = sorted(df_f1['HE THONG'].dropna().unique().tolist())
            list_ht = sorted(raw_list_ht, key=lambda x: priority_order.index(x.upper().strip()) if x.upper().strip() in priority_order else 999)
            sel_ht = st.selectbox("2. Hệ thống", options=list_ht)
            df_f2 = df_f1[df_f1['HE THONG'] == sel_ht]

        with c3:
            list_st = sorted(df_f2['SIEU THI'].dropna().unique())
            sel_st = st.selectbox("3. Siêu thị", options=list_st)

        st.divider()

        # --- FORM NHẬP LIỆU ---
        st.subheader(f"📝 Nhập số liệu: {sel_st}")
        
        ht_check = sel_ht.upper().strip()
        # Logic phân nhóm sản phẩm
        if ht_check == "BHX": list_sp = ["Sa Xi Lon"]
        elif ht_check == "GS25": list_sp = ["Sa Xi Lon", "Sa Xi Zero Lon", "Xi Pet 390"]
        elif ht_check in ["EMART", "CM", "XTRA", "FL", "CF", "SF"]: list_sp = ["Sa Xi Lon", "Sa Xi Zero Lon", "Xi Pet 390", "Xi Pet 1.5L"]
        elif ht_check in ["GO!", "GO", "BIGC", "MIO"]: list_sp = ["Sa Xi Lon", "Sa Xi Zero Lon", "Xi Pet 390", "Xi Pet 1.5L", "Soda Kem Lon"]
        else: list_sp = ["Sa Xi Lon", "Sa Xi Zero Lon", "Xi Pet 390", "Xi Pet 1.5L", "Soda Kem Lon", "Suoi 500mL", "Soda Lon"]
        
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
            ghi_chu = st.text_area("💬 Ghi chú", placeholder="Ghi số lẻ hoặc tình trạng hết hàng tại đây...")

            if st.form_submit_button("🚀 Gửi báo cáo"):
                now = datetime.now(tz)
                rows_to_add = []
                for sp, values in data_inputs.items():
                    if values['fc'] > 0 or values['tk'] > 0: 
                        rows_to_add.append({
                            "NGAY": now.strftime("%d/%m/%Y"), "GIO": now.strftime("%H:%M:%S"),
                            "NHAN VIEN": sel_nv, "HE THONG": sel_ht, "PHUONG": "N/A", "SIEU THI": sel_st,
                            "SAN PHAM": sp, "FACING": values['fc'], "TON KHO": values['tk'],
                            "GHI CHU": ghi_chu, "HINH ANH": hinh_anh
                        })

                if rows_to_add:
                    try:
                        df_old = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                        df_final = pd.concat([df_old, pd.DataFrame(rows_to_add)], ignore_index=True)
                        conn.update(worksheet="Data_Bao_Cao_MT", data=df_final)
                        st.success(f"✅ Đã gửi báo cáo thành công!")
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
                else:
                    st.warning("Vui lòng nhập số liệu.")
