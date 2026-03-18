import streamlit as st
import datetime
import random
import pandas as pd
import requests
import base64
import re

# ==========================================
# HÀM LẤY GIỜ VIỆT NAM (UTC+7)
# ==========================================
def get_vn_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=7)

# ==========================================
# 1. LÁ CHẮN BẢO VỆ BỘ NHỚ
# ==========================================
def khoi_tao_he_thong():
    if 'current_view' not in st.session_state: st.session_state['current_view'] = "landing_page"
    if 'current_user' not in st.session_state: st.session_state['current_user'] = None
    if 'active_chat' not in st.session_state: st.session_state['active_chat'] = None 
    if 'menu_gv' not in st.session_state: st.session_state['menu_gv'] = "mo"
    if 'theme_color' not in st.session_state: st.session_state['theme_color'] = "Xanh Mặc Định"
    if 'just_updated' not in st.session_state: st.session_state['just_updated'] = False 
    
    # BIẾN LÀM SẠCH FORM HỌC SINH
    if 'form_key' not in st.session_state: st.session_state['form_key'] = 0 
    if 'show_success' not in st.session_state: st.session_state['show_success'] = None
    
    if 'users' not in st.session_state:
        st.session_state['users'] = {
            'hoanganh_dev': {'pass': 'admin9999', 'role': 'admin', 'name': 'Nhà Phát Triển', 'avatar': ''}, 
            'admin': {'pass': 'admin123', 'role': 'admin', 'name': 'Ban Giám Hiệu'},
            'gv01': {'pass': '1111', 'role': 'teacher', 'name': 'Thầy Lý Hoàng Anh', 'avatar': ''}
        }
    if 'database' not in st.session_state: st.session_state['database'] = {}
    if 'config' not in st.session_state: st.session_state['config'] = {'active_key': 'FREE-1YEAR', 'school_code': '123456'} 
    if 'licenses' not in st.session_state: 
        st.session_state['licenses'] = {'FREE-1YEAR': {'school_name': 'Miễn phí 1 Năm Đầu', 'expiry_date': (get_vn_time() + datetime.timedelta(days=365)).strftime('%d/%m/%Y'), 'active': True}}

khoi_tao_he_thong()

theme_map = {"Xanh Mặc Định": "#0068ff", "Tím Tinh Tế": "#6366f1", "Xanh Lá Tươi": "#10b981", "Đen Huyền Bí": "#1f2937", "Đỏ Năng Động": "#e53935"}
main_color = theme_map.get(st.session_state.get('theme_color', 'Xanh Mặc Định'), "#0068ff")

def xoa_rac_html(text):
    return re.sub(r'<.*?>', '', str(text))

# ==========================================
# 2. CẤU HÌNH GIAO DIỆN & NỀN CÂY TRE CHÌM
# ==========================================
st.set_page_config(page_title="Hệ thống Tư vấn Học đường AI", page_icon="🏫", layout="wide", initial_sidebar_state="collapsed")

st.markdown(f"""
    <style>
    /* HÌNH NỀN CÂY TRE CHÌM */
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.90), rgba(255, 255, 255, 0.90)), url("https://images.unsplash.com/photo-1533038590840-1cbea676aeb0?q=80&w=2070&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    
    @media (prefers-color-scheme: dark) {{
        [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.92)), url("https://images.unsplash.com/photo-1533038590840-1cbea676aeb0?q=80&w=2070&auto=format&fit=crop") !important;
        }}
    }}
    
    .block-container {{ padding: 0.5rem 1rem !important; max-width: 100% !important; margin-top: -30px !important; }}
    header {{ display: none !important; }}
    [data-testid="collapsedControl"], section[data-testid="stSidebar"] {{ display: none !important; }}
    
    .top-title {{ text-align: center; color: {main_color}; font-size: 24px; font-weight: 800; text-transform: uppercase; border-bottom: 2px solid {main_color}; padding-bottom: 5px; margin-bottom: 10px; }}
    
    /* MENU BÊN TRÁI */
    div[data-testid="column"]:nth-of-type(1) {{ background: transparent !important; background-color: transparent !important; border-right: 1px solid #e5e7eb !important; padding-top: 10px !important; }}
    div[data-testid="column"]:nth-of-type(1) > div {{ background: transparent !important; background-color: transparent !important; }}
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button {{ background-color: transparent !important; color: #4B5563 !important; border: none !important; padding: 10px 5px !important; width: 100% !important; font-size: 15px !important; font-weight: 600 !important; text-align: left !important; justify-content: flex-start !important; margin-bottom: 5px !important; box-shadow: none !important; }}
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button:hover {{ background-color: #F3F4F6 !important; border-radius: 8px !important; color: {main_color} !important; }}
    
    /* HỘP THƯ LÀM VIỆC */
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stVerticalBlock"] > div {{ padding: 0 !important; gap: 0 !important; margin-bottom: -15px !important; }}
    .chat-list-btn button {{ width: 100% !important; background-color: white !important; border: 1px solid #eaedf0 !important; border-radius: 8px !important; padding: 12px 10px !important; text-align: left !important; justify-content: flex-start !important; color: #111 !important; margin-bottom: 5px !important; box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important; }}
    .chat-list-btn button p {{ margin: 0 !important; line-height: 1.5 !important; font-size: 14px !important; white-space: pre-wrap !important; }}
    .chat-list-btn button:hover {{ background-color: #f8fafc !important; border-color: {main_color} !important; transform: translateY(-2px); }}
    
    /* ĐIỆN THOẠI */
    @media (max-width: 768px) {{
        [data-testid="column"]:nth-of-type(1) {{ border-right: none !important; border-bottom: 1px solid #e5e7eb; padding-bottom: 10px; margin-bottom: 10px; }}
        [data-testid="column"]:nth-of-type(1) div[data-testid="stVerticalBlock"] {{ flex-direction: row !important; flex-wrap: wrap !important; justify-content: space-around !important; gap: 5px !important; }}
        [data-testid="column"]:nth-of-type(1) div.element-container {{ width: auto !important; flex: 1 1 auto !important; }}
        [data-testid="column"]:nth-of-type(1) button {{ text-align: center !important; justify-content: center !important; padding: 8px !important; font-size: 13px !important; margin-bottom: 0 !important; border-radius: 20px !important; background-color: #F3F4F6 !important; }}
        [data-testid="column"]:nth-of-type(1) button:active {{ background-color: {main_color} !important; color: white !important; }}
    }}
    </style>
""", unsafe_allow_html=True)

if st.session_state.get('active_chat'):
    st.markdown("<style>@media (max-width: 768px) { [data-testid='column']:nth-of-type(2) { display: none !important; } }</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>@media (max-width: 768px) { [data-testid='column']:nth-of-type(3) { display: none !important; } }</style>", unsafe_allow_html=True)

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError: HAS_AUTOREFRESH = False

# LỌC VÀ LẤY API KEY
try:
    if "API_KEYS" in st.secrets: 
        danh_sach_keys = [k.strip().strip('"').strip("'") for k in st.secrets["API_KEYS"].split(",") if k.strip()]
    elif "API_KEY" in st.secrets: 
        danh_sach_keys = [st.secrets["API_KEY"].strip().strip('"').strip("'")]
    else: danh_sach_keys = []
except: danh_sach_keys = []

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
    st.session_state['just_updated'] = True
    du_lieu_dong_bo = {'users': st.session_state['users'], 'database': st.session_state['database'], 'config': st.session_state['config'], 'licenses': st.session_state.get('licenses', {})}
    try: requests.put(f"{FIREBASE_URL}/he_thong.json", json=du_lieu_dong_bo, timeout=5)
    except: pass

if not st.session_state.get('just_updated'):
    du_lieu_dam_may = tai_du_lieu_tu_may()
    if du_lieu_dam_may:
        st.session_state['database'] = du_lieu_dam_may.get('database', {})
        st.session_state['config'] = du_lieu_dam_may.get('config', st.session_state.get('config'))
        st.session_state['licenses'] = du_lieu_dam_may.get('licenses', st.session_state.get('licenses'))
        for k, v in du_lieu_dam_may.get('users', {}).items():
            if k in st.session_state['users']: st.session_state['users'][k].update(v)
            else: st.session_state['users'][k] = v
else:
    st.session_state['just_updated'] = False

danh_sach_gv = {k: v.get('name', 'GV') for k, v in st.session_state['users'].items() if v.get('role') == 'teacher'}

def kiem_tra_ban_quyen_mem():
    active_key = st.session_state['config'].get('active_key', '')
    licenses = st.session_state.get('licenses', {})
    if st.session_state.get('current_user') == 'hoanganh_dev': return True 
    if active_key not in licenses or not licenses[active_key].get('active', False): return False
    try:
        if get_vn_time() > datetime.datetime.strptime(licenses[active_key]['expiry_date'], '%d/%m/%Y'): return False
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
        st.markdown(f"""
            <div style='text-align: center; background: rgba(255,255,255,0.9); padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eee; margin-bottom: 20px;'>
                <h2 style='color: {main_color}; font-weight: 800; margin: 0;'>🔒 ĐĂNG NHẬP HỆ THỐNG</h2>
            </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            with st.container(border=True):
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
        <div style='text-align: center; background: rgba(255,255,255,0.85); padding: 40px 20px; border-radius: 20px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.5);'>
            <h1 style='color: {main_color}; font-weight: 900; margin-top: 0; font-size: 40px; text-transform: uppercase; letter-spacing: 1px;'>HỆ THỐNG TƯ VẤN HỌC ĐƯỜNG AI</h1>
            <p style='color: #475569; font-size: 18px; max-width: 650px; margin: 10px auto; font-weight: 500;'>Không gian an toàn, tĩnh tại để học sinh chia sẻ cảm xúc và nhận hỗ trợ kịp thời từ Trí tuệ Nhân tạo & Đội ngũ Chuyên gia.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.markdown(f"<div style='background: rgba(255,255,255,0.9); padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 1px solid #eee; height: 100%;'><h3 style='color:#334155;'>🎓 Cổng Học Sinh</h3><p style='color:#64748b;'>Check-in cảm xúc mỗi ngày, ẩn danh an toàn và trò chuyện 24/7 với Trợ lý AI thấu cảm.</p></div>", unsafe_allow_html=True)
        if st.button("Tham Gia Ngay ➡️", use_container_width=True, type="primary"):
            st.session_state['current_view'] = "student_view"; st.rerun()
    with col2:
        st.markdown(f"<div style='background: rgba(255,255,255,0.9); padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 1px solid #eee; height: 100%;'><h3 style='color:#334155;'>👨‍🏫 Cổng Giáo Viên</h3><p style='color:#64748b;'>Quản lý hồ sơ học sinh, nhận phân tích tâm lý sâu sắc và gợi ý xử lý tình huống từ AI.</p></div>", unsafe_allow_html=True)
        if st.button("Khu Vực Chuyên Gia ➡️", use_container_width=True):
            st.session_state['current_view'] = "teacher_view"; st.rerun()
    with col3:
        st.markdown(f"<div style='background: rgba(255,255,255,0.9); padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 1px solid #eee; height: 100%;'><h3 style='color:#334155;'>⚙️ Ban Giám Hiệu</h3><p style='color:#64748b;'>Bảng điều khiển toàn cảnh, thống kê rủi ro tâm lý và quản lý toàn diện hệ thống.</p></div>", unsafe_allow_html=True)
        if st.button("Khu Vực Quản Trị ➡️", use_container_width=True):
            st.session_state['current_view'] = "admin_view"; st.rerun()
            
    st.markdown("<br><hr style='opacity: 0.3'><p style='text-align: center; color: #64748b; font-size: 13px; font-weight: bold;'>Bản quyền thuộc về: Lý Hoàng Anh - Bảo mật tuyệt đối dữ liệu học đường</p>", unsafe_allow_html=True)

# 2. KHÔNG GIAN HỌC SINH
elif st.session_state.get('current_view') == "student_view":
    if st.button("⬅️ Trở về Trang chủ"): st.session_state['current_view'] = "landing_page"; st.rerun()
    st.markdown("<div class='top-title'>HỆ THỐNG TƯ VẤN HỌC ĐƯỜNG AI</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='background: rgba(255,255,255,0.95); padding: 15px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        tab_gui, tab_xem = st.tabs(["📝 Gửi Tâm Sự", "💬 Phòng Chat Bảo Mật"])
        with tab_gui:
            
            # HIỂN THỊ THÔNG BÁO VÀ BÓNG BAY TỪ LẦN GỬI TRƯỚC
            if st.session_state.get('show_success'):
                st.success(f"✅ Gửi thành công! Để xem lại thầy cô trả lời, em hãy lưu lại mã này nhé: **{st.session_state['show_success']}**")
                st.balloons()
                st.session_state['show_success'] = None
                
            ma_bao_mat_he_thong = st.session_state['config'].get('school_code', '123456')
            
            # SỬ DỤNG KEY ĐỘNG ĐỂ LÀM SẠCH FORM HỌC SINH
            k = st.session_state.get('form_key', 0)
            
            ma_xac_thuc = st.text_input("🔑 Mã bảo mật của trường:", type="password", key=f"ma_{k}")
            hs_khoi_lop = st.text_input("Khối/Lớp của em (Không bắt buộc):", key=f"lop_{k}")
            hs_cam_xuc = st.selectbox("Ngay lúc này, em cảm thấy thế nào?", ["😐 Bình thường", "😔 Buồn bã", "😰 Áp lực", "😡 Tức giận", "😨 Sợ hãi", "😭 Tuyệt vọng"], key=f"cx_{k}")
            gv_duoc_chon = st.selectbox("Chọn Thầy/Cô để tâm sự:", options=list(danh_sach_gv.keys()), format_func=lambda x: danh_sach_gv.get(x, x), key=f"gv_{k}")
            hinh_thuc_tv = st.radio("Hình thức muốn hỗ trợ:", ["💬 Nhắn tin trên web (Ẩn danh)", "🤝 Hẹn gặp trực tiếp"], key=f"ht_{k}")
            
            ngay_hen, gio_hen = "", ""
            if "Trực tiếp" in hinh_thuc_tv:
                c_ngay, c_gio = st.columns(2)
                ngay_hen, gio_hen = c_ngay.date_input("Ngày hẹn:", key=f"nh_{k}"), c_gio.time_input("Giờ hẹn:", key=f"gh_{k}")
                
            tam_su_input = st.text_area("Hãy viết ra những điều đang làm em bận lòng nhé...", height=100, key=f"ts_{k}")
            
            if st.button("🚀 Gửi đi an toàn", type="primary", key=f"btn_{k}"):
                if not ma_xac_thuc or str(ma_xac_thuc).strip().upper() != str(ma_bao_mat_he_thong).strip().upper(): 
                    st.error("❌ Sai Mã bảo mật! Vui lòng hỏi Thầy Cô/Ban Giám Hiệu để lấy mã chính xác.")
                elif not tam_su_input.strip():
                    st.warning("⚠️ Vui lòng nhập nội dung tâm sự trước khi gửi.")
                else:
                    ma_bi_mat = f"HS-{random.randint(1000, 9999)}"
                    st.session_state['database'][ma_bi_mat] = {
                        "thoi_gian": get_vn_time().strftime('%d/%m/%Y %H:%M'), "lop": hs_khoi_lop if hs_khoi_lop else "Ẩn danh",
                        "cam_xuc_ban_dau": hs_cam_xuc, "gv_phu_trach": gv_duoc_chon, "hinh_thuc": hinh_thuc_tv,
                        "lich_hen": f"{ngay_hen.strftime('%d/%m/%Y')} lúc {gio_hen.strftime('%H:%M')}" if "Trực tiếp" in hinh_thuc_tv else "Không",
                        "tin_nhan": [{"nguoi_gui": "Học sinh", "noi_dung": tam_su_input, "thoi_gian": get_vn_time().strftime('%H:%M')}],
                        "ai_phan_tich": None, "muc_do_rui_ro": "Chờ AI phân tích", "trang_thai": "Chờ xử lý"
                    }
                    luu_du_lieu_len_may()
                    
                    # Bật cờ thành công và Tăng Key để đổi form mới (Xóa trắng)
                    st.session_state['show_success'] = ma_bi_mat
                    st.session_state['form_key'] = k + 1
                    st.rerun()

        with tab_xem:
            if HAS_AUTOREFRESH: st_autorefresh(interval=30000, limit=None, key="hs_refresh") 
            ma_tra_cuu = st.text_input("Nhập Mã tra cứu của em (VD: HS-1234):")
            if st.button("Truy cập"): st.session_state['ca_dang_xem'] = ma_tra_cuu.strip()
                
            if 'ca_dang_xem' in st.session_state and st.session_state.get('ca_dang_xem') in st.session_state['database']:
                ca = st.session_state['database'][st.session_state['ca_dang_xem']]
                st.markdown(f"### 💬 Trò chuyện cùng Thầy/Cô")
                with st.container(height=350, border=True):
                    for tn in ca['tin_nhan']:
                        with st.chat_message("user" if tn.get('nguoi_gui') == "Học sinh" else "assistant"):
                            st.markdown(f"**{tn.get('nguoi_gui')}** <span style='font-size:0.8em; color:gray;'>{tn.get('thoi_gian', '')}</span>", unsafe_allow_html=True)
                            st.write(tn.get('noi_dung'))
                
                if ca.get('trang_thai') != "Đã đóng ca":
                    hs_phan_hoi = st.chat_input("Nhập tin nhắn phản hồi của em...")
                    if hs_phan_hoi:
                        ca['tin_nhan'].append({"nguoi_gui": "Học sinh", "noi_dung": hs_phan_hoi, "thoi_gian": get_vn_time().strftime('%H:%M')})
                        ca['trang_thai'] = "HS vừa nhắn lại" 
                        ca['ai_phan_tich'] = None 
                        luu_du_lieu_len_may()
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# 3. KHÔNG GIAN GIÁO VIÊN
elif st.session_state.get('current_view') == "teacher_view":
    if kiem_tra_dang_nhap(role_can_thiet='teacher'):
        user_id = st.session_state.get('current_user')
        user_info = st.session_state['users'].get(user_id, {})
        phan_mem_hoat_dong = kiem_tra_ban_quyen_mem()
        
        if HAS_AUTOREFRESH: st_autorefresh(interval=30000, limit=None, key="gv_refresh") 
        if 'menu_gv' not in st.session_state: st.session_state['menu_gv'] = "mo"
        
        ca_cua_toi = {k: v for k, v in st.session_state['database'].items() if v.get('gv_phu_trach') == user_id}
        ca_dang_mo = {k: v for k, v in ca_cua_toi.items() if v.get('trang_thai') != "Đã đóng ca"}
        ca_da_dong = {k: v for k, v in ca_cua_toi.items() if v.get('trang_thai') == "Đã đóng ca"}

        st.markdown("<div class='top-title'>HỆ THỐNG TƯ VẤN - KHU VỰC CHUYÊN GIA</div>", unsafe_allow_html=True)

        col_menu, col_danh_sach, col_chat = st.columns([1.5, 3.5, 7], gap="small")
        
        with col_menu:
            st.markdown("<div style='background: rgba(255,255,255,0.95); border-radius: 15px; padding: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); height: 100%; border: 1px solid rgba(255,255,255,0.5);'>", unsafe_allow_html=True)
            if user_info.get('avatar'): st.markdown(f'<div style="text-align:center; margin-bottom: 10px;"><img src="data:image/png;base64,{user_info.get("avatar")}" width="60" style="border-radius: 50%; box-shadow: 0 2px 5px rgba(0,0,0,0.1);"></div>', unsafe_allow_html=True)
            else: st.markdown(f'<div style="text-align:center; font-size:30px; margin-bottom: 5px;">👨‍🏫</div>', unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center; font-size:14px; font-weight:bold; color:#1f2937; margin-bottom:15px;'>{user_info.get('name', 'Giáo viên')}</div>", unsafe_allow_html=True)
            
            if st.button("💬 Cần hỗ trợ", use_container_width=True): st.session_state['menu_gv'] = "mo"; st.session_state['active_chat'] = None; st.rerun()
            if st.button("📦 Đã khép lại", use_container_width=True): st.session_state['menu_gv'] = "xong"; st.session_state['active_chat'] = None; st.rerun()
            if st.button("👤 Hồ sơ", use_container_width=True): st.session_state['menu_gv'] = "ho_so"; st.session_state['active_chat'] = None; st.rerun()
            if st.button("🚪 Thoát", use_container_width=True):
                st.session_state['current_user'] = None
                st.session_state['current_view'] = "landing_page"
                st.query_params.clear()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col_danh_sach:
            st.markdown("<div style='background: rgba(255,255,255,0.95); border-radius: 15px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); height: 100%; border: 1px solid rgba(255,255,255,0.5);'>", unsafe_allow_html=True)
            if st.session_state.get('menu_gv') == "mo":
                st.markdown(f"<b style='color:#1f2937; font-size:16px; border-bottom:1px solid #eee; padding-bottom:5px; display:block; margin-bottom:10px;'>📥 Danh sách cần hỗ trợ</b>", unsafe_allow_html=True)
                if not phan_mem_hoat_dong: st.error("⛔ Hết hạn!")
                
                if not ca_dang_mo: st.info("Không có học sinh nào đang cần hỗ trợ.")
                else:
                    danh_sach_ca_sap_xep = sorted(ca_dang_mo.items(), key=lambda x: (0 if x[1].get('trang_thai')=="HS vừa nhắn lại" else 1, x[0]))
                    with st.container(height=650, border=False):
                        for i, (ma_ca, ca) in enumerate(danh_sach_ca_sap_xep, 1):
                            thoi_gian_ca = ca['tin_nhan'][-1].get('thoi_gian', '')
                            if ca.get('trang_thai') == "HS vừa nhắn lại": icon_tt = "🔴"
                            elif ca.get('trang_thai') == "Chờ xử lý": icon_tt = "🟡"
                            else: icon_tt = "🟢"
                                
                            tn_cuoi = xoa_rac_html(ca['tin_nhan'][-1].get('noi_dung', ''))
                            tn_rut_gon = tn_cuoi[:35] + "..." if len(tn_cuoi) > 35 else tn_cuoi
                            
                            st.markdown('<div class="chat-list-btn">', unsafe_allow_html=True)
                            label_nut = f"{icon_tt} {ma_ca} (Lớp {ca.get('lop', '')})\n🕒 {thoi_gian_ca} | 💬 {tn_rut_gon}"
                            btn_type = "primary" if st.session_state.get('active_chat') == ma_ca else "secondary"
                            if st.button(label_nut, key=f"btn_{ma_ca}", type=btn_type):
                                st.session_state['active_chat'] = ma_ca; st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                            
            elif st.session_state.get('menu_gv') == "xong":
                st.markdown(f"<b style='color:#1f2937; font-size:16px; border-bottom:1px solid #eee; padding-bottom:5px; display:block; margin-bottom:10px;'>📦 Hồ sơ đã khép lại</b>", unsafe_allow_html=True)
                with st.container(height=650, border=False):
                    for i, (ma_ca, ca) in enumerate(ca_da_dong.items(), 1):
                        st.markdown('<div class="chat-list-btn">', unsafe_allow_html=True)
                        btn_type = "primary" if st.session_state.get('active_chat') == ma_ca else "secondary"
                        if st.button(f"📦 {ma_ca} (Lớp {ca.get('lop', '')})\nĐã đóng hồ sơ", key=f"btn_x_{ma_ca}", type=btn_type):
                            st.session_state['active_chat'] = ma_ca; st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                        
            elif st.session_state.get('menu_gv') == "ho_so":
                st.info("👉 Cài đặt hệ thống bên cạnh.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_chat:
            st.markdown("<div style='background: rgba(255,255,255,0.95); border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); height: 100%; border: 1px solid rgba(255,255,255,0.5);'>", unsafe_allow_html=True)
            if not phan_mem_hoat_dong: st.error("⛔ Hết hạn Bản quyền. Tính năng AI bị khóa.")
            
            if st.session_state.get('menu_gv') in ["mo", "xong"]:
                ma_dang_chon = st.session_state.get('active_chat')
                
                if not ma_dang_chon or ma_dang_chon not in ca_cua_toi:
                    st.markdown("""<div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 75vh; text-align: center; color: #9CA3AF;'>
                        <h2 style='font-size: 50px; margin-bottom:0;'>🍃</h2>
                        <h2>Chào ngày mới tĩnh tại!</h2><p>Vui lòng chọn một học sinh bên trái để bắt đầu phiên tư vấn.</p></div>""", unsafe_allow_html=True)
                else:
                    ca_hien_tai = ca_cua_toi[ma_dang_chon]
                    
                    c_head1, c_head2 = st.columns([4, 1])
                    c_head1.markdown(f"<h4 style='margin-bottom:0; color:{main_color};'>🗣️ {ma_dang_chon} | Lớp {ca_hien_tai.get('lop', '')}</h4>", unsafe_allow_html=True)
                    c_head1.caption(f"**Gốc:** {xoa_rac_html(ca_hien_tai['tin_nhan'][0].get('noi_dung', ''))[:80]}...")
                    
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
                            st.success(f"✨ **AI CỐ VẤN:**\n\n{ca_hien_tai['ai_phan_tich']}")
                            if st.button("🗑️ Xóa kết quả phân tích để gọn màn hình"):
                                ca_hien_tai['ai_phan_tich'] = None
                                luu_du_lieu_len_may(); st.rerun()
                                
                        if not ca_hien_tai.get('ai_phan_tich'):
                            if st.button("🧠 Phân tích tâm lý bằng AI (Google Gemini)", type="primary", use_container_width=True):
                                if not danh_sach_keys:
                                    st.error("🚨 **CHƯA CÓ API KEY:** Hệ thống chưa nhận được Key của Google. Thầy hãy kiểm tra lại mục Secrets.")
                                else:
                                    with st.spinner("AI đang đọc tin nhắn và phân tích..."):
                                        tin_nhan_moi_lien_tiep = []
                                        for t in reversed(ca_hien_tai['tin_nhan']):
                                            if t.get('nguoi_gui') == "Học sinh": tin_nhan_moi_lien_tiep.insert(0, xoa_rac_html(t.get('noi_dung', '')))
                                            else: break 
                                        cum_tin_nhan_moi = "\n".join(tin_nhan_moi_lien_tiep)
                                        
                                        lich_su_cu_len = len(ca_hien_tai['tin_nhan']) - len(tin_nhan_moi_lien_tiep)
                                        lich_su_cu = ""
                                        if lich_su_cu_len > 0:
                                            for t in ca_hien_tai['tin_nhan'][:lich_su_cu_len]: lich_su_cu += f"{t.get('nguoi_gui')}: {xoa_rac_html(t.get('noi_dung', ''))}\n"
                                        
                                        prompt = f"""[BỐI CẢNH CŨ]: {lich_su_cu if lich_su_cu else 'Không.'}
                                        [TIN MỚI LIÊN TIẾP TỪ HỌC SINH]: "{cum_tin_nhan_moi}"
                                        
                                        1. Phân tích tâm lý học sinh trong cụm tin nhắn mới.
                                        2. Đánh giá MỨC ĐỘ RỦI RO (Thấp/Trung/Cao). Nếu chỉ là cảm ơn/vâng dạ thì rủi ro là Thấp.
                                        Trả lời theo format:
                                        [RỦI RO]: ...
                                        [PHÂN TÍCH NHANH]: ...
                                        [GỢI Ý TRẢ LỜI]: ..."""
                                        
                                        thanh_cong = False
                                        loi_chi_tiet = ""
                                        keys_luot_nay = danh_sach_keys.copy()
                                        random.shuffle(keys_luot_nay)
                                        
                                        # ==============================================================
                                        # PHỤC HỒI NGUYÊN TRẠNG 100% ĐOẠN AI GOOGLE GEMINI THEO FILE GỐC
                                        # ==============================================================
                                        for key_sach in keys_luot_nay:
                                            if not key_sach.startswith("AIza"):
                                                loi_chi_tiet = "Mã Key không hợp lệ. API Key của Google Gemini bắt buộc phải bắt đầu bằng chữ 'AIza'."
                                                continue

                                            headers = {'Content-Type': 'application/json'}
                                            payload = {"contents": [{"parts": [{"text": prompt}]}]}
                                            
                                            models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"]
                                            for model in models_to_try:
                                                if thanh_cong: break
                                                try:
                                                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key_sach}"
                                                    res = requests.post(url, json=payload, headers=headers, timeout=15)
                                                    if res.status_code == 200:
                                                        data = res.json()
                                                        if 'candidates' in data and len(data['candidates']) > 0:
                                                            ca_hien_tai['ai_phan_tich'] = data['candidates'][0]['content']['parts'][0]['text']
                                                            thanh_cong = True
                                                            break
                                                        else:
                                                            loi_chi_tiet = "Google từ chối trả lời (vướng từ khóa)."
                                                    else:
                                                        loi_chi_tiet = f"Lỗi Google {model} ({res.status_code}): {res.text[:150]}..."
                                                except Exception as err:
                                                    loi_chi_tiet = f"Lỗi kết nối Google ({model}): {err}"
                                            
                                            if thanh_cong: break
                                        # ==============================================================
                                                        
                                        if not thanh_cong: 
                                            st.error(f"🚨 **GOOGLE AI BÁO LỖI CHI TIẾT:**\n\n`{loi_chi_tiet}`")
                                        else:
                                            luu_du_lieu_len_may()
                                            st.rerun()
                                
                        gv_tra_loi = st.chat_input("Nhập tin nhắn hỗ trợ học sinh...")
                        if gv_tra_loi:
                            ca_hien_tai['tin_nhan'].append({"nguoi_gui": "Giáo viên", "noi_dung": gv_tra_loi, "thoi_gian": get_vn_time().strftime('%H:%M')})
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
            st.markdown("</div>", unsafe_allow_html=True)

# 4. KHÔNG GIAN QUẢN TRỊ ADMIN
elif st.session_state.get('current_view') == "admin_view":
    if kiem_tra_dang_nhap(role_can_thiet='admin'):
        user_hien_tai = st.session_state.get('current_user')
        phan_mem_hoat_dong = kiem_tra_ban_quyen_mem()
        
        st.markdown("<div class='top-title'>TRUNG TÂM QUẢN TRỊ AI</div>", unsafe_allow_html=True)
        col_menu_ad, col_main_ad = st.columns([1.5, 8.5], gap="small")
        
        with col_menu_ad:
            st.markdown("<div style='background: rgba(255,255,255,0.95); border-radius: 15px; padding: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); height: 100%; border: 1px solid rgba(255,255,255,0.5);'>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;'><b>⚙️ {st.session_state['users'].get(user_hien_tai, {}).get('name', '')}</b></div>", unsafe_allow_html=True)
            st.markdown("---")
            danh_muc_admin = ["📊 Thống kê", "📂 Giám sát Hồ sơ", "👥 Quản lý Nhân sự", "📥 Xuất Báo cáo", "⚙️ Cài đặt Hệ thống", "🔐 Đổi Mật khẩu"]
            if user_hien_tai == "admin": danh_muc_admin.append("🔑 Nhập Mã Gia hạn")
            if user_hien_tai == "hoanganh_dev": danh_muc_admin.append("🛠️ TÁC GIẢ: Cấp Key")
                
            menu_admin = st.radio("🧭 MENU QUẢN TRỊ", danh_muc_admin, label_visibility="collapsed")
            st.markdown("---")
            if st.button("🚪 Đăng xuất", use_container_width=True):
                st.session_state['current_user'] = None
                st.session_state['current_view'] = "landing_page"
                st.query_params.clear()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col_main_ad:
            st.markdown("<div style='background: rgba(255,255,255,0.95); border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); height: 100%; border: 1px solid rgba(255,255,255,0.5);'>", unsafe_allow_html=True)
            if HAS_AUTOREFRESH: st_autorefresh(interval=10000, limit=None, key="admin_refresh")
            
            if not phan_mem_hoat_dong and user_hien_tai != "hoanganh_dev":
                st.error("⛔ PHẦN MỀM ĐÃ HẾT HẠN HOẶC CHƯA KÍCH HOẠT BẢN QUYỀN CHÍNH THỨC.")
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
                st.write("#### 📂 Quản lý, Giám sát & Xóa Hồ sơ tư vấn")
                if tong_ca == 0: st.info("Hệ thống chưa có ca tư vấn nào.")
                else:
                    for ma_ca in list(st.session_state['database'].keys()):
                        ca = st.session_state['database'][ma_ca]
                        ten_gv = st.session_state['users'].get(ca.get('gv_phu_trach'), {}).get('name', 'Không rõ')
                        icon_tt = "🔒 Đã đóng" if ca.get('trang_thai', '') == "Đã đóng ca" else "🟢 Đang mở"
                        with st.expander(f"Hồ sơ {ma_ca} | Lớp {ca.get('lop','')} | GV: {ten_gv} | {icon_tt}"):
                            c_del1, c_del2 = st.columns([5, 1])
                            c_del1.caption(f"**Rủi ro AI:** {ca.get('muc_do_rui_ro','')}")
                            
                            # NÚT XÓA CA TƯ VẤN (ADMIN)
                            if c_del2.button("🗑️ Xóa ca này", key=f"del_{ma_ca}", type="primary"):
                                del st.session_state['database'][ma_ca]
                                luu_du_lieu_len_may()
                                st.rerun()
                                
                            with st.container(height=300, border=True):
                                for tn in ca['tin_nhan']:
                                    st.markdown(f"**{tn.get('nguoi_gui')}** <span style='font-size:0.8em; color:gray;'>{tn.get('thoi_gian', '')}</span>:<br> {xoa_rac_html(tn.get('noi_dung', ''))}", unsafe_allow_html=True)
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

            # TAB MỚI: CÀI ĐẶT MÃ BẢO MẬT
            elif menu_admin == "⚙️ Cài đặt Hệ thống":
                st.write("#### ⚙️ Cài đặt Mã bảo mật dành cho Học sinh")
                st.info("Mã bảo mật giúp ngăn chặn người lạ hoặc học sinh spam tin nhắn rác vào hệ thống.")
                
                ma_hien_tai = st.session_state['config'].get('school_code', '123456')
                st.markdown(f"Mã bảo mật hiện tại đang là: **`{ma_hien_tai}`**")
                
                c_ma1, c_ma2 = st.columns([2, 1])
                new_code = c_ma1.text_input("Nhập mã bảo mật mới:")
                if c_ma2.button("💾 Lưu mã mới", type="primary"):
                    if new_code.strip():
                        st.session_state['config']['school_code'] = new_code.strip()
                        luu_du_lieu_len_may()
                        st.success("✅ Đã cập nhật mã bảo mật thành công!")
                        st.rerun()
                    else:
                        st.warning("Vui lòng nhập mã hợp lệ.")

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
                            st.session_state['licenses'][key]['expiry_date'] = (get_vn_time() + datetime.timedelta(days=365)).strftime('%d/%m/%Y')
                            st.session_state['licenses'][key]['active'] = True
                            luu_du_lieu_len_may(); st.rerun()
                        if c2.button("Khóa Key", key=f"lock_{key}"):
                            st.session_state['licenses'][key]['active'] = False
                            luu_du_lieu_len_may(); st.rerun()
                new_school = st.text_input("Tên trường đối tác mới:")
                if st.button("➕ Tạo License Key Mới", type="primary"):
                    tao_ma_moi = f"KEY-{random.randint(10000, 99999)}"
                    st.session_state['licenses'][tao_ma_moi] = {'school_name': new_school, 'expiry_date': (get_vn_time() + datetime.timedelta(days=365)).strftime('%d/%m/%Y'), 'active': True}
                    luu_du_lieu_len_may(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)