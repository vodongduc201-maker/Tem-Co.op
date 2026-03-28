import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Team MT - Báo Cáo Tổng", layout="wide", page_icon="🥤")

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

DS_SAN_PHAM = [
    "Sá Xị Chương Dương (Lon 330ml)",
    "Sá Xị Zero (Lon 330ml)",
    "Sá Xị Chương Dương (Chai PET 390ml)",
    "Soda Kem (Lon 330ml)",
    "Sá Xị Chương Dương (Chai 1.5L)",
    "Nước Tinh Khiết CD (Chai 500ml)"
]

# --- 2. KẾT NỐI ---
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
        uploaded_file = st.file_uploader("📸 Tải ảnh trưng bày:", type=['jpg','png','jpeg'])
        ghi_chu = st.text_area("🗒️ Ghi chú:")
        submit = st.form_submit_button("🚀 GỬI BÁO CÁO")

    if submit:
        # BƯỚC QUAN TRỌNG: Tạo data và ép kiểu string ngay lập tức
        time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        s_facing = "; ".join([f"{d['Sản phẩm']}: {d['Facing']}" for d in data_input])
        s_ton = "; ".join([f"{d['Sản phẩm']}: {d['Tồn']}" for d in data_input])
        
        new_row = pd.DataFrame([{
            "Thời gian": str(time_now),
            "Nhân viên": str(nv_selected),
            "Hệ thống": str(ht_selected),
            "Siêu thị": str(st_selected),
            "Facing": str(s_facing),
            "Tồn kho": str(s_ton),
            "Ghi chú": str(ghi_chu),
            "Có ảnh": "CÓ" if uploaded_file else "KHÔNG"
        }])

        try:
            # 1. Đọc dữ liệu hiện tại
            existing_data = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
            
            # 2. Gộp dữ liệu mới vào
            if existing_data is not None and not existing_data.empty:
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            else:
                updated_df = new_row
            
            # 3. ÉP KIỂU TOÀN BỘ SANG STRING VÀ CHUẨN HÓA (Fix lỗi ASCII)
            updated_df = updated_df.astype(str)
            
            # 4. Ghi đè bằng phương thức update
            conn.update(worksheet="Data_Bao_Cao_MT", data=updated_df)
            
            st.success(f"✅ Đã gửi báo cáo {st_selected} thành công!")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")
            st.info("💡 Mẹo cuối cùng: Hãy thử đổi tiêu đề cột trên Google Sheets thành KHÔNG DẤU (Ví dụ: Thoi gian, Nhan vien, Sieu thi...)")

st.markdown("---")
st.caption("© 2026 Chương Dương Beverage")
