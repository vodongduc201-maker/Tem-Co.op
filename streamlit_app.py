import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io
import qrcode
from datetime import datetime

st.set_page_config(page_title="In Tem QR Chuong Duong - New Format", page_icon="📱")

def remove_accents(input_str):
    import unicodedata
    if not isinstance(input_str, str): return str(input_str)
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')

st.title("📱 Hệ thống In Tem QR (Format Mới)")
st.write("App sẽ tự động tìm các cột: Mã booking, Mã kho, Mã siêu thị, Số Kiện NCC, Số Hóa Đơn NCC, Ngày giao dự kiến.")

uploaded_file = st.file_uploader("Tải file Excel mới nhất", type=['xlsx'])

if uploaded_file:
    try:
        # Đọc dữ liệu từ dòng 1 (Tiêu đề nằm ở dòng 1)
        df = pd.read_excel(uploaded_file).astype(str)
        
        # Ánh xạ các cột dựa trên tiêu đề trong ảnh bạn gửi
        col_map = {
            'booking': 'Mã booking',
            'ma_kho': 'Mã kho',
            'ma_st': 'Mã siêu thị',
            'so_kien': 'Số Kiện NCC',
            'so_hd': 'Số Hóa Đơn NCC',
            'ngay_giao': 'Ngày giao dự kiến'
        }

        # Kiểm tra xem file có đủ các cột cần thiết không
        missing_cols = [v for k, v in col_map.items() if v not in df.columns]
        
        if missing_cols:
            st.error(f"Thiếu các cột: {', '.join(missing_cols)}. Hãy kiểm tra lại file Excel.")
        else:
            if st.button("🚀 XUẤT PDF THEO FORMAT MỚI"):
                buffer = io.BytesIO()
                c = canvas.Canvas(buffer, pagesize=(4*inch, 2*inch))
                
                for _, row in df.iterrows():
                    # Lấy dữ liệu và làm sạch
                    booking = row[col_map['booking']].replace(".0", "")
                    ma_kho = row[col_map['ma_kho']].replace(".0", "")
                    ma_st = row[col_map['ma_st']].replace(".0", "")
                    so_hd = row[col_map['so_hd']].replace(".0", "")
                    ngay_giao = row[col_map['ngay_giao']].replace(".0", "")
                    
                    # Logic xử lý số kiện (ít nhất là 1)
                    try:
                        tong_so_kien = int(float(row[col_map['so_kien']]))
                        if tong_so_kien <= 0: tong_so_kien = 1
                    except:
                        tong_so_kien = 1

                    # Vòng lặp in từng tem cho mỗi kiện
                    for i in range(1, tong_so_kien + 1):
                        # QR Content: Booking-MaKho-MaST-SoKien-SoHD-KienThu
                        qr_content = f"{booking}-{ma_kho}-{ma_st}-{tong_so_kien}-{so_hd}-K{i}"
                        
                        qr = qrcode.QRCode(version=1, border=1)
                        qr.add_data(qr_content)
                        qr.make(fit=True)
                        img_qr = qr.make_image(fill_color="black", back_color="white")
                        
                        qr_stream = io.BytesIO()
                        img_qr.save(qr_stream, format='PNG')
                        qr_stream.seek(0)

                        # --- VẼ GIAO DIỆN TEM (Giữ nguyên layout chuyên nghiệp) ---
                        c.setLineWidth(1.2)
                        c.rect(0.1*inch, 0.1*inch, 3.8*inch, 1.8*inch)
                        c.line(0.1*inch, 1.45*inch, 3.9*inch, 1.45*inch) # Ngang trên
                        c.line(1.3*inch, 0.55*inch, 1.3*inch, 1.45*inch) # Dọc trái
                        c.line(2.0*inch, 0.55*inch, 2.0*inch, 1.45*inch) # Dọc giữa
                        
                        c.setFont("Helvetica-Bold", 8)
                        c.drawString(0.2*inch, 1.6*inch, f"NCC: CHUONG DUONG")
                        c.drawRightString(3.8*inch, 1.6*inch, f"BOOKING: {booking}")
                        
                        c.setFont("Helvetica-Bold", 10)
                        c.drawString(0.2*inch, 1.15*inch, f"MA KHO: {ma_kho}")
                        c.drawString(0.2*inch, 0.9*inch, f"MA ST: {ma_st}")
                        
                        # Hiển thị số kiện to giữa tem
                        c.setFont("Helvetica-Bold", 24)
                        c.drawCentredString(1.65*inch, 0.85*inch, f"{i} / {tong_so_kien}")
                        
                        c.setFont("Helvetica", 8)
                        c.drawString(0.2*inch, 0.3*inch, f"GIAO DU KIEN: {ngay_giao}")
                        
                        # Chèn QR
                        c.drawImage(qr_stream, 2.1*inch, 0.58*inch, width=1.6*inch, height=0.85*inch, preserveAspectRatio=True)
                        c.setFont("Helvetica", 7)
                        c.drawCentredString(3.0*inch, 0.45*inch, qr_content)

                        c.showPage()
                
                c.save()
                st.download_button("📥 TẢI TEM PDF", buffer.getvalue(), f"Tem_MT_Moi_{datetime.now().strftime('%d%m')}.pdf")
                
    except Exception as e:
        st.error(f"Lỗi: {e}")
