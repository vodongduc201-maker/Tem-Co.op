import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Team MT Chương Dương - Báo Cáo", page_icon="🥤", layout="wide")

# 1. ĐỌC DỮ LIỆU TỪ FILE EXCEL BẠN GỬI
@st.cache_data
def load_data():
    try:
        # Đọc file excel (đảm bảo file này đã được up lên GitHub cùng thư mục app)
        df = pd.read_excel("data nhân viên.xlsx")
        # Chuẩn hóa tên cột (bỏ khoảng trắng thừa nếu có)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        st.error("❌ Không tìm thấy file 'data nhân viên.xlsx'. Vui lòng kiểm tra lại trên GitHub!")
        return None

df_master = load_data()

# DANH SÁCH SẢN PHẨM (Bạn có thể điều chỉnh SKU tại đây)
DS_SAN_PHAM = [
    "Sá Xị Chương Dương (Lon 330ml)",
    "Sá Xị Zero (Lon 330ml)",
    "Soda Kem (Lon 330ml)",
    "Sá Xị Chương Dương (Chai 1.5L)",
    "Nước Tinh Khiết CD (Chai 500ml)"
]

if df_master is not None:
    st.title("🥤 Hệ thống Báo Cáo Team MT")
    
    # 2. BỘ LỌC THÔNG MINH TRÊN SIDEBAR
    with st.sidebar:
        st.header("🔍 Lọc địa điểm")
        # Lấy danh sách Hệ thống (Cột thứ 3 trong file của bạn)
        col_he_thong = df_master.columns[2] 
        list_he_thong = sorted(df_master[col_he_thong].unique().tolist())
        he_thong_selected = st.selectbox("1. Chọn Hệ thống:", list_he_thong)

        # Lọc danh sách Nhân viên theo Hệ thống (Cột thứ 4)
        col_nhan_vien = df_master.columns[3]
        df_filtered_nv = df_master[df_master[col_he_thong] == he_thong_selected]
        list_nv = sorted(df_filtered_nv[col_nhan_vien].unique().tolist())
        nv_selected = st.selectbox("2. Chọn Nhân viên:", list_nv)

        # Lọc danh sách Siêu thị theo Nhân viên đã chọn (Cột thứ 2)
        col_ten_st = df_master.columns[1]
        df_filtered_st = df_filtered_nv[df_filtered_nv[col_nhan_vien] == nv_selected]
        list_st = sorted(df_filtered_st[col_ten_st].unique().tolist())
        st_selected = st.selectbox("3. Chọn Siêu thị:", list_st)

    # 3. FORM NHẬP LIỆU
    with st.form("form_nhap_lieu", clear_on_submit=True):
        st.subheader(f"📍 Báo cáo tại: {st_selected}")
        st.write(f"👤 Nhân viên: **{nv_selected}** | Hệ thống: **{he_thong_selected}**")
        st.markdown("---")
        
        data_input = []
        for sp in DS_SAN_PHAM:
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.write(f"**{sp}**")
            with c2:
                f = st.number_input(f"Facing", min_value=0, step=1, key=f"f_{sp}")
            with c3:
                s = st.number_input(f"Tồn kho", min_value=0, step=1, key=f"s_{sp}")
            data_input.append({"Sản phẩm": sp, "Facing": f, "Tồn kho": s})

        ghi_chu = st.text_area("🗒️ Ghi chú (KM, Đối thủ, v.v...):")
        submit = st.form_submit_button("🚀 GỬI BÁO CÁO")

    # 4. XỬ LÝ KẾT QUẢ
    if submit:
        df_final = pd.DataFrame(data_input)
        df_final.insert(0, "Ngày", datetime.now().strftime('%d/%m/%Y'))
        df_final.insert(1, "Nhân viên", nv_selected)
        df_final.insert(2, "Hệ thống", he_thong_selected)
        df_final.insert(3, "Siêu thị", st_selected)
        df_final["Ghi chú"] = ghi_chu

        st.success(f"✅ Đã lưu báo cáo {st_selected} thành công!")
        st.dataframe(df_final, use_container_width=True)

        # Xuất file Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 TẢI FILE EXCEL VỀ MÁY",
            data=output.getvalue(),
            file_name=f"BC_{st_selected}_{datetime.now().strftime('%d%m')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.markdown("---")
st.caption("© 2026 Chuong Duong Beverage - Quản lý dữ liệu MT")
