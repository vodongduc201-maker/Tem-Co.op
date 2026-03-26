import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Team MT - Nhập Báo Cáo", page_icon="📝")

# 1. Danh sách dữ liệu mẫu (Bạn có thể tự sửa lại theo danh sách thực tế của Chương Dương)
DS_SIEU_THI = ["Co.op Mart Cống Quỳnh", "Co.op Mart Hùng Vương", "BigC Miền Đông", "WinMart Thảo Điền", "BHX Tân Phú"]
DS_SAN_PHAM = ["Sá Xị Chương Dương (Lon)", "Sá Xị Zero (Lon)", "Soda Kem (Lon)", "Sá Xị 1.5L (Chai)", "Nước tinh khiết CD"]

st.title("🥤 Hệ thống Nhập Báo Cáo Thị Trường")
st.markdown(f"**Ngày thực hiện:** {datetime.now().strftime('%d/%m/%Y')}")

# 2. Giao diện nhập liệu
with st.form("form_bao_cao", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        sieu_thi = st.selectbox("🏢 Chọn Siêu thị / Cửa hàng:", DS_SIEU_THI)
    with col2:
        nhan_vien = st.text_input("👤 Tên nhân viên:")

    st.markdown("---")
    st.subheader("📦 Số lượng kiểm kê")
    
    # Tạo các hàng nhập liệu cho từng sản phẩm
    data_input = []
    for sp in DS_SAN_PHAM:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.write(f"**{sp}**")
        with c2:
            facing = st.number_input(f"Facing", min_value=0, step=1, key=f"f_{sp}")
        with c3:
            stock = st.number_input(f"Tồn kho", min_value=0, step=1, key=f"s_{sp}")
        data_input.append({"Sản phẩm": sp, "Facing": facing, "Tồn kho": stock})

    ghi_chu = st.text_area("🗒️ Ghi chú thêm (Khuyến mãi, đối thủ...):")
    
    submit = st.form_submit_button("🚀 GỬI BÁO CÁO & XUẤT EXCEL")

# 3. Xử lý sau khi nhấn Gửi
if submit:
    if not nhan_vien:
        st.error("Vui lòng nhập tên nhân viên trước khi gửi!")
    else:
        # Tạo DataFrame từ dữ liệu đã nhập
        df = pd.DataFrame(data_input)
        df['Siêu thị'] = sieu_thi
        df['Nhân viên'] = nhan_vien
        df['Thời gian'] = datetime.now().strftime('%H:%M:%S')
        df['Ghi chú'] = ghi_chu
        
        # Sắp xếp lại thứ tự cột cho đẹp
        df = df[['Thời gian', 'Nhân viên', 'Siêu thị', 'Sản phẩm', 'Facing', 'Tồn kho', 'Ghi chú']]
        
        st.success(f"✅ Đã ghi nhận báo cáo từ {sieu_thi}!")
        st.dataframe(df)

        # Xuất file Excel để tải về máy ngay lập tức
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Bao_cao_MT')
        
        st.download_button(
            label="📥 TẢI FILE EXCEL VỪA NHẬP",
            data=output.getvalue(),
            file_name=f"Bao_cao_{sieu_thi}_{datetime.now().strftime('%d%m')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
