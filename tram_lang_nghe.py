import streamlit as st
import datetime
import random
import pandas as pd
import requests
import base64

# ==========================================
# KHỞI TẠO STATE & ĐỒNG BỘ TRƯỚC (ĐỂ LẤY THEME)
# ==========================================
if 'current_view' not in st.session_state: st.session_state['current_view'] = "landing_page"
if 'current_user' not in st.session_state: st.session_state['current_user'] = None
if 'active_chat' not in st.session_state: st.session_state['active_chat'] = None 
if 'menu_expanded' not in st.session_state: st.session_state['menu_expanded'] = True 
if 'inbox_expanded' not in st.session_state: st.session_state['inbox_expanded'] = True 
if 'theme_color' not in st.session_state: st.session_state['theme_color'] = "Xanh Zalo"

# BỘ MÀU THEME ĐA DẠNG
theme_map = {
    "Xanh Zalo": "#0068ff", 
    "Tím Tinh Tế": "#6366f1", 
    "Xanh Lá Tươi": "#10b981", 
    "Đen Huyền Bí": "#1f2937",
    "Đỏ Áp Lực": "#e53935"
}
main_color = theme_map.get(st.session_state['theme_color'], "#0068ff")

# ==========================================
# CẤU HÌNH HỆ THỐNG & CSS (GẮN MÀU THEME ĐỘNG)
# ==========================================
st.set_page_config(page_title="Hệ thống Quản trị Tâm lý Học đường AI", page_icon="🏫", layout="wide", initial_sidebar_state="collapsed")

st.markdown(f"""
    <style>
    /* Ép kịch trần, bỏ khoảng trắng trên cùng */
    .block-container {{ padding: 0rem 0.5rem 0.5rem 0.5rem !important; max-width: 100% !important; margin-top: -30px !important; }}
    header {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}
    section[data-testid="stSidebar"] {{ display: none !important; }}
    
    /* Tiêu đề TRẠM TƯ VẤN (Đổi màu theo Theme) */
    .top-title {{
        text-align: center; color: {main_color}; font-size: 26px; font-weight: 800;
        text-transform: uppercase; border-bottom: 2px solid {main_color}; 
        padding-bottom: 5px; margin-bottom: 10px;
    }}

    /* CỘT MENU BÊN TRÁI (Màu nền đổi theo Theme) */
    [data-testid="column"]:nth-of-type(1) {{
        background-color: {main_color}; border-radius: 12px; padding: 10px 0;
        text-align: center; height: 90vh; box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    }}
    
    [data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button {{
        background-color: transparent !important; color: white !important; border: none !important;
        padding: 15px 0 !important; width: 100% !important; font-size: 15px !important;
    }}
    [data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button:hover {{ background-color: rgba(255,255,255,0.2) !important; }}

    /* CỘT DANH SÁCH (HỘP THƯ) - ÉP CÁC CA DÍNH SÁT RẠT NHAU */
    [data-testid="column"]:nth-of-type(2) div[data-testid="stVerticalBlock"] > div {{
        padding: 0 !important; gap: 0 !important; margin-bottom: -15px !important; /* Âm margin để các nút đè lên nhau */
    }}
    .zalo-list-btn button {{
        width: 100% !important; background-color: white !important; border: 1px solid #eaedf0 !important;
        border-radius: 0px !important; padding: 12px 10px !important; text-align: left !important;
        justify-content: flex-start !important; color: #111 !important; margin-top: -1px !important; 
    }}
    .zalo-list-btn button:hover {{ background-color: #f3f5f6 !important; }}
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

MA_BAO_MAT_TRUONG = "123456" 
FIREBASE_URL = "https://tram-lang-nghe-data-default-rtdb.firebaseio.com"

def tai_du_lieu_tu_may():
    try:
        r = requests.get(f"{FIREBASE_URL}/he_thong.json")
        if r.status_code == 200 and r.json(): return r.json()
    except: pass
    return None

def luu_du_lieu_len_may():
    du_lieu_dong_bo = {'users': st.session_state['users'], 'database': st.session_state['database'], 'config': st.session_state['config'], 'licenses': st.session_state.get('licenses', {})}
    try: requests.put(f"{FIREBASE_URL}/he_thong.json", json=du_lieu_dong_bo)
    except: pass

if 'he_thong_da_khoi_dong' not in st.session_state:
    st.session_state['users'] = {
        'hoanganh_dev': {'pass': 'admin9999', 'role': 'admin', 'name': 'Nhà Phát Triển', 'avatar': ''}, 
        'admin': {'pass': 'admin123', 'role': 'admin', 'name': 'Ban Giám Hiệu'},
        'gv01': {'pass': '1111', 'role': 'teacher', 'name': 'Thầy Lý Hoàng Anh', 'avatar': ''}
    }
    st.session_state['database'] = {}
    st.session_state['config'] = {'active_key': 'FREE-1YEAR'} 
    st.session_state['licenses'] = {'FREE-1YEAR': {'school_name': 'Miễn phí 1 Năm Đầu', 'expiry_date': (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y'), 'active': True}}
    st.session_state['he_thong_da_khoi_dong'] = True

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
# GIAO DIỆN ĐĂNG NHẬP (ĐÃ FIX LỖI KẸT TOKEN)
# ==========================================
def kiem_tra_dang_nhap(role_can_thiet=None):
    if 'token_login' in st.query_params:
        user_luu = st.query_params['token_login']
        if user_luu in st.session_state['users']: st.session_state['current_user'] = user_luu

    if not st.session_state['current_user']:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.warning("🔒 Vui lòng đăng nhập để truy cập hệ thống.")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            u = st.text_input("Tài khoản", key=f"user_{role_can_thiet}")
            p = st.text_input("Mật khẩu", type="password", key=f"pass_{role_can_thiet}")
            nho_mk = st.checkbox("Ghi nhớ tài khoản trên máy này")
            if st.button("🔑 Đăng nhập", type="primary", use_container_width=True):
                if u in st.session_state['users'] and st.session_state['users'][u]['pass'] == p:
                    st.session_state['current_user'] = u
                    if nho_mk: st.query_params['token_login'] = u
                    st.rerun()
                else: st.error("❌ Sai thông tin!")
        return False
    else:
        user_info = st.session_state['users'][st.session_state['current_user']]
        if role_can_thiet and user_info['role'] != role_can_thiet:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.error("🚫 Bạn đang dùng tài khoản không có quyền truy cập khu vực này!")
            # NÚT XÓA KẸT TOKEN
            if st.button("🔄 Thoát tài khoản cũ & Đăng nhập lại", type="primary"):
                st.session_state['current_user'] = None
                if 'token_login' in st.query_params: del st.query_params['token_login']
                st.rerun()
            return False
        return True

# ==========================================
# 1. TRANG CHỦ (LANDING PAGE) 
# ==========================================
if st.session_state['current_view'] == "landing_page":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color: {main_color}; font-weight: 800;'>🏫 HỆ THỐNG QUẢN TRỊ TÂM LÝ HỌC ĐƯỜNG AI</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #4B5563; margin-bottom: 50px;'>Nền tảng Lắng nghe, Chia sẻ và Phân tích Rủi ro Tâm lý Chuyên sâu</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.info("### 🎓 Cổng Học Sinh\nNơi các em chia sẻ khó khăn, ẩn danh và an toàn tuyệt đối.")
        if st.button("Học Sinh Truy Cập ➡️", use_container_width=True):
            st.session_state['current_view'] = "student_view"
            st.rerun()
    with col2:
        st.success("### 👨‍🏫 Cổng Giáo Viên\nQuản lý hồ sơ tâm lý và nhận gợi ý tư vấn từ AI.")
        if st.button("Giáo Viên Truy Cập ➡️", use_container_width=True):
            st.session_state['current_view'] = "teacher_view"
            st.rerun()
    with col3:
        st.warning("### ⚙️ Cổng BGH / Quản Trị\nThống kê dữ liệu, xuất báo cáo và Quản lý hệ thống.")
        if st.button("Ban Giám Hiệu Truy Cập ➡️", use_container_width=True):
            st.session_state['current_view'] = "admin_view"
            st.rerun()
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.caption("<div style='text-align: center;'>Phần mềm phát triển bởi: Lý Hoàng Anh | SĐT: 0969969189</div>", unsafe_allow_html=True)

# ==========================================
# 2. KHÔNG GIAN HỌC SINH 
# ==========================================
elif st.session_state['current_view'] == "student_view":
    if st.button("⬅️ Trở về Trang chủ"):
        st.session_state['current_view'] = "landing_page"
        st.rerun()
        
    st.markdown("<div class='top-title'>TRẠM TƯ VẤN HỌC ĐƯỜNG</div>", unsafe_allow_html=True)
    tab_gui, tab_xem = st.tabs(["📝 Gửi Tâm Sự", "💬 Phòng Chat"])
    with tab_gui:
        ma_xac_thuc = st.text_input("🔑 Mã bảo mật của trường:", type="password")
        hs_khoi_lop = st.text_input("Khối/Lớp của em (Không bắt buộc):")
        hs_cam_xuc = st.selectbox("Cảm xúc hiện tại?", ["😐 Bình thường", "😔 Buồn bã", "😰 Áp lực", "😡 Tức giận", "😨 Sợ hãi", "😭 Tuyệt vọng"])
        gv_duoc_chon = st.selectbox("Chọn Thầy/Cô:", options=list(danh_sach_gv.keys()), format_func=lambda x: danh_sach_gv[x])
        hinh_thuc_tv = st.radio("Hình thức:", ["💬 Nhắn tin trên web", "🤝 Hẹn gặp trực tiếp"])
        ngay_hen, gio_hen = "", ""
        if "Trực tiếp" in hinh_thuc_tv:
            c_ngay, c_gio = st.columns(2)
            ngay_hen, gio_hen = c_ngay.date_input("Ngày hẹn:"), c_gio.time_input("Giờ hẹn:")
            
        tam_su_input = st.text_area("Kể chi tiết câu chuyện:", height=100)
        if st.button("🚀 Gửi an toàn", type="primary"):
            if not ma_xac_thuc or ma_xac_thuc.upper() != MA_BAO_MAT_TRUONG: st.error("❌ Sai Mã bảo mật!")
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
            
        if 'ca_dang_xem' in st.session_state and st.session_state['ca_dang_xem'] in st.session_state['database']:
            ca = st.session_state['database'][st.session_state['ca_dang_xem']]
            st.markdown(f"### 💬 Chat với {st.session_state['users'][ca['gv_phu_trach']]['name']}")
            with st.container(height=350, border=True):
                for tn in ca['tin_nhan']:
                    with st.chat_message("user" if tn['nguoi_gui'] == "Học sinh" else "assistant"):
                        st.markdown(f"**{tn['nguoi_gui']}** <span style='font-size:0.8em; color:gray;'>{tn.get('thoi_gian', '')}</span>", unsafe_allow_html=True)
                        st.write(tn['noi_dung'])
            
            if ca['trang_thai'] != "Đã đóng ca":
                hs_phan_hoi = st.chat_input("Nhập tin nhắn...")
                if hs_phan_hoi:
                    ca['tin_nhan'].append({"nguoi_gui": "Học sinh", "noi_dung": hs_phan_hoi, "thoi_gian": datetime.datetime.now().strftime('%H:%M')})
                    ca['trang_thai'] = "HS vừa nhắn lại" 
                    ca['ai_phan_tich'] = None 
                    luu_du_lieu_len_may()
                    st.rerun()

# ==========================================
# 3. KHÔNG GIAN GIÁO VIÊN (ZALO TỶ LỆ VÀNG THEME ĐỘNG)
# ==========================================
elif st.session_state['current_view'] == "teacher_view":
    if kiem_tra_dang_nhap(role_can_thiet='teacher'):
        user_id = st.session_state['current_user']
        user_info = st.session_state['users'][user_id]
        phan_mem_hoat_dong = kiem_tra_ban_quyen_mem()
        if HAS_AUTOREFRESH: st_autorefresh(interval=6000, limit=None, key="gv_refresh") 

        st.markdown("<div class='top-title'>TRẠM TƯ VẤN</div>", unsafe_allow_html=True)

        w_menu = 1.6 if st.session_state['menu_expanded'] else 0.4
        w_inbox = 3.4 if st.session_state['inbox_expanded'] else 0.4
        w_chat = 12 - w_menu - w_inbox
        
        col_menu, col_danh_sach, col_chat = st.columns([w_menu, w_inbox, w_chat], gap="small")
        
        # --- CỘT 1: MENU SIDEBAR ---
        with col_menu:
            if st.session_state['menu_expanded']:
                c_btn_m1, c_btn_m2 = st.columns([4, 1])
                if c_btn_m2.button("◀", key="hide_menu", help="Thu gọn"): 
                    st.session_state['menu_expanded'] = False; st.rerun()
                
                if user_info.get('avatar'): st.markdown(f'<div style="text-align:center; margin-bottom: 10px;"><img src="data:image/png;base64,{user_info["avatar"]}" width="50" style="border-radius: 50%;"></div>', unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; font-size:13px; font-weight:bold; color:white; margin-bottom:10px;'>{user_info.get('name', 'Giáo viên')}</div>", unsafe_allow_html=True)
                
                if st.button("💬 Ca đang mở", key="m_mo"): st.session_state['menu_gv'] = "mo"
                if st.button("📦 Ca đã đóng", key="m_xong"): st.session_state['menu_gv'] = "xong"
                if st.button("👤 Hồ sơ", key="m_hs"): st.session_state['menu_gv'] = "ho_so"
                
                # TÍNH NĂNG CHỌN MÀU THEME CHO GIÁO VIÊN
                st.markdown("<hr style='margin: 10px 0; border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
                st.markdown("<div style='color:white; font-size:12px; text-align:center;'>Đổi Giao diện:</div>", unsafe_allow_html=True)
                st.session_state['theme_color'] = st.selectbox("", list(theme_map.keys()), index=list(theme_map.keys()).index(st.session_state['theme_color']), label_visibility="collapsed")
                
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("🚪 Đăng xuất", key="m_out"):
                    st.session_state['current_user'] = None
                    st.session_state['current_view'] = "landing_page"
                    if 'token_login' in st.query_params: del st.query_params['token_login']
                    st.rerun()
            else:
                if st.button("▶", key="show_menu", help="Mở Menu"): 
                    st.session_state['menu_expanded'] = True; st.rerun()
                if st.button("💬", key="m_mo2"): st.session_state['menu_gv'] = "mo"
                if st.button("📦", key="m_xong2"): st.session_state['menu_gv'] = "xong"
                if st.button("👤", key="m_hs2"): st.session_state['menu_gv'] = "ho_so"
                if st.button("🚪", key="m_out2"):
                    st.session_state['current_user'] = None
                    st.session_state['current_view'] = "landing_page"
                    if 'token_login' in st.query_params: del st.query_params['token_login']
                    st.rerun()

        if 'menu_gv' not in st.session_state: st.session_state['menu_gv'] = "mo"
        ca_cua_toi = {k: v for k, v in st.session_state['database'].items() if v['gv_phu_trach'] == user_id}
        ca_dang_mo = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] not in ["Đã đóng ca"]}
        ca_da_dong = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] == "Đã đóng ca"}

        # --- CỘT 2: DANH SÁCH (HỘP THƯ) ---
        with col_danh_sach:
            c_title, c_toggle = st.columns([5, 1])
            if st.session_state['inbox_expanded']:
                if c_toggle.button("◀", key="hide_inbox", help="Thu gọn"):
                    st.session_state['inbox_expanded'] = False; st.rerun()
                
                if st.session_state['menu_gv'] == "mo":
                    c_title.markdown(f"<b style='color:{main_color}; font-size:16px;'>📥 Hộp thư làm việc</b>", unsafe_allow_html=True)
                    if not phan_mem_hoat_dong: st.error("⛔ Hết hạn!")
                    
                    if not ca_dang_mo: st.info("Trống.")
                    else:
                        danh_sach_ca_sap_xep = sorted(ca_dang_mo.items(), key=lambda x: (0 if x[1]['trang_thai']=="HS vừa nhắn lại" else 1, x[0]), reverse=False)
                        with st.container(height=700, border=False):
                            for i, (ma_ca, ca) in enumerate(danh_sach_ca_sap_xep, 1):
                                thoi_gian_ca = ca['tin_nhan'][-1].get('thoi_gian', ca.get('thoi_gian', ''))[-5:]
                                if ca['trang_thai'] == "HS vừa nhắn lại": icon_tt = "🔴"
                                elif ca['trang_thai'] == "Chờ xử lý": icon_tt = "🟡"
                                else: icon_tt = "🟢"
                                    
                                tn_cuoi = ca['tin_nhan'][-1]['noi_dung']
                                tn_rut_gon = tn_cuoi[:35] + "..." if len(tn_cuoi) > 35 else tn_cuoi
                                
                                st.markdown('<div class="zalo-list-btn">', unsafe_allow_html=True)
                                btn_type = "primary" if st.session_state.get('active_chat') == ma_ca else "secondary"
                                if st.button(f"{i}. {icon_tt} **{ma_ca}** (Lớp {ca['lop']})\n<span style='font-size:12px; color:gray;'>🕒 {thoi_gian_ca} | 💬 {tn_rut_gon}</span>", key=f"btn_{ma_ca}", type=btn_type):
                                    st.session_state['active_chat'] = ma_ca
                                    st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)
                elif st.session_state['menu_gv'] == "xong":
                    c_title.markdown(f"<b style='color:{main_color}; font-size:16px;'>📦 Đã hoàn thành</b>", unsafe_allow_html=True)
                    with st.container(height=700, border=False):
                        for i, (ma_ca, ca) in enumerate(ca_da_dong.items(), 1):
                            st.markdown('<div class="zalo-list-btn">', unsafe_allow_html=True)
                            btn_type = "primary" if st.session_state.get('active_chat') == ma_ca else "secondary"
                            if st.button(f"{i}. {ma_ca} (Lớp {ca['lop']})\nĐã đóng hồ sơ", key=f"btn_{ma_ca}", type=btn_type):
                                st.session_state['active_chat'] = ma_ca; st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
            else:
                if st.button("▶", key="show_inbox", help="Mở Hộp thư"):
                    st.session_state['inbox_expanded'] = True; st.rerun()

        # --- CỘT 3: KHÔNG GIAN CHAT RỘNG RÃI ---
        with col_chat:
            if not phan_mem_hoat_dong: st.error("⛔ Phần mềm hết hạn Bản quyền. AI và Chat bị khóa.")
            
            if st.session_state['menu_gv'] in ["mo", "xong"]:
                ma_dang_chon = st.session_state.get('active_chat')
                
                if not ma_dang_chon or ma_dang_chon not in ca_cua_toi:
                    st.markdown("""<div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; text-align: center; color: #9CA3AF;'>
                        <h2>Chào buổi sáng! 🌻</h2><p>👉 Bấm vào một ca bất kỳ ở Hộp thư để bắt đầu làm việc.</p></div>""", unsafe_allow_html=True)
                else:
                    ca_hien_tai = ca_cua_toi[ma_dang_chon]
                    
                    c_head1, c_head2 = st.columns([5, 1])
                    c_head1.markdown(f"<h4 style='margin-bottom:0; color:{main_color};'>🗣️ {ma_dang_chon} | Lớp {ca_hien_tai['lop']} | 🎭 Cảm xúc ban đầu: {ca_hien_tai.get('cam_xuc_ban_dau', 'N/A')}</h4>", unsafe_allow_html=True)
                    c_head1.caption(f"**Gốc:** {ca_hien_tai['tin_nhan'][0]['noi_dung'][:80]}...")
                    
                    if ca_hien_tai['trang_thai'] != "Đã đóng ca":
                        if c_head2.button("📦 Đóng ca này", use_container_width=True):
                            ca_hien_tai['trang_thai'] = "Đã đóng ca"
                            st.session_state['active_chat'] = None
                            luu_du_lieu_len_may()
                            st.rerun()
                            
                    st.markdown("<hr style='margin-top:5px; margin-bottom:10px;'>", unsafe_allow_html=True)
                    
                    if "Trực tiếp" in ca_hien_tai.get('hinh_thuc', ''):
                        st.error(f"⏰ **Hẹn gặp trực tiếp lúc:** {ca_hien_tai.get('lich_hen', '')}")
                    
                    with st.container(height=350, border=False):
                        for tn in ca_hien_tai['tin_nhan']:
                            with st.chat_message("user" if tn['nguoi_gui'] == "Học sinh" else "assistant"):
                                tg = tn.get('thoi_gian', '')
                                st.markdown(f"**{tn['nguoi_gui']}** <span style='font-size:0.8em; color:gray;'>{tg}</span>", unsafe_allow_html=True)
                                st.write(tn['noi_dung'])
                                
                    if phan_mem_hoat_dong and ca_hien_tai['trang_thai'] != "Đã đóng ca":
                        if ca_hien_tai.get('ai_phan_tich'):
                            st.success(f"✨ **AI CỐ VẤN:**\n\n{ca_hien_tai['ai_phan_tich']}")
                            if st.button("🗑️ Xóa kết quả phân tích để gọn màn hình"):
                                ca_hien_tai['ai_phan_tich'] = None
                                luu_du_lieu_len_may()
                                st.rerun()
                                
                        if not ca_hien_tai.get('ai_phan_tich'):
                            if st.button("🧠 AI Phân tích các tin nhắn mới nhất", type="secondary"):
                                with st.spinner("AI đang làm việc..."):
                                    tin_nhan_moi_lien_tiep = []
                                    for t in reversed(ca_hien_tai['tin_nhan']):
                                        if t['nguoi_gui'] == "Học sinh": tin_nhan_moi_lien_tiep.insert(0, t['noi_dung'])
                                        else: break 
                                    cum_tin_nhan_moi = "\n".join(tin_nhan_moi_lien_tiep)
                                    
                                    lich_su_cu_len = len(ca_hien_tai['tin_nhan']) - len(tin_nhan_moi_lien_tiep)
                                    lich_su_cu = ""
                                    if lich_su_cu_len > 0:
                                        for t in ca_hien_tai['tin_nhan'][:lich_su_cu_len]: lich_su_cu += f"{t['nguoi_gui']}: {t['noi_dung']}\n"
                                    
                                    prompt = f"""[BỐI CẢNH CŨ]: {lich_su_cu if lich_su_cu else 'Không.'}
                                    [TIN MỚI LIÊN TIẾP]: "{cum_tin_nhan_moi}"
                                    1. CHỈ PHÂN TÍCH THÁI ĐỘ TRONG CỤM TIN MỚI NÀY.
                                    2. Nếu tin mới là: cảm ơn, vâng dạ, đã hiểu -> BẮT BUỘC RỦI RO: Thấp.
                                    Trả lời:
                                    [RỦI RO]: Thấp/Trung/Cao
                                    [PHÂN TÍCH NHANH]: ...
                                    [GỢI Ý TRẢ LỜI]: ..."""
                                    
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
                                                thanh_cong = True
                                                break  
                                        if not thanh_cong: ca_hien_tai['ai_phan_tich'] = "⏳ **LỖI 20 LẦN/NGÀY:** Vui lòng dùng API Key Gmail dự phòng."
                                        luu_du_lieu_len_may()
                                        st.rerun()
                                    except Exception as e: st.error(f"Lỗi: {e}")
                                
                        gv_tra_loi = st.chat_input("Nhập tin nhắn gửi học sinh (Ấn Enter để gửi)...")
                        if gv_tra_loi:
                            ca_hien_tai['tin_nhan'].append({"nguoi_gui": "Giáo viên", "noi_dung": gv_tra_loi, "thoi_gian": datetime.datetime.now().strftime('%H:%M')})
                            ca_hien_tai['trang_thai'] = "GV đã phản hồi"
                            ca_hien_tai['ai_phan_tich'] = None 
                            luu_du_lieu_len_may()
                            st.rerun()

            elif st.session_state['menu_gv'] == "ho_so":
                st.subheader("👤 Cập nhật Hồ sơ & Ảnh Đại Diện")
                c_img, c_info = st.columns([1, 2])
                with c_img:
                    if user_info.get('avatar'): st.markdown(f'<img src="data:image/png;base64,{user_info["avatar"]}" width="150" style="border-radius: 10px;">', unsafe_allow_html=True)
                    file_anh = st.file_uploader("Tải ảnh mới", type=['png', 'jpg', 'jpeg'])
                with c_info:
                    new_name = st.text_input("Họ tên:", value=user_info.get('name', ''))
                    new_phone = st.text_input("SĐT:", value=user_info.get('phone', ''))
                    new_pw = st.text_input("Mật khẩu mới:", type="password")
                if st.button("💾 Lưu thay đổi", type="primary"):
                    st.session_state['users'][user_id]['name'] = new_name
                    st.session_state['users'][user_id]['phone'] = new_phone
                    if new_pw: st.session_state['users'][user_id]['pass'] = new_pw
                    if file_anh is not None: st.session_state['users'][user_id]['avatar'] = base64.b64encode(file_anh.read()).decode('utf-8')
                    luu_du_lieu_len_may()
                    st.success("✅ Cập nhật thành công!")
                    st.rerun()

# ==========================================
# 4. KHÔNG GIAN BẢN QUẢN LÝ (ADMIN)
# ==========================================
elif st.session_state['current_view'] == "admin_view":
    if kiem_tra_dang_nhap(role_can_thiet='admin'):
        user_hien_tai = st.session_state['current_user']
        phan_mem_hoat_dong = kiem_tra_ban_quyen_mem()
        
        st.markdown("<div class='top-title'>TRUNG TÂM QUẢN TRỊ</div>", unsafe_allow_html=True)
        col_menu_ad, col_main_ad = st.columns([1.5, 8.5], gap="small")
        
        with col_menu_ad:
            st.markdown(f"<div style='text-align:center;'><b>⚙️ {st.session_state['users'][user_hien_tai]['name']}</b></div>", unsafe_allow_html=True)
            st.markdown("---")
            danh_muc_admin = ["📊 Thống kê", "👥 Quản lý Nhân sự", "📥 Xuất Báo cáo"]
            if user_hien_tai == "admin": danh_muc_admin.append("🔑 Nhập Mã Gia hạn")
            if user_hien_tai == "hoanganh_dev": danh_muc_admin.append("🛠️ TÁC GIẢ: Cấp Key")
                
            menu_admin = st.radio("🧭 MENU", danh_muc_admin, label_visibility="collapsed")
            st.markdown("---")
            if st.button("🚪 Đăng xuất", use_container_width=True):
                st.session_state['current_user'] = None
                st.session_state['current_view'] = "landing_page"
                if 'token_login' in st.query_params: del st.query_params['token_login']
                st.rerun()

        with col_main_ad:
            if HAS_AUTOREFRESH: st_autorefresh(interval=10000, limit=None, key="admin_refresh")
            if not phan_mem_hoat_dong and user_hien_tai != "hoanganh_dev": st.error("⛔ PHẦN MỀM CHƯA KÍCH HOẠT HOẶC ĐÃ HẾT HẠN.")
                
            tong_ca = len(st.session_state['database'])
            ca_khan_cap = len([ca for ca in st.session_state['database'].values() if "Cao" in ca['muc_do_rui_ro']])
            danh_sach_tai_khoan_gv = [k for k, v in st.session_state['users'].items() if v['role'] == 'teacher']

            if menu_admin == "📊 Thống kê":
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("Tổng số ca tiếp nhận", f"{tong_ca} ca")
                c_b.metric("Ca Khẩn cấp", f"{ca_khan_cap} ca", delta="Cảnh báo", delta_color="inverse")
                c_c.metric("Nhân sự", f"{len(danh_sach_tai_khoan_gv)} GV")

            elif menu_admin == "👥 Quản lý Nhân sự":
                st.write("👉 **Sửa hồ sơ / Đổi mật khẩu Giáo viên**")
                if danh_sach_tai_khoan_gv:
                    gv_can_sua = st.selectbox("Chọn tài khoản:", options=danh_sach_tai_khoan_gv)
                    c_edit1, c_edit2, c_edit3 = st.columns(3)
                    ten_moi = c_edit1.text_input("Tên mới:", value=st.session_state['users'][gv_can_sua].get('name',''))
                    pass_moi = c_edit2.text_input("Mật khẩu mới:", value=st.session_state['users'][gv_can_sua]['pass'])
                    if c_edit3.button("💾 Lưu", type="primary"):
                        st.session_state['users'][gv_can_sua]['name'] = ten_moi
                        st.session_state['users'][gv_can_sua]['pass'] = pass_moi
                        luu_du_lieu_len_may(); st.rerun()
                st.write("👉 **Tạo tài khoản Giáo viên mới:**")
                c_add1, c_add2, c_add3 = st.columns(3)
                new_id = c_add1.text_input("Tên đăng nhập mới")
                new_name = c_add2.text_input("Tên hiển thị")
                new_pass = c_add3.text_input("Mật khẩu")
                if st.button("➕ Tạo tài khoản"):
                    st.session_state['users'][new_id] = {'pass': new_pass, 'role': 'teacher', 'name': new_name, 'avatar': '', 'phone': '', 'email': ''}
                    luu_du_lieu_len_may(); st.rerun()

            elif menu_admin == "📥 Xuất Báo cáo":
                if tong_ca > 0:
                    du_lieu_xuat = [{"Mã Hồ Sơ": k, "Thời gian": v['thoi_gian'], "Lớp": v['lop'], "Cảm xúc": v.get('cam_xuc_ban_dau', ''), "Rủi ro": v['muc_do_rui_ro'], "Trạng thái": v['trang_thai']} for k, v in st.session_state['database'].items()]
                    st.download_button("📥 Tải File CSV", data=pd.DataFrame(du_lieu_xuat).to_csv(index=False).encode('utf-8-sig'), file_name="Bao_Cao.csv", mime="text/csv", type="primary")

            elif menu_admin == "🔑 Nhập Mã Gia hạn":
                st.write(f"**Mã đang dùng:** `{st.session_state['config'].get('active_key', '')}`")
                new_key = st.text_input("Nhập Mã Bản Quyền mới:")
                if st.button("🚀 Kích hoạt", type="primary"):
                    if new_key in st.session_state['licenses'] and st.session_state['licenses'][new_key]['active']:
                        st.session_state['config']['active_key'] = new_key
                        luu_du_lieu_len_may(); st.rerun()
                    else: st.error("❌ Mã Bản Quyền không hợp lệ!")

            elif menu_admin == "🛠️ TÁC GIẢ: Cấp Key":
                for key, data in st.session_state['licenses'].items():
                    trang_thai = "🟢 HĐ" if data['active'] else "🔴 Khóa"
                    with st.expander(f"{data['school_name']} | {key} | {data['expiry_date']} | {trang_thai}"):
                        c1, c2 = st.columns(2)
                        if c1.button("Gia hạn 1 Năm", key=f"gh_{key}"):
                            st.session_state['licenses'][key]['expiry_date'] = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y')
                            st.session_state['licenses'][key]['active'] = True
                            luu_du_lieu_len_may(); st.rerun()
                        if c2.button("Khóa Key", key=f"lock_{key}"):
                            st.session_state['licenses'][key]['active'] = False
                            luu_du_lieu_len_may(); st.rerun()
                st.write("👉 **Tạo Mã Bản Quyền Mới:**")
                new_school = st.text_input("Tên trường đối tác:")
                if st.button("➕ Tạo Key Mới", type="primary"):
                    st.session_state['licenses'][f"KEY-{random.randint(10000, 99999)}"] = {'school_name': new_school, 'expiry_date': (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y'), 'active': True}
                    luu_du_lieu_len_may(); st.rerun()