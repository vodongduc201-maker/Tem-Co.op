import streamlit as st
import pandas as pd
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Chương Dương OCR Pro", layout="wide")
st.title("📸 Số hóa Báo cáo MT (Bản nâng cao)")

uploaded_file = st.file_uploader("Tải ảnh báo cáo lên", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Ảnh gốc", width=700)
    
    if st.button("🚀 BẮT ĐẦU XỬ LÝ"):
        with st.spinner("Đang làm sạch ảnh và đọc dữ liệu..."):
            # 1. Chuyển sang ảnh xám
            img = np.array(image)
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            
            # 2. Xử lý khử nhiễu và làm rõ nét chữ viết tay
            # Dùng Adaptive Thresholding để loại bỏ bóng đổ
            processed_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # 3. Quét với cấu hình chỉ nhận diện Số và Chữ Tiếng Việt
            # --psm 6: Coi như một khối văn bản thống nhất
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰự/ '
            
            text_data = pytesseract.image_to_string(processed_img, lang='vie', config=custom_config)
            
            # 4. Hậu xử lý: Tách dòng và lọc bỏ ký tự rác
            lines = text_data.split('\n')
            clean_rows = []
            for line in lines:
                # Chỉ lấy những dòng có dữ liệu (có độ dài > 5 ký tự)
                if len(line.strip()) > 5:
                    parts = line.split()
                    clean_rows.append(parts)
            
            if clean_rows:
                df = pd.DataFrame(clean_rows)
                st.subheader("📊 Kết quả sau khi làm sạch:")
                st.table(df) # Dùng table cho dễ nhìn
                
                # Xuất Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, header=False)
                
                st.download_button("📥 TẢI EXCEL SẠCH", output.getvalue(), "Bao_cao_MT_Clean.xlsx")
            else:
                st.error("Không nhận diện được bảng. Vui lòng chụp ảnh gần và thẳng hơn!")
