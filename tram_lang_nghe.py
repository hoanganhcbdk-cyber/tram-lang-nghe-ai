import streamlit as st
import datetime
import random
import pandas as pd
import requests
import base64

# ==========================================
# CẤU HÌNH HỆ THỐNG & CSS TÙY CHỈNH (ULTRA ZALO)
# ==========================================
st.set_page_config(page_title="Hệ thống Quản trị Tâm lý Học đường AI", page_icon="🏫", layout="wide", initial_sidebar_state="collapsed")

# CSS ÉP GIAO DIỆN TRÀN VIỀN KỊCH TRẦN & NÚT BẤM DÍNH SÁT
st.markdown("""
    <style>
    /* Ép kịch trần, bỏ khoảng trắng trên cùng */
    .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Ẩn Header mặc định của Streamlit */
    header { visibility: hidden !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    
    /* CSS Ép các nút trong danh sách sát nhau */
    .zalo-list-btn button {
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: 1px solid #E5E7EB !important;
        border-radius: 0px !important;
        padding: 8px 5px !important;
        margin: 0px !important;
        color: #1f2937 !important;
        line-height: 1.4 !important;
    }
    .zalo-list-btn button:hover { background-color: #F3F4F6 !important; }
    
    /* CSS cho các nút thu gọn siêu nhỏ */
    .tiny-btn button {
        padding: 0px !important;
        border: none !important;
        background: transparent !important;
        color: #9CA3AF !important;
        font-size: 12px !important;
    }
    .tiny-btn button:hover { color: #3B82F6 !important; }
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
FIREBASE_URL = "https://tram-lang-nghe-data-default-rtdb.firebaseio.com"

# ==========================================
# KẾT NỐI BỘ NHỚ VĨNH VIỄN (FIREBASE)
# ==========================================
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
if 'active_chat' not in st.session_state: st.session_state['active_chat'] = None 
if 'menu_expanded' not in st.session_state: st.session_state['menu_expanded'] = True 
if 'inbox_expanded' not in st.session_state: st.session_state['inbox_expanded'] = True 

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
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.warning("🔒 Vui lòng đăng nhập để truy cập hệ thống quản trị.")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            u = st.text_input("Tài khoản đăng nhập", key=f"user_{role_can_thiet}")
            p = st.text_input("Mật khẩu", type="password", key=f"pass_{role_can_thiet}")
            if st.button("🔑 Đăng nhập hệ thống", type="primary", use_container_width=True):
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

# ==========================================
# 1. TRANG CHỦ (LANDING PAGE) 
# ==========================================
if st.session_state['current_view'] == "landing_page":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-weight: 800;'>🏫 HỆ THỐNG QUẢN TRỊ TÂM LÝ HỌC ĐƯỜNG AI</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #4B5563; margin-bottom: 50px;'>Nền tảng Lắng nghe, Chia sẻ và Phân tích Rủi ro Tâm lý Chuyên sâu</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
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
        st.warning("### ⚙️ Cổng BGH / Quản Trị\nThống kê dữ liệu, xuất báo cáo và Quản lý hệ thống toàn trường.")
        if st.button("Ban Giám Hiệu Truy Cập ➡️", use_container_width=True):
            st.session_state['current_view'] = "admin_view"
            st.rerun()
            
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.caption("<div style='text-align: center;'>Phần mềm được phát triển bởi: Lý Hoàng Anh | SĐT: 0969969189</div>", unsafe_allow_html=True)

# ==========================================
# 2. KHÔNG GIAN HỌC SINH 
# ==========================================
elif st.session_state['current_view'] == "student_view":
    c_btn, c_blank = st.columns([1, 5])
    if c_btn.button("⬅️ Trở về Trang chủ"):
        st.session_state['current_view'] = "landing_page"
        st.rerun()
        
    st.title("🎓 CỔNG KẾT NỐI TÂM LÝ HỌC SINH")
    
    tab_gui, tab_xem = st.tabs(["📝 Gửi Lời Tâm Sự Mới", "💬 Phòng Chat Của Em"])
    with tab_gui:
        ma_xac_thuc = st.text_input("🔑 Nhập Mã bảo mật của trường (Hỏi GVCN nếu em không biết):", type="password")
        hs_khoi_lop = st.text_input("Khối/Lớp của em (Không bắt buộc):")
        hs_cam_xuc = st.selectbox("Ngay lúc này, em đang cảm thấy thế nào?", 
                                  ["😐 Bình thường", "😔 Hơi buồn, suy tư", "😰 Căng thẳng, áp lực thi cử", "😡 Tức giận, uất ức", "😨 Sợ hãi, lo âu", "😭 Tuyệt vọng, cần giúp đỡ gấp"])
        
        gv_duoc_chon = st.selectbox("Em muốn tâm sự với thầy cô nào?", options=list(danh_sach_gv.keys()), format_func=lambda x: danh_sach_gv[x])
        st.markdown("---")
        hinh_thuc_tv = st.radio("Em muốn thầy cô hỗ trợ theo hình thức nào?", ["💬 Tư vấn Gián tiếp (Nhắn tin trên web)", "🤝 Tư vấn Trực tiếp (Hẹn gặp mặt tại phòng Tâm lý)"])
        
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
# 3. KHÔNG GIAN GIÁO VIÊN (ULTRA ZALO 3 CỘT)
# ==========================================
elif st.session_state['current_view'] == "teacher_view":
    if kiem_tra_dang_nhap(role_can_thiet='teacher'):
        user_id = st.session_state['current_user']
        user_info = st.session_state['users'][user_id]
        phan_mem_hoat_dong = kiem_tra_ban_quyen_mem()
        
        if HAS_AUTOREFRESH: st_autorefresh(interval=6000, limit=None, key="gv_refresh") 

        # ĐỘ RỘNG 3 CỘT DỰA TRÊN TRẠNG THÁI ẨN/HIỆN
        w_menu = 1.5 if st.session_state['menu_expanded'] else 0.4
        w_inbox = 3.5 if st.session_state['inbox_expanded'] else 0.4
        w_chat = 10 - w_menu - w_inbox
        
        col_menu, col_danh_sach, col_chat = st.columns([w_menu, w_inbox, w_chat], gap="small")
        
        # --- CỘT 1: MENU SIDEBAR ---
        with col_menu:
            st.markdown('<div class="tiny-btn">', unsafe_allow_html=True)
            if st.session_state['menu_expanded']:
                c_btn_m1, c_btn_m2 = st.columns([4, 1])
                if c_btn_m2.button("◀", key="hide_menu", help="Thu gọn Menu"): 
                    st.session_state['menu_expanded'] = False
                    st.rerun()
                if user_info.get('avatar'):
                    st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{user_info["avatar"]}" width="60" style="border-radius: 50%;"></div>', unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; font-size:14px; font-weight:bold; color:#1E3A8A; margin-bottom:10px;'>{user_info.get('name', 'Giáo viên')}</div>", unsafe_allow_html=True)
                
                if st.button("💬 Ca đang mở", use_container_width=True): st.session_state['menu_gv'] = "mo"
                if st.button("📦 Ca đã đóng", use_container_width=True): st.session_state['menu_gv'] = "xong"
                if st.button("👤 Hồ sơ", use_container_width=True): st.session_state['menu_gv'] = "ho_so"
                if st.button("🚪 Đăng xuất", use_container_width=True):
                    st.session_state['current_user'] = None
                    st.session_state['active_chat'] = None
                    st.session_state['current_view'] = "landing_page"
                    st.rerun()
            else:
                if st.button("▶", key="show_menu", help="Mở rộng Menu"): 
                    st.session_state['menu_expanded'] = True
                    st.rerun()
                if st.button("💬", use_container_width=True): st.session_state['menu_gv'] = "mo"
                if st.button("📦", use_container_width=True): st.session_state['menu_gv'] = "xong"
                if st.button("👤", use_container_width=True): st.session_state['menu_gv'] = "ho_so"
                if st.button("🚪", use_container_width=True):
                    st.session_state['current_user'] = None
                    st.session_state['current_view'] = "landing_page"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        if 'menu_gv' not in st.session_state: st.session_state['menu_gv'] = "mo"
        
        ca_cua_toi = {k: v for k, v in st.session_state['database'].items() if v['gv_phu_trach'] == user_id}
        ca_dang_mo = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] not in ["Đã đóng ca"]}
        ca_da_dong = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] == "Đã đóng ca"}

        # --- CỘT 2: DANH SÁCH (HỘP THƯ LÀM VIỆC) ---
        with col_danh_sach:
            st.markdown('<div class="tiny-btn">', unsafe_allow_html=True)
            c_title, c_toggle = st.columns([5, 1])
            if st.session_state['inbox_expanded']:
                c_title.markdown("<b style='color:#374151; font-size:16px;'>📥 Hộp thư</b>", unsafe_allow_html=True)
                if c_toggle.button("◀", key="hide_inbox", help="Thu gọn Hộp thư"):
                    st.session_state['inbox_expanded'] = False
                    st.rerun()
                    
                if st.session_state['menu_gv'] == "mo":
                    if not ca_dang_mo: st.info("Trống.")
                    else:
                        danh_sach_ca_sap_xep = sorted(ca_dang_mo.items(), key=lambda x: (0 if x[1]['trang_thai']=="HS vừa nhắn lại" else 1, x[0]), reverse=False)
                        with st.container(height=650, border=False):
                            for i, (ma_ca, ca) in enumerate(danh_sach_ca_sap_xep, 1):
                                thoi_gian_ca = ca['tin_nhan'][-1].get('thoi_gian', ca.get('thoi_gian', ''))[-5:]
                                if ca['trang_thai'] == "HS vừa nhắn lại": icon_tt = "🔴 [TIN MỚI]"
                                elif ca['trang_thai'] == "Chờ xử lý": icon_tt = "🟡 [LẦN ĐẦU]"
                                else: icon_tt = "🟢 [THEO DÕI]"
                                    
                                tn_cuoi = ca['tin_nhan'][-1]['noi_dung']
                                tn_rut_gon = tn_cuoi[:35] + "..." if len(tn_cuoi) > 35 else tn_cuoi
                                
                                st.markdown('<div class="zalo-list-btn">', unsafe_allow_html=True)
                                btn_type = "primary" if st.session_state.get('active_chat') == ma_ca else "secondary"
                                if st.button(f"**{i}. {icon_tt} {ma_ca}**\n🕒 {thoi_gian_ca} | 💬 {tn_rut_gon}", key=f"btn_{ma_ca}", type=btn_type):
                                    st.session_state['active_chat'] = ma_ca
                                    st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)
                elif st.session_state['menu_gv'] == "xong":
                    with st.container(height=650, border=False):
                        for i, (ma_ca, ca) in enumerate(ca_da_dong.items(), 1):
                            st.markdown('<div class="zalo-list-btn">', unsafe_allow_html=True)
                            btn_type = "primary" if st.session_state.get('active_chat') == ma_ca else "secondary"
                            if st.button(f"**{i}. {ma_ca}** (Lớp {ca['lop']})\nĐã đóng hồ sơ", key=f"btn_{ma_ca}", type=btn_type):
                                st.session_state['active_chat'] = ma_ca
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
            else:
                if st.button("▶", key="show_inbox", help="Mở Hộp thư"):
                    st.session_state['inbox_expanded'] = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # --- CỘT 3: KHÔNG GIAN LÀM VIỆC CHÍNH ---
        with col_chat:
            if st.session_state['menu_gv'] in ["mo", "xong"]:
                ma_dang_chon = st.session_state.get('active_chat')
                
                if not ma_dang_chon or ma_dang_chon not in ca_cua_toi:
                    st.markdown("""
                    <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; text-align: center; color: #9CA3AF;'>
                        <h2>Chào buổi sáng, Thầy/Cô! 🌻</h2>
                        <p>👉 Bấm vào một ca bất kỳ ở cột hộp thư để bắt đầu làm việc.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    ca_hien_tai = ca_cua_toi[ma_dang_chon]
                    
                    # HEADER GIÀU THÔNG TIN
                    c_head1, c_head2 = st.columns([5, 1])
                    c_head1.markdown(f"<h4 style='margin-bottom:0;'>🗣️ {ma_dang_chon} | Lớp {ca_hien_tai['lop']} | 🎭 Cảm xúc: {ca_hien_tai.get('cam_xuc_ban_dau', 'N/A')}</h4>", unsafe_allow_html=True)
                    c_head1.caption(f"**Vấn đề gốc:** {ca_hien_tai['tin_nhan'][0]['noi_dung'][:80]}...")
                    
                    if ca_hien_tai['trang_thai'] != "Đã đóng ca":
                        if c_head2.button("📦 Đóng ca này", use_container_width=True):
                            ca_hien_tai['trang_thai'] = "Đã đóng ca"
                            st.session_state['active_chat'] = None
                            luu_du_lieu_len_may()
                            st.rerun()
                            
                    st.markdown("<hr style='margin-top:0; margin-bottom:10px;'>", unsafe_allow_html=True)
                    
                    # LỊCH SỬ CHAT
                    with st.container(height=350, border=False):
                        for tn in ca_hien_tai['tin_nhan']:
                            with st.chat_message("user" if tn['nguoi_gui'] == "Học sinh" else "assistant"):
                                tg = tn.get('thoi_gian', '')
                                st.markdown(f"**{tn['nguoi_gui']}** <span style='font-size:0.8em; color:gray;'>{tg}</span>", unsafe_allow_html=True)
                                st.write(tn['noi_dung'])
                                
                    # KHỐI PHÂN TÍCH AI GHIM CỐ ĐỊNH
                    if phan_mem_hoat_dong and ca_hien_tai['trang_thai'] != "Đã đóng ca":
                        if ca_hien_tai.get('ai_phan_tich'):
                            st.success(f"✨ **AI CỐ VẤN:**\n\n{ca_hien_tai['ai_phan_tich']}")
                            if st.button("🗑️ Xóa kết quả phân tích để gọn màn hình"):
                                ca_hien_tai['ai_phan_tich'] = None
                                luu_du_lieu_len_may()
                                st.rerun()
                                
                        if not ca_hien_tai.get('ai_phan_tich'):
                            if st.button("🧠 AI Đọc & Phân tích các tin nhắn mới nhất", type="secondary"):
                                with st.spinner("AI đang làm việc..."):
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
                                        if not thanh_cong: ca_hien_tai['ai_phan_tich'] = "⏳ **LỖI 20 LẦN/NGÀY:** Vui lòng dùng Key Gmail dự phòng."
                                        luu_du_lieu_len_may()
                                        st.rerun()
                                    except Exception as e: st.error(f"Lỗi: {e}")
                                
                        # KHUNG NHẬP CHAT
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
                    new_phone = st.text_input("SĐT (Zalo):", value=user_info.get('phone', ''))
                    new_pw = st.text_input("Mật khẩu mới (Bỏ trống nếu không đổi):", type="password")
                if st.button("💾 Lưu thay đổi", type="primary"):
                    st.session_state['users'][user_id]['name'] = new_name
                    st.session_state['users'][user_id]['phone'] = new_phone
                    if new_pw: st.session_state['users'][user_id]['pass'] = new_pw
                    if file_anh is not None: st.session_state['users'][user_id]['avatar'] = base64.b64encode(file_anh.read()).decode('utf-8')
                    luu_du_lieu_len_may()
                    st.rerun()

# ==========================================
# 4. KHÔNG GIAN BẢN QUẢN LÝ (ADMIN)
# ==========================================
elif st.session_state['current_view'] == "admin_view":
    if kiem_tra_dang_nhap(role_can_thiet='admin'):
        user_hien_tai = st.session_state['current_user']
        phan_mem_hoat_dong = kiem_tra_ban_quyen_mem()
        
        col_menu_ad, col_main_ad = st.columns([1.5, 8.5], gap="small")
        
        with col_menu_ad:
            st.markdown(f"<div style='text-align:center;'><b>⚙️ {st.session_state['users'][user_hien_tai]['name']}</b></div>", unsafe_allow_html=True)
            st.markdown("---")
            danh_muc_admin = ["📊 Thống kê", "👥 Quản lý Nhân sự", "📥 Xuất Báo cáo", "🔐 Đổi Mật khẩu"]
            if user_hien_tai == "admin": danh_muc_admin.append("🔑 Nhập Mã Gia hạn")
            if user_hien_tai == "hoanganh_dev": danh_muc_admin.append("🛠️ NHÀ PHÁT TRIỂN: Cấp Key")
                
            menu_admin = st.radio("🧭 MENU QUẢN TRỊ", danh_muc_admin, label_visibility="collapsed")
            st.markdown("---")
            if st.button("🚪 Đăng xuất", use_container_width=True):
                st.session_state['current_user'] = None
                st.session_state['current_view'] = "landing_page"
                st.rerun()

        with col_main_ad:
            if HAS_AUTOREFRESH: st_autorefresh(interval=10000, limit=None, key="admin_refresh")
            st.title("⚙️ TRUNG TÂM QUẢN TRỊ HỆ THỐNG")
            
            if not phan_mem_hoat_dong and user_hien_tai != "hoanganh_dev":
                st.error("⛔ PHẦN MỀM ĐÃ HẾT HẠN HOẶC CHƯA KÍCH HOẠT BẢN QUYỀN CHÍNH THỨC.")
                
            tong_ca = len(st.session_state['database'])
            ca_khan_cap = len([ca for ca in st.session_state['database'].values() if "Cao" in ca['muc_do_rui_ro']])
            ca_tb = len([ca for ca in st.session_state['database'].values() if "Trung bình" in ca['muc_do_rui_ro']])
            ca_thap = len([ca for ca in st.session_state['database'].values() if "Thấp" in ca['muc_do_rui_ro']])
            ca_cho = tong_ca - ca_khan_cap - ca_tb - ca_thap 
            danh_sach_tai_khoan_gv = [k for k, v in st.session_state['users'].items() if v['role'] == 'teacher']

            if menu_admin == "📊 Thống kê":
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("Tổng số ca tiếp nhận", f"{tong_ca} ca")
                c_b.metric("Ca Khẩn cấp", f"{ca_khan_cap} ca")
                c_c.metric("Nhân sự", f"{len(danh_sach_tai_khoan_gv)} GV")
                if tong_ca > 0:
                    chart_data = pd.DataFrame({"Mức độ": ["Cao", "Trung", "Thấp", "Chưa phân tích"], "Số lượng": [ca_khan_cap, ca_tb, ca_thap, ca_cho]})
                    st.bar_chart(chart_data.set_index("Mức độ"), color="#3B82F6")

            elif menu_admin == "👥 Quản lý Nhân sự":
                st.write("👉 **Sửa hồ sơ / Đổi mật khẩu Giáo viên**")
                if danh_sach_tai_khoan_gv:
                    gv_can_sua = st.selectbox("Chọn tài khoản:", options=danh_sach_tai_khoan_gv, format_func=lambda x: f"{x} ({st.session_state['users'][x].get('name','')})")
                    c_edit1, c_edit2, c_edit3 = st.columns(3)
                    ten_moi = c_edit1.text_input("Tên mới:", value=st.session_state['users'][gv_can_sua].get('name',''))
                    pass_moi = c_edit2.text_input("Pass mới:", value=st.session_state['users'][gv_can_sua]['pass'])
                    if c_edit3.button("💾 Lưu", type="primary"):
                        st.session_state['users'][gv_can_sua]['name'] = ten_moi
                        st.session_state['users'][gv_can_sua]['pass'] = pass_moi
                        luu_du_lieu_len_may()
                        st.rerun()

            elif menu_admin == "📥 Xuất Báo cáo":
                if tong_ca > 0:
                    du_lieu_xuat = []
                    for ma_ca, ca in st.session_state['database'].items():
                        du_lieu_xuat.append({
                            "Mã": ma_ca, "TG": ca['thoi_gian'], "Lớp": ca['lop'],
                            "Cảm xúc": ca.get('cam_xuc_ban_dau', 'N/A'), "Rủi ro": ca['muc_do_rui_ro'], "Trạng thái": ca['trang_thai']
                        })
                    df_export = pd.DataFrame(du_lieu_xuat)
                    csv = df_export.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Tải Báo cáo", data=csv, file_name="Bao_Cao.csv", mime="text/csv", type="primary")

            elif menu_admin == "🔐 Đổi Mật khẩu Admin":
                admin_new_pass = st.text_input("Mật khẩu Admin mới:", type="password")
                if st.button("🔑 Cập nhật", type="primary"):
                    st.session_state['users'][user_hien_tai]['pass'] = admin_new_pass
                    luu_du_lieu_len_may()
                    st.success("Thành công!")

            elif menu_admin == "🔑 Nhập Mã Gia hạn":
                current_key = st.session_state['config'].get('active_key', '')
                st.write(f"**Mã đang dùng:** `{current_key}`")
                new_key = st.text_input("Nhập Mã Bản Quyền mới:")
                if st.button("🚀 Kích hoạt", type="primary"):
                    if new_key in st.session_state['licenses'] and st.session_state['licenses'][new_key]['active']:
                        st.session_state['config']['active_key'] = new_key
                        luu_du_lieu_len_may()
                        st.rerun()

            elif menu_admin == "🛠️ NHÀ PHÁT TRIỂN: Cấp Key":
                for key, data in st.session_state['licenses'].items():
                    trang_thai = "🟢 HĐ" if data['active'] else "🔴 Khóa"
                    with st.expander(f"{data['school_name']} | {key} | {data['expiry_date']} | {trang_thai}"):
                        if st.button("Gia hạn 1 Năm", key=f"gh_{key}"):
                            st.session_state['licenses'][key]['expiry_date'] = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y')
                            st.session_state['licenses'][key]['active'] = True
                            luu_du_lieu_len_may()
                            st.rerun()
                new_school = st.text_input("Tên trường mới:")
                if st.button("➕ Tạo Key Mới", type="primary"):
                    tao_ma_moi = f"KEY-{random.randint(10000, 99999)}"
                    st.session_state['licenses'][tao_ma_moi] = {'school_name': new_school, 'expiry_date': (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d/%m/%Y'), 'active': True}
                    luu_du_lieu_len_may()
                    st.rerun()