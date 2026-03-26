import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Team MT - Báo Cáo", layout="wide")

@st.cache_data
def load_master_data():
    try:
        # 1. Đọc file thô
        df = pd.read_excel("data nhân viên.xlsx", header=None)
        
        # 2. Tìm dòng chứa tiêu đề (Dòng có chữ NHÂN VIÊN hoặc HỆ THỐNG)
        header_row = 0
        for i in range(len(df)):
            row_str = " ".join([str(x).upper() for x in df.iloc[i].values])
            if "NHÂN VIÊN" in row_str or "HỆ THỐNG" in row_str:
                header_row = i
                break
        
        # 3. Đọc lại với header chuẩn
        df = pd.read_excel("data nhân viên.xlsx", header=header_row)
        
        # 4. LÀM SẠCH TÊN CỘT (Quan trọng nhất)
        # Xóa khoảng trắng, xóa dấu xuống dòng, viết hoa
        df.columns = [str(c).replace('\n', ' ').strip().upper() for c in df.columns]
        
        # 5. Làm sạch dữ liệu trong ô
        df = df.dropna(how='all')
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else x)
        
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
        return None

df_master = load_master_data()

# Danh mục sản phẩm mới theo yêu cầu
DS_SAN_PHAM = [
    "Sá Xị Chương Dương (Lon 330ml)",
    "Sá Xị Zero (Lon 330ml)",
    "Sá Xị Chương Dương (Chai PET 390ml)",
    "Soda Kem (Lon 330ml)",
    "Sá Xị Chương Dương (Chai 1.5L)",
    "Nước Tinh Khiết CD (Chai 500ml)"
]

if df_master is not None:
    # Tự động gán tên cột dựa trên từ khóa (Tránh KeyError)
    cols = df_master.columns
    col_nv = next((c for c in cols if "NHÂN VIÊN" in c), None)
    col_ht = next((c for c in cols if "HỆ THỐNG" in c), None)
    col_ph = next((c for c in cols if "PHƯỜNG" in c), None)
    col_st = next((c for c in cols if "SIÊU THỊ" in c), None)

    if not all([col_nv, col_ht, col_ph, col_st]):
        st.error("⚠️ Không tìm thấy đủ các cột cần thiết (Nhân viên, Hệ thống, Phường, Siêu thị).")
        st.write("Các cột hiện có:", list(cols))
    else:
        # --- SIDEBAR 4 TẦNG ---
        with st.sidebar:
            st.header("👤 Định danh")
            
            list_nv = sorted([x for x in df_master[col_nv].unique() if x not in ['nan', 'None']])
            nv_selected = st.selectbox("1. Nhân viên:", list_nv)
            df_f1 = df_master[df_master[col_nv] == nv_selected]

            list_ht = sorted([x for x in df_f1[col_ht].unique() if x not in ['nan', 'None']])
            ht_selected = st.selectbox("2. Hệ thống:", list_ht)
            df_f2 = df_f1[df_f1[col_ht] == ht_selected]

            list_ph = sorted([x for x in df_f2[col_ph].unique() if x not in ['nan', 'None']])
            ph_selected = st.selectbox("3. Phường:", list_ph)
            df_f3 = df_f2[df_f2[col_ph] == ph_selected]

            list_st = sorted([x for x in df_f3[col_st].unique() if x not in ['nan', 'None']])
            st_selected = st.selectbox("4. Siêu thị:", list_st)

        # --- GIAO DIỆN NHẬP LIỆU ---
        st.title(f"🥤 {st_selected}")
        st.info(f"Phụ trách: {nv_selected} | {ht_selected} | {ph_selected}")

        with st.form("form_nhap", clear_on_submit=True):
            data_rows = []
            for sp in DS_SAN_PHAM:
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1: st.write(f"**{sp}**")
                with c2: f = st.number_input("Facing", min_value=0, step=1, key=f"f_{sp}")
                with c3: s = st.number_input("Tồn kho", min_value=0, step=1, key=f"s_{sp}")
                data_rows.append({"Sản phẩm": sp, "Facing": f, "Tồn kho": s})
            
            ghi_chu = st.text_area("Ghi chú:")
            submit = st.form_submit_button("🚀 XUẤT BÁO CÁO")

        if submit:
            df_report = pd.DataFrame(data_rows)
            df_report.insert(0, "Ngày", datetime.now().strftime("%d/%m/%Y"))
            df_report.insert(1, "Nhân viên", nv_selected)
            df_report.insert(2, "Hệ thống", ht_selected)
            df_report.insert(3, "Phường", ph_selected)
            df_report.insert(4, "Siêu thị", st_selected)
            df_report["Ghi chú"] = ghi_chu
            
            st.success("✅ Đã tạo báo cáo thành công!")
            st.dataframe(df_report)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_report.to_excel(writer, index=False)
            st.download_button("📥 Tải Excel", output.getvalue(), f"BC_{st_selected}.xlsx")

st.markdown("---")
st.caption("© 2026 Chuong Duong Beverage - Team MT")
