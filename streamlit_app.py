# --- KẾT NỐI (Sửa lại dòng này) ---
# Tên kết nối "gsheets" phải trùng với tên trong [connections.gsheets] ở Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# ... (Các phần chọn siêu thị giữ nguyên) ...

if submit:
    time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # Tạo DataFrame mới từ dữ liệu nhập
    new_data = pd.DataFrame([{
        "Thời gian": time_now,
        "Nhân viên": nv_selected,
        "Hệ thống": ht_selected,
        "Siêu thị": st_selected,
        "Sản phẩm": str([row["Sản phẩm"] for row in data_rows]),
        "Facing": str([row["Facing"] for row in data_rows]),
        "Tồn kho": str([row["Tồn kho"] for row in data_rows]),
        "Ghi chú": ghi_chu,
        "Ảnh": "Có" if uploaded_file else "Không"
    }])
    
    try:
        # ĐỌC dữ liệu cũ đang có trên Sheet
        existing_data = conn.read(worksheet="Data_Bao_Cao_MT", ttl=0)
        # GỘP dữ liệu cũ và mới
        updated_df = pd.concat([existing_data, new_data], ignore_index=True)
        # GỬI ngược lại toàn bộ lên Sheet
        conn.update(worksheet="Data_Bao_Cao_MT", data=updated_df)
        
        st.success("✅ Đã lưu dữ liệu thành công!")
        st.balloons()
    except Exception as e:
        st.error(f"Lỗi gửi dữ liệu: {e}")
        st.info("Kiểm tra lại: 1. Tên Sheet có đúng là 'Data_Bao_Cao_MT' không? 2. Đã Share quyền Editor cho Email Service Account chưa?")
