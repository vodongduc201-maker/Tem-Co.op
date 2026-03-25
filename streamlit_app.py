import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import io
import qrcode
from datetime import datetime

st.set_page_config(page_title="In Tem QR Chuong Duong - Fixed", page_icon="📱")

def remove_accents(input_str):
    import unicodedata
    if not isinstance(input_str, str): return str(input_str)
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')

st.title("📱 Hệ thống In Tem QR - Team MT")
st.info("Cấu trúc QR: Booking-MãKho-MãST-SốKiện-SốHD")

uploaded_file = st.file_uploader("Tải file Excel (Cấu trúc mới nhất)", type=['xlsx'])

if uploaded_file:
    try:
        # Đọc dữ liệu và làm sạch tên cột
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        df = df.astype(str)
        
        if st.button("🚀 XUẤT PDF TẤT CẢ TEM"):
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=(4*inch, 2*inch))
            
            for _, row in df.iterrows():
                # Lấy dữ liệu theo tiêu đề cột trong ảnh mới nhất của bạn
                booking = row.get('Mã booking', '').replace(".0", "")
                ma_kho = row.get('Mã kho', '').replace(".0", "")
                ma_st = row.get('Mã siêu thị', '').replace(".0", "")
                so_hd = row.get('Số Hóa Đơn NCC', '').replace(".0", "")
                ngay_giao = row.get('Ngày giao dự kiến', '').replace(".0", "")
                
                # Xử lý số lượng kiện để in số lượng tem tương ứng
                try:
                    val_kien = row.get('Số Kiện NCC', '1')
                    tong_so_kien = int(float(val_kien))
                    if tong_so_kien <= 0: tong_so_kien = 1
                except: # Đã thêm dấu hai chấm ở đây để sửa lỗi Syntax
                    tong_so_kien = 1

                # TẠO NỘI DUNG QR (Đồng nhất cho các kiện cùng lô)
                qr_content = f"{booking}-{ma_kho}-{ma_st}-{tong_so_kien}-{so_hd}"
                
                qr = qrcode.QRCode(version=1, border=1)
                qr.add_data(qr_content)
                qr.make(fit=True)
                img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')
                qr_reader = ImageReader(img_qr)

                # Vòng lặp in số lượng tem
                for i in range(1, tong_so_kien + 1):
                    c.setLineWidth(1.2)
                    c.rect(0.1*inch, 0.1*inch, 3.8*inch, 1.8*inch)
                    c.line(0.1*inch, 1.45*inch, 3.9*inch, 1.45*inch)
                    c.line(1.3*inch, 0.55*inch, 1.3*inch, 1.45*inch)
                    c.line(2.0*inch, 0.55*inch, 2.0*inch, 1.45*inch)
                    
                    c.setFont("Helvetica-Bold", 8)
                    c.drawString(0.2*inch, 1.6*inch, "NCC: CHUONG DUONG BEVERAGE")
                    c.drawRightString(3.8*inch, 1.6*inch, f"BOOKING: {booking}")
                    
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(0.2*inch, 1.15*inch, f"MA KHO: {ma_kho}")
                    c.drawString(0.2*inch, 0.9*inch, f"MA ST: {ma_st}")
                    
                    # Số thứ tự kiện
                    c.setFont("Helvetica-Bold", 24)
                    c.drawCentredString(1.65*inch, 0.85*inch, f"{i} / {tong_so_kien}")
                    
                    c.setFont("Helvetica", 8)
                    c.drawString(0.2*inch, 0.3*inch, f"GIAO DU KIEN: {ngay_giao}")
                    
                    # Chèn QR Code
                    c.drawImage(qr_reader, 2.1*inch, 0.58*inch, width=1.6*inch, height=0.85*inch, preserveAspectRatio=True)
                    
                    # Text dưới QR
                    c.setFont("Helvetica", 7)
                    c.drawCentredString(3.0*inch, 0.45*inch, qr_content)

                    c.showPage()
            
            c.save()
            st.download_button("📥 TẢI TEM PDF", buffer.getvalue(), f"Tem_QR_Fixed_{datetime.now().strftime('%d%m')}.pdf")
            
    except Exception as e:
        st.error(f"Lỗi: {e}")
