import streamlit as st
import datetime
import random
import pandas as pd
import requests

# ==========================================
# CẤU HÌNH HỆ THỐNG & API
# ==========================================
st.set_page_config(page_title="Trạm Lắng Nghe AI - Hoàng Su Phì", page_icon="🏫", layout="wide", initial_sidebar_state="expanded")

try:
    if "API_KEYS" in st.secrets:
        danh_sach_keys = [k.strip() for k in st.secrets["API_KEYS"].split(",") if k.strip()]
    elif "API_KEY" in st.secrets:
        danh_sach_keys = [st.secrets["API_KEY"].strip()]
    else:
        st.error("❌ Chưa cấu hình API_KEYS trong mục Secrets!")
        st.stop()
except Exception as e:
    st.error(f"❌ Lỗi cấu hình Secrets: {e}")
    st.stop()

MA_BAO_MAT_TRUONG = "HSP2026" 

# ==========================================
# CÁC HÀM TIỆN ÍCH (TELEGRAM)
# ==========================================
def gui_thong_bao_ve_dien_thoai(tin_nhan_bao_cao):
    try:
        bot_token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")
        if bot_token and chat_id:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": tin_nhan_bao_cao, "parse_mode": "Markdown"}
            requests.post(url, json=payload, timeout=3)
    except: pass

# ==========================================
# KẾT NỐI BỘ NHỚ VĨNH VIỄN (FIREBASE)
# ==========================================
FIREBASE_URL = "https://tram-lang-nghe-data-default-rtdb.firebaseio.com"

def tai_du_lieu_tu_may():
    try:
        r = requests.get(f"{FIREBASE_URL}/he_thong.json")
        if r.status_code == 200 and r.json(): return r.json()
    except: pass
    return None

def luu_du_lieu_len_may():
    du_lieu_dong_bo = {'users': st.session_state['users'], 'database': st.session_state['database']}
    try: requests.put(f"{FIREBASE_URL}/he_thong.json", json=du_lieu_dong_bo)
    except: pass

# ==========================================
# KHỞI TẠO STATE & DỮ LIỆU
# ==========================================
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = "landing_page"
if 'current_user' not in st.session_state: 
    st.session_state['current_user'] = None

if 'he_thong_da_khoi_dong' not in st.session_state:
    du_lieu_dam_may = tai_du_lieu_tu_may()
    if du_lieu_dam_may:
        st.session_state['users'] = du_lieu_dam_may.get('users', {})
        st.session_state['database'] = du_lieu_dam_may.get('database', {})
    else:
        st.session_state['users'] = {
            'admin': {'pass': 'admin123', 'role': 'admin', 'name': 'Ban Giám Hiệu', 'phone': '', 'email': '', 'dob': ''},
            'gv01': {'pass': '1111', 'role': 'teacher', 'name': 'Thầy Lý Hoàng Anh', 'phone': '0969969189', 'email': 'hoanganhcbdk@gmail.com', 'dob': ''},
            'gv02': {'pass': '2222', 'role': 'teacher', 'name': 'Cô Phương (Toán)', 'phone': '', 'email': '', 'dob': ''}
        }
        st.session_state['database'] = {}
        luu_du_lieu_len_may()
    st.session_state['he_thong_da_khoi_dong'] = True

danh_sach_gv = {k: v['name'] for k, v in st.session_state['users'].items() if v['role'] == 'teacher'}

def kiem_tra_dang_nhap(role_can_thiet=None):
    if 'token_login' in st.query_params:
        user_luu = st.query_params['token_login']
        if user_luu in st.session_state['users']:
            st.session_state['current_user'] = user_luu

    if not st.session_state['current_user']:
        st.warning("🔒 Vui lòng đăng nhập để truy cập không gian làm việc.")
        col1, col2 = st.columns(2)
        with col1:
            u = st.text_input("Tài khoản đăng nhập", key=f"user_{role_can_thiet}")
            p = st.text_input("Mật khẩu", type="password", key=f"pass_{role_can_thiet}")
            nho_mat_khau = st.checkbox("Ghi nhớ thiết bị này (Giữ đăng nhập)", key=f"nho_{role_can_thiet}")
            
            if st.button("🔑 Đăng nhập hệ thống", type="primary", key=f"login_btn_{role_can_thiet}"):
                if u in st.session_state['users'] and st.session_state['users'][u]['pass'] == p:
                    st.session_state['current_user'] = u
                    if nho_mat_khau: st.query_params['token_login'] = u
                    st.rerun()
                else: st.error("❌ Sai tài khoản hoặc mật khẩu!")
        return False
    else:
        user_info = st.session_state['users'][st.session_state['current_user']]
        if role_can_thiet and user_info['role'] != role_can_thiet:
            st.error("🚫 Bạn không có quyền truy cập khu vực này!")
            return False
        return True

def nut_dang_xuat():
    if st.sidebar.button("🚪 Đăng xuất / Đổi vai trò", use_container_width=True):
        st.session_state['current_user'] = None
        st.session_state['current_view'] = "landing_page"
        if 'token_login' in st.query_params: del st.query_params['token_login']
        st.rerun()

def render_ban_quyen():
    st.sidebar.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.caption("🔰 **BẢN QUYỀN SÁNG CHẾ**\n\n👨‍💻 Tác giả: Thầy Lý Hoàng Anh\n📍 Đơn vị: THPT Hoàng Su Phì\n📞 Zalo: 0969969189\n📧 hoanganhcbdk@gmail.com\n\n© 2026 Trạm Lắng Nghe AI")

# ==========================================
# 1. TRANG CHỦ (LANDING PAGE) CHUYÊN NGHIỆP
# ==========================================
if st.session_state['current_view'] == "landing_page":
    st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-weight: 800;'>🏫 TRẠM LẮNG NGHE TÂM LÝ HỌC ĐƯỜNG</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #4B5563; margin-bottom: 30px;'>Trường THPT Hoàng Su Phì - Nơi thấu hiểu, sẻ chia và đồng hành cùng học sinh</h4>", unsafe_allow_html=True)
    
    # 3 Khối Nút Bấm To Đẹp (Đẩy lên trên cùng)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 🎓 Cổng Học Sinh\nNơi các em an tâm chia sẻ mọi khó khăn, áp lực trong học tập và cuộc sống.")
        if st.button("Truy cập Cổng Học Sinh ➡️", use_container_width=True):
            st.session_state['current_view'] = "student_view"
            st.rerun()
    with col2:
        st.success("### 👨‍🏫 Cổng Giáo Viên\nKhông gian làm việc, quản lý hồ sơ tâm lý và nhận phân tích từ AI.")
        if st.button("Truy cập Cổng Giáo Viên ➡️", use_container_width=True):
            st.session_state['current_view'] = "teacher_view"
            st.rerun()
    with col3:
        st.warning("### ⚙️ Cổng Quản Lý\nBảng điều khiển dành cho BGH, thống kê dữ liệu và xuất báo cáo chuẩn.")
        if st.button("Truy cập Cổng Quản Lý ➡️", use_container_width=True):
            st.session_state['current_view'] = "admin_view"
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hình ảnh minh họa (Đẩy xuống dưới, tỷ lệ dài)
    st.image("https://images.unsplash.com/photo-1529390079861-591de354faf5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1800&q=80", use_container_width=True, caption="Trạm Lắng Nghe - Đồng hành cùng học sinh mỗi ngày đến trường")

# ==========================================
# 2. KHÔNG GIAN HỌC SINH
# ==========================================
elif st.session_state['current_view'] == "student_view":
    if st.sidebar.button("⬅️ Quay lại Trang chủ", use_container_width=True):
        st.session_state['current_view'] = "landing_page"
        st.rerun()
    render_ban_quyen()
        
    st.title("🎓 CỔNG KẾT NỐI TÂM LÝ DÀNH CHO HỌC SINH")
    st.info("**👋 CHÀO MỪNG CÁC EM!** Mọi tâm sự của em đều được giữ bí mật tuyệt đối. Em có thể chọn gửi tin nhắn (Gián tiếp) hoặc đặt lịch hẹn gặp (Trực tiếp).")
    
    tab_gui, tab_xem = st.tabs(["📝 Gửi Lời Tâm Sự Mới", "💬 Tra Cứu Phản Hồi"])
    with tab_gui:
        ma_xac_thuc = st.text_input("🔑 Nhập Mã bảo mật của trường (Hỏi GVCN nếu em không biết):", type="password")
        hs_khoi_lop = st.text_input("Khối/Lớp của em (Không bắt buộc):")
        hs_cam_xuc = st.selectbox("Ngay lúc này, em đang cảm thấy thế nào?", 
                                  ["😐 Bình thường", "😔 Hơi buồn, suy tư", "😰 Căng thẳng, áp lực thi cử", "😡 Tức giận, uất ức", "😨 Sợ hãi, lo âu", "😭 Tuyệt vọng, cần giúp đỡ gấp"])
        gv_duoc_chon = st.selectbox("Em muốn tâm sự với thầy cô nào?", options=list(danh_sach_gv.keys()), format_func=lambda x: danh_sach_gv[x])
        
        st.markdown("---")
        hinh_thuc_tv = st.radio("Em muốn thầy cô hỗ trợ theo hình thức nào?", ["💬 Tư vấn Gián tiếp (Nhắn tin)", "🤝 Tư vấn Trực tiếp (Hẹn gặp)"])
        
        ngay_hen, gio_hen = "", ""
        if hinh_thuc_tv == "🤝 Tư vấn Trực tiếp (Hẹn gặp)":
            st.warning("📍 Thầy cô sẽ đợi em tại Phòng Tâm lý. Em hãy chọn thời gian em rảnh nhé:")
            c_ngay, c_gio = st.columns(2)
            ngay_hen = c_ngay.date_input("Chọn ngày hẹn:")
            gio_hen = c_gio.time_input("Chọn giờ hẹn (VD: 14:30):")
            
        tam_su_input = st.text_area("Hãy kể chi tiết câu chuyện của em để thầy cô hiểu rõ hơn nhé:", height=120)
        
        if st.button("🚀 Gửi đi an toàn", type="primary"):
            if not ma_xac_thuc or ma_xac_thuc.upper() != MA_BAO_MAT_TRUONG:
                st.error("❌ Sai Mã bảo mật của trường! Hệ thống từ chối nhận tin nhắn để chống spam.")
            elif tam_su_input:
                ma_bi_mat = f"HS-{random.randint(1000, 9999)}"
                chuoi_lich_hen = f"{ngay_hen.strftime('%d/%m/%Y')} lúc {gio_hen.strftime('%H:%M')}" if hinh_thuc_tv == "🤝 Tư vấn Trực tiếp (Hẹn gặp)" else "Không có"
                
                st.session_state['database'][ma_bi_mat] = {
                    "thoi_gian": datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
                    "lop": hs_khoi_lop if hs_khoi_lop else "Ẩn danh",
                    "cam_xuc_ban_dau": hs_cam_xuc,
                    "gv_phu_trach": gv_duoc_chon,
                    "hinh_thuc": hinh_thuc_tv,
                    "lich_hen": chuoi_lich_hen,
                    "tin_nhan": [{"nguoi_gui": "Học sinh", "noi_dung": tam_su_input}],
                    "ai_phan_tich": None,
                    "muc_do_rui_ro": "Chờ AI phân tích",
                    "trang_thai": "Chờ xử lý"
                }
                luu_du_lieu_len_may()
                gui_thong_bao_ve_dien_thoai(f"🚨 CÓ CA TƯ VẤN MỚI!\n- Mã ca: {ma_bi_mat}\n- Hình thức: {hinh_thuc_tv}")
                st.success(f"✅ Gửi thành công! Mã bí mật để em xem lại tin nhắn là: **{ma_bi_mat}**")
                st.balloons() 
            else: st.warning("Em hãy viết nội dung trước khi gửi.")

    with tab_xem:
        ma_tra_cuu = st.text_input("Nhập Mã bí mật hệ thống đã cấp cho em (VD: HS-1234):")
        if st.button("Truy cập phòng chat"): st.session_state['ca_dang_xem'] = ma_tra_cuu.strip()
            
        if 'ca_dang_xem' in st.session_state and st.session_state['ca_dang_xem'] in st.session_state['database']:
            ca = st.session_state['database'][st.session_state['ca_dang_xem']]
            ten_gv_phu_trach = st.session_state['users'][ca['gv_phu_trach']]['name']
            
            st.markdown(f"### 💬 Cuộc trò chuyện với {ten_gv_phu_trach}")
            if "Trực tiếp" in ca.get('hinh_thuc', ''): st.warning(f"⏰ **Lịch hẹn gặp:** {ca.get('lich_hen', 'Chưa rõ')}")
            
            with st.container(height=350, border=True):
                for tn in ca['tin_nhan']:
                    with st.chat_message("user" if tn['nguoi_gui'] == "Học sinh" else "assistant"):
                        st.markdown(f"**{tn['nguoi_gui']}**")
                        st.write(tn['noi_dung'])
            
            if ca['trang_thai'] in ["GV đã phản hồi", "Đã chốt lịch hẹn"]:
                hs_phan_hoi = st.text_input("Gửi tin nhắn phản hồi của em:")
                if st.button("Gửi trả lời", key="hs_reply"):
                    ca['tin_nhan'].append({"nguoi_gui": "Học sinh", "noi_dung": hs_phan_hoi})
                    ca['trang_thai'] = "HS vừa nhắn lại" 
                    luu_du_lieu_len_may()
                    gui_thong_bao_ve_dien_thoai(f"🔔 Học sinh ca {st.session_state['ca_dang_xem']} vừa nhắn tin phản hồi!")
                    st.rerun()
            elif ca['trang_thai'] in ["Chờ xử lý", "HS vừa nhắn lại"]: st.warning("⏳ Thầy cô đang đọc và soạn tin nhắn trả lời. Em chờ chút nhé!")

# ==========================================
# 3. KHÔNG GIAN GIÁO VIÊN (CÓ CẬP NHẬT HỒ SƠ)
# ==========================================
elif st.session_state['current_view'] == "teacher_view":
    if kiem_tra_dang_nhap(role_can_thiet='teacher'):
        user_id = st.session_state['current_user']
        user_name = st.session_state['users'][user_id].get('name', 'Giáo viên')
        
        # MENU SIDEBAR
        st.sidebar.markdown(f"👨‍🏫 **Đang đăng nhập:** {user_name}")
        st.sidebar.markdown("---")
        menu_gv = st.sidebar.radio("🧭 DANH MỤC QUẢN LÝ", [
            "📥 Ca chờ xử lý (Khẩn cấp/Hẹn gặp)", 
            "🟢 Lịch sử Ca đã chốt", 
            "👤 Hồ sơ cá nhân & Cài đặt"
        ])
        
        # NÚT LÀM MỚI (Thay thế cho Auto-refresh nháy màn hình)
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Cập nhật hộp thư", use_container_width=True):
            tai_du_lieu_tu_may()
            st.rerun()
            
        nut_dang_xuat()
        render_ban_quyen()

        st.title("👨‍🏫 KHÔNG GIAN LÀM VIỆC GIÁO VIÊN")
        ca_cua_toi = {k: v for k, v in st.session_state['database'].items() if v['gv_phu_trach'] == user_id}
        ca_cho = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] in ["Chờ xử lý", "HS vừa nhắn lại"]}
        ca_xong = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] not in ["Chờ xử lý", "HS vừa nhắn lại"]}

        if menu_gv == "📥 Ca chờ xử lý (Khẩn cấp/Hẹn gặp)":
            col_tieu_de, col_loc = st.columns([2, 1])
            col_tieu_de.subheader(f"🔴 Danh sách cần xử lý ({len(ca_cho)})")
            loc_ca = col_loc.selectbox("Bộ lọc nhanh:", ["Tất cả ca chờ", "Chỉ ca hẹn Trực tiếp", "Chỉ ca Khẩn cấp (Rủi ro Cao)"])
            
            if loc_ca == "Chỉ ca Khẩn cấp (Rủi ro Cao)": ca_cho = {k: v for k, v in ca_cho.items() if "Cao" in v['muc_do_rui_ro']}
            elif loc_ca == "Chỉ ca hẹn Trực tiếp": ca_cho = {k: v for k, v in ca_cho.items() if "Trực tiếp" in v.get('hinh_thuc', '')}
            
            if not ca_cho: st.success("✅ Bạn không có ca tồn đọng nào. Hãy nghỉ ngơi một chút nhé!")
            else:
                for ma_ca, ca in ca_cho.items():
                    hinh_thuc_hien_tai = ca.get('hinh_thuc', '💬 Tư vấn Gián tiếp')
                    tn_cuoi = ca['tin_nhan'][-1]['noi_dung']
                    tn_rut_gon = tn_cuoi[:55] + "..." if len(tn_cuoi) > 55 else tn_cuoi
                    label_thu_gon = f"[{hinh_thuc_hien_tai.split(' ')[0]}] {ma_ca} | Lớp {ca['lop']} | Rủi ro: {ca['muc_do_rui_ro']} | 📝 {tn_rut_gon}"
                    
                    with st.expander(label_thu_gon):
                        if "Trực tiếp" in hinh_thuc_hien_tai:
                            st.error(f"⏰ **Học sinh yêu cầu hẹn gặp mặt lúc:** {ca.get('lich_hen', 'Chưa xác định')}")
                        
                        with st.container(height=300, border=True):
                            for tn in ca['tin_nhan']:
                                with st.chat_message("user" if tn['nguoi_gui'] == "Học sinh" else "assistant"):
                                    st.markdown(f"**{tn['nguoi_gui']}**")
                                    st.write(tn['noi_dung'])
                        
                        if st.button(f"🧠 AI Cố vấn ca này", key=f"ai_{ma_ca}"):
                            with st.spinner("AI đang phân tích..."):
                                lich_su = "\n".join([f"{t['nguoi_gui']}: {t['noi_dung']}" for t in ca['tin_nhan']])
                                prompt = f"Đọc lịch sử: {lich_su}\nHãy phân tích Rủi ro Tâm lý, Nguyên nhân, Giải pháp và Gợi ý trả lời."
                                try:
                                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                                    headers = {'Content-Type': 'application/json'}
                                    thanh_cong = False
                                    keys_luot_nay = danh_sach_keys.copy()
                                    random.shuffle(keys_luot_nay)
                                    for key_hien_tai in keys_luot_nay:
                                        res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key_hien_tai}", json=payload, headers=headers)
                                        if res.status_code == 200:
                                            res_text = res.json()['candidates'][0]['content']['parts'][0]['text']
                                            ca['ai_phan_tich'] = res_text
                                            if "Cao" in res_text[:80]: ca['muc_do_rui_ro'] = "Cao (Khẩn cấp)"
                                            elif "Trung bình" in res_text[:80]: ca['muc_do_rui_ro'] = "Trung bình"
                                            else: ca['muc_do_rui_ro'] = "Thấp"
                                            thanh_cong = True
                                            break  
                                    if not thanh_cong: ca['ai_phan_tich'] = "⏳ HỆ THỐNG ĐANG QUÁ TẢI. Chờ 15 giây!"
                                    luu_du_lieu_len_may()
                                    st.rerun()
                                except Exception as e: st.error(f"Lỗi mạng: {e}")
                                    
                        if ca.get('ai_phan_tich'):
                            if "🚨" in ca.get('ai_phan_tich') or "⏳" in ca.get('ai_phan_tich'): st.warning(ca.get('ai_phan_tich'))
                            else:
                                st.markdown("##### ✨ Cố vấn AI")
                                with st.container(height=200, border=True): st.markdown(ca.get('ai_phan_tich'))
                                
                            gv_tra_loi = st.text_area("Soạn trả lời/Xác nhận lịch hẹn:", height=80, key=f"txt_{ma_ca}")
                            col_btn1, col_btn2 = st.columns(2)
                            if col_btn1.button("✅ Gửi trả lời & Đang theo dõi", type="primary", key=f"gui_{ma_ca}"):
                                ca['tin_nhan'].append({"nguoi_gui": "Giáo viên", "noi_dung": gv_tra_loi})
                                ca['trang_thai'] = "GV đã phản hồi"
                                luu_du_lieu_len_may()
                                st.rerun()
                            if "Trực tiếp" in hinh_thuc_hien_tai:
                                if col_btn2.button("📅 Gửi & Chốt lịch hẹn", key=f"chot_{ma_ca}"):
                                    ca['tin_nhan'].append({"nguoi_gui": "Giáo viên", "noi_dung": gv_tra_loi})
                                    ca['trang_thai'] = "Đã chốt lịch hẹn"
                                    luu_du_lieu_len_may()
                                    st.rerun()

        elif menu_gv == "🟢 Lịch sử Ca đã chốt":
            st.subheader(f"🟢 Hồ sơ các ca đã xử lý ({len(ca_xong)})")
            for ma_ca, ca in ca_xong.items():
                hinh_thuc_hien_tai = ca.get('hinh_thuc', '💬 Gián tiếp')
                tn_rut_gon = ca['tin_nhan'][0]['noi_dung'][:50] + "..."
                with st.expander(f"Ca {ma_ca} | Lớp {ca['lop']} | Trạng thái: {ca['trang_thai']} | 📝 {tn_rut_gon}"):
                    with st.container(height=200, border=True):
                        for tn in ca['tin_nhan']:
                            with st.chat_message("user" if tn['nguoi_gui'] == "Học sinh" else "assistant"):
                                st.markdown(f"**{tn['nguoi_gui']}**")
                                st.write(tn['noi_dung'])

        elif menu_gv == "👤 Hồ sơ cá nhân & Cài đặt":
            st.subheader("👤 Thông tin cá nhân & Liên hệ")
            st.info("💡 Thông tin này giúp Ban giám hiệu và Học sinh thuận tiện liên hệ khi cần thiết.")
            user_info = st.session_state['users'][user_id]
            
            c_info1, c_info2 = st.columns(2)
            with c_info1:
                new_name = st.text_input("Họ và tên hiển thị:", value=user_info.get('name', ''))
                new_dob = st.text_input("Ngày tháng năm sinh:", value=user_info.get('dob', ''))
            with c_info2:
                new_phone = st.text_input("Số điện thoại (Zalo):", value=user_info.get('phone', ''))
                new_email = st.text_input("Địa chỉ Email:", value=user_info.get('email', ''))
            
            st.markdown("---")
            st.subheader("🔐 Bảo mật tài khoản")
            new_pw = st.text_input("Mật khẩu mới (Bỏ trống nếu không muốn đổi):", type="password")
            
            if st.button("💾 Lưu tất cả thay đổi", type="primary"):
                st.session_state['users'][user_id]['name'] = new_name
                st.session_state['users'][user_id]['dob'] = new_dob
                st.session_state['users'][user_id]['phone'] = new_phone
                st.session_state['users'][user_id]['email'] = new_email
                if new_pw: st.session_state['users'][user_id]['pass'] = new_pw
                luu_du_lieu_len_may()
                st.success("✅ Đã cập nhật hồ sơ thành công!")

# ==========================================
# 4. KHÔNG GIAN BẢN QUẢN LÝ (ADMIN)
# ==========================================
elif st.session_state['current_view'] == "admin_view":
    if kiem_tra_dang_nhap(role_can_thiet='admin'):
        st.sidebar.markdown("⚙️ **Đang đăng nhập:** Ban Giám Hiệu")
        st.sidebar.markdown("---")
        menu_admin = st.sidebar.radio("🧭 DANH MỤC QUẢN TRỊ", [
            "📊 Thống kê Tổng quan", 
            "👥 Quản lý Nhân sự (Giáo viên)",
            "📥 Xuất Báo cáo Excel",
            "🔐 Cài đặt Mật khẩu Admin"
        ])
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Cập nhật dữ liệu", use_container_width=True):
            tai_du_lieu_tu_may()
            st.rerun()
            
        nut_dang_xuat()
        render_ban_quyen()

        st.title("⚙️ TRUNG TÂM QUẢN TRỊ HỆ THỐNG")
        tong_ca = len(st.session_state['database'])
        ca_khan_cap = len([ca for ca in st.session_state['database'].values() if "Cao" in ca['muc_do_rui_ro']])
        ca_tb = len([ca for ca in st.session_state['database'].values() if "Trung bình" in ca['muc_do_rui_ro']])
        ca_thap = len([ca for ca in st.session_state['database'].values() if "Thấp" in ca['muc_do_rui_ro']])
        ca_cho = tong_ca - ca_khan_cap - ca_tb - ca_thap 
        danh_sach_tai_khoan_gv = [k for k, v in st.session_state['users'].items() if v['role'] == 'teacher']

        if menu_admin == "📊 Thống kê Tổng quan":
            c_a, c_b, c_c = st.columns(3)
            c_a.metric("Tổng số ca tiếp nhận", f"{tong_ca} ca")
            c_b.metric("Ca Khẩn cấp (Rủi ro Cao)", f"{ca_khan_cap} ca", delta="Báo động đỏ", delta_color="inverse")
            c_c.metric("Nhân sự Tư vấn", f"{len(danh_sach_tai_khoan_gv)} GV")
            
            if tong_ca > 0:
                st.markdown("---")
                st.markdown("**Biểu đồ Phân bổ Mức độ Rủi ro Tâm lý:**")
                chart_data = pd.DataFrame({
                    "Mức độ": ["Cao (Khẩn cấp)", "Trung bình", "Thấp", "Chưa phân tích"],
                    "Số lượng": [ca_khan_cap, ca_tb, ca_thap, ca_cho]
                })
                st.bar_chart(chart_data.set_index("Mức độ"), color="#3B82F6")

        elif menu_admin == "👥 Quản lý Nhân sự (Giáo viên)":
            st.write("👉 **Sửa hồ sơ / Đổi mật khẩu Giáo viên**")
            if danh_sach_tai_khoan_gv:
                gv_can_sua = st.selectbox("Chọn tài khoản để chỉnh sửa:", options=danh_sach_tai_khoan_gv, format_func=lambda x: f"{x} ({st.session_state['users'][x].get('name','')})")
                c_edit1, c_edit2, c_edit3 = st.columns(3)
                ten_moi = c_edit1.text_input("Tên hiển thị mới:", value=st.session_state['users'][gv_can_sua].get('name',''))
                pass_moi = c_edit2.text_input("Cấp lại mật khẩu mới:", value=st.session_state['users'][gv_can_sua]['pass'])
                c_btn1, c_btn2 = c_edit3.columns(2)
                if c_btn1.button("💾 Lưu Sửa đổi", type="primary"):
                    st.session_state['users'][gv_can_sua]['name'] = ten_moi
                    st.session_state['users'][gv_can_sua]['pass'] = pass_moi
                    luu_du_lieu_len_may()
                    st.success(f"Đã cập nhật {gv_can_sua}!")
                    st.rerun()
                if c_btn2.button("🗑️ Xóa GV này"):
                    del st.session_state['users'][gv_can_sua]
                    luu_du_lieu_len_may()
                    st.rerun()

            st.markdown("---")
            st.write("👉 **Tạo tài khoản Giáo viên mới:**")
            c_add1, c_add2, c_add3 = st.columns(3)
            new_id = c_add1.text_input("Tên đăng nhập (VD: gv06)")
            new_name = c_add2.text_input("Tên hiển thị (VD: Cô Ngọc)")
            new_pass = c_add3.text_input("Mật khẩu")
            if st.button("➕ Tạo tài khoản"):
                if new_id and new_name and new_pass:
                    st.session_state['users'][new_id] = {'pass': new_pass, 'role': 'teacher', 'name': new_name, 'dob': '', 'phone': '', 'email': ''}
                    luu_du_lieu_len_may()
                    st.success("Tạo thành công!")
                    st.rerun()

        elif menu_admin == "📥 Xuất Báo cáo Excel":
            if tong_ca > 0:
                st.info("Mẫu báo cáo chuẩn hóa để in nộp phòng Giáo vụ.")
                du_lieu_xuat = []
                for ma_ca, ca in st.session_state['database'].items():
                    lich_su_chat = " | ".join([f"{t['nguoi_gui']}: {t['noi_dung']}" for t in ca['tin_nhan']])
                    du_lieu_xuat.append({
                        "Mã Hồ Sơ": ma_ca, "Thời gian": ca['thoi_gian'], "Lớp": ca['lop'],
                        "Cảm xúc": ca.get('cam_xuc_ban_dau', 'N/A'),
                        "Hình thức": ca.get('hinh_thuc', 'Gián tiếp'),
                        "GV Phụ trách": st.session_state['users'][ca['gv_phu_trach']].get('name',''),
                        "Rủi ro (AI)": ca['muc_do_rui_ro'], "Kết quả xử lý": ca['trang_thai'],
                        "Nhật ký Chat": lich_su_chat
                    })
                df_export = pd.DataFrame(du_lieu_xuat)
                csv = df_export.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Tải File CSV Báo cáo", data=csv, file_name="Bao_Cao_Tam_Ly.csv", mime="text/csv", type="primary")
            else: st.warning("Chưa có dữ liệu để xuất!")
            
            st.markdown("---")
            st.error("🗑️ Dọn dẹp Hệ thống (Xóa hồ sơ cũ)")
            danh_sach_ca = list(st.session_state['database'].keys())
            if danh_sach_ca:
                ca_can_xoa = st.selectbox("Chọn ca cần xóa:", options=danh_sach_ca, format_func=lambda x: f"{x} - Lớp: {st.session_state['database'][x]['lop']}")
                if st.button("🚨 Xóa vĩnh viễn"):
                    del st.session_state['database'][ca_can_xoa]
                    luu_du_lieu_len_may()
                    st.success("Đã xóa!")
                    st.rerun()

        elif menu_admin == "🔐 Cài đặt Mật khẩu Admin":
            st.subheader("🔐 Thay đổi mật khẩu quản trị")
            admin_new_pass = st.text_input("Nhập mật khẩu Admin mới:", type="password")
            if st.button("🔑 Cập nhật mật khẩu", type="primary"):
                if admin_new_pass:
                    st.session_state['users'][st.session_state['current_user']]['pass'] = admin_new_pass
                    luu_du_lieu_len_may()
                    st.success("Đổi mật khẩu thành công!")