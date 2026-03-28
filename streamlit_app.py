import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import unicodedata

# 1. Cau hinh trang
st.set_page_config(page_title="Team MT - Chuong Duong", layout="wide", page_icon="🥤")

# Ham xoa dau tieng Viet (Dung de xử lý trước khi gửi lên Sheets)
def remove_accents(text):
    if not isinstance(text, str): return text
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn').replace('đ', 'd').replace('Đ', 'D')

@st.cache_data
def load_master_data():
    try:
        # Giu nguyen file co dau de hien thi
        df_raw = pd.read_excel("data nhan vien.xlsx", header=None)
        header_row = 0
        for i in range(len(df_raw)):
            row_str = " ".join([str(x).upper() for x in df_raw.iloc[i].values])
            if "NHÂN VIÊN" in row_str or "HỆ THỐNG" in row_str:
                header_row = i
                break
        df = pd.read_excel("data nhan vien.xlsx", header=header_row)
        df = df.iloc[:, :4] 
        df.columns = ["NHAN VIEN", "HE THONG", "PHUONG", "TEN SIEU THI"]
        df = df.dropna(subset=["TEN SIEU THI"])
        # Chi xoa khoang trang, GIỮ NGUYÊN DẤU de hien thi tren App
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else x)
        return df
    except Exception as e:
        st.error(f"Loi doc file Excel: {e}")
        return None

df_master = load_master_data()

# Danh muc san pham (Hien thi co dau cho dep)
DS_SAN_PHAM = [
    "Sá Xị Chương Dương (Lon 330ml)",
    "Sá Xị Zero (Lon 330ml)",
    "Sá Xị Chương Dương (PET 390ml)",
    "Soda Kem (Lon 330ml)",
    "Sá Xị Chương Dương (Chai 1.5L)",
    "Nước Tinh Khiết CD (Chai 500ml)"
]

conn = st.connection("gsheets", type=GSheetsConnection)

if df_master is not None:
    with st.sidebar:
        st.header("👤 THÔNG TIN")
        list_nv = sorted([x for x in df_master["NHAN VIEN"].unique() if str(x).upper() not in ['NAN', 'NONE']])
        nv_selected = st.selectbox("1. Nhân viên:", list_nv)
        df_f1 = df_master[df_master["NHAN VIEN"] == nv_selected]
        
        list_ht = sorted([x for x in df_f1["HE THONG"].unique() if str(x).upper() not in ['NAN', 'NONE']])
        ht_selected = st.selectbox("2. Hệ thống:", list_ht)
        df_f2 = df_f1[df_f1["HE THONG"] == ht_selected]
        
        list_ph = sorted([x for x in df_f2["PHUONG"].unique() if str(x).upper() not in ['NAN', 'NONE']])
        ph_selected = st.selectbox("3. Phường:", list_ph)
        
        df_f3 = df_f2[df_f2["PHUONG"] == ph_selected]
        st_selected = st.selectbox("4. Siêu thị:", sorted(df_f3["TEN SIEU THI"].unique()))

    st.title(f"🥤 {st_selected}")
    
    with st.form("entry_form", clear_on_submit=True):
        st.subheader("📊 NHẬP SỐ LIỆU")
        all_entries = []
        for sp in DS_SAN_PHAM:
            st.write(f"**{sp}**")
            c1, c2 = st.columns(2)
            with c1: f = st.number_input(f"Facing", min_value=0, step=1, key=f"f_{sp}")
            with c2: s = st.number_input(f"Tồn kho", min_value=0, step=1, key=f"s_{sp}")
            all_entries.append({"SP": sp, "F": f, "S": s})
        
        st.divider()
        uploaded_file = st.file_uploader("📸 Ảnh trưng bày:", type=['jpg','png','jpeg'])
        ghi_chu = st.text_area("🗒️ Ghi chú (Có thể viết có dấu):")
        submit = st.form_submit_button("🚀 GỬI BÁO CÁO")

    if submit:
        now = datetime.now()
        ngay = now.strftime("%d/%m/%Y")
        gio = now.strftime("%H:%M:%S")
        
        new_rows_list = []
        for item in all_entries:
            if item["F"] > 0 or item["S"] > 0:
                # O DAY: Chung ta dung ham remove_accents de xoa dau truoc khi luu
                new_rows_list.append({
                    "NGAY": ngay,
                    "GIO": gio,
                    "NHAN VIEN": remove_accents(nv_selected),
                    "HE THONG": remove_accents(ht_selected),
                    "PHUONG": remove_accents(ph_selected),
                    "SIEU THI": remove_accents(st_selected),
                    "SAN PHAM": remove_accents(item["SP"]),
                    "FACING": str(item["F"]),
                    "TON KHO": str(item["S"]),
                    "GHI CHU": remove_accents(ghi_chu),
                    "HINH ANH": "CO" if uploaded_file else "KHONG"
                })
        
        if not new_rows_list:
            st.warning("⚠️ Bạn chưa nhập số liệu!")
        else:
            try:
                existing_data = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                new_data_df = pd.DataFrame(new_rows_list)
                
                if existing_data is not None and not existing_data.empty:
                    existing_data = existing_data.dropna(axis=1, how='all')
                    updated_df = pd.concat([existing_data, new_data_df], ignore_index=True)
                else:
                    updated_df = new_data_df
                
                # Ep tat ca ve string de bao dam khong loi encoding
                updated_df = updated_df.astype(str)
                conn.update(worksheet="Data_Bao_Cao_MT", data=updated_df)
                
                st.success(f"✅ Đã gửi báo cáo thành công (Dữ liệu đã được chuẩn hóa không dấu)!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Lỗi gửi dữ liệu: {str(e)}")

st.markdown("---")
st.caption("© 2026 Chuong Duong Beverage")
