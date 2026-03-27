import streamlit as st
import pandas as pd
from datetime import datetime
import io
from streamlit_gsheets import GSheetsConnection

# Cấu hình trang
st.set_page_config(page_title="Team MT - Báo Cáo Tổng", layout="wide", page_icon="🥤")

# --- 1. ĐỌC DỮ LIỆU DANH MỤC (MASTER DATA) ---
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
        # Chuẩn hóa In hoa để gộp tên Hiền/HIỀN
        df = df.map(lambda x: str(x).strip().upper() if pd.notnull(x) else x)
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file danh mục: {e}")
        return None

df_master = load_master_data()

# Danh mục sản phẩm cố định
DS_SAN_PHAM = [
    "Sá Xị Chương Dương (Lon 330ml)",
    "Sá Xị Zero (Lon 330ml)",
    "Sá Xị Chương Dương (Chai PET 390ml)",
    "Soda Kem (Lon 330ml)",
    "Sá Xị Chương Dương (Chai 1.5L)",
    "Nước Tinh Khiết CD (Chai 500ml)"
]

# --- 2. KẾT NỐI GOOGLE SHEETS (Sử dụng Secrets) ---
# Đảm bảo bạn đã dán Service Account vào Secrets của App này
conn = st.connection("gsheets", type=GSheetsConnection)

if df_master is not None:
    # --- SIDEBAR LỌC 4 TẦNG ---
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

    # --- GIAO DIỆN NHẬP LIỆU ---
    st.title(f"🥤 {st_selected}")
    st.info(f"Đang báo cáo cho: {nv_selected} | Hệ thống: {ht_selected}")

    with st.form("entry_form", clear_on_submit=True):
        st.subheader("📊 Số liệu trưng bày & Tồn kho")
        data_input = []
        for sp in DS_SAN_PHAM:
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1: st.write(f"**{sp}**")
            with c2: f = st.number_input("Facing", min_value=0, step=1, key=f"f_{sp}")
            with c3: s = st.number_input("Tồn", min_value=0, step=1, key=f"s_{sp}")
            data_input.append({"Sản phẩm": sp, "Facing": f, "Tồn": s})
        
        st.divider()
        st.subheader("📸 Hình ảnh & Ghi chú")
        uploaded_file = st.file_uploader("Tải ảnh trưng bày (JPG/PNG):", type=['jpg','png','jpeg'])
        ghi_chu = st.text_area("Ghi chú thêm:")
        
        submit = st.form_submit_button("🚀 GỬI BÁO CÁO VỀ TỔNG")

    if submit:
        # 1. Tạo DataFrame dòng mới
        time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # Chuyển dữ liệu Facing/Tồn thành chuỗi để lưu vào 1 dòng cho gọn
        summary_facing = ", ".join([f"{d['Sản phẩm']}: {d['Facing']}" for d in data_input])
        summary_ton = ", ".join([f"{d['Sản phẩm']}: {d['Tồn']}" for d in data_input])
        
        new_row = pd.DataFrame([{
            "Thời gian": time_now,
            "Nhân viên": nv_selected,
            "Hệ thống": ht_selected,
            "Siêu thị": st_selected,
            "Chi tiết Facing": summary_facing,
            "Chi tiết Tồn": summary_ton,
            "Ghi chú": ghi_chu,
            "Có ảnh": "CÓ" if uploaded_file else "KHÔNG"
        }])

        try:
            # 2. Đọc dữ liệu cũ từ Sheet (Tên Sheet phải là 'Data_Bao_Cao_MT')
            # ttl=0 để luôn lấy dữ liệu mới nhất, không lấy từ bộ nhớ đệm
            existing_data = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
            
            # 3. Kết hợp cũ và mới
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            
            # 4. Cập nhật lại toàn bộ Sheet
            conn.update(worksheet="Data_Bao_Cao_MT", data=updated_df)
            
            st.success("✅ Tuyệt vời! Dữ liệu đã được gửi về File Tổng.")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Lỗi khi gửi dữ liệu: {e}")
            st.warning("Mẹo: Hãy đảm bảo bạn đã Share quyền Editor cho email Service Account trong Google Sheets.")

st.markdown("---")
st.caption("© 2026 Chương Dương Beverage - Team MT Management System")
