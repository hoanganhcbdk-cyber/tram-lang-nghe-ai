import streamlit as st
import datetime
import random
import pandas as pd
import requests
import base64

# ==========================================
# CẤU HÌNH HỆ THỐNG & CSS TÙY CHỈNH
# ==========================================
st.set_page_config(page_title="Hệ thống Quản trị Tâm lý Học đường AI", page_icon="🏫", layout="wide", initial_sidebar_state="expanded")

# CSS để biến nút bấm thành thẻ Chat (Căn lề trái giống Zalo)
st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px !important;
        height: auto !important;
        white-space: pre-wrap !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

try:
    if "API_KEYS" in st.secrets:
        danh_sach_keys = [k.strip() for k in st.secrets["API_KEYS"].split(",") if k.strip()]
    elif "API_KEY" in st.secrets:
        danh_sach_keys = [st.secrets["API_KEY"].strip()]
    else:
        st.error("❌ Chưa cấu hình API Key!")
        st.stop()
except: pass

MA_BAO_MAT_TRUONG = "123456" 

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
    du_lieu_dong_bo = {
        'users': st.session_state['users'], 
        'database': st.session_state['database'], 
        'config': st.session_state['config'],
        'licenses': st.session_state.get('licenses', {})
    }
    try: requests.put(f"{FIREBASE_URL}/he_thong.json", json=du_lieu_dong_bo)
    except: pass

# ==========================================
# KHỞI TẠO STATE & ĐỒNG BỘ 
# ==========================================
if 'current_view' not in st.session_state: st.session_state['current_view'] = "landing_page"
if 'current_user' not in st.session_state: st.session_state['current_user'] = None
if 'active_chat' not in st.session_state: st.session_state['active_chat'] = None # Biến lưu Ca đang chọn

if 'he_thong_da_khoi_dong' not in st.session_state:
    st.session_state['users'] = {
        'hoanganh_dev': {'pass': 'admin9999', 'role': 'admin', 'name': 'Nhà Phát Triển', 'avatar': ''}, 
        'admin': {'pass': 'admin123', 'role': 'admin', 'name': 'Ban Giám Hiệu'},
        'gv01': {'pass': '1111', 'role': 'teacher', 'name': 'Thầy Lý Hoàng Anh', 'avatar': ''}
    }
    st.session_state['database'] = {}
    st.session_state['config'] = {'active_key': 'FREE-1YEAR'} 
    st.session_state['licenses'] = {
        'FREE-1YEAR': {'school_name': 'Miễn phí 1 Năm Đầu', 'expiry_date': (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y'), 'active': True}
    }
    st.session_state['he_thong_da_khoi_dong'] = True

du_lieu_dam_may = tai_du_lieu_tu_may()
if du_lieu_dam_may:
    st.session_state['database'] = du_lieu_dam_may.get('database', {})
    if 'licenses' not in du_lieu_dam_may:
        st.session_state['config'] = {'active_key': 'FREE-1YEAR'}
        st.session_state['licenses'] = {'FREE-1YEAR': {'school_name': 'Bản quyền 1 Năm Đầu', 'expiry_date': (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y'), 'active': True}}
        luu_du_lieu_len_may()
    else:
        st.session_state['config'] = du_lieu_dam_may.get('config', st.session_state.get('config'))
        st.session_state['licenses'] = du_lieu_dam_may.get('licenses', st.session_state.get('licenses'))
        
    for k, v in du_lieu_dam_may.get('users', {}).items():
        if k in st.session_state['users']: st.session_state['users'][k].update(v)
        else: st.session_state['users'][k] = v
else:
    luu_du_lieu_len_may()

danh_sach_gv = {k: v['name'] for k, v in st.session_state['users'].items() if v['role'] == 'teacher'}

def kiem_tra_ban_quyen_mem():
    active_key = st.session_state['config'].get('active_key', '')
    licenses = st.session_state.get('licenses', {})
    if st.session_state.get('current_user') == 'hoanganh_dev': return True 
    if active_key not in licenses or not licenses[active_key]['active']: return False
    try:
        if datetime.datetime.now() > datetime.datetime.strptime(licenses[active_key]['expiry_date'], '%d/%m/%Y'): return False
    except: return False
    return True

# ==========================================
# GIAO DIỆN ĐĂNG NHẬP 
# ==========================================
def kiem_tra_dang_nhap(role_can_thiet=None):
    if 'token_login' in st.query_params:
        user_luu = st.query_params['token_login']
        if user_luu in st.session_state['users']: st.session_state['current_user'] = user_luu

    if not st.session_state['current_user']:
        st.warning("🔒 Vui lòng đăng nhập để truy cập hệ thống.")
        c1, c2 = st.columns(2)
        with c1:
            u = st.text_input("Tài khoản đăng nhập", key=f"user_{role_can_thiet}")
            p = st.text_input("Mật khẩu", type="password", key=f"pass_{role_can_thiet}")
            if st.button("🔑 Đăng nhập hệ thống", type="primary", key=f"login_btn_{role_can_thiet}"):
                if u in st.session_state['users'] and st.session_state['users'][u]['pass'] == p:
                    st.session_state['current_user'] = u
                    st.query_params['token_login'] = u
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
    if st.sidebar.button("🚪 Đăng xuất / Trở về", use_container_width=True):
        st.session_state['current_user'] = None
        st.session_state['active_chat'] = None
        st.session_state['current_view'] = "landing_page"
        if 'token_login' in st.query_params: del st.query_params['token_login']
        st.rerun()

def render_ban_quyen():
    st.sidebar.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.caption("🔰 **BẢN QUYỀN SÁNG CHẾ**\n\n👨‍💻 Tác giả: Lý Hoàng Anh\n📞 Zalo: 0969969189\n📧 hoanganhcbdk@gmail.com")

# ==========================================
# 1. TRANG CHỦ (LANDING PAGE) 
# ==========================================
if st.session_state['current_view'] == "landing_page":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-weight: 800;'>🏫 HỆ THỐNG QUẢN TRỊ TÂM LÝ HỌC ĐƯỜNG AI</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #4B5563; margin-bottom: 50px;'>Nền tảng Lắng nghe, Chia sẻ và Phân tích Rủi ro Tâm lý Chuyên sâu</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 🎓 Cổng Học Sinh\nNơi các em chia sẻ khó khăn, ẩn danh và an toàn tuyệt đối.")
        if st.button("Học Sinh Truy Cập ➡️", use_container_width=True):
            st.session_state['current_view'] = "student_view"
            st.rerun()
    with col2:
        st.success("### 👨‍🏫 Cổng Giáo Viên\nQuản lý hồ sơ tâm lý và nhận gợi ý tư vấn từ Trí tuệ Nhân tạo AI.")
        if st.button("Giáo Viên Truy Cập ➡️", use_container_width=True):
            st.session_state['current_view'] = "teacher_view"
            st.rerun()
    with col3:
        st.warning("### ⚙️ Cổng Ban Giám Hiệu\nThống kê dữ liệu, xuất báo cáo và Quản lý hệ thống toàn trường.")
        if st.button("BGH Truy Cập ➡️", use_container_width=True):
            st.session_state['current_view'] = "admin_view"
            st.rerun()
            
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.caption("<div style='text-align: center;'>Phần mềm được phát triển bởi: Lý Hoàng Anh | SĐT: 0969969189</div>", unsafe_allow_html=True)

# ==========================================
# 2. KHÔNG GIAN HỌC SINH 
# ==========================================
elif st.session_state['current_view'] == "student_view":
    if st.sidebar.button("⬅️ Quay lại Trang chủ", use_container_width=True):
        st.session_state['current_view'] = "landing_page"
        st.rerun()
    render_ban_quyen()
        
    st.title("🎓 CỔNG KẾT NỐI TÂM LÝ HỌC SINH")
    
    tab_gui, tab_xem = st.tabs(["📝 Gửi Lời Tâm Sự Mới", "💬 Phòng Chat Của Em"])
    with tab_gui:
        ma_xac_thuc = st.text_input("🔑 Nhập Mã bảo mật của trường (Hỏi GVCN nếu em không biết):", type="password")
        hs_khoi_lop = st.text_input("Khối/Lớp của em (Không bắt buộc):")
        hs_cam_xuc = st.selectbox("Ngay lúc này, em đang cảm thấy thế nào?", 
                                  ["😐 Bình thường", "😔 Hơi buồn, suy tư", "😰 Căng thẳng, áp lực thi cử", "😡 Tức giận, uất ức", "😨 Sợ hãi, lo âu", "😭 Tuyệt vọng, cần giúp đỡ gấp"])
        
        gv_duoc_chon = st.selectbox("Em muốn tâm sự với thầy cô nào?", options=list(danh_sach_gv.keys()), format_func=lambda x: danh_sach_gv[x])
        
        st.markdown("---")
        hinh_thuc_tv = st.radio("Em muốn thầy cô hỗ trợ theo hình thức nào?", ["💬 Tư vấn Gián tiếp (Nhắn tin ẩn danh trên web)", "🤝 Tư vấn Trực tiếp (Hẹn gặp mặt tại phòng Tâm lý)"])
        
        ngay_hen, gio_hen = "", ""
        if "Trực tiếp" in hinh_thuc_tv:
            c_ngay, c_gio = st.columns(2)
            ngay_hen = c_ngay.date_input("Chọn ngày hẹn:")
            gio_hen = c_gio.time_input("Chọn giờ hẹn:")
            
        tam_su_input = st.text_area("Hãy kể chi tiết câu chuyện của em để thầy cô hiểu rõ hơn nhé:", height=120)
        
        if st.button("🚀 Gửi đi an toàn", type="primary"):
            if not ma_xac_thuc or ma_xac_thuc.upper() != MA_BAO_MAT_TRUONG:
                st.error("❌ Sai Mã bảo mật của trường! Vui lòng nhập đúng để gửi tin.")
            elif tam_su_input:
                ma_bi_mat = f"HS-{random.randint(1000, 9999)}"
                chuoi_lich_hen = f"{ngay_hen.strftime('%d/%m/%Y')} lúc {gio_hen.strftime('%H:%M')}" if "Trực tiếp" in hinh_thuc_tv else "Không có"
                
                st.session_state['database'][ma_bi_mat] = {
                    "thoi_gian": datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
                    "lop": hs_khoi_lop if hs_khoi_lop else "Ẩn danh",
                    "cam_xuc_ban_dau": hs_cam_xuc,
                    "gv_phu_trach": gv_duoc_chon,
                    "hinh_thuc": hinh_thuc_tv,
                    "lich_hen": chuoi_lich_hen,
                    "tin_nhan": [{"nguoi_gui": "Học sinh", "noi_dung": tam_su_input, "thoi_gian": datetime.datetime.now().strftime('%H:%M')}],
                    "ai_phan_tich": None,
                    "muc_do_rui_ro": "Chờ AI phân tích",
                    "trang_thai": "Chờ xử lý"
                }
                luu_du_lieu_len_may()
                st.success(f"✅ Gửi thành công! Mã bí mật để em xem lại tin nhắn là: **{ma_bi_mat}**")
                st.balloons() 
            else: st.warning("Em hãy viết nội dung trước khi gửi.")

    with tab_xem:
        if HAS_AUTOREFRESH: st_autorefresh(interval=6000, limit=None, key="hs_refresh") 
        
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
                        tg = tn.get('thoi_gian', '')
                        st.markdown(f"**{tn['nguoi_gui']}** <span style='font-size:0.8em; color:gray;'>{tg}</span>", unsafe_allow_html=True)
                        st.write(tn['noi_dung'])
            
            if ca['trang_thai'] != "Đã đóng ca":
                # Ô CHAT NHƯ ZALO DÀNH CHO HỌC SINH
                hs_phan_hoi = st.chat_input("Nhập tin nhắn gửi thầy cô...")
                if hs_phan_hoi:
                    ca['tin_nhan'].append({"nguoi_gui": "Học sinh", "noi_dung": hs_phan_hoi, "thoi_gian": datetime.datetime.now().strftime('%H:%M')})
                    ca['trang_thai'] = "HS vừa nhắn lại" 
                    ca['ai_phan_tich'] = None 
                    luu_du_lieu_len_may()
                    st.rerun()
            else:
                st.info("🔒 Hồ sơ tư vấn này đã được thầy cô đóng lại.")

# ==========================================
# 3. KHÔNG GIAN GIÁO VIÊN (GIAO DIỆN 3 CỘT ZALO)
# ==========================================
elif st.session_state['current_view'] == "teacher_view":
    if kiem_tra_dang_nhap(role_can_thiet='teacher'):
        user_id = st.session_state['current_user']
        user_info = st.session_state['users'][user_id]
        phan_mem_hoat_dong = kiem_tra_ban_quyen_mem()
        
        # --- CỘT 1: THANH SIDEBAR MENU ---
        if user_info.get('avatar'):
            st.sidebar.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{user_info["avatar"]}" width="80" style="border-radius: 50%;"></div>', unsafe_allow_html=True)
        st.sidebar.markdown(f"<div style='text-align:center;'><b>👨‍🏫 {user_info.get('name', 'Giáo viên')}</b></div>", unsafe_allow_html=True)
        st.sidebar.markdown("---")
        
        menu_gv = st.sidebar.radio("🧭 MENU LÀM VIỆC", [
            "💬 Chat & Tư vấn (Đang mở)", 
            "📦 Lịch sử Ca đã đóng", 
            "👤 Hồ sơ cá nhân"
        ])
        
        if menu_gv == "💬 Chat & Tư vấn (Đang mở)" and HAS_AUTOREFRESH:
            st_autorefresh(interval=6000, limit=None, key="gv_refresh") 
                
        nut_dang_xuat()
        render_ban_quyen()

        st.title("👨‍🏫 KHÔNG GIAN LÀM VIỆC GIÁO VIÊN")
        
        ca_cua_toi = {k: v for k, v in st.session_state['database'].items() if v['gv_phu_trach'] == user_id}
        ca_dang_mo = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] not in ["Đã đóng ca"]}
        ca_da_dong = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] == "Đã đóng ca"}

        # GIAO DIỆN ZALO CHAT (CỘT 2 & CỘT 3)
        if menu_gv == "💬 Chat & Tư vấn (Đang mở)":
            if not phan_mem_hoat_dong:
                st.error("⛔ PHẦN MỀM ĐÃ HẾT HẠN BẢN QUYỀN. TÍNH NĂNG AI VÀ CHAT BỊ KHÓA.")
            
            # CHIA MÀN HÌNH THÀNH 2 CỘT CHÍNH 
            col_danh_sach, col_chat = st.columns([1.5, 3.5], gap="large")
            
            # --- CỘT 2: DANH SÁCH CA ĐANG MỞ ---
            with col_danh_sach:
                st.markdown("#### 📥 Hộp thư")
                if not ca_dang_mo:
                    st.info("Hộp thư trống.")
                else:
                    # Sắp xếp: Ca có tin mới lên đầu, sau đó theo ID
                    danh_sach_ca_sap_xep = sorted(ca_dang_mo.items(), key=lambda x: (0 if x[1]['trang_thai']=="HS vừa nhắn lại" else 1, x[0]), reverse=False)
                    
                    with st.container(height=600, border=True):
                        for ma_ca, ca in danh_sach_ca_sap_xep:
                            thoi_gian_ca = ca['tin_nhan'][-1].get('thoi_gian', ca.get('thoi_gian', ''))[-5:] # Lấy giờ phút cuối
                            
                            # Nhận diện trạng thái
                            if ca['trang_thai'] == "HS vừa nhắn lại": icon_tt = "🔴 [MỚI]"
                            elif ca['trang_thai'] == "Chờ xử lý": icon_tt = "🟡 [LẦN ĐẦU]"
                            else: icon_tt = "🟢"
                                
                            tn_cuoi = ca['tin_nhan'][-1]['noi_dung']
                            tn_rut_gon = tn_cuoi[:30] + "..." if len(tn_cuoi) > 30 else tn_cuoi
                            
                            label_nut = f"{icon_tt} {ma_ca} - Lớp {ca['lop']}\n🕒 {thoi_gian_ca} | 💬 {tn_rut_gon}"
                            
                            # BẤM LÀ MỞ NGAY
                            if st.button(label_nut, key=f"btn_{ma_ca}", use_container_width=True):
                                st.session_state['active_chat'] = ma_ca
                                st.rerun()

            # --- CỘT 3: KHÔNG GIAN CHAT & AI PHÂN TÍCH ---
            with col_chat:
                ma_dang_chon = st.session_state.get('active_chat')
                
                if not ma_dang_chon or ma_dang_chon not in ca_dang_mo:
                    st.info("👈 Bấm vào một ca bất kỳ ở cột bên trái để bắt đầu trò chuyện.")
                else:
                    ca_hien_tai = ca_dang_mo[ma_dang_chon]
                    
                    # Thanh Header của Chat
                    c_head1, c_head2 = st.columns([3, 1])
                    c_head1.subheader(f"🗣️ {ma_dang_chon} - Lớp {ca_hien_tai['lop']}")
                    if c_head2.button("📦 Đóng ca", use_container_width=True):
                        ca_hien_tai['trang_thai'] = "Đã đóng ca"
                        st.session_state['active_chat'] = None
                        luu_du_lieu_len_may()
                        st.rerun()
                        
                    if "Trực tiếp" in ca_hien_tai.get('hinh_thuc', ''):
                        st.error(f"⏰ **Học sinh yêu cầu hẹn gặp mặt lúc:** {ca_hien_tai.get('lich_hen', '')}")
                    
                    # VÙNG LỊCH SỬ CHAT
                    with st.container(height=350, border=True):
                        for tn in ca_hien_tai['tin_nhan']:
                            with st.chat_message("user" if tn['nguoi_gui'] == "Học sinh" else "assistant"):
                                tg = tn.get('thoi_gian', '')
                                st.markdown(f"**{tn['nguoi_gui']}** <span style='font-size:0.8em; color:gray;'>{tg}</span>", unsafe_allow_html=True)
                                st.write(tn['noi_dung'])
                                
                    # VÙNG PHÂN TÍCH AI (GỌN GÀNG DƯỚI LỊCH SỬ CHAT)
                    if phan_mem_hoat_dong:
                        if st.button("🧠 AI Phân tích cụm tin nhắn mới nhất", type="secondary", use_container_width=True):
                            with st.spinner("AI đang đọc toàn bộ câu chuyện và tập trung phân tích phản hồi mới..."):
                                # GỘP TẤT CẢ TIN NHẮN HS LIÊN TIẾP THÀNH 1 CỤM TÌNH HUỐNG MỚI
                                tin_nhan_moi_lien_tiep = []
                                for t in reversed(ca_hien_tai['tin_nhan']):
                                    if t['nguoi_gui'] == "Học sinh": tin_nhan_moi_lien_tiep.insert(0, t['noi_dung'])
                                    else: break 
                                cum_tin_nhan_moi = "\n".join(tin_nhan_moi_lien_tiep)
                                
                                lich_su_cu_len = len(ca_hien_tai['tin_nhan']) - len(tin_nhan_moi_lien_tiep)
                                lich_su_cu = ""
                                if lich_su_cu_len > 0:
                                    for t in ca_hien_tai['tin_nhan'][:lich_su_cu_len]:
                                        lich_su_cu += f"{t['nguoi_gui']}: {t['noi_dung']}\n"
                                
                                # PROMPT KỶ LUẬT SẮT
                                prompt = f"""Bạn là Chuyên gia Tâm lý Học đường.
                                [THÔNG TIN BỐI CẢNH CŨ]:
                                {lich_su_cu if lich_su_cu else 'Không có.'}
                                
                                [NHIỆM VỤ BẮT BUỘC KHÔNG THỎA HIỆP]:
                                Học sinh vừa nhắn LIÊN TỤC (các) tin nhắn mới như sau:
                                "{cum_tin_nhan_moi}"
                                
                                1. CHỈ PHÂN TÍCH THÁI ĐỘ TRONG CỤM TIN NHẮN MỚI NÀY. KHÔNG phân tích lại vấn đề cũ.
                                2. Nếu tin nhắn mới là: cảm ơn, vâng dạ, đã hiểu, ổn hơn -> BẮT BUỘC RỦI RO: Thấp.
                                
                                Trả lời:
                                [RỦI RO TÂM LÝ]: Thấp/Trung bình/Cao
                                [1. PHÂN TÍCH NHANH CẢM XÚC HIỆN TẠI]: ...
                                [2. GỢI Ý TRẢ LỜI]: ..."""
                                
                                try:
                                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                                    headers = {'Content-Type': 'application/json'}
                                    thanh_cong = False
                                    keys_luot_nay = danh_sach_keys.copy()
                                    random.shuffle(keys_luot_nay)
                                    for key_hien_tai in keys_luot_nay:
                                        res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key_hien_tai}", json=payload, headers=headers)
                                        if res.status_code == 200:
                                            ca_hien_tai['ai_phan_tich'] = res.json()['candidates'][0]['content']['parts'][0]['text']
                                            if "Cao" in ca_hien_tai['ai_phan_tich'][:80]: ca_hien_tai['muc_do_rui_ro'] = "Cao (Khẩn cấp)"
                                            elif "Trung bình" in ca_hien_tai['ai_phan_tich'][:80]: ca_hien_tai['muc_do_rui_ro'] = "Trung bình"
                                            else: ca_hien_tai['muc_do_rui_ro'] = "Thấp"
                                            thanh_cong = True
                                            break  
                                    if not thanh_cong: ca_hien_tai['ai_phan_tich'] = "⏳ HỆ THỐNG ĐANG QUÁ TẢI."
                                    luu_du_lieu_len_may()
                                    st.rerun()
                                except Exception as e: st.error(f"Lỗi: {e}")
                                
                        if ca_hien_tai.get('ai_phan_tich'):
                            st.info(ca_hien_tai['ai_phan_tich'])
                            
                        # KHUNG NHẬP CHAT BÁM ĐÁY (ZALO STYLE)
                        gv_tra_loi = st.chat_input("Nhập tin nhắn gửi học sinh (Ấn Enter để gửi)...")
                        if gv_tra_loi:
                            ca_hien_tai['tin_nhan'].append({"nguoi_gui": "Giáo viên", "noi_dung": gv_tra_loi, "thoi_gian": datetime.datetime.now().strftime('%H:%M')})
                            ca_hien_tai['trang_thai'] = "GV đã phản hồi"
                            luu_du_lieu_len_may()
                            st.rerun()

        elif menu_gv == "📦 Lịch sử Ca đã đóng":
            st.subheader(f"📦 Hồ sơ các ca đã đóng ({len(ca_da_dong)})")
            for ma_ca, ca in ca_da_dong.items():
                tn_goc = ca['tin_nhan'][0]['noi_dung'][:50] + "..." 
                with st.expander(f"Ca {ma_ca} | Lớp {ca['lop']} | Gốc: {tn_goc}", expanded=False):
                    with st.container(height=250, border=True):
                        for tn in ca['tin_nhan']:
                            with st.chat_message("user" if tn['nguoi_gui'] == "Học sinh" else "assistant"):
                                st.write(tn['noi_dung'])

        elif menu_gv == "👤 Hồ sơ cá nhân":
            st.subheader("👤 Cập nhật Hồ sơ & Ảnh Đại Diện")
            c_img, c_info = st.columns([1, 2])
            with c_img:
                if user_info.get('avatar'): st.markdown(f'<img src="data:image/png;base64,{user_info["avatar"]}" width="150" style="border-radius: 10px;">', unsafe_allow_html=True)
                file_anh = st.file_uploader("Tải ảnh mới (JPG, PNG)", type=['png', 'jpg', 'jpeg'])
            with c_info:
                new_name = st.text_input("Họ và tên hiển thị:", value=user_info.get('name', ''))
                new_phone = st.text_input("Số điện thoại (Zalo):", value=user_info.get('phone', ''))
                new_email = st.text_input("Địa chỉ Email:", value=user_info.get('email', ''))
                new_pw = st.text_input("Mật khẩu mới (Bỏ trống nếu không đổi):", type="password")
            
            if st.button("💾 Lưu thay đổi", type="primary"):
                st.session_state['users'][user_id]['name'] = new_name
                st.session_state['users'][user_id]['phone'] = new_phone
                st.session_state['users'][user_id]['email'] = new_email
                if new_pw: st.session_state['users'][user_id]['pass'] = new_pw
                if file_anh is not None:
                    st.session_state['users'][user_id]['avatar'] = base64.b64encode(file_anh.read()).decode('utf-8')
                luu_du_lieu_len_may()
                st.success("✅ Đã cập nhật thành công!")
                st.rerun()

# ==========================================
# 4. KHÔNG GIAN BẢN QUẢN LÝ (ADMIN)
# ==========================================
elif st.session_state['current_view'] == "admin_view":
    if kiem_tra_dang_nhap(role_can_thiet='admin'):
        user_hien_tai = st.session_state['current_user']
        phan_mem_hoat_dong = kiem_tra_ban_quyen_mem()
        
        st.sidebar.markdown(f"⚙️ **Đang đăng nhập:** {st.session_state['users'][user_hien_tai]['name']}")
        st.sidebar.markdown("---")
        
        danh_muc_admin = ["📊 Thống kê Tổng quan", "👥 Quản lý Nhân sự", "📥 Xuất Báo cáo Excel", "🔐 Đổi Mật khẩu Admin"]
        
        if user_hien_tai == "admin": danh_muc_admin.append("🔑 Quản lý Bản Quyền")
        if user_hien_tai == "hoanganh_dev": danh_muc_admin.append("🛠️ NHÀ PHÁT TRIỂN: Cấp Key")
            
        menu_admin = st.sidebar.radio("🧭 DANH MỤC QUẢN TRỊ", danh_muc_admin)
        if HAS_AUTOREFRESH: st_autorefresh(interval=10000, limit=None, key="admin_refresh")
        nut_dang_xuat()
        render_ban_quyen()

        st.title("⚙️ TRUNG TÂM QUẢN TRỊ HỆ THỐNG")
        
        if not phan_mem_hoat_dong and user_hien_tai != "hoanganh_dev":
            st.error("⛔ PHẦN MỀM CHƯA KÍCH HOẠT HOẶC ĐÃ HẾT HẠN.")
            st.warning("Vui lòng vào mục **🔑 Quản lý Bản Quyền** ở menu bên trái để nhập mã.")
            st.markdown("---")
            
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
                chart_data = pd.DataFrame({"Mức độ": ["Cao", "Trung bình", "Thấp", "Chưa phân tích"], "Số lượng": [ca_khan_cap, ca_tb, ca_thap, ca_cho]})
                st.bar_chart(chart_data.set_index("Mức độ"), color="#3B82F6")

        elif menu_admin == "👥 Quản lý Nhân sự":
            st.write("👉 **Sửa hồ sơ / Đổi mật khẩu Giáo viên**")
            if danh_sach_tai_khoan_gv:
                gv_can_sua = st.selectbox("Chọn tài khoản:", options=danh_sach_tai_khoan_gv, format_func=lambda x: f"{x} ({st.session_state['users'][x].get('name','')})")
                c_edit1, c_edit2, c_edit3 = st.columns(3)
                ten_moi = c_edit1.text_input("Tên hiển thị mới:", value=st.session_state['users'][gv_can_sua].get('name',''))
                pass_moi = c_edit2.text_input("Mật khẩu mới:", value=st.session_state['users'][gv_can_sua]['pass'])
                c_btn1, c_btn2 = c_edit3.columns(2)
                if c_btn1.button("💾 Lưu Sửa đổi", type="primary"):
                    st.session_state['users'][gv_can_sua]['name'] = ten_moi
                    st.session_state['users'][gv_can_sua]['pass'] = pass_moi
                    luu_du_lieu_len_may()
                    st.rerun()
                if c_btn2.button("🗑️ Xóa GV này"):
                    del st.session_state['users'][gv_can_sua]
                    luu_du_lieu_len_may()
                    st.rerun()
            st.write("👉 **Tạo tài khoản Giáo viên mới:**")
            c_add1, c_add2, c_add3 = st.columns(3)
            new_id = c_add1.text_input("Tên đăng nhập (VD: gv06)")
            new_name = c_add2.text_input("Tên hiển thị (VD: Cô Ngọc)")
            new_pass = c_add3.text_input("Mật khẩu")
            if st.button("➕ Tạo tài khoản"):
                if new_id and new_name and new_pass:
                    st.session_state['users'][new_id] = {'pass': new_pass, 'role': 'teacher', 'name': new_name, 'avatar': '', 'phone': '', 'email': ''}
                    luu_du_lieu_len_may()
                    st.rerun()

        elif menu_admin == "📥 Xuất Báo cáo Excel":
            if tong_ca > 0:
                du_lieu_xuat = []
                for ma_ca, ca in st.session_state['database'].items():
                    du_lieu_xuat.append({
                        "Mã Hồ Sơ": ma_ca, "Thời gian": ca['thoi_gian'], "Lớp": ca['lop'],
                        "Cảm xúc": ca.get('cam_xuc_ban_dau', 'N/A'), "Hình thức": ca.get('hinh_thuc', 'Gián tiếp'),
                        "GV Phụ trách": st.session_state['users'][ca['gv_phu_trach']].get('name',''),
                        "Rủi ro (AI)": ca['muc_do_rui_ro'], "Kết quả xử lý": ca['trang_thai'],
                    })
                df_export = pd.DataFrame(du_lieu_xuat)
                csv = df_export.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Tải File CSV Báo cáo", data=csv, file_name="Bao_Cao_Tam_Ly.csv", mime="text/csv", type="primary")

        elif menu_admin == "🔐 Đổi Mật khẩu Admin":
            admin_new_pass = st.text_input("Nhập mật khẩu Admin mới:", type="password")
            if st.button("🔑 Cập nhật mật khẩu", type="primary"):
                st.session_state['users'][user_hien_tai]['pass'] = admin_new_pass
                luu_du_lieu_len_may()
                st.success("Đổi mật khẩu thành công!")

        elif menu_admin == "🔑 Quản lý Bản Quyền":
            current_key = st.session_state['config'].get('active_key', '')
            st.write(f"**Mã đang dùng hiện tại:** `{current_key}`")
            new_key = st.text_input("Nhập Mã Bản Quyền mới do Tác giả cấp:")
            if st.button("🚀 Kích hoạt phần mềm", type="primary"):
                if new_key in st.session_state['licenses'] and st.session_state['licenses'][new_key]['active']:
                    st.session_state['config']['active_key'] = new_key
                    luu_du_lieu_len_may()
                    st.success(f"🎉 Chúc mừng! Kích hoạt thành công cho trường: {st.session_state['licenses'][new_key]['school_name']}")
                    st.rerun()
                else: st.error("❌ Mã Bản Quyền không hợp lệ!")

        elif menu_admin == "🛠️ NHÀ PHÁT TRIỂN: Cấp Key":
            st.write("**Danh sách các trường đang sử dụng phần mềm:**")
            for key, data in st.session_state['licenses'].items():
                trang_thai = "🟢 Đang hoạt động" if data['active'] else "🔴 Đã Khóa"
                with st.expander(f"Trường: {data['school_name']} | Mã: {key} | Hết hạn: {data['expiry_date']} | {trang_thai}"):
                    c1, c2, c3 = st.columns(3)
                    if c1.button("Gia hạn 1 Năm", key=f"gh_{key}"):
                        st.session_state['licenses'][key]['expiry_date'] = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y')
                        st.session_state['licenses'][key]['active'] = True
                        luu_du_lieu_len_may()
                        st.rerun()
                    if c2.button("Khóa Key này", key=f"lock_{key}"):
                        st.session_state['licenses'][key]['active'] = False
                        luu_du_lieu_len_may()
                        st.rerun()
            st.markdown("---")
            new_school = st.text_input("Tên trường đối tác:")
            if st.button("➕ Tạo License Key Mới", type="primary"):
                tao_ma_moi = f"KEY-{random.randint(10000, 99999)}"
                st.session_state['licenses'][tao_ma_moi] = {'school_name': new_school, 'expiry_date': (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y'), 'active': True}
                luu_du_lieu_len_may()
                st.rerun()