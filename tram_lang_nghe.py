import streamlit as st
import datetime
import random
import pandas as pd
import requests
import base64

# ==========================================
# 1. LÁ CHẮN BẢO VỆ BỘ NHỚ
# ==========================================
def khoi_tao_he_thong():
    if 'current_view' not in st.session_state: st.session_state['current_view'] = "landing_page"
    if 'current_user' not in st.session_state: st.session_state['current_user'] = None
    if 'active_chat' not in st.session_state: st.session_state['active_chat'] = None 
    if 'menu_gv' not in st.session_state: st.session_state['menu_gv'] = "mo"
    if 'theme_color' not in st.session_state: st.session_state['theme_color'] = "Xanh Mặc Định"
    
    if 'users' not in st.session_state:
        st.session_state['users'] = {
            'hoanganh_dev': {'pass': 'admin9999', 'role': 'admin', 'name': 'Nhà Phát Triển', 'avatar': ''}, 
            'admin': {'pass': 'admin123', 'role': 'admin', 'name': 'Ban Giám Hiệu'},
            'gv01': {'pass': '1111', 'role': 'teacher', 'name': 'Thầy Lý Hoàng Anh', 'avatar': ''}
        }
    if 'database' not in st.session_state: st.session_state['database'] = {}
    if 'config' not in st.session_state: st.session_state['config'] = {'active_key': 'FREE-1YEAR'} 
    if 'licenses' not in st.session_state: 
        st.session_state['licenses'] = {'FREE-1YEAR': {'school_name': 'Miễn phí 1 Năm Đầu', 'expiry_date': (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y'), 'active': True}}

khoi_tao_he_thong()

theme_map = {"Xanh Mặc Định": "#0068ff", "Tím Tinh Tế": "#6366f1", "Xanh Lá Tươi": "#10b981", "Đen Huyền Bí": "#1f2937", "Đỏ Năng Động": "#e53935"}
main_color = theme_map.get(st.session_state.get('theme_color', 'Xanh Mặc Định'), "#0068ff")

# ==========================================
# 2. CẤU HÌNH GIAO DIỆN & CSS (TRONG SUỐT VÀ SẠCH SẼ)
# ==========================================
st.set_page_config(page_title="Trạm Lắng Nghe AI", page_icon="🏫", layout="wide", initial_sidebar_state="collapsed")

st.markdown(f"""
    <style>
    .block-container {{ padding: 0.5rem 1rem !important; max-width: 100% !important; margin-top: -30px !important; }}
    header {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}
    section[data-testid="stSidebar"] {{ display: none !important; }}
    
    .top-title {{ text-align: center; color: {main_color}; font-size: 24px; font-weight: 800; text-transform: uppercase; border-bottom: 2px solid {main_color}; padding-bottom: 5px; margin-bottom: 10px; }}
    
    /* MENU BÊN TRÁI: Trong suốt 100% */
    [data-testid="column"]:nth-of-type(1) {{
        background-color: transparent !important; border-right: 1px solid #e5e7eb; padding-top: 10px;
    }}
    [data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button {{
        background-color: transparent !important; color: #4B5563 !important; border: none !important;
        padding: 10px 5px !important; width: 100% !important; font-size: 15px !important; font-weight: 600 !important;
        text-align: left !important; justify-content: flex-start !important; margin-bottom: 5px !important;
    }}
    [data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button:hover {{ background-color: #F3F4F6 !important; border-radius: 8px !important; color: {main_color} !important; }}
    
    /* HỘP THƯ LÀM VIỆC */
    [data-testid="column"]:nth-of-type(2) div[data-testid="stVerticalBlock"] > div {{ padding: 0 !important; gap: 0 !important; margin-bottom: -15px !important; }}
    .chat-list-btn button {{ width: 100% !important; background-color: white !important; border: 1px solid #eaedf0 !important; border-radius: 8px !important; padding: 12px 10px !important; text-align: left !important; justify-content: flex-start !important; color: #111 !important; margin-bottom: 5px !important; }}
    .chat-list-btn button p {{ margin: 0 !important; line-height: 1.5 !important; font-size: 14px !important; white-space: pre-wrap !important; }}
    .chat-list-btn button:hover {{ background-color: #f3f5f6 !important; border-color: {main_color} !important; }}
    </style>
""", unsafe_allow_html=True)

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError: HAS_AUTOREFRESH = False

try:
    if "API_KEYS" in st.secrets: danh_sach_keys = [k.strip() for k in st.secrets["API_KEYS"].split(",") if k.strip()]
    elif "API_KEY" in st.secrets: danh_sach_keys = [st.secrets["API_KEY"].strip()]
    else: st.stop()
except: pass

FIREBASE_URL = "https://tram-lang-nghe-data-default-rtdb.firebaseio.com"

# ==========================================
# 3. ĐỒNG BỘ DỮ LIỆU ĐÁM MÂY
# ==========================================
def tai_du_lieu_tu_may():
    try:
        r = requests.get(f"{FIREBASE_URL}/he_thong.json", timeout=5)
        if r.status_code == 200 and r.json(): return r.json()
    except: pass
    return None

def luu_du_lieu_len_may():
    du_lieu_dong_bo = {'users': st.session_state['users'], 'database': st.session_state['database'], 'config': st.session_state['config'], 'licenses': st.session_state.get('licenses', {})}
    try: requests.put(f"{FIREBASE_URL}/he_thong.json", json=du_lieu_dong_bo, timeout=5)
    except: pass

du_lieu_dam_may = tai_du_lieu_tu_may()
if du_lieu_dam_may:
    st.session_state['database'] = du_lieu_dam_may.get('database', {})
    st.session_state['config'] = du_lieu_dam_may.get('config', st.session_state.get('config'))
    st.session_state['licenses'] = du_lieu_dam_may.get('licenses', st.session_state.get('licenses'))
    for k, v in du_lieu_dam_may.get('users', {}).items():
        if k in st.session_state['users']: st.session_state['users'][k].update(v)
        else: st.session_state['users'][k] = v
else:
    luu_du_lieu_len_may()

danh_sach_gv = {k: v.get('name', 'GV') for k, v in st.session_state['users'].items() if v.get('role') == 'teacher'}

def kiem_tra_ban_quyen_mem():
    active_key = st.session_state['config'].get('active_key', '')
    licenses = st.session_state.get('licenses', {})
    if st.session_state.get('current_user') == 'hoanganh_dev': return True 
    if active_key not in licenses or not licenses[active_key].get('active', False): return False
    try:
        if datetime.datetime.now() > datetime.datetime.strptime(licenses[active_key]['expiry_date'], '%d/%m/%Y'): return False
    except: return False
    return True

# ==========================================
# 4. GIAO DIỆN ĐĂNG NHẬP
# ==========================================
def kiem_tra_dang_nhap(role_can_thiet=None):
    if 'token_login' in st.query_params:
        user_luu = st.query_params['token_login']
        if user_luu in st.session_state['users']: st.session_state['current_user'] = user_luu

    current_user = st.session_state.get('current_user')
    if not current_user:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.warning("🔒 Vui lòng đăng nhập để truy cập hệ thống.")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            u = st.text_input("Tài khoản đăng nhập", key=f"user_{role_can_thiet}")
            p = st.text_input("Mật khẩu", type="password", key=f"pass_{role_can_thiet}")
            nho_mk = st.checkbox("Ghi nhớ thiết bị này")
            if st.button("🔑 Đăng nhập hệ thống", type="primary", use_container_width=True):
                if u in st.session_state['users'] and st.session_state['users'][u].get('pass') == p:
                    st.session_state['current_user'] = u
                    if nho_mk: st.query_params['token_login'] = u
                    st.rerun()
                else: st.error("❌ Sai thông tin đăng nhập!")
        return False
    else:
        user_info = st.session_state['users'].get(current_user, {})
        if role_can_thiet and user_info.get('role') != role_can_thiet:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.error("🚫 Tài khoản của bạn không có quyền truy cập khu vực này!")
            if st.button("🔄 Bấm vào đây để Thoát và Đăng nhập lại", type="primary"):
                st.session_state['current_user'] = None
                st.query_params.clear() 
                st.rerun()
            return False
        return True

# ==========================================
# ĐIỀU HƯỚNG CHÍNH CỦA ỨNG DỤNG
# ==========================================

# 1. TRANG CHỦ 
if st.session_state.get('current_view') == "landing_page":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='text-align: center; padding: 30px 20px; border-radius: 20px; margin-bottom: 20px;'>
            <h2 style='color: {main_color}; font-weight: 800; margin-top: 0; text-transform: uppercase;'>TRẠM TƯ VẤN HỌC ĐƯỜNG AI</h2>
            <p style='color: #64748b; font-size: 18px; max-width: 600px; margin: 10px auto;'>Nơi an toàn để học sinh chia sẻ cảm xúc, nhận hỗ trợ kịp thời từ Trí tuệ Nhân tạo và Đội ngũ Chuyên gia.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.info("### 🎓 Cổng Học Sinh\nNơi chia sẻ khó khăn, an toàn tuyệt đối.")
        if st.button("Truy Cập Học Sinh ➡️", use_container_width=True):
            st.session_state['current_view'] = "student_view"; st.rerun()
    with col2:
        st.success("### 👨‍🏫 Cổng Giáo Viên\nQuản lý hồ sơ và nhận gợi ý tư vấn từ ChatGPT.")
        if st.button("Truy Cập Giáo Viên ➡️", use_container_width=True):
            st.session_state['current_view'] = "teacher_view"; st.rerun()
    with col3:
        st.warning("### ⚙️ Cổng BGH / Quản Trị\nThống kê, xuất báo cáo và Quản lý hệ thống.")
        if st.button("Truy Cập Ban Giám Hiệu ➡️", use_container_width=True):
            st.session_state['current_view'] = "admin_view"; st.rerun()

# 2. KHÔNG GIAN HỌC SINH
elif st.session_state.get('current_view') == "student_view":
    if st.button("⬅️ Trở về Trang chủ"): st.session_state['current_view'] = "landing_page"; st.rerun()
    st.markdown("<div class='top-title'>TRẠM TƯ VẤN HỌC ĐƯỜNG</div>", unsafe_allow_html=True)
    
    tab_gui, tab_xem = st.tabs(["📝 Gửi Tâm Sự", "💬 Phòng Chat"])
    with tab_gui:
        ma_xac_thuc = st.text_input("🔑 Mã bảo mật của trường (VD: 123456):", type="password")
        hs_khoi_lop = st.text_input("Khối/Lớp của em (Không bắt buộc):")
        hs_cam_xuc = st.selectbox("Cảm xúc hiện tại?", ["😐 Bình thường", "😔 Buồn bã", "😰 Áp lực", "😡 Tức giận", "😨 Sợ hãi", "😭 Tuyệt vọng"])
        gv_duoc_chon = st.selectbox("Chọn Thầy/Cô:", options=list(danh_sach_gv.keys()), format_func=lambda x: danh_sach_gv.get(x, x))
        hinh_thuc_tv = st.radio("Hình thức:", ["💬 Nhắn tin trên web", "🤝 Hẹn gặp trực tiếp"])
        ngay_hen, gio_hen = "", ""
        if "Trực tiếp" in hinh_thuc_tv:
            c_ngay, c_gio = st.columns(2)
            ngay_hen, gio_hen = c_ngay.date_input("Ngày hẹn:"), c_gio.time_input("Giờ hẹn:")
            
        tam_su_input = st.text_area("Kể chi tiết câu chuyện:", height=100)
        if st.button("🚀 Gửi an toàn", type="primary"):
            if not ma_xac_thuc or ma_xac_thuc.upper() != "123456": st.error("❌ Sai Mã bảo mật!")
            elif tam_su_input:
                ma_bi_mat = f"HS-{random.randint(1000, 9999)}"
                st.session_state['database'][ma_bi_mat] = {
                    "thoi_gian": datetime.datetime.now().strftime('%d/%m/%Y %H:%M'), "lop": hs_khoi_lop if hs_khoi_lop else "Ẩn danh",
                    "cam_xuc_ban_dau": hs_cam_xuc, "gv_phu_trach": gv_duoc_chon, "hinh_thuc": hinh_thuc_tv,
                    "lich_hen": f"{ngay_hen.strftime('%d/%m/%Y')} lúc {gio_hen.strftime('%H:%M')}" if "Trực tiếp" in hinh_thuc_tv else "Không",
                    "tin_nhan": [{"nguoi_gui": "Học sinh", "noi_dung": tam_su_input, "thoi_gian": datetime.datetime.now().strftime('%H:%M')}],
                    "ai_phan_tich": None, "muc_do_rui_ro": "Chờ AI phân tích", "trang_thai": "Chờ xử lý"
                }
                luu_du_lieu_len_may()
                st.success(f"✅ Gửi thành công! Mã tra cứu của em là: **{ma_bi_mat}**")
                st.balloons()

    with tab_xem:
        if HAS_AUTOREFRESH: st_autorefresh(interval=6000, limit=None, key="hs_refresh") 
        ma_tra_cuu = st.text_input("Nhập Mã tra cứu:")
        if st.button("Truy cập"): st.session_state['ca_dang_xem'] = ma_tra_cuu.strip()
            
        if 'ca_dang_xem' in st.session_state and st.session_state.get('ca_dang_xem') in st.session_state['database']:
            ca = st.session_state['database'][st.session_state['ca_dang_xem']]
            st.markdown(f"### 💬 Chat với Thầy/Cô")
            with st.container(height=350, border=True):
                for tn in ca['tin_nhan']:
                    with st.chat_message("user" if tn.get('nguoi_gui') == "Học sinh" else "assistant"):
                        st.markdown(f"**{tn.get('nguoi_gui')}** <span style='font-size:0.8em; color:gray;'>{tn.get('thoi_gian', '')}</span>", unsafe_allow_html=True)
                        st.write(tn.get('noi_dung'))
            
            if ca.get('trang_thai') != "Đã đóng ca":
                hs_phan_hoi = st.chat_input("Nhập tin nhắn...")
                if hs_phan_hoi:
                    ca['tin_nhan'].append({"nguoi_gui": "Học sinh", "noi_dung": hs_phan_hoi, "thoi_gian": datetime.datetime.now().strftime('%H:%M')})
                    ca['trang_thai'] = "HS vừa nhắn lại" 
                    ca['ai_phan_tich'] = None 
                    luu_du_lieu_len_may()
                    st.rerun()

# 3. KHÔNG GIAN GIÁO VIÊN
elif st.session_state.get('current_view') == "teacher_view":
    if kiem_tra_dang_nhap(role_can_thiet='teacher'):
        user_id = st.session_state.get('current_user')
        user_info = st.session_state['users'].get(user_id, {})
        phan_mem_hoat_dong = kiem_tra_ban_quyen_mem()
        
        if HAS_AUTOREFRESH: st_autorefresh(interval=6000, limit=None, key="gv_refresh") 
        if 'menu_gv' not in st.session_state: st.session_state['menu_gv'] = "mo"
        
        ca_cua_toi = {k: v for k, v in st.session_state['database'].items() if v.get('gv_phu_trach') == user_id}
        ca_dang_mo = {k: v for k, v in ca_cua_toi.items() if v.get('trang_thai') != "Đã đóng ca"}
        ca_da_dong = {k: v for k, v in ca_cua_toi.items() if v.get('trang_thai') == "Đã đóng ca"}

        st.markdown("<div class='top-title'>TRẠM TƯ VẤN</div>", unsafe_allow_html=True)

        col_menu, col_danh_sach, col_chat = st.columns([1.5, 3.5, 7], gap="small")
        
        with col_menu:
            if user_info.get('avatar'): st.markdown(f'<div style="text-align:center; margin-bottom: 10px;"><img src="data:image/png;base64,{user_info.get("avatar")}" width="60" style="border-radius: 50%;"></div>', unsafe_allow_html=True)
            else: st.markdown(f'<div style="text-align:center; font-size:30px; margin-bottom: 5px;">👨‍🏫</div>', unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center; font-size:14px; font-weight:bold; color:#1f2937; margin-bottom:15px;'>{user_info.get('name', 'Giáo viên')}</div>", unsafe_allow_html=True)
            
            if st.button("💬 Ca đang mở", use_container_width=True): st.session_state['menu_gv'] = "mo"; st.session_state['active_chat'] = None; st.rerun()
            if st.button("📦 Ca đã đóng", use_container_width=True): st.session_state['menu_gv'] = "xong"; st.session_state['active_chat'] = None; st.rerun()
            if st.button("👤 Hồ sơ", use_container_width=True): st.session_state['menu_gv'] = "ho_so"; st.session_state['active_chat'] = None; st.rerun()
            if st.button("🚪 Thoát", use_container_width=True):
                st.session_state['current_user'] = None
                st.session_state['current_view'] = "landing_page"
                st.query_params.clear()
                st.rerun()

        with col_danh_sach:
            if st.session_state.get('menu_gv') == "mo":
                st.markdown(f"<b style='color:#1f2937; font-size:16px; border-bottom:1px solid #eee; padding-bottom:5px; display:block; margin-bottom:10px;'>📥 Hộp thư làm việc</b>", unsafe_allow_html=True)
                if not phan_mem_hoat_dong: st.error("⛔ Hết hạn!")
                
                if not ca_dang_mo: st.info("Hộp thư trống.")
                else:
                    danh_sach_ca_sap_xep = sorted(ca_dang_mo.items(), key=lambda x: (0 if x[1].get('trang_thai')=="HS vừa nhắn lại" else 1, x[0]))
                    with st.container(height=650, border=False):
                        for i, (ma_ca, ca) in enumerate(danh_sach_ca_sap_xep, 1):
                            thoi_gian_ca = ca['tin_nhan'][-1].get('thoi_gian', '')
                            if ca.get('trang_thai') == "HS vừa nhắn lại": icon_tt = "🔴"
                            elif ca.get('trang_thai') == "Chờ xử lý": icon_tt = "🟡"
                            else: icon_tt = "🟢"
                                
                            tn_cuoi = ca['tin_nhan'][-1].get('noi_dung', '')
                            tn_rut_gon = tn_cuoi[:35] + "..." if len(tn_cuoi) > 35 else tn_cuoi
                            
                            st.markdown('<div class="chat-list-btn">', unsafe_allow_html=True)
                            
                            # Text sạch sẽ không có HTML
                            label_nut = f"{icon_tt} {ma_ca} (Lớp {ca.get('lop', '')})\n🕒 {thoi_gian_ca} | 💬 {tn_rut_gon}"
                            
                            btn_type = "primary" if st.session_state.get('active_chat') == ma_ca else "secondary"
                            if st.button(label_nut, key=f"btn_{ma_ca}", type=btn_type):
                                st.session_state['active_chat'] = ma_ca; st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                            
            elif st.session_state.get('menu_gv') == "xong":
                st.markdown(f"<b style='color:#1f2937; font-size:16px; border-bottom:1px solid #eee; padding-bottom:5px; display:block; margin-bottom:10px;'>📦 Đã hoàn thành</b>", unsafe_allow_html=True)
                with st.container(height=650, border=False):
                    for i, (ma_ca, ca) in enumerate(ca_da_dong.items(), 1):
                        st.markdown('<div class="chat-list-btn">', unsafe_allow_html=True)
                        btn_type = "primary" if st.session_state.get('active_chat') == ma_ca else "secondary"
                        if st.button(f"📦 {ma_ca} (Lớp {ca.get('lop', '')})\nĐã đóng hồ sơ", key=f"btn_x_{ma_ca}", type=btn_type):
                            st.session_state['active_chat'] = ma_ca; st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                        
            elif st.session_state.get('menu_gv') == "ho_so":
                st.info("👉 Hãy điền thông tin bên Cột phải.")

        with col_chat:
            if not phan_mem_hoat_dong: st.error("⛔ Hết hạn Bản quyền. Tính năng AI và Chat bị khóa.")
            
            if st.session_state.get('menu_gv') in ["mo", "xong"]:
                ma_dang_chon = st.session_state.get('active_chat')
                
                if not ma_dang_chon or ma_dang_chon not in ca_cua_toi:
                    st.markdown("""<div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; text-align: center; color: #9CA3AF;'>
                        <h2 style='font-size: 50px; margin-bottom:0;'>☕</h2>
                        <h2>Chào ngày mới!</h2><p>Bấm vào một học sinh bên trái để bắt đầu hỗ trợ.</p></div>""", unsafe_allow_html=True)
                else:
                    ca_hien_tai = ca_cua_toi[ma_dang_chon]
                    
                    c_head1, c_head2 = st.columns([4, 1])
                    c_head1.markdown(f"<h4 style='margin-bottom:0; color:{main_color};'>🗣️ {ma_dang_chon} | Lớp {ca_hien_tai.get('lop', '')}</h4>", unsafe_allow_html=True)
                    c_head1.caption(f"**Gốc:** {ca_hien_tai['tin_nhan'][0].get('noi_dung', '')[:80]}...")
                    
                    if ca_hien_tai.get('trang_thai') != "Đã đóng ca":
                        if c_head2.button("🔙 Đóng / Trở lại", use_container_width=True):
                            ca_hien_tai['trang_thai'] = "Đã đóng ca"
                            st.session_state['active_chat'] = None
                            luu_du_lieu_len_may(); st.rerun()
                            
                    st.markdown("<hr style='margin-top:5px; margin-bottom:10px;'>", unsafe_allow_html=True)
                    if "Trực tiếp" in ca_hien_tai.get('hinh_thuc', ''): st.error(f"⏰ **Hẹn gặp trực tiếp lúc:** {ca_hien_tai.get('lich_hen', '')}")
                    
                    with st.container(height=350, border=False):
                        for tn in ca_hien_tai['tin_nhan']:
                            with st.chat_message("user" if tn.get('nguoi_gui') == "Học sinh" else "assistant"):
                                st.markdown(f"**{tn.get('nguoi_gui')}** <span style='font-size:0.8em; color:gray;'>{tn.get('thoi_gian', '')}</span>", unsafe_allow_html=True)
                                st.write(tn.get('noi_dung'))
                                
                    if phan_mem_hoat_dong and ca_hien_tai.get('trang_thai') != "Đã đóng ca":
                        if ca_hien_tai.get('ai_phan_tich'):
                            st.success(f"✨ **AI CỐ VẤN (Bởi ChatGPT):**\n\n{ca_hien_tai['ai_phan_tich']}")
                            if st.button("🗑️ Xóa kết quả phân tích để gọn màn hình"):
                                ca_hien_tai['ai_phan_tich'] = None
                                luu_du_lieu_len_may(); st.rerun()
                                
                        if not ca_hien_tai.get('ai_phan_tich'):
                            if st.button("🧠 Phân tích bằng ChatGPT", type="primary", use_container_width=True):
                                with st.spinner("ChatGPT đang phân tích chuyên sâu..."):
                                    tin_nhan_moi_lien_tiep = []
                                    for t in reversed(ca_hien_tai['tin_nhan']):
                                        if t.get('nguoi_gui') == "Học sinh": tin_nhan_moi_lien_tiep.insert(0, t.get('noi_dung', ''))
                                        else: break 
                                    cum_tin_nhan_moi = "\n".join(tin_nhan_moi_lien_tiep)
                                    
                                    lich_su_cu_len = len(ca_hien_tai['tin_nhan']) - len(tin_nhan_moi_lien_tiep)
                                    lich_su_cu = ""
                                    if lich_su_cu_len > 0:
                                        for t in ca_hien_tai['tin_nhan'][:lich_su_cu_len]: lich_su_cu += f"{t.get('nguoi_gui')}: {t.get('noi_dung')}\n"
                                    
                                    prompt = f"""[BỐI CẢNH CŨ]: {lich_su_cu if lich_su_cu else 'Không.'}
                                    [TIN MỚI LIÊN TIẾP TỪ HỌC SINH]: "{cum_tin_nhan_moi}"
                                    
                                    Nhiệm vụ của bạn:
                                    1. Phân tích thái độ và tâm lý của học sinh trong cụm tin nhắn mới.
                                    2. Đánh giá MỨC ĐỘ RỦI RO tâm lý (Thấp/Trung bình/Cao). Lưu ý: Nếu tin nhắn chỉ là cảm ơn, dạ vâng, đã hiểu thì rủi ro bắt buộc là Thấp.
                                    
                                    Hãy trả lời chính xác theo format sau:
                                    [RỦI RO]: <Mức độ>
                                    [PHÂN TÍCH NHANH]: <Phân tích của bạn>
                                    [GỢI Ý TRẢ LỜI]: <Viết sẵn 1 câu để giáo viên có thể copy gửi cho học sinh>"""
                                    
                                    try:
                                        thanh_cong = False
                                        loi_chi_tiet = ""
                                        keys_luot_nay = danh_sach_keys.copy()
                                        random.shuffle(keys_luot_nay)
                                        
                                        # TÍCH HỢP ĐỘNG CƠ CHATGPT (OPENAI API)
                                        for key_hien_tai in keys_luot_nay:
                                            key_sach = key_hien_tai.strip()
                                            if not key_sach.startswith("sk-"):
                                                loi_chi_tiet = "Lỗi: API Key trong phần Secrets không phải của OpenAI (Key OpenAI phải bắt đầu bằng chữ 'sk-')"
                                                continue
                                                
                                            headers = {
                                                "Content-Type": "application/json",
                                                "Authorization": f"Bearer {key_sach}"
                                            }
                                            
                                            payload = {
                                                "model": "gpt-4o-mini", # Model nhanh và cực thông minh của ChatGPT
                                                "messages": [
                                                    {"role": "system", "content": "Bạn là chuyên gia tư vấn tâm lý học đường dày dặn kinh nghiệm, thấu cảm và nhạy bén."},
                                                    {"role": "user", "content": prompt}
                                                ],
                                                "temperature": 0.7
                                            }
                                            
                                            try:
                                                res = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=20)
                                                if res.status_code == 200:
                                                    data = res.json()
                                                    ca_hien_tai['ai_phan_tich'] = data['choices'][0]['message']['content']
                                                    thanh_cong = True
                                                    break
                                                else:
                                                    # Bắt lỗi chuẩn từ OpenAI
                                                    loi_chi_tiet = f"Lỗi {res.status_code}: {res.text}"
                                            except Exception as req_err:
                                                loi_chi_tiet = f"Lỗi Request Timeout: Máy chủ OpenAI phản hồi quá chậm ({req_err})"
                                                    
                                        if not thanh_cong: 
                                            # BÁO LỖI ĐỎ CHÓT NẾU CHATGPT THẤT BẠI
                                            ca_hien_tai['ai_phan_tich'] = f"🚨 **CHATGPT BÁO LỖI:**\n\n`{loi_chi_tiet}`\n\n*(Lưu ý: Hãy chắc chắn thầy đã lấy đúng Key của OpenAI, bắt đầu bằng sk-... và tài khoản vẫn còn tiền/lượt sử dụng)*"
                                        luu_du_lieu_len_may(); st.rerun()
                                    except Exception as e:
                                        ca_hien_tai['ai_phan_tich'] = f"🚨 **LỖI CHƯA XÁC ĐỊNH:** {e}"
                                        luu_du_lieu_len_may(); st.rerun()
                                
                        gv_tra_loi = st.chat_input("Nhập tin nhắn hỗ trợ học sinh...")
                        if gv_tra_loi:
                            ca_hien_tai['tin_nhan'].append({"nguoi_gui": "Giáo viên", "noi_dung": gv_tra_loi, "thoi_gian": datetime.datetime.now().strftime('%H:%M')})
                            ca_hien_tai['trang_thai'] = "GV đã phản hồi"
                            ca_hien_tai['ai_phan_tich'] = None 
                            luu_du_lieu_len_may(); st.rerun()

            elif st.session_state.get('menu_gv') == "ho_so":
                st.subheader("👤 Cài đặt Giao diện & Hồ sơ")
                c_img, c_info = st.columns([1, 2])
                with c_img:
                    if user_info.get('avatar'): st.markdown(f'<img src="data:image/png;base64,{user_info["avatar"]}" width="150" style="border-radius: 10px;">', unsafe_allow_html=True)
                    file_anh = st.file_uploader("Tải ảnh đại diện", type=['png', 'jpg', 'jpeg'])
                with c_info:
                    new_name = st.text_input("Họ tên hiển thị:", value=user_info.get('name', ''))
                    new_pw = st.text_input("Đổi Mật khẩu (Bỏ trống nếu giữ nguyên):", type="password")
                    st.write("**Chọn Tone màu Giao diện:**")
                    st.session_state['theme_color'] = st.selectbox("", list(theme_map.keys()), index=list(theme_map.keys()).index(st.session_state.get('theme_color', 'Xanh Mặc Định')), label_visibility="collapsed")
                if st.button("💾 Cập nhật cài đặt", type="primary"):
                    st.session_state['users'][user_id]['name'] = new_name
                    if new_pw: st.session_state['users'][user_id]['pass'] = new_pw
                    if file_anh is not None: st.session_state['users'][user_id]['avatar'] = base64.b64encode(file_anh.read()).decode('utf-8')
                    luu_du_lieu_len_may(); st.rerun()

# 4. KHÔNG GIAN QUẢN TRỊ ADMIN 
elif st.session_state.get('current_view') == "admin_view":
    if kiem_tra_dang_nhap(role_can_thiet='admin'):
        user_hien_tai = st.session_state.get('current_user')
        phan_mem_hoat_dong = kiem_tra_ban_quyen_mem()
        
        st.markdown("<div class='top-title'>TRUNG TÂM QUẢN TRỊ</div>", unsafe_allow_html=True)
        col_menu_ad, col_main_ad = st.columns([1.5, 8.5], gap="small")
        
        with col_menu_ad:
            st.markdown(f"<div style='text-align:center;'><b>⚙️ {st.session_state['users'].get(user_hien_tai, {}).get('name', '')}</b></div>", unsafe_allow_html=True)
            st.markdown("---")
            danh_muc_admin = ["📊 Thống kê", "📂 Giám sát Hồ sơ", "👥 Quản lý Nhân sự", "📥 Xuất Báo cáo", "🔐 Đổi Mật khẩu"]
            if user_hien_tai == "admin": danh_muc_admin.append("🔑 Nhập Mã Gia hạn")
            if user_hien_tai == "hoanganh_dev": danh_muc_admin.append("🛠️ TÁC GIẢ: Cấp Key")
                
            menu_admin = st.radio("🧭 MENU", danh_muc_admin, label_visibility="collapsed")
            st.markdown("---")
            if st.button("🚪 Đăng xuất", use_container_width=True):
                st.session_state['current_user'] = None
                st.session_state['current_view'] = "landing_page"
                st.query_params.clear()
                st.rerun()

        with col_main_ad:
            if HAS_AUTOREFRESH: st_autorefresh(interval=10000, limit=None, key="admin_refresh")
            
            if not phan_mem_hoat_dong and user_hien_tai != "hoanganh_dev":
                st.error("⛔ PHẦN MỀM ĐÃ HẾT HẠN HOẶC CHƯA KÍCH HOẠT BẢN QUYỀN.")
                st.markdown("---")
                
            tong_ca = len(st.session_state['database'])
            ca_khan_cap = len([ca for ca in st.session_state['database'].values() if "Cao" in ca.get('muc_do_rui_ro', '')])
            ca_tb = len([ca for ca in st.session_state['database'].values() if "Trung bình" in ca.get('muc_do_rui_ro', '')])
            ca_thap = len([ca for ca in st.session_state['database'].values() if "Thấp" in ca.get('muc_do_rui_ro', '')])
            ca_cho = tong_ca - ca_khan_cap - ca_tb - ca_thap 
            danh_sach_tai_khoan_gv = [k for k, v in st.session_state['users'].items() if v.get('role') == 'teacher']

            if menu_admin == "📊 Thống kê":
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("Tổng số ca tiếp nhận", f"{tong_ca} ca")
                c_b.metric("Ca Khẩn cấp", f"{ca_khan_cap} ca", delta="Báo động đỏ", delta_color="inverse")
                c_c.metric("Nhân sự", f"{len(danh_sach_tai_khoan_gv)} GV")
                if tong_ca > 0:
                    chart_data = pd.DataFrame({"Mức độ": ["Cao", "Trung", "Thấp", "Chưa phân tích"], "Số lượng": [ca_khan_cap, ca_tb, ca_thap, ca_cho]})
                    st.bar_chart(chart_data.set_index("Mức độ"), color=main_color)

            elif menu_admin == "📂 Giám sát Hồ sơ":
                st.write("#### 📂 Quản lý & Đọc tin nhắn các ca tư vấn")
                if tong_ca == 0: st.info("Chưa có ca tư vấn nào.")
                else:
                    for ma_ca, ca in st.session_state['database'].items():
                        ten_gv = st.session_state['users'].get(ca.get('gv_phu_trach'), {}).get('name', 'Không rõ')
                        icon_tt = "🔒 Đã đóng" if ca.get('trang_thai', '') == "Đã đóng ca" else "🟢 Đang mở"
                        with st.expander(f"Hồ sơ {ma_ca} | Lớp {ca.get('lop','')} | GV: {ten_gv} | {icon_tt}"):
                            st.caption(f"**Rủi ro AI:** {ca.get('muc_do_rui_ro','')}")
                            with st.container(height=300, border=True):
                                for tn in ca['tin_nhan']:
                                    st.markdown(f"**{tn.get('nguoi_gui')}** <span style='font-size:0.8em; color:gray;'>{tn.get('thoi_gian', '')}</span>:<br> {tn.get('noi_dung')}", unsafe_allow_html=True)
                                    st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)

            elif menu_admin == "👥 Quản lý Nhân sự":
                if danh_sach_tai_khoan_gv:
                    gv_can_sua = st.selectbox("Chọn tài khoản để sửa:", options=danh_sach_tai_khoan_gv, format_func=lambda x: f"{x} ({st.session_state['users'].get(x, {}).get('name','')})")
                    c_edit1, c_edit2, c_edit3 = st.columns(3)
                    ten_moi = c_edit1.text_input("Tên mới:", value=st.session_state['users'][gv_can_sua].get('name',''))
                    pass_moi = c_edit2.text_input("Mật khẩu mới:", value=st.session_state['users'][gv_can_sua].get('pass', ''))
                    if c_edit3.button("💾 Lưu thay đổi", type="primary"):
                        st.session_state['users'][gv_can_sua]['name'] = ten_moi
                        st.session_state['users'][gv_can_sua]['pass'] = pass_moi
                        luu_du_lieu_len_may(); st.rerun()
                st.markdown("---")
                c_add1, c_add2, c_add3 = st.columns(3)
                new_id = c_add1.text_input("Tạo ID đăng nhập mới")
                new_name = c_add2.text_input("Tên hiển thị (VD: Cô Lan)")
                new_pass = c_add3.text_input("Mật khẩu")
                if st.button("➕ Tạo tài khoản Giáo viên"):
                    if new_id:
                        st.session_state['users'][new_id] = {'pass': new_pass, 'role': 'teacher', 'name': new_name, 'avatar': '', 'phone': '', 'email': ''}
                        luu_du_lieu_len_may(); st.rerun()

            elif menu_admin == "📥 Xuất Báo cáo":
                if tong_ca > 0:
                    du_lieu_xuat = [{"Mã Hồ Sơ": k, "Thời gian": v.get('thoi_gian', ''), "Lớp": v.get('lop', ''), "Rủi ro (AI)": v.get('muc_do_rui_ro', ''), "Trạng thái": v.get('trang_thai', '')} for k, v in st.session_state['database'].items()]
                    st.download_button("📥 Tải File Báo Cáo CSV", data=pd.DataFrame(du_lieu_xuat).to_csv(index=False).encode('utf-8-sig'), file_name="Bao_Cao.csv", mime="text/csv", type="primary")

            elif menu_admin == "🔐 Đổi Mật khẩu":
                admin_new_pass = st.text_input("Mật khẩu Admin mới:", type="password")
                if st.button("🔑 Cập nhật mật khẩu", type="primary"):
                    st.session_state['users'][user_hien_tai]['pass'] = admin_new_pass
                    luu_du_lieu_len_may(); st.success("Đổi thành công!")

            elif menu_admin == "🔑 Nhập Mã Gia hạn":
                current_key = st.session_state['config'].get('active_key', '')
                st.write(f"**Mã đang dùng:** `{current_key}`")
                new_key = st.text_input("Nhập Mã Bản Quyền mới:")
                if st.button("🚀 Kích hoạt Bản quyền", type="primary"):
                    if new_key in st.session_state.get('licenses', {}) and st.session_state['licenses'][new_key].get('active', False):
                        st.session_state['config']['active_key'] = new_key
                        luu_du_lieu_len_may(); st.rerun()
                    else: st.error("❌ Mã không hợp lệ!")

            elif menu_admin == "🛠️ TÁC GIẢ: Cấp Key":
                for key, data in st.session_state.get('licenses', {}).items():
                    trang_thai = "🟢 Đang HĐ" if data.get('active', False) else "🔴 Khóa"
                    with st.expander(f"{data.get('school_name', '')} | {key} | {data.get('expiry_date', '')} | {trang_thai}"):
                        c1, c2 = st.columns(2)
                        if c1.button("Gia hạn 1 Năm", key=f"gh_{key}"):
                            st.session_state['licenses'][key]['expiry_date'] = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y')
                            st.session_state['licenses'][key]['active'] = True
                            luu_du_lieu_len_may(); st.rerun()
                        if c2.button("Khóa Key", key=f"lock_{key}"):
                            st.session_state['licenses'][key]['active'] = False
                            luu_du_lieu_len_may(); st.rerun()
                new_school = st.text_input("Tên trường đối tác mới:")
                if st.button("➕ Tạo License Key Mới", type="primary"):
                    tao_ma_moi = f"KEY-{random.randint(10000, 99999)}"
                    st.session_state['licenses'][tao_ma_moi] = {'school_name': new_school, 'expiry_date': (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y'), 'active': True}
                    luu_du_lieu_len_may(); st.rerun()