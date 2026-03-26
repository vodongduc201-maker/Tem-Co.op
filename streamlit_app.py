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
        # Chuẩn hóa tên cột để tránh lỗi khoảng trắng
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
        return None

df_master = load_master_data()
DS_SAN_PHAM = ["Sá Xị Chương Dương (Lon)", "Sá Xị Zero (Lon)", "Soda Kem (Lon)", "Sá Xị 1.5L", "Nước tinh khiết CD"]

if df_master is not None:
    # Xác định tên cột dựa trên file bạn gửi (Cột 4 là NV, Cột 3 là Hệ thống, Cột 2 là Siêu thị)
    col_ten_st = df_master.columns[1]
    col_he_thong = df_master.columns[2]
    col_nhan_vien = df_master.columns[3]

    # --- ĐIỀU CHỈNH SIDEBAR: ƯU TIÊN NHÂN VIÊN ---
    with st.sidebar:
        st.header("👤 Định danh")
        
        # 1. Chọn Nhân viên trước
        list_nv = sorted(df_master[col_nhan_vien].unique().tolist())
        nv_selected = st.selectbox("1. Bạn là ai?", list_nv)

        # 2. Chọn Hệ thống (Lọc theo nhân viên đã chọn)
        df_f1 = df_master[df_master[col_nhan_vien] == nv_selected]
        list_he_thong = sorted(df_f1[col_he_thong].unique().tolist())
        he_thong_selected = st.selectbox("2. Chọn Hệ thống:", list_he_thong)

        # 3. Chọn Siêu thị (Lọc theo nhân viên và hệ thống đã chọn)
        df_f2 = df_f1[df_f1[col_he_thong] == he_thong_selected]
        list_st = sorted(df_f2[col_ten_st].unique().tolist())
        st_selected = st.selectbox("3. Chọn Siêu thị:", list_st)

    # --- GIAO DIỆN NHẬP LIỆU CHÍNH ---
    st.title(f"🥤 Báo cáo: {st_selected}")
    st.info(f"Đang nhập báo cáo cho hệ thống **{he_thong_selected}** - Nhân viên: **{nv_selected}**")

    with st.form("form_nhap", clear_on_submit=True):
        data_rows = []
        for sp in DS_SAN_PHAM:
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1: st.write(f"**{sp}**")
            with c2: f = st.number_input("Facing", min_value=0, step=1, key=f"f_{sp}")
            with c3: s = st.number_input("Tồn kho", min_value=0, step=1, key=f"s_{sp}")
            data_rows.append({"Sản phẩm": sp, "Facing": f, "Tồn kho": s})
        
        ghi_chu = st.text_area("🗒️ Ghi chú (KM, đối thủ...):")
        submit = st.form_submit_button("🚀 XUẤT BÁO CÁO")

    if submit:
        # Xử lý dữ liệu ra DataFrame để nhân viên xem lại hoặc tải về (trước khi kết nối Sheets)
        df_final = pd.DataFrame(data_rows)
        df_final.insert(0, "Ngày", datetime.now().strftime("%d/%m/%Y"))
        df_final.insert(1, "Nhân viên", nv_selected)
        df_final.insert(2, "Hệ thống", he_thong_selected)
        df_final.insert(3, "Siêu thị", st_selected)
        df_final["Ghi chú"] = ghi_chu
        
        st.success(f"✅ Báo cáo {st_selected} đã sẵn sàng!")
        st.dataframe(df_final, use_container_width=True)
        
        # Tạm thời vẫn để nút tải Excel để nhân viên test app
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False)
        st.download_button("📥 TẢI EXCEL (BẢN NHÁP)", output.getvalue(), f"BC_{st_selected}.xlsx")

st.markdown("---")
st.caption("©
