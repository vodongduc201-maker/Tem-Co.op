import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="Chương Dương - Số hóa Báo cáo", page_icon="📝")

st.title("📝 Hệ thống Số hóa Báo cáo Team MT")
st.markdown("---")

st.info("💡 **Cách dùng:** Mở ảnh báo cáo bằng Google Lens trên điện thoại -> 'Chọn tất cả' -> 'Sao chép văn bản' -> Dán vào ô dưới đây.")

# Ô nhập liệu
user_input = st.text_area("📍 Dán văn bản từ Google Lens vào đây:", height=300, 
                         placeholder="Ví dụ:\nSá xị zero 5 7\nSoda kem 10 12\nChuong Duong 1.5L 2 4")

if user_input:
    # Xử lý tách dòng
    raw_lines = user_input.split('\n')
    processed_data = []

    for line in raw_lines:
        if line.strip():
            # Tìm tất cả các con số trong dòng (thường là số Facing/Tồn kho)
            numbers = re.findall(r'\d+', line)
            # Tìm phần chữ (thường là tên sản phẩm)
            text_part = re.sub(r'\d+', '', line).strip()
            
            if text_part or numbers:
                row = [text_part] + numbers
                processed_data.append(row)

    if processed_data:
        # Tạo DataFrame với các cột tạm thời
        max_cols = max(len(row) for row in processed_data)
        col_names = ["Sản phẩm"] + [f"Số liệu {i+1}" for i in range(max_cols - 1)]
        
        df = pd.DataFrame(processed_data, columns=col_names)
        
        st.subheader("📊 Dữ liệu đã chuyển đổi")
        st.dataframe(df, use_container_width=True)

        # Xuất file Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Bao_cao_MT')
        
        st.success("✅ Chuyển đổi thành công!")
        st.download_button(
            label="📥 TẢI FILE EXCEL BÁO CÁO",
            data=output.getvalue(),
            file_name=f"Bao_cao_MT_CD_{datetime.now().strftime('%d%m_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Không tìm thấy dữ liệu hợp lệ. Vui lòng kiểm tra lại nội dung dán.")

# Chân trang
st.markdown("---")
st.caption("Phát triển bởi Team MT - Chương Dương Beverage")
