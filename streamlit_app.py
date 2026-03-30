import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import unicodedata

# 1. Cau hinh trang
st.set_page_config(page_title="MT Team - Chuong Duong", layout="wide", page_icon="🥤")

# Ham xoa dau tieng Viet (Dung de lam sach moi thu)
def remove_accents(text):
    if not isinstance(text, str): return str(text)
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')

@st.cache_data
def load_master_data():
    try:
        # Doc file Excel (Su dung engine openpyxl de ho tro tot hon)
        df_raw = pd.read_excel("data nhan vien.xlsx", header=None, engine='openpyxl')
        
        # Tim dong tieu de
        header_row = 0
        for i in range(len(df_raw)):
            row_str = " ".join([str(x).upper() for x in df_raw.iloc[i].values])
            if "NHAN VIEN" in remove_accents(row_row_str) or "HE THONG" in remove_accents(row_str):
                header_row = i
                break
        
        df = pd.read_excel("data nhan vien.xlsx", header=header_row, engine='openpyxl')
        df = df.iloc[:, :4] 
        df.columns = ["NHAN VIEN", "HE THONG", "PHUONG", "TEN SIEU THI"]
        
        # BUOC QUAN TRONG: Xoa sach dau ngay tu khi doc vao de tranh loi ASCII
        df = df.dropna(subset=["TEN SIEU THI"])
        df = df.map(lambda x: remove_accents(str(x)).strip().upper() if pd.notnull(x) else x)
        return df
    except Exception as e:
        st.error(f"Loi doc file: {str(e)}")
        return None

df_master = load_master_data()

# Danh muc san pham (Khong dau)
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
        list_nv = sorted([x for x in df_master["NHAN VIEN"].unique() if x not in ['NAN', 'NONE']])
        nv_selected = st.selectbox("1. Nhan vien:", list_nv)
        df_f1 = df_master[df_master["NHAN VIEN"] == nv_selected]
        
        list_ht = sorted([x for x in df_f1["HE THONG"].unique() if x not in ['NAN', 'NONE']])
        ht_selected = st.selectbox("2. He thong:", list_ht)
        df_f2 = df_f1[df_f1["HE THONG"] == ht_selected]
        
        st_selected = st.selectbox("3. Sieu thi:", sorted(df_f2["TEN SIEU THI"].unique()))

    st.title(f"🥤 {st_selected}")
    
    with st.form("entry_form", clear_on_submit=True):
        st.subheader("📊 NHAP SO LIEU")
        all_entries = []
        for sp in DS_SAN_PHAM:
            st.write(f"**{sp}**")
            c1, c2 = st.columns(2)
            with c1: f = st.number_input(f"Facing", min_value=0, step=1, key=f"f_{sp}")
            with c2: s = st.number_input(f"Ton kho", min_value=0, step=1, key=f"s_{sp}")
            all_entries.append({"SP": sp, "F": f, "S": s})
        
        st.divider()
        uploaded_file = st.file_uploader("📸 Anh trung bay:", type=['jpg', 'png', 'jpeg'])
        ghi_chu = st.text_area("🗒️ Ghi chu (Khong dau):")
        submit = st.form_submit_button("🚀 GUI BAO CAO")

    if submit:
        now = datetime.now()
        ngay = now.strftime("%d/%m/%Y")
        gio = now.strftime("%H:%M:%S")
        
        new_rows = []
        for item in all_entries:
            if item["F"] > 0 or item["S"] > 0:
                new_rows.append({
                    "NGAY": str(ngay),
                    "GIO": str(gio),
                    "NHAN VIEN": str(nv_selected),
                    "HE THONG": str(ht_selected),
                    "SIEU THI": str(st_selected),
                    "SAN PHAM": str(item["SP"]),
                    "FACING": str(item["F"]),
                    "TON KHO": str(item["S"]),
                    "GHI CHU": remove_accents(ghi_chu).upper(),
                    "HINH ANH": "CO" if uploaded_file else "KHONG"
                })
        
        if not new_rows:
            st.warning("⚠️ Ban chua nhap so lieu!")
        else:
            try:
                # 1. Doc du lieu cu va EP KIEU STRING NGAY LAP TUC
                existing_data = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
                new_df = pd.DataFrame(new_rows).astype(str)
                
                if existing_data is not None and not existing_data.empty:
                    # Chuyen tieu de va noi dung cu sang String khong dau de gop cho khop
                    existing_data.columns = [remove_accents(str(c)) for c in existing_data.columns]
                    existing_data = existing_data.astype(str)
                    updated_df = pd.concat([existing_data, new_df], ignore_index=True)
                else:
                    updated_df = new_df
                
                # 2. Cap nhat (astype(str) lan cuoi de dam bao an toan)
                updated_df = updated_df.astype(str)
                conn.update(worksheet="Data_Bao_Cao_MT", data=updated_df)
                st.success("✅ Da gui bao cao thanh cong!")
                st.balloons()
            except Exception as e:
                st.error(f"Loi gui Sheets: {str(e)}")

st.markdown("---")
st.caption("© 2026 Chuong Duong Beverage")
