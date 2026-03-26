import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Team MT - Báo Cáo", layout="wide")

# 1. ĐỌC DỮ LIỆU TỪ FILE EXCEL
@st.cache_data
def load_master_data():
    try:
        # Đọc file excel bạn đã up lên GitHub
        df = pd.read_excel("data nhân viên.xlsx")
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
        return None

df_master = load_master_data()

# 2. DANH SÁCH SẢN PHẨM CẬP NHẬT (Đã thêm PET 390)
DS_SAN_PHAM = [
    "Sá Xị Chương Dương (Lon 330ml)",
    "Sá Xị Zero (Lon 330ml)",
    "Sá Xị Chương Dương (PET 390ml)", # <-- Sản phẩm mới thêm
    "Soda Kem (Lon 330ml)",
    "Sá Xị Chương Dương (Chai 1.5L)",
    "Nước Tinh Khiết CD (Chai 500ml)"
]

if df_master is not None:
    col_ten_st = df_master.columns[1]
    col_he_thong = df_master.columns[2]
    col_nhan_vien = df_master.columns[3]

    # --- SIDEBAR: ƯU TIÊN NHÂN VIÊN ---
    with st.sidebar:
        st.header("👤 Định danh")
        list_nv = sorted([str(x) for x in df_master[col_nhan_vien].unique() if str(x) != 'nan'])
        nv_selected = st.selectbox("1. Bạn là ai?", list_nv)

        df_f1 = df_master[df_master[col_nhan_vien] == nv_selected]
        list_he_thong = sorted([str(x) for x in df_f1[col_he_thong].unique() if str(x) != 'nan'])
        he_thong_selected = st.selectbox("2. Chọn Hệ thống:", list_he_thong)

        df_f2 = df_f1[df_f1[col_he_thong] == he_thong_selected]
        list_st = sorted([str(x) for x in df_f2[col_ten_st].unique() if str(x) != 'nan'])
        st_selected = st.selectbox("3. Chọn Siêu thị:", list_st)

    # --- GIAO DIỆN NHẬP LIỆU ---
    st.title(f"🥤 Báo cáo: {st_selected}")
    st.info(f"Đang nhập cho: **{he_thong_selected}** | NV: **{nv_selected}**")

    with st.form("form_nhap", clear_on_submit=True):
        data_rows = []
        # Tạo bảng nhập liệu cho từng sản phẩm
        for sp in DS_SAN_PHAM:
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1: st.write(f"**{sp}**")
            with c2: f = st.number_input("Facing", min_value=0, step=1, key=f"f_{sp}")
            with c3: s = st.number_input("Tồn kho", min_value=0, step=1, key=f"s_{sp}")
            data_rows.append({"Sản phẩm": sp, "Facing": f, "Tồn kho": s})
        
        ghi_chu = st.text_area("🗒️ Ghi chú:")
        submit = st.form_submit_button("🚀 XUẤT BÁO CÁO")

    if submit:
        df_final = pd.DataFrame(data_rows)
        df_final.insert(0, "Ngày", datetime.now().strftime("%d/%m/%Y"))
        df_final.insert(1, "Nhân viên", nv_selected)
        df_final.insert(2, "Hệ thống", he_thong_selected)
        df_final.insert(3, "Siêu thị", st_selected)
        df_final["Ghi chú"] = ghi_chu
        
        st.success(f"✅ Đã xử lý xong dữ liệu cho {st_selected}!")
        st.dataframe(df_final, use_container_width=True)
        
        # Nút tải Excel tạm thời
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False)
        st.download_button("📥 TẢI EXCEL TẠM THỜI", output.getvalue(), f"BC_{st_selected}.xlsx")

st.markdown("---")
st.caption("Team MT")
