import streamlit as st
import pandas as pd
from datetime import datetime
import io
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Team MT - Báo Cáo Tổng", layout="wide")

# --- 1. ĐỌC MASTER DATA ---
@st.cache_data
def load_master_data():
    try:
        df_raw = pd.read_excel("data nhân viên.xlsx", header=None)
        header_row = 0
        for i in range(len(df_raw)):
            row_str = " ".join([str(x).upper() for x in df_raw.iloc[i].values])
            if "NHÂN VIÊN" in row_str or "HỆ THỐNG" in row_str:
                header_row = i
                break
        df = pd.read_excel("data nhân viên.xlsx", header=header_row)
        df = df.iloc[:, :4] 
        df.columns = ["NHÂN VIÊN", "HỆ THỐNG", "PHƯỜNG", "TÊN SIÊU THỊ"]
        df = df.dropna(subset=["TÊN SIÊU THỊ"])
        df = df.map(lambda x: str(x).strip().upper() if pd.notnull(x) else x)
        return df
    except: return None

df_master = load_master_data()

# DANH MỤC SẢN PHẨM
DS_SAN_PHAM = [
    "Sá Xị Chương Dương (Lon 330ml)",
    "Sá Xị Zero (Lon 330ml)",
    "Sá Xị Chương Dương (Chai PET 390ml)",
    "Soda Kem (Lon 330ml)",
    "Sá Xị Chương Dương (Chai 1.5L)",
    "Nước Tinh Khiết CD (Chai 500ml)"
]

# --- 2. KẾT NỐI GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

if df_master is not None:
    with st.sidebar:
        st.header("👤 Định danh công tác")
        list_nv = sorted([x for x in df_master["NHÂN VIÊN"].unique() if x not in ['NAN', 'NONE']])
        nv_selected = st.selectbox("1. Nhân viên:", list_nv)
        df_f1 = df_master[df_master["NHÂN VIÊN"] == nv_selected]

        list_ht = sorted([x for x in df_f1["HỆ THỐNG"].unique() if x not in ['NAN', 'NONE']])
        ht_selected = st.selectbox("2. Hệ thống:", list_ht)
        df_f2 = df_f1[df_f1["HỆ THỐNG"] == ht_selected]

        list_ph = sorted([x for x in df_f2["PHƯỜNG"].unique() if x not in ['NAN', 'NONE']])
        ph_selected = st.selectbox("3. Phường:", list_ph)
        df_f3 = df_f2[df_f2["PHƯỜNG"] == ph_selected]

        list_st = sorted([x for x in df_f3["TÊN SIÊU THỊ"].unique() if x not in ['NAN', 'NONE']])
        st_selected = st.selectbox("4. Siêu thị:", list_st)

    st.title(f"🥤 {st_selected}")
    
    # Form nhập liệu
    with st.form("entry_form", clear_on_submit=True):
        st.subheader("Số liệu trưng bày & Tồn kho")
        data_rows = []
        for sp in DS_SAN_PHAM:
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1: st.write(f"**{sp}**")
            with c2: f = st.number_input("Facing", min_value=0, step=1, key=f"f_{sp}")
            with c3: s = st.number_input("Tồn kho", min_value=0, step=1, key=f"s_{sp}")
            data_rows.append({"Sản phẩm": sp, "Facing": f, "Tồn kho": s})
        
        st.divider()
        st.subheader("📸 Hình ảnh")
        uploaded_file = st.file_uploader("Chụp ảnh trưng bày:", type=['jpg','png','jpeg'])
        ghi_chu = st.text_area("🗒️ Ghi chú:")
        submit = st.form_submit_button("🚀 GỬI BÁO CÁO")

    if submit:
        # Chuẩn bị dữ liệu gửi đi
        time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        final_df = pd.DataFrame([{
            "Thời gian": time_now,
            "Nhân viên": nv_selected,
            "Hệ thống": ht_selected,
            "Siêu thị": st_selected,
            "Dữ liệu": str(data_rows), # Gộp data vào 1 ô để dễ quản lý
            "Ghi chú": ghi_chu,
            "Ảnh": "Có" if uploaded_file else "Không"
        }])
        
        try:
            # Gửi dữ liệu lên Google Sheets (Sheet tên là 'Data_Bao_Cao_MT')
            conn.create(worksheet="Data_Bao_Cao_MT", data=final_df)
            st.success("✅ Đã lưu dữ liệu vào Google Sheets tổng!")
            st.balloons()
        except Exception as e:
            st.error(f"Lỗi gửi dữ liệu: {e}")

st.markdown("---")
st.caption("© 2026 Chương Dương Beverage")
