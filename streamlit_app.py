import streamlit as st
import pandas as pd
import cv2
import numpy as np
from PIL import Image
import easyocr
import io

# Cấu hình trang
st.set_page_config(page_title="Chương Dương OCR", layout="wide")

st.title("📝 Số hóa Báo cáo MT Chương Dương")

# Khởi tạo EasyOCR (Sử dụng cache để không tải lại nhiều lần)
@st.cache_resource
def load_reader():
    # Chỉ tải ngôn ngữ tiếng Việt và Anh
    return easyocr.Reader(['vi', 'en'], gpu=False)

reader = load_reader()

uploaded_file = st.file_uploader("Tải ảnh báo cáo", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Ảnh gốc", width=500)
    
    if st.button("🚀 TRÍCH XUẤT"):
        img_np = np.array(image)
        results = reader.readtext(img_np)
        
        # Hiển thị kết quả dạng bảng đơn giản
        data = [res[1] for res in results]
        st.write("Dữ liệu tìm thấy:")
        st.write(data)
