import streamlit as st
import pandas as pd
import easyocr
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Chương Dương - Số hóa Báo cáo Giấy", layout="wide")
st.title("📝 Chuyển Báo cáo Giấy sang Excel")
st.info("Dành cho báo cáo Facing/Tồn kho viết tay của nhân viên thị trường.")

uploaded_file = st.file_uploader("Tải ảnh chụp báo cáo (Form giấy)", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Ảnh báo cáo gốc", width=600)
    
    if st.button("🚀 TRÍCH XUẤT DỮ LIỆU"):
        with st.spinner("AI đang đọc chữ viết tay và phân tích bảng..."):
            # Chuyển ảnh sang định dạng OpenCV
            img_np = np.array(image)
            img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            
            # Khởi tạo EasyOCR cho tiếng Việt và tiếng Anh
            reader = easyocr.Reader(['vi', 'en'])
            
            # Đọc dữ liệu từ ảnh (Kết quả gồm: Tọa độ, Nội dung, Độ tin cậy)
            results = reader.readtext(img_np)
            
            # Xử lý logic theo hàng (Sắp xếp các chữ có cùng tung độ Y vào một hàng)
            # Đây là kỹ thuật quan trọng để tái tạo lại cấu trúc bảng từ ảnh chụp
            lines = {}
            threshold = 20  # Khoảng cách sai lệch giữa các chữ trên cùng 1 hàng
            
            for (bbox, text, prob) in results:
                y_center = (bbox[0][1] + bbox[2][1]) / 2
                
                # Tìm hàng phù hợp
                found_line = False
                for line_y in lines.keys():
                    if abs(y_center - line_y) < threshold:
                        lines[line_y].append((bbox[0][0], text))
                        found_line = True
                        break
                if not found_line:
                    lines[y_center] = [(bbox[0][0], text)]
            
            # Sắp xếp các hàng từ trên xuống dưới và các cột từ trái sang phải
            sorted_rows = []
            for y in sorted(lines.keys()):
                row = sorted(lines[y], key=lambda x: x[0])
                sorted_rows.append([item[1] for item in row])
            
            # Hiển thị kết quả tạm thời
            if sorted_rows:
                df_final = pd.DataFrame(sorted_rows)
                
                st.subheader("📊 Dữ liệu dự kiến trích xuất:")
                st.dataframe(df_final, use_container_width=True)
                
                # Xuất file Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False, header=False, sheet_name='BaoCaoThiTruong')
                
                st.success("Đã trích xuất xong! Bạn có thể tải file về và chỉnh sửa lại các ô chữ viết tay quá mờ.")
                st.download_button(
                    label="📥 TẢI FILE EXCEL BÁO CÁO",
                    data=output.getvalue(),
                    file_name=f"Bao_cao_giay_{pd.Timestamp.now().strftime('%d%m')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
