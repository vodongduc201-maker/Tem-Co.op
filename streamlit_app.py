import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Team MT - Báo Cáo", layout="wide")

# 1. ĐỌC DỮ LIỆU TỪ FILE EXCEL
@st.cache_data
def load_master_data():
    try:
        # Đọc file excel "data nhân viên.xlsx" trên GitHub
        df = pd.read_excel("data nhân viên.xlsx")
        # Làm sạch tên cột (xóa khoảng trắng thừa nếu có)
        df.columns = [str(c).strip() for c in df.columns]
        # Xóa các dòng trống hoàn toàn và làm sạch dữ liệu trong ô
        df = df.dropna(how='all').applymap(lambda x: str(x).strip() if pd.notnull(x) else x)
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
        return None

df_master = load_master_data()

# Danh mục sản phẩm
DS_SAN_PHAM = [
    "Sá Xị Chương Dương (Lon 330ml)",
    "Sá Xị Zero (Lon 330ml)",
    "Sá Xị Chương Dương (PET 390ml)",
    "Soda Kem (Lon 330ml)",
    "Sá Xị Chương Dương (Chai 1.5L)",
    "Nước Tinh Khiết CD (Chai 500ml)"
]

if df_master is not None:
    # --- PHẦN SIDEBAR: CẤU TRÚC 4 TẦNG ---
    with st.sidebar:
        st.header("👤 Định danh công tác")
        
        # Tầng 1: Nhân viên
        col_nv = "NHÂN VIÊN"
        list_nv = sorted(df_master[col_nv].unique())
        nv_selected = st.selectbox("1. Chọn Nhân viên:", list_nv)
        df_f1 = df_master[df_master[col_nv] == nv_selected]

        # Tầng 2: Hệ thống
        col_ht = "HỆ THỐNG"
        list_ht = sorted(df_f1[col_ht].unique())
        ht_selected = st.selectbox("2. Chọn Hệ thống:", list_ht)
        df_f2 = df_f1[df_f1[col_ht] == ht_selected]

        # Tầng 3: Phường
        col_ph = "PHƯỜNG"
        list_ph = sorted(df_f2[col_ph].unique())
        ph_selected = st.selectbox("3. Chọn Phường:", list_ph)
        df_f3 = df_f2[df_f2[col_ph] == ph_selected]

        # Tầng 4: Siêu thị
        col_st = "TÊN SIÊU THỊ"
        list_st = sorted(df_f3[col_st].unique())
        st_selected = st.selectbox("4. Chọn Siêu thị:", list_st)

    # --- GIAO DIỆN NHẬP LIỆU CHÍNH ---
    st.title(f"🥤 {st_selected}")
    st.caption(f"Khu vực: {ph_selected} | Hệ thống: {ht_selected} | NV: {nv_selected}")

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
        ghi_chu = st.text_area("🗒️ Ghi chú (Chương trình KM, đối thủ, hỏng hóc...):")
        
        submit = st.form_submit_button("🚀 XUẤT BÁO CÁO")

    if submit:
        # Tổng hợp dữ liệu
        df_report = pd.DataFrame(data_rows)
        df_report.insert(0, "Ngày", datetime.now().strftime("%d/%m/%Y"))
        df_report.insert(1, "Nhân viên", nv_selected)
        df_report.insert(2, "Hệ thống", ht_selected)
        df_report.insert(3, "Phường", ph_selected)
        df_report.insert(4, "Siêu thị", st_selected)
        df_report["Ghi chú"] = ghi_chu
        
        st.success(f"✅ Đã chuẩn bị báo cáo cho {st_selected}!")
        st.dataframe(df_report, use_container_width=True)
        
        # Tạo file Excel để tải về
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_report.to_excel(writer, index=False)
        st.download_button(
            label="📥 Tải file Excel báo cáo",
            data=output.getvalue(),
            file_name=f"BC_MT_{st_selected}_{datetime.now().strftime('%H%M')}.xlsx"
        )

st.markdown("---")
st.info("💡 Mẹo: Sau khi nhấn 'Gửi', app sẽ tự động xóa số liệu cũ để bạn nhập siêu thị tiếp theo.")
