import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import unicodedata

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Bao Cao MT - Chuong Duong", layout="wide", page_icon="🥤")

# --- 2. HÀM LÀM SẠCH DỮ LIỆU (CHỐNG LỖI ASCII) ---
def clean_text(text):
    if not isinstance(text, str): 
        text = str(text) if text is not None else ""
    # Chuyển Tiếng Việt có dấu thành không dấu
    nfkd_form = unicodedata.normalize('NFKD', text)
    clean = "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')
    # Loại bỏ ký tự đặc biệt gây lỗi JSON/ASCII
    clean = clean.replace("'", "").replace('"', "").replace("\n", " ").strip()
    return clean.encode('ascii', 'ignore').decode('ascii')

# --- 3. KẾT NỐI GOOGLE SHEETS (ÉP XÁC THỰC) ---
# Sử dụng ttl=0 để luôn đọc dữ liệu mới nhất và ép dùng Service Account trong Secrets
conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)

# --- 4. TẢI DỮ LIỆU NHÂN VIÊN (MASTER DATA) ---
@st.cache_data(ttl=600)
def load_master():
    try:
        # Đảm bảo file này có trên GitHub của bạn
        df = pd.read_excel("data nhan vien.xlsx", engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Khong tim thay file 'data nhan vien.xlsx': {e}")
        return None

df_master = load_master()

# --- 5. GIAO DIỆN NHẬP LIỆU ---
if df_master is not None:
    st.title("🚀 HE THONG BAO CAO MT")
    
    with st.sidebar:
        st.header("THONG TIN CHUNG")
        nv = st.selectbox("Nhan vien:", sorted(df_master.iloc[:, 0].unique()))
        ht = st.selectbox("He thong:", sorted(df_master.iloc[:, 1].unique()))
        
        # Loc danh sach sieu thi theo he thong
        st_list = df_master[df_master.iloc[:, 1] == ht].iloc[:, 3].unique()
        st_name = st.selectbox("Sieu thi:", sorted(st_list))

    with st.form("mt_form", clear_on_submit=True):
        st.subheader(f"📍 Đang bao cao tai: {st_name}")
        
        # Danh sach san pham rut gon (de tranh loi cot)
        list_sp = ["SA XI LON", "SA XI ZERO", "SA XI PET", "SODA KEM", "SA XI 1.5L", "NUOC SUOI"]
        input_data = []
        
        col1, col2 = st.columns(2)
        for i, sp in enumerate(list_sp):
            with col1 if i % 2 == 0 else col2:
                st.write(f"**{sp}**")
                f = st.number_input("Facing", min_value=0, step=1, key=f"f_{sp}")
                s = st.number_input("Ton kho", min_value=0, step=1, key=f"s_{sp}")
                input_data.append({"SP": sp, "F": f, "S": s})
        
        st.markdown("---")
        note = st.text_input("Ghi chu (Khong dau):")
        submit = st.form_submit_button("📤 GUI BAO CAO")

    # --- 6. XỬ LÝ LƯU DỮ LIỆU ---
    if submit:
        new_rows = []
        for item in input_data:
            if item["F"] > 0 or item["S"] > 0:
                new_rows.append({
                    "NGAY": datetime.now().strftime("%d/%m/%Y"),
                    "GIO": datetime.now().strftime("%H:%M:%S"),
                    "NHAN VIEN": clean_text(nv).upper(),
                    "HE THONG": clean_text(ht).upper(),
                    "SIEU THI": clean_text(st_name).upper(),
                    "SAN PHAM": item["SP"],
                    "FACING": str(item["F"]),
                    "TON KHO": str(item["S"]),
                    "GHI CHU": clean_text(note).upper()
                })
        
        if not new_rows:
            st.warning("Vui long nhap so luong Facing hoac Ton kho!")
        else:
            try:
                # Doc du lieu cu tu Sheets
                # Luu y: Worksheet phai ten la 'Data_Bao_Cao_MT'
                try:
                    existing_data = conn.read(worksheet="Data_Bao_Cao_MT")
                except:
                    existing_data = pd.DataFrame()

                df_new = pd.DataFrame(new_rows)

                # Hop nhat du lieu
                if existing_data is not None and not existing_data.empty:
                    updated_df = pd.concat([existing_data.astype(str), df_new.astype(str)], ignore_index=True)
                else:
                    updated_df = df_new

                # Cap nhat len Google Sheets
                conn.update(worksheet="Data_Bao_Cao_MT", data=updated_df)
                
                st.success("✅ GUI DU LIEU THANH CONG!")
                st.balloons()
            except Exception as e:
                st.error(f"Loi ket noi Sheets: {e}")
                st.info("Kiem tra lai: 1. Quyen Editor cho Service Account. 2. Ten Tab 'Data_Bao_Cao_MT'.")
else:
    st.warning("Dang tai du lieu Master... Vui long cho giay lat.")
