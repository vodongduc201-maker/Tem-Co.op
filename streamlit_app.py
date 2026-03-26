import streamlit as st
import pandas as pd
from PIL import Image
import io

st.set_page_config(page_title="Chương Dương - Team MT", layout="wide")

st.title("📱 Hệ thống Quản lý Team MT")

tab1, tab2 = st.tabs(["In Tem QR", "Số hóa Báo cáo"])

with tab1:
    st.header("In Tem QR")
    st.info("Chức năng in tem vẫn hoạt động bình thường với file Excel.")
    # Chèn lại đoạn code in tem QR cũ của bạn ở đây

with tab2:
    st.header("Số hóa Báo cáo (OCR)")
    st.warning("Hệ thống đang bảo trì thư viện quét ảnh nâng cao. Vui lòng sử dụng Google Lens để copy văn bản và dán vào bảng dưới đây.")
    
    user_input = st.text_area("Dán dữ liệu quét từ Google Lens vào đây:")
    if user_input:
        lines = [line.split() for line in user_input.split('\n') if line.strip()]
        df = pd.DataFrame(lines)
        st.dataframe(df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
        st.download_button("📥 TẢI EXCEL", output.getvalue(), "Bao_cao_CD.xlsx")
