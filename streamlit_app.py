import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Team MT - Báo Cáo", layout="wide")

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
        # Ép 4 cột đầu tiên theo đúng thứ tự Sidebar
        df = df.iloc[:, :4] 
        df.columns = ["NHÂN VIÊN", "HỆ THỐNG", "PHƯỜNG", "TÊN SIÊU THỊ"]
        df = df.dropna(subset=["TÊN SIÊU THỊ"])
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else x)
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
        return None

df_master = load_master_data()

DS_SAN_PHAM = [
    "Sá Xị Chương Dương (Lon 330ml)",
    "Sá Xị Zero (Lon 330ml)",
    "Sá Xị Chương Dương (Chai PET 390ml)",
    "Soda Kem (Lon 330ml)",
    "Sá Xị Chương Dương (Chai 1.5L)",
    "Nước Tinh Khiết CD (Chai 500ml)"
]

if df_master is not None:
    col_nv, col_ht, col_ph, col_st = "NHÂN VIÊN", "HỆ THỐNG", "PHƯỜNG", "TÊN SIÊU THỊ"

    with st.sidebar:
        st.header("👤 Định danh công tác")
        list_nv = sorted([x for x in df_master[col_nv].unique() if x not in ['nan', 'None']])
        nv_selected = st.selectbox("1. Chọn Nhân viên:", list_nv)
        df_f1 = df_master[df_master[col_nv] == nv_selected]

        list_ht = sorted([x for x in df_f1[col_ht].unique() if x not in ['nan', 'None']])
        ht_selected = st.selectbox("2. Chọn Hệ thống:", list_ht)
        df_f2 = df_f1[df_f1[col_ht] == ht_selected]

        list_ph = sorted([x for x in df_f2[col_ph].unique() if x not in ['nan', 'None']])
        ph_selected = st.selectbox("3. Chọn Phường:", list_ph)
        df_f3 = df_f2[df_f2[col_ph] == ph_selected]

        list_st = sorted([x for x in df_f3[col_st].unique() if x not in ['nan', 'None']])
        st_selected = st.selectbox("4. Chọn Siêu thị:", list_st)

    st.title(f"🥤 {st_selected}")
    st.caption(f"Khu vực: {ph_selected} | Hệ thống: {ht_selected} | NV: {nv_selected}")

    with st.form("entry_form", clear_on_submit=True):
        st.subheader("Số liệu trưng bày & Tồn kho")
        data_rows = []
        for sp in DS_SAN_PHAM:
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1: st.write(f"**{sp}**")
            # --- ĐÃ SỬA LỖI ĐÓNG NGOẶC TẠI ĐÂY ---
            with c2: f = st.number_input("Facing", min_value=0, step=1, key=f"f_{sp}")
            with c3: s = st.number_input("Tồn kho", min_value=0, step=1, key=f"s_{sp}")
            data_rows.append({"Sản phẩm": sp, "Facing": f, "Tồn kho": s})
        
        st.divider()
        ghi_chu = st.text_area("🗒️ Ghi chú:")
        submit = st.form_submit_button("🚀 XUẤT BÁO CÁO")

    if submit:
        df_report = pd.DataFrame(data_rows)
        df_report.insert(0, "Ngày", datetime.now().strftime("%d/%m/%Y"))
        df_report.insert(1, "Nhân viên", nv_selected)
        df_report.insert(2, "Hệ thống", ht_selected)
        df_report.insert(3, "Phường", ph_selected)
        df_report.insert(4, "Siêu thị", st_selected)
        df_report["Ghi chú"] = ghi_chu
        
        st.success(f"✅ Đã chuẩn bị báo cáo cho {st_selected}!")
        st.dataframe(df_report, use_container_width=True)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_report.to_excel(writer, index=False)
        st.download_button("📥 Tải Excel", output.getvalue(), f"BC_{st_selected}.xlsx")

st.markdown("---")
st.caption("© 2026 Chương Dương Beverage - Team MT")
