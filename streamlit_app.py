import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import unicodedata

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="CD Beverage - MT Report", layout="wide", page_icon="🥤")

# --- HÀM XỬ LÝ DỮ LIỆU SẠCH (CHỐNG LỖI ASCII) ---
def clean_text(text):
    if not isinstance(text, str): 
        text = str(text) if text is not None else ""
    # Xóa các ký tự gây lỗi hệ thống
    text = text.replace("'", "").replace("’", "").replace('"', "").replace("\n", " ")
    # Chuyển Tiếng Việt có dấu thành không dấu
    nfkd_form = unicodedata.normalize('NFKD', text)
    clean = "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')
    # Ép về ASCII chuẩn, bỏ qua ký tự lạ
    return clean.encode('ascii', 'ignore').decode('ascii').strip()

# --- LOAD MASTER DATA (DANH SÁCH NHÂN VIÊN/SIÊU THỊ) ---
@st.cache_data(ttl=600)
def load_master_data():
    try:
        df = pd.read_excel("data nhan vien.xlsx", engine='openpyxl')
        # Làm sạch toàn bộ bảng Master Data
        for col in df.columns:
            df[col] = df[col].apply(lambda x: clean_text(x).upper())
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file Excel Master: {e}")
        return None

df_master = load_master_data()

# Danh mục sản phẩm (Đã làm sạch)
DS_SAN_PHAM = [
    "SA XI CHUONG DUONG (LON 330ML)",
    "SA XI ZERO (LON 330ML)",
    "SA XI CHUONG DUONG (PET 390ML)",
    "SODA KEM (LON 330ML)",
    "SA XI CHUONG DUONG (CHAI 1.5L)",
    "NUOC TINH KHIET CD (CHAI 500ML)"
]

# --- KẾT NỐI GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

if df_master is not None:
    st.title("🚀 HỆ THỐNG BÁO CÁO MT - CHƯƠNG DƯƠNG")
    
    # --- GIAO DIỆN NHẬP LIỆU ---
    with st.sidebar:
        st.header("👤 THÔNG TIN CHUNG")
        nv_selected = st.selectbox("Nhân viên:", sorted(df_master.iloc[:, 0].unique()))
        ht_selected = st.selectbox("Hệ thống:", sorted(df_master.iloc[:, 1].unique()))
        
        # Lọc siêu thị theo hệ thống đã chọn
        df_st = df_master[df_master.iloc[:, 1] == ht_selected]
        st_selected = st.selectbox("Siêu thị:", sorted(df_st.iloc[:, 3].unique()))

    with st.form("entry_form", clear_on_submit=True):
        st.subheader(f"📍 Đang báo cáo tại: {st_selected}")
        
        inputs = []
        cols = st.columns(2)
        for i, sp in enumerate(DS_SAN_PHAM):
            with cols[i % 2]:
                st.markdown(f"**{sp}**")
                f = st.number_input("Facing", min_value=0, step=1, key=f"f_{sp}")
                s = st.number_input("Tồn kho", min_value=0, step=1, key=f"s_{sp}")
                inputs.append({"SP": sp, "F": f, "S": s})
        
        st.markdown("---")
        ghi_chu = st.text_area("Ghi chú thêm (Không dấu):")
        uploaded_file = st.file_uploader("Chụp ảnh trưng bày (Nếu có)", type=['jpg', 'png', 'jpeg'])
        
        submit = st.form_submit_button("📤 GỬI BÁO CÁO")

    # --- XỬ LÝ GỬI DỮ LIỆU ---
    if submit:
        now = datetime.now()
        new_entries = []
        
        for item in inputs:
            if item["F"] > 0 or item["S"] > 0:
                new_entries.append({
                    "NGAY": now.strftime("%d/%m/%Y"),
                    "GIO": now.strftime("%H:%M:%S"),
                    "NHAN VIEN": clean_text(nv_selected),
                    "HE THONG": clean_text(ht_selected),
                    "SIEU THI": clean_text(st_selected),
                    "SAN PHAM": clean_text(item["SP"]),
                    "FACING": str(item["F"]),
                    "TON KHO": str(item["S"]),
                    "GHI CHU": clean_text(ghi_chu).upper(),
                    "HINH ANH": "CO" if uploaded_file else "KHONG"
                })
        
        if not new_entries:
            st.warning("Vui lòng nhập ít nhất một số lượng Facing hoặc Tồn kho!")
        else:
            try:
                # 1. Đọc dữ liệu cũ (Xử lý lỗi 400 bằng cách ép kiểu sạch)
                try:
                    existing = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                except:
                    existing = pd.DataFrame()

                # 2. Tạo DataFrame mới
                new_df = pd.DataFrame(new_entries).astype(str)
                
                # 3. Hợp nhất dữ liệu
                if existing is not None and not existing.empty:
                    # Đảm bảo cột cũ và mới khớp nhau
                    existing.columns = [clean_text(c).upper() for c in existing.columns]
                    final_df = pd.concat([existing.astype(str), new_df], ignore_index=True)
                else:
                    final_df = new_df
                
                # 4. Ép sạch dữ liệu lần cuối (Bảo hiểm ASCII)
                for col in final_df.columns:
                    final_df[col] = final_df[col].apply(lambda x: clean_text(str(x)))

                # 5. Cập nhật lên Sheets
                conn.update(worksheet="Data_Bao_Cao_MT", data=final_df)
                
                st.success("✅ GỬI BÁO CÁO THÀNH CÔNG!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ LỖI GỬI DỮ LIỆU: {str(e)}")
                st.info("Mẹo: Hãy chắc chắn bạn đã đổi tên Tab trong Sheets thành 'Data_Bao_Cao_MT'")

else:
    st.error("Không thể tải dữ liệu Master. Vui lòng kiểm tra file 'data nhan vien.xlsx' trên GitHub.")
