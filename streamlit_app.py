import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import unicodedata

# 1. Cau hinh trang
st.set_page_config(page_title="MT Team - Chuong Duong", layout="wide")

# Ham xoa dau tieng Viet triet de (Diet loi ASCII)
def remove_accents(text):
    if not isinstance(text, str): return str(text)
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')

@st.cache_data
def load_master_data():
    try:
        # Doc file Excel (Kiem tra ten file tren GitHub: "data nhan vien.xlsx")
        df_raw = pd.read_excel("data nhan vien.xlsx", header=None, engine='openpyxl')
        
        header_row = 0
        for i in range(len(df_raw)):
            # Quet dong de tim tieu de, xoa dau de so sanh cho chuan
            row_str = " ".join([remove_accents(str(x)).upper() for x in df_raw.iloc[i].values])
            if "NHAN VIEN" in row_str or "HE THONG" in row_str:
                header_row = i
                break
        
        df = pd.read_excel("data nhan vien.xlsx", header=header_row, engine='openpyxl')
        df = df.iloc[:, :4] 
        df.columns = ["NHAN VIEN", "HE THONG", "PHUONG", "TEN SIEU THI"]
        df = df.dropna(subset=["TEN SIEU THI"])
        
        # Ep toan bo Master Data ve KHONG DAU ngay tu dau
        df = df.map(lambda x: remove_accents(str(x)).strip().upper() if pd.notnull(x) else x)
        return df
    except Exception as e:
        st.error(f"Loi doc file Excel: {str(e)}")
        return None

df_master = load_master_data()

# Danh muc san pham KHONG DAU (De khong bi loi khi gui Sheets)
DS_SAN_PHAM = [
    "SA XI CHUONG DUONG (LON 330ML)",
    "SA XI ZERO (LON 330ML)",
    "SA XI CHUONG DUONG (PET 390ML)",
    "SODA KEM (LON 330ML)",
    "SA XI CHUONG DUONG (CHAI 1.5L)",
    "NUOC TINH KHIET CD (CHAI 500ML)"
]

conn = st.connection("gsheets", type=GSheetsConnection)

if df_master is not None:
    with st.sidebar:
        st.header("👤 THONG TIN")
        nv_list = sorted(df_master["NHAN VIEN"].unique())
        nv_selected = st.selectbox("1. Nhan vien:", nv_list)
        
        df_f1 = df_master[df_master["NHAN VIEN"] == nv_selected]
        ht_list = sorted(df_f1["HE THONG"].unique())
        ht_selected = st.selectbox("2. He thong:", ht_list)
        
        df_f2 = df_f1[df_f1["HE THONG"] == ht_selected]
        st_selected = st.selectbox("3. Sieu thi:", sorted(df_f2["TEN SIEU THI"].unique()))

    st.title(f"🥤 {st_selected}")
    
    with st.form("entry_form", clear_on_submit=True):
        st.subheader("📊 SO LIEU")
        inputs = []
        for sp in DS_SAN_PHAM:
            st.write(f"**{sp}**")
            c1, c2 = st.columns(2)
            with c1: f = st.number_input("Facing", min_value=0, step=1, key=f"f_{sp}")
            with c2: s = st.number_input("Ton", min_value=0, step=1, key=f"s_{sp}")
            inputs.append({"SP": sp, "F": f, "S": s})
        
        st.divider()
        uploaded_file = st.file_uploader("📸 Anh:", type=['jpg', 'png', 'jpeg'])
        ghi_chu = st.text_area("🗒️ Ghi chu (Khong dau):")
        submit = st.form_submit_button("🚀 GUI BAO CAO")

    if submit:
        now = datetime.now()
        new_entries = []
        for item in inputs:
            if item["F"] > 0 or item["S"] > 0:
                # Ép tất cả dữ liệu về string và xóa dấu ngay lập tức
                new_entries.append({
                    "NGAY": str(now.strftime("%d/%m/%Y")),
                    "GIO": str(now.strftime("%H:%M:%S")),
                    "NHAN VIEN": remove_accents(str(nv_selected)),
                    "HE THONG": remove_accents(str(ht_selected)),
                    "SIEU THI": remove_accents(str(st_selected)),
                    "SAN PHAM": remove_accents(str(item["SP"])),
                    "FACING": str(item["F"]),
                    "TON KHO": str(item["S"]),
                    "GHI CHU": remove_accents(str(ghi_chu)).upper(),
                    "HINH ANH": "CO" if uploaded_file else "KHONG"
                })
        
        if new_entries:
            try:
                # 1. Đọc dữ liệu cũ
                existing = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                new_df = pd.DataFrame(new_entries).astype(str)
                
                if existing is not None and not existing.empty:
                    # Tẩy sạch dấu ở tiêu đề cột cũ (để tránh lệch cột)
                    existing.columns = [remove_accents(str(c)) for c in existing.columns]
                    existing = existing.astype(str)
                    final_df = pd.concat([existing, new_df], ignore_index=True)
                else:
                    final_df = new_df

                # 2. BƯỚC QUAN TRỌNG NHẤT: Ép toàn bộ bảng về ASCII 'ignore'
                # Việc này sẽ loại bỏ mọi ký tự lạ gây ra lỗi \xc3
                for col in final_df.columns:
                    final_df[col] = final_df[col].apply(lambda x: str(x).encode('ascii', 'ignore').decode('ascii'))
                
                # 3. Gửi lên Sheets
                conn.update(worksheet="Data_Bao_Cao_MT", data=final_df)
                st.success("✅ GUI THANH CONG!")
                st.balloons()
            except Exception as e:
                st.error(f"LOI GUI SHEETS: {str(e)}")
        now = datetime.now()
        new_entries = []
        for item in inputs:
            if item["F"] > 0 or item["S"] > 0:
                new_entries.append({
                    "NGAY": now.strftime("%d/%m/%Y"),
                    "GIO": now.strftime("%H:%M:%S"),
                    "NHAN VIEN": str(nv_selected),
                    "HE THONG": str(ht_selected),
                    "SIEU THI": str(st_selected),
                    "SAN PHAM": str(item["SP"]),
                    "FACING": str(item["F"]),
                    "TON KHO": str(item["S"]),
                    "GHI CHU": remove_accents(ghi_chu).upper(),
                    "HINH ANH": "CO" if uploaded_file else "KHONG"
                })
        
        if new_entries:
            try:
                # 1. Doc du lieu cu va EP KIEU STRING de diet loi Unicode/ASCII
                existing = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                new_df = pd.DataFrame(new_entries).astype(str)
                
                if existing is not None and not existing.empty:
                    # Chuan hoa tieu de cu ve khong dau va ep kieu string
                    existing.columns = [remove_accents(str(c)) for c in existing.columns]
                    existing = existing.astype(str).dropna(axis=1, how='all')
                    final_df = pd.concat([existing, new_df], ignore_index=True)
                else:
                    final_df = new_df
                
                # 2. Update len Sheets (Tat ca da la String khong dau)
                conn.update(worksheet="Data_Bao_Cao_MT", data=final_df.astype(str))
                st.success("✅ GUI THANH CONG!")
                st.balloons()
            except Exception as e:
                st.error(f"LOI GUI SHEETS: {str(e)}")
                st.info("Meo: Hay xoa sach du lieu cu co dau tren Google Sheets truoc khi gui lai.")
        else:
            st.warning("⚠️ Ban chua nhap so lieu!")

st.markdown("---")
st.caption("© 2026 Chuong Duong Beverage")
