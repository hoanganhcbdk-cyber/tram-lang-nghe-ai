import streamlit as st
import datetime
import random
import pandas as pd
import requests

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
API_KEY = st.secrets["API_KEY"]
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
            st.