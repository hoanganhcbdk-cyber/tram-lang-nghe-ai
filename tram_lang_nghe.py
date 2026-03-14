import streamlit as st
import datetime
import random
import pandas as pd
import requests

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
try:
    API_KEY = st.secrets["API_KEY"].strip()
except:
    st.error("❌ Chưa cấu hình API_KEY trong mục Secrets của Streamlit!")
    st.stop()
    
st.set_page_config(page_title="Trạm Lắng Nghe AI - Pro Max", page_icon="🏫", layout="wide")

# ==========================================
# KẾT NỐI BỘ NHỚ VĨNH VIỄN (FIREBASE)
# ==========================================
FIREBASE_URL = "https://tram-lang-nghe-data-default-rtdb.firebaseio.com"

def tai_du_lieu_tu_may():
    try:
        r = requests.get(f"{FIREBASE_URL}/he_thong.json")
        if r.status_code == 200 and r.json():
            return r.json()
    except: pass
    return None

def luu_du_lieu_len_may():
    du_lieu_dong_bo = {
        'users': st.session_state['users'],
        'database': st.session_state['database']
    }
    try:
        requests.put(f"{FIREBASE_URL}/he_thong.json", json=du_lieu_dong_bo)
    except: pass

# ==========================================
# KHỞI TẠO CƠ SỞ DỮ LIỆU CHÍNH
# ==========================================
if 'he_thong_da_khoi_dong' not in st.session_state:
    du_lieu_dam_may = tai_du_lieu_tu_may()
    
    if du_lieu_dam_may:
        st.session_state['users'] = du_lieu_dam_may.get('users', {})
        st.session_state['database'] = du_lieu_dam_may.get('database', {})
    else:
        st.session_state['users'] = {
            'admin': {'pass': 'admin123', 'role': 'admin', 'name': 'Ban Giám Hiệu'},
            'gv01': {'pass': '1111', 'role': 'teacher', 'name': 'Thầy Hoàng Anh (Sinh học)'},
            'gv02': {'pass': '2222', 'role': 'teacher', 'name': 'Cô Phương (Toán)'},
            'gv03': {'pass': '3333', 'role': 'teacher', 'name': 'Thầy Cường (Đoàn Đội)'},
            'gv04': {'pass': '4444', 'role': 'teacher', 'name': 'Cô Yến (Tâm lý)'}
        }
        st.session_state['database'] = {}
        luu_du_lieu_len_may()
        
    st.session_state['he_thong_da_khoi_dong'] = True

if 'current_user' not in st.session_state: st.session_state['current_user'] = None
danh_sach_gv = {k: v['name'] for k, v in st.session_state['users'].items() if v['role'] == 'teacher'}

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
st.title("🏫 HỆ THỐNG TƯ VẤN TÂM LÝ & QUẢN TRỊ HỌC ĐƯỜNG BẰNG AI")
st.markdown("---")

tab_hoc_sinh, tab_giao_vien, tab_quan_ly = st.tabs([
    "🎓 1. Cổng dành cho Học Sinh", 
    "👨‍🏫 2. Không gian làm việc Giáo Viên", 
    "⚙️ 3. Trung tâm Quản lý (Admin)"
])

# ==========================================
# TAB 1: CỔNG HỌC SINH
# ==========================================
with tab_hoc_sinh:
    col_gui, col_xem = st.columns(2)
    with col_gui:
        st.header("💌 Kết nối với Thầy Cô")
        st.info("Em có thể để trống lớp nếu muốn giấu kín hoàn toàn nhé!")
        hs_khoi_lop = st.text_input("Khối/Lớp của em (Không bắt buộc, VD: 12A1):")
        gv_duoc_chon = st.selectbox("Em muốn tâm sự với thầy cô nào?", options=list(danh_sach_gv.keys()), format_func=lambda x: danh_sach_gv[x])
        tam_su_input = st.text_area("Hôm nay em gặp chuyện gì? Hãy kể chi tiết nhé:", height=120)
        
        if st.button("🚀 Gửi đi an toàn", type="primary"):
            if tam_su_input:
                ma_bi_mat = f"HS-{random.randint(1000, 9999)}"
                st.session_state['database'][ma_bi_mat] = {
                    "thoi_gian": datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
                    "lop": hs_khoi_lop if hs_khoi_lop else "Ẩn danh",
                    "gv_phu_trach": gv_duoc_chon,
                    "tin_nhan": [{"nguoi_gui": "Học sinh", "noi_dung": tam_su_input}],
                    "ai_phan_tich": None,
                    "muc_do_rui_ro": "Chờ AI phân tích",
                    "trang_thai": "Chờ xử lý"
                }
                luu_du_lieu_len_may()
                st.success(f"✅ Gửi thành công! Mã bí mật của em là: **{ma_bi_mat}**")
            else: st.warning("Em hãy viết nội dung trước khi gửi.")

    with col_xem:
        st.header("💬 Phòng Chat Riêng Tư")
        ma_tra_cuu = st.text_input("Nhập Mã bí mật hệ thống đã cấp cho em:")
        if st.button("Truy cập phòng chat"): st.session_state['ca_dang_xem'] = ma_tra_cuu.strip()
            
        if 'ca_dang_xem' in st.session_state and st.session_state['ca_dang_xem'] in st.session_state['database']:
            ca = st.session_state['database'][st.session_state['ca_dang_xem']]
            ten_gv_phu_trach = st.session_state['users'][ca['gv_phu_trach']]['name']
            
            st.markdown(f"### Cuộc trò chuyện với {ten_gv_phu_trach}")
            with st.container(height=300, border=True):
                for tn in ca['tin_nhan']:
                    if tn['nguoi_gui'] == "Học sinh": st.info(f"**Em:** {tn['noi_dung']}")
                    else: st.success(f"**Thầy/Cô:** {tn['noi_dung']}")
            
            if ca['trang_thai'] == "GV đã phản hồi":
                hs_phan_hoi = st.text_input("Gửi tin nhắn tiếp theo của em:")
                if st.button("Gửi trả lời", key="hs_reply"):
                    ca['tin_nhan'].append({"nguoi_gui": "Học sinh", "noi_dung": hs_phan_hoi})
                    ca['trang_thai'] = "HS vừa nhắn lại" 
                    ca['ai_phan_tich'] = None 
                    luu_du_lieu_len_may()
                    st.rerun()
            elif ca['trang_thai'] in ["Chờ xử lý", "HS vừa nhắn lại"]: st.warning("⏳ Thầy cô đang soạn tin nhắn trả lời em. Em quay lại sau ít phút nhé!")
        elif 'ca_dang_xem' in st.session_state: st.error("Không tìm thấy mã này. Em nhập đúng chưa?")

# ==========================================
# HÀM KIỂM TRA ĐĂNG NHẬP
# ==========================================
def kiem_tra_dang_nhap(role_can_thiet=None):
    if not st.session_state['current_user']:
        st.warning("🔒 Yêu cầu đăng nhập tài khoản Cán bộ/Giáo viên.")
        u = st.text_input("Tài khoản", key=f"user_{role_can_thiet}")
        p = st.text_input("Mật khẩu", type="password", key=f"pass_{role_can_thiet}")
        if st.button("Đăng nhập", key=f"login_btn_{role_can_thiet}"):
            if u in st.session_state['users'] and st.session_state['users'][u]['pass'] == p:
                st.session_state['current_user'] = u
                st.rerun()
            else: st.error("Sai tài khoản hoặc mật khẩu!")
        return False
    else:
        user_info = st.session_state['users'][st.session_state['current_user']]
        if role_can_thiet and user_info['role'] != role_can_thiet:
            st.error("🚫 Bạn không có quyền truy cập khu vực này!")
            return False
        col_info, col_btn = st.columns([8, 2])
        col_info.write(f"👤 Đang đăng nhập: **{user_info['name']}**")
        if col_btn.button("🚪 Đăng xuất", key=f"logout_btn_{role_can_thiet}"):
            st.session_state['current_user'] = None
            st.rerun()
        return True

# ==========================================
# TAB 2: KHÔNG GIAN LÀM VIỆC CỦA GIÁO VIÊN
# ==========================================
with tab_giao_vien:
    if kiem_tra_dang_nhap(role_can_thiet='teacher'):
        user_id = st.session_state['current_user']
        st.header(f"Bảng điều khiển Tư vấn của {st.session_state['users'][user_id]['name']}")
        
        ca_cua_toi = {k: v for k, v in st.session_state['database'].items() if v['gv_phu_trach'] == user_id}
        ca_cho_xu_ly = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] in ["Chờ xử lý", "HS vừa nhắn lại"]}
        ca_da_phan_hoi = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] == "GV đã phản hồi"}
        
        st.subheader(f"🔴 Các ca đang chờ bạn xử lý ({len(ca_cho_xu_ly)})")
        if not ca_cho_xu_ly: st.write("✅ Tuyệt vời, bạn không có ca tồn đọng nào!")
        else:
            for ma_ca, ca in ca_cho_xu_ly.items():
                with st.expander(f"⚠️ Ca {ma_ca} | Lớp: {ca['lop']} | Báo động: {ca['muc_do_rui_ro']}", expanded=True):
                    st.write("**Lịch sử hội thoại:**")
                    with st.container(height=150, border=True):
                        for tn in ca['tin_nhan']: st.write(f"*{tn['nguoi_gui']}*: {tn['noi_dung']}")
                    
                    if st.button(f"🧠 Yêu cầu AI Cố vấn ca này", key=f"ai_{ma_ca}"):
                        with st.spinner("Đang kết nối siêu trí tuệ Gemini 2.5 Flash..."):
                            lich_su = "\n".join([f"{t['nguoi_gui']}: {t['noi_dung']}" for t in ca['tin_nhan']])
                            prompt = f"Đọc lịch sử trò chuyện:\n{lich_su}\nĐóng vai Chuyên gia Tâm lý, phân tích theo cấu trúc:\n[RỦI RO TÂM LÝ]: Thấp/Trung bình/Cao\n[1. PHÂN TÍCH]: Tâm lý, Môi trường.\n[2. HƯỚNG GIẢI QUYẾT]\n[3. GỢI Ý TIN NHẮN]"
                            
                            try:
                                # GỌI ĐÚNG CON GEMINI 2.5 MÀ BẠN ĐƯỢC PHÉP DÙNG!
                                url_main = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
                                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                                headers = {'Content-Type': 'application/json'}
                                
                                response = requests.post(url_main, json=payload, headers=headers)
                                
                                if response.status_code == 200:
                                    res_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                                    ca['ai_phan_tich'] = res_text
                                    if "Cao" in res_text[:80]: ca['muc_do_rui_ro'] = "Cao (Khẩn cấp)"
                                    elif "Trung bình" in res_text[:80]: ca['muc_do_rui_ro'] = "Trung bình"
                                    else: ca['muc_do_rui_ro'] = "Thấp"
                                elif response.status_code == 429:
                                    ca['ai_phan_tich'] = "⏳ BẠN ĐANG HỎI QUÁ NHANH: Quota của bạn là 5 lần/phút. Xin đợi 15 giây rồi bấm lại nhé!"
                                else:
                                    ca['ai_phan_tich'] = f"🚨 LỖI {response.status_code}: {response.text}"
                                
                                luu_du_lieu_len_may()
                                st.rerun()
                                
                            except Exception as e: 
                                st.error(f"Lỗi mạng: {e}")
                                
                    # === GIAO DIỆN CỬA SỔ GEMINI MỚI TẠI ĐÂY ===
                    if ca.get('ai_phan_tich'):
                        if "🚨" in ca.get('ai_phan_tich') or "⏳" in ca.get('ai_phan_tich'):
                            st.warning(ca.get('ai_phan_tich'))
                        else:
                            st.markdown("##### ✨ Cửa sổ Cố vấn AI (Gemini)")
                            with st.container(height=300, border=True):
                                st.markdown(ca.get('ai_phan_tich'))
                            
                        st.markdown("---")
                        gv_tra_loi = st.text_area("Soạn tin nhắn trả lời học sinh (Dựa trên tư vấn của AI):", height=80, key=f"txt_{ma_ca}")
                        if st.button("✅ Gửi trả lời", type="primary", key=f"gui_{ma_ca}"):
                            ca['tin_nhan'].append({"nguoi_gui": "Giáo viên", "noi_dung": gv_tra_loi})
                            ca['trang_thai'] = "GV đã phản hồi"
                            luu_du_lieu_len_may()
                            st.rerun()

        st.markdown("---")
        st.subheader(f"🟢 Các ca đang theo dõi / Đã phản hồi ({len(ca_da_phan_hoi)})")
        for ma_ca, ca in ca_da_phan_hoi.items():
            with st.expander(f"Ca {ma_ca} | Lớp: {ca['lop']} (Đã gửi tin nhắn)"):
                with st.container(height=150, border=True):
                        for tn in ca['tin_nhan']: st.write(f"*{tn['nguoi_gui']}*: {tn['noi_dung']}")

# ==========================================
# TAB 3: TRUNG TÂM QUẢN LÝ (Chỉ Admin)
# ==========================================
with tab_quan_ly:
    if kiem_tra_dang_nhap(role_can_thiet='admin'):
        st.header("⚙️ QUẢN TRỊ HỆ THỐNG TỔNG THỂ")
        with st.expander("🛠 Quản lý Nhân sự (Thêm/Sửa/Xóa Giáo viên)", expanded=True):
            st.write("👉 **1. SỬA HOẶC XÓA GIÁO VIÊN ĐANG CÓ:**")
            danh_sach_tai_khoan_gv = [k for k, v in st.session_state['users'].items() if v['role'] == 'teacher']
            if danh_sach_tai_khoan_gv:
                gv_can_sua = st.selectbox("Chọn tài khoản để chỉnh sửa:", options=danh_sach_tai_khoan_gv, format_func=lambda x: f"{x} ({st.session_state['users'][x]['name']})")
                c_edit1, c_edit2, c_edit3 = st.columns(3)
                ten_moi = c_edit1.text_input("Tên hiển thị mới:", value=st.session_state['users'][gv_can_sua]['name'])
                pass_moi = c_edit2.text_input("Mật khẩu mới:", value=st.session_state['users'][gv_can_sua]['pass'])
                c_btn1, c_btn2 = c_edit3.columns(2)
                if c_btn1.button("💾 Lưu Sửa đổi"):
                    st.session_state['users'][gv_can_sua]['name'] = ten_moi
                    st.session_state['users'][gv_can_sua]['pass'] = pass_moi
                    luu_du_lieu_len_may()
                    st.success("Cập nhật thành công!")
                    st.rerun()
                if c_btn2.button("🗑️ Xóa GV này"):
                    del st.session_state['users'][gv_can_sua]
                    luu_du_lieu_len_may()
                    st.warning(f"Đã xóa tài khoản {gv_can_sua}!")
                    st.rerun()

            st.markdown("---")
            st.write("👉 **2. THÊM MỚI GIÁO VIÊN TƯ VẤN:**")
            c_add1, c_add2, c_add3 = st.columns(3)
            new_id = c_add1.text_input("Tên đăng nhập (VD: gv06)")
            new_name = c_add2.text_input("Tên hiển thị (VD: Cô Ngọc)")
            new_pass = c_add3.text_input("Mật khẩu")
            if st.button("➕ Thêm Giáo viên", type="primary"):
                if new_id and new_name and new_pass:
                    if new_id in st.session_state['users']: st.error("Tên đăng nhập này đã tồn tại!")
                    else:
                        st.session_state['users'][new_id] = {'pass': new_pass, 'role': 'teacher', 'name': new_name}
                        luu_du_lieu_len_may()
                        st.success("Đã thêm giáo viên thành công!")
                        st.rerun()
                else: st.warning("Vui lòng điền đầy đủ thông tin.")
        
        st.subheader("📊 Bảng vàng Thống kê")
        tong_ca = len(st.session_state['database'])
        ca_khan_cap = len([ca for ca in st.session_state['database'].values() if "Cao" in ca['muc_do_rui_ro']])
        c_a, c_b, c_c = st.columns(3)
        c_a.metric("Tổng số ca đã tiếp nhận", f"{tong_ca} ca")
        c_b.metric("Ca Khẩn cấp (Cần BGH chú ý)", f"{ca_khan_cap} ca", delta="Nguy hiểm", delta_color="inverse")
        c_c.metric("Số lượng GV tham gia", f"{len(danh_sach_tai_khoan_gv)} người")
        
        if tong_ca > 0:
            st.subheader("📥 Trích xuất Hồ sơ Tư vấn (Export Data)")
            du_lieu_xuat = []
            for ma_ca, ca in st.session_state['database'].items():
                lich_su_chat = " | ".join([f"{t['nguoi_gui']}: {t['noi_dung']}" for t in ca['tin_nhan']])
                du_lieu_xuat.append({
                    "Mã Ca": ma_ca, "Thời gian": ca['thoi_gian'], "Lớp": ca['lop'],
                    "Giáo viên": st.session_state['users'][ca['gv_phu_trach']]['name'],
                    "Rủi ro": ca['muc_do_rui_ro'], "Trạng thái": ca['trang_thai'],
                    "Nội dung Chat": lich_su_chat
                })
            df_export = pd.DataFrame(du_lieu_xuat)
            csv = df_export.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Tải xuống Báo cáo (CSV)", data=csv, file_name="Bao_Cao_Tam_Ly.csv", mime="text/csv", type="primary")

            # === TÍNH NĂNG MỚI: DỌN DẸP DỮ LIỆU ===
            st.markdown("---")
            st.subheader("🗑️ Dọn dẹp Hệ thống (Xóa ca test)")
            st.warning("Chú ý: Dữ liệu sau khi xóa sẽ biến mất khỏi cơ sở dữ liệu và không thể khôi phục!")
            danh_sach_ca = list(st.session_state['database'].keys())
            ca_can_xoa = st.selectbox("Chọn mã ca cần xóa:", options=danh_sach_ca, format_func=lambda x: f"{x} - Lớp: {st.session_state['database'][x]['lop']} ({st.session_state['database'][x]['thoi_gian']})")
            
            if st.button("🚨 Xóa vĩnh viễn ca này"):
                del st.session_state['database'][ca_can_xoa]
                luu_du_lieu_len_may()
                st.success(f"Đã dọn dẹp thành công hồ sơ {ca_can_xoa}!")
                st.rerun()