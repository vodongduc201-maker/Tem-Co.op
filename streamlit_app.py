import streamlit as st
import pandas as pd
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io
import re

st.set_page_config(page_title="Chương Dương OCR - Trực tiếp", page_icon="📸")

st.title("📸 Quét Báo cáo trực tiếp từ Ảnh")
st.info("Tải ảnh form báo cáo Facing/Tồn kho lên, hệ thống sẽ tự chuyển thành bảng.")

uploaded_file = st.file_uploader("Chọn ảnh báo cáo...", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    # Hiển thị ảnh
    image = Image.open(uploaded_file)
    st.image(image, caption="Ảnh đã tải lên", width=500)
    
    if st.button("🚀 BẮT ĐẦU QUÉT"):
        with st.spinner("Đang xử lý dữ liệu..."):
            # 1. Chuyển ảnh sang OpenCV và làm sạch để AI dễ đọc hơn
            img_np = np.array(image)
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            # Tăng độ tương phản (Thresholding)
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            # 2. Dùng Tesseract quét chữ tiếng Việt
            # Cấu hình --psm 6 (Assume a single uniform block of text)
            custom_config = r'--oem 3 --psm 6'
            text_data = pytesseract.image_to_string(gray, lang='vie', config=custom_config)

            # 3. Xử lý văn bản thành bảng
            lines = text_data.split('\n')
            final_data = []
            for line in lines:
                if line.strip():
                    # Tách chữ và số
                    parts = line.split()
                    final_data.append(parts)

            if final_data:
                df = pd.DataFrame(final_data)
                st.subheader("📊 Kết quả dự kiến:")
                st.dataframe(df)

                # 4. Xuất file Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, header=False)
                
                st.success("Quét xong!")
                st.download_button("📥 TẢI EXCEL", output.getvalue(), "Bao_cao_truc_tiep.xlsx")
            else:
                st.error("Không đọc được dữ liệu. Hãy thử ảnh rõ nét hơn.")

st.warning("⚠️ Lưu ý: Ảnh chụp cần thẳng, đủ sáng và chữ viết tay rõ ràng để đạt độ chính xác cao nhất.")
