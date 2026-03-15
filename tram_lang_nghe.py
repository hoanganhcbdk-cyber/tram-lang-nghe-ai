import streamlit as st
import datetime
import random
import pandas as pd
import requests

# ==========================================
# CẤU HÌNH HỆ THỐNG & API
# ==========================================
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
    
st.set_page_config(page_title="Trạm Lắng Nghe AI - Bản Chuyên Nghiệp", page_icon="🏫", layout="wide", initial_sidebar_state="expanded")

def gui_thong_bao_ve_dien_thoai(tin_nhan_bao_cao):
    try:
        bot_token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")
        if bot_token and chat_id:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": tin_nhan_bao_cao, "parse_mode": "Markdown"}
            requests.post(url, json=payload, timeout=3)
    except: pass

def tu_dong_cap_nhat_du_lieu(giay=30):
    st.components.v1.html(
        f"<script>setTimeout(function() {{ window.parent.location.reload(); }}, {giay * 1000});</script>",
        height=0, width=0,
    )

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

if 'he_thong_da_khoi_dong' not in st.session_state:
    du_lieu_dam_may = tai_du_lieu_tu_may()
    if du_lieu_dam_may:
        st.session_state['users'] = du_lieu_dam_may.get('users', {})
        st.session_state['database'] = du_lieu_dam_may.get('database', {})
    else:
        st.session_state['users'] = {
            'admin': {'pass': 'admin123', 'role': 'admin', 'name': 'Ban Giám Hiệu'},
            'gv01': {'pass': '1111', 'role': 'teacher', 'name': 'Thầy Lý Hoàng Anh'},
            'gv02': {'pass': '2222', 'role': 'teacher', 'name': 'Cô Phương (Toán)'},
            'gv03': {'pass': '3333', 'role': 'teacher', 'name': 'Thầy Cường (Đoàn Đội)'},
            'gv04': {'pass': '4444', 'role': 'teacher', 'name': 'Cô Yến (Tâm lý)'}
        }
        st.session_state['database'] = {}
        luu_du_lieu_len_may()
    st.session_state['he_thong_da_khoi_dong'] = True

if 'current_user' not in st.session_state: st.session_state['current_user'] = None
danh_sach_gv = {k: v['name'] for k, v in st.session_state['users'].items() if v['role'] == 'teacher'}

def kiem_tra_dang_nhap(role_can_thiet=None):
    if 'token_login' in st.query_params:
        user_luu = st.query_params['token_login']
        if user_luu in st.session_state['users']:
            st.session_state['current_user'] = user_luu

    if not st.session_state['current_user']:
        st.warning("🔒 Yêu cầu đăng nhập tài khoản Cán bộ/Giáo viên.")
        u = st.text_input("Tài khoản", key=f"user_{role_can_thiet}")
        p = st.text_input("Mật khẩu", type="password", key=f"pass_{role_can_thiet}")
        nho_mat_khau = st.checkbox("Ghi nhớ thiết bị này (Tự động đăng nhập lần sau)", key=f"nho_{role_can_thiet}")
        
        if st.button("Đăng nhập", key=f"login_btn_{role_can_thiet}"):
            if u in st.session_state['users'] and st.session_state['users'][u]['pass'] == p:
                st.session_state['current_user'] = u
                if nho_mat_khau: st.query_params['token_login'] = u
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
            if 'token_login' in st.query_params: del st.query_params['token_login']
            st.rerun()
        return True

# ==========================================
# 🔰 BỐ CỤC MỚI: THANH MENU BÊN (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", width=60)
    st.markdown("### 🧭 MENU LÀM VIỆC")
    
    # Thiết kế Menu dọc thay cho Tab ngang
    menu_chinh = st.radio("Chọn không gian của bạn:", [
        "🎓 1. Cổng dành cho Học Sinh", 
        "👨‍🏫 2. Không gian Giáo Viên", 
        "⚙️ 3. Trung tâm Quản lý (BGH)"
    ])
    
    st.markdown("<br><br><br>", unsafe_allow_html=True) # Tạo khoảng trống đẩy bản quyền xuống dưới
    st.markdown("---")
    st.markdown("###### 🔰 BẢN QUYỀN SÁNG CHẾ")
    st.caption("👨‍💻 **Tác giả:** Thầy Lý Hoàng Anh\n\n📍 **Đơn vị:** Hoàng Su Phì\n\n📞 **Hotline/Zalo:** 0969969189\n\n© 2026 Mọi hành vi sao chép không xin phép đều vi phạm bản quyền.")

# ==========================================
# HIỂN THỊ NỘI DUNG CHÍNH DỰA THEO MENU
# ==========================================
st.title("🏫 HỆ THỐNG TƯ VẤN TÂM LÝ & QUẢN TRỊ HỌC ĐƯỜNG BẰNG AI")
st.markdown("---")

# ------------------------------------------
# PHẦN 1: CỔNG HỌC SINH
# ------------------------------------------
if menu_chinh == "🎓 1. Cổng dành cho Học Sinh":
    st.info("""
    **👋 CHÀO MỪNG CÁC EM ĐẾN VỚI TRẠM LẮNG NGHE!** Nơi đây, mọi tâm sự của em đều được giữ bí mật tuyệt đối. Em có thể chọn 1 trong 2 hình thức:
    * 💬 **Tư vấn Gián tiếp (Nhắn tin ẩn danh):** Em chỉ cần nhắn tin trên web này, thầy cô sẽ phân tích và phản hồi lại bằng tin nhắn. Không ai biết em là ai nếu em không ghi tên.
    * 🤝 **Tư vấn Trực tiếp (Hẹn gặp):** Nếu em muốn trò chuyện trực tiếp, hãy đặt lịch hẹn. Thầy cô sẽ đợi em tại Phòng Tư vấn Tâm lý của nhà trường.
    """)
    
    col_gui, col_xem = st.columns(2)
    with col_gui:
        st.header("💌 Kết nối với Thầy Cô")
        
        ma_xac_thuc = st.text_input("🔑 Nhập Mã bảo mật của trường (Hỏi GVCN nếu em không biết):", type="password")
        hs_khoi_lop = st.text_input("Khối/Lớp của em (Không bắt buộc, VD: 12A1):")
        hs_cam_xuc = st.selectbox("Ngay lúc này, em đang cảm thấy thế nào?", 
                                  ["😐 Bình thường", "😔 Hơi buồn, suy tư", "😰 Căng thẳng, áp lực thi cử", "😡 Tức giận, uất ức", "😨 Sợ hãi, lo âu", "😭 Tuyệt vọng, cần giúp đỡ gấp"])
        gv_duoc_chon = st.selectbox("Em muốn tâm sự với thầy cô nào?", options=list(danh_sach_gv.keys()), format_func=lambda x: danh_sach_gv[x])
        
        st.markdown("---")
        hinh_thuc_tv = st.radio("Em muốn thầy cô hỗ trợ theo hình thức nào?", ["💬 Tư vấn Gián tiếp (Nhắn tin)", "🤝 Tư vấn Trực tiếp (Hẹn gặp)"])
        
        ngay_hen = ""
        gio_hen = ""
        if hinh_thuc_tv == "🤝 Tư vấn Trực tiếp (Hẹn gặp)":
            st.warning("📍 Thầy cô sẽ đợi em tại Phòng Tâm lý. Em hãy chọn thời gian em rảnh nhé:")
            col_ngay, col_gio = st.columns(2)
            ngay_hen = col_ngay.date_input("Chọn ngày hẹn:")
            gio_hen = col_gio.time_input("Chọn giờ hẹn (VD: 14:30):")
            
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
                
                thong_bao = f"🚨 CÓ CA TƯ VẤN MỚI!\n- Mã ca: {ma_bi_mat}\n- Lớp: {hs_khoi_lop}\n- Cảm xúc: {hs_cam_xuc}\n- Hình thức: {hinh_thuc_tv}"
                gui_thong_bao_ve_dien_thoai(thong_bao)
                
                st.success(f"✅ Gửi thành công! Mã bí mật để em xem lại tin nhắn là: **{ma_bi_mat}**")
                st.balloons() 
            else: st.warning("Em hãy viết nội dung trước khi gửi.")

    with col_xem:
        st.header("💬 Phòng Chat Riêng Tư")
        ma_tra_cuu = st.text_input("Nhập Mã bí mật hệ thống đã cấp cho em (VD: HS-1234):")
        if st.button("Truy cập phòng chat"): st.session_state['ca_dang_xem'] = ma_tra_cuu.strip()
            
        if 'ca_dang_xem' in st.session_state and st.session_state['ca_dang_xem'] in st.session_state['database']:
            ca = st.session_state['database'][st.session_state['ca_dang_xem']]
            ten_gv_phu_trach = st.session_state['users'][ca['gv_phu_trach']]['name']
            
            st.markdown(f"### Cuộc trò chuyện với {ten_gv_phu_trach}")
            if "Trực tiếp" in ca.get('hinh_thuc', ''):
                st.warning(f"⏰ **Lịch hẹn gặp:** {ca.get('lich_hen', 'Chưa rõ')} tại Phòng Tâm lý.")
            
            with st.container(height=350, border=True):
                for tn in ca['tin_nhan']:
                    with st.chat_message("user" if tn['nguoi_gui'] == "Học sinh" else "assistant"):
                        st.markdown(f"**{tn['nguoi_gui']}**")
                        st.write(tn['noi_dung'])
            
            if ca['trang_thai'] == "GV đã phản hồi" or ca['trang_thai'] == "Đã chốt lịch hẹn":
                hs_phan_hoi = st.text_input("Gửi tin nhắn phản hồi của em:")
                if st.button("Gửi trả lời", key="hs_reply"):
                    ca['tin_nhan'].append({"nguoi_gui": "Học sinh", "noi_dung": hs_phan_hoi})
                    ca['trang_thai'] = "HS vừa nhắn lại" 
                    ca['ai_phan_tich'] = None 
                    luu_du_lieu_len_may()
                    gui_thong_bao_ve_dien_thoai(f"🔔 Học sinh ca {st.session_state['ca_dang_xem']} vừa nhắn tin phản hồi!")
                    st.rerun()
            elif ca['trang_thai'] in ["Chờ xử lý", "HS vừa nhắn lại"]: st.warning("⏳ Thầy cô đang soạn tin nhắn trả lời em. Em chờ chút nhé!")
        elif 'ca_dang_xem' in st.session_state: st.error("Không tìm thấy mã này. Em nhập đúng chưa?")

# ------------------------------------------
# PHẦN 2: KHÔNG GIAN GIÁO VIÊN
# ------------------------------------------
elif menu_chinh == "👨‍🏫 2. Không gian Giáo Viên":
    if kiem_tra_dang_nhap(role_can_thiet='teacher'):
        
        auto_refresh = st.checkbox("🔄 Bật chế độ Tự động làm mới dữ liệu (Tự F5 sau mỗi 30 giây để kiểm tra tin nhắn mới)", value=True)
        if auto_refresh: tu_dong_cap_nhat_du_lieu(30)
            
        user_id = st.session_state['current_user']
        st.header(f"Bảng điều khiển Tư vấn của {st.session_state['users'][user_id]['name']}")
        
        with st.expander("🔐 Quản lý Tài khoản (Đổi mật khẩu cá nhân)"):
            new_pw = st.text_input("Nhập mật khẩu mới của bạn:", type="password", key=f"new_pw_{user_id}")
            if st.button("💾 Lưu mật khẩu mới", key=f"save_pw_{user_id}"):
                if new_pw:
                    st.session_state['users'][user_id]['pass'] = new_pw
                    luu_du_lieu_len_may()
                    st.success("Đổi mật khẩu thành công! Hãy ghi nhớ mật khẩu mới nhé.")
                else: st.warning("Vui lòng nhập mật khẩu mới trước khi lưu.")
        
        st.markdown("---")
        
        ca_cua_toi = {k: v for k, v in st.session_state['database'].items() if v['gv_phu_trach'] == user_id}
        ca_cho_xu_ly = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] in ["Chờ xử lý", "HS vừa nhắn lại"]}
        ca_da_phan_hoi = {k: v for k, v in ca_cua_toi.items() if v['trang_thai'] not in ["Chờ xử lý", "HS vừa nhắn lại"]}
        
        loc_ca = st.selectbox("Hiển thị dữ liệu theo:", ["Hiển thị Tất cả các ca đang chờ", "Chỉ hiển thị ca Trực tiếp (Hẹn gặp)", "Chỉ hiển thị ca Rủi ro Cao/Khẩn cấp"])
        if loc_ca == "Chỉ hiện ca Rủi ro Cao/Khẩn cấp":
            ca_cho_xu_ly = {k: v for k, v in ca_cho_xu_ly.items() if "Cao" in v['muc_do_rui_ro']}
        elif loc_ca == "Chỉ hiển thị ca Trực tiếp (Hẹn gặp)":
            # Fix lỗi get() cho các ca cũ
            ca_cho_xu_ly = {k: v for k, v in ca_cho_xu_ly.items() if "Trực tiếp" in v.get('hinh_thuc', '')}
            
        st.subheader(f"🔴 CÁC CA ĐANG CHỜ XỬ LÝ ({len(ca_cho_xu_ly)})")
        if not ca_cho_xu_ly: st.write("✅ Tuyệt vời, bạn không có ca tồn đọng nào!")
        else:
            for ma_ca, ca in ca_cho_xu_ly.items():
                # Xử lý tương thích ngược cho dữ liệu cũ không có 'hinh_thuc'
                hinh_thuc_hien_tai = ca.get('hinh_thuc', '💬 Tư vấn Gián tiếp (Nhắn tin)')
                
                with st.expander(f"[{hinh_thuc_hien_tai}] Ca {ma_ca} | Lớp: {ca['lop']} | Báo động: {ca['muc_do_rui_ro']}", expanded=True):
                    if "Trực tiếp" in hinh_thuc_hien_tai:
                        st.error(f"⏰ **Học sinh yêu cầu hẹn gặp mặt lúc:** {ca.get('lich_hen', 'Chưa xác định')}")
                    
                    st.write("**Nội dung cuộc trò chuyện:**")
                    with st.container(height=250, border=True):
                        for tn in ca['tin_nhan']:
                            with st.chat_message("user" if tn['nguoi_gui'] == "Học sinh" else "assistant"):
                                st.markdown(f"**{tn['nguoi_gui']}**")
                                st.write(tn['noi_dung'])
                    
                    if st.button(f"🧠 Yêu cầu AI Cố vấn ca này", key=f"ai_{ma_ca}"):
                        with st.spinner("AI đang phân tích bối cảnh..."):
                            lich_su = "\n".join([f"{t['nguoi_gui']}: {t['noi_dung']}" for t in ca['tin_nhan']])
                            tin_nhan_moi_nhat = ca['tin_nhan'][-1]['noi_dung']
                            
                            prompt = f"""Dưới đây là lịch sử cuộc trò chuyện tâm lý học đường:
                            {lich_su}
                            TIN NHẮN MỚI NHẤT học sinh vừa gửi là: "{tin_nhan_moi_nhat}"
                            Yêu cầu học sinh: {hinh_thuc_hien_tai}.
                            Dựa vào lịch sử để hiểu bối cảnh, nhưng hãy TRỌNG TÂM PHÂN TÍCH tin nhắn MỚI NHẤT theo cấu trúc:
                            [RỦI RO TÂM LÝ]: Thấp/Trung bình/Cao
                            [1. PHÂN TÍCH TIN NHẮN MỚI NHẤT]: ...
                            [2. HƯỚNG GIẢI QUYẾT]: ...
                            [3. GỢI Ý GIÁO VIÊN NHẮN TIN TRẢ LỜI]: (Nếu học sinh đòi gặp trực tiếp, hãy gợi ý câu xác nhận lịch hẹn)."""
                            
                            try:
                                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                                headers = {'Content-Type': 'application/json'}
                                thanh_cong = False
                                keys_luot_nay = danh_sach_keys.copy()
                                random.shuffle(keys_luot_nay)
                                
                                for key_hien_tai in keys_luot_nay:
                                    url_main = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key_hien_tai}"
                                    response = requests.post(url_main, json=payload, headers=headers)
                                    
                                    if response.status_code == 200:
                                        res_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                                        ca['ai_phan_tich'] = res_text
                                        if "Cao" in res_text[:80]: ca['muc_do_rui_ro'] = "Cao (Khẩn cấp)"
                                        elif "Trung bình" in res_text[:80]: ca['muc_do_rui_ro'] = "Trung bình"
                                        else: ca['muc_do_rui_ro'] = "Thấp"
                                        thanh_cong = True
                                        break  
                                    elif response.status_code == 429: continue 
                                    else:
                                        ca['ai_phan_tich'] = f"🚨 LỖI MÁY CHỦ GOOGLE ({response.status_code}): {response.text}"
                                        thanh_cong = True
                                        break
                                
                                if not thanh_cong: ca['ai_phan_tich'] = "⏳ HỆ THỐNG ĐANG QUÁ TẢI: Xin chờ 15 giây rồi bấm lại!"
                                luu_du_lieu_len_may()
                                st.rerun()
                                
                            except Exception as e: st.error(f"Lỗi mạng: {e}")
                                
                    if ca.get('ai_phan_tich'):
                        if "🚨" in ca.get('ai_phan_tich') or "⏳" in ca.get('ai_phan_tich'):
                            st.warning(ca.get('ai_phan_tich'))
                        else:
                            st.markdown("##### ✨ Cửa sổ Cố vấn AI (Trọng tâm phân tích tin nhắn cuối)")
                            with st.container(height=300, border=True):
                                st.markdown(ca.get('ai_phan_tich'))
                            
                        st.markdown("---")
                        gv_tra_loi = st.text_area("Soạn tin nhắn trả lời / Xác nhận lịch hẹn với học sinh:", height=80, key=f"txt_{ma_ca}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        if col_btn1.button("✅ Gửi trả lời & Đang theo dõi", type="primary", key=f"gui_{ma_ca}"):
                            ca['tin_nhan'].append({"nguoi_gui": "Giáo viên", "noi_dung": gv_tra_loi})
                            ca['trang_thai'] = "GV đã phản hồi"
                            luu_du_lieu_len_may()
                            st.rerun()
                        if "Trực tiếp" in hinh_thuc_hien_tai:
                            if col_btn2.button("📅 Gửi tin nhắn & Chốt lịch hẹn", key=f"chot_{ma_ca}"):
                                ca['tin_nhan'].append({"nguoi_gui": "Giáo viên", "noi_dung": gv_tra_loi})
                                ca['trang_thai'] = "Đã chốt lịch hẹn"
                                luu_du_lieu_len_may()
                                st.rerun()

        st.markdown("---")
        st.subheader(f"🟢 CÁC CA ĐANG THEO DÕI / ĐÃ LÊN LỊCH ({len(ca_da_phan_hoi)})")
        for ma_ca, ca in ca_da_phan_hoi.items():
            hinh_thuc_hien_tai = ca.get('hinh_thuc', '💬 Tư vấn Gián tiếp (Nhắn tin)')
            with st.expander(f"Ca {ma_ca} | Trạng thái: {ca['trang_thai']} | {hinh_thuc_hien_tai}"):
                with st.container(height=200, border=True):
                        for tn in ca['tin_nhan']:
                            with st.chat_message("user" if tn['nguoi_gui'] == "Học sinh" else "assistant"):
                                st.markdown(f"**{tn['nguoi_gui']}**")
                                st.write(tn['noi_dung'])

# ------------------------------------------
# PHẦN 3: TRUNG TÂM QUẢN LÝ (ADMIN)
# ------------------------------------------
elif menu_chinh == "⚙️ 3. Trung tâm Quản lý (BGH)":
    if kiem_tra_dang_nhap(role_can_thiet='admin'):
        auto_refresh_admin = st.checkbox("🔄 Bật chế độ Tự động làm mới dữ liệu (Auto-Refresh)", value=True)
        if auto_refresh_admin: tu_dong_cap_nhat_du_lieu(30)
            
        st.header("⚙️ QUẢN TRỊ HỆ THỐNG TỔNG THỂ")
        
        st.subheader("📊 Bảng vàng Thống kê & Phân tích")
        tong_ca = len(st.session_state['database'])
        ca_khan_cap = len([ca for ca in st.session_state['database'].values() if "Cao" in ca['muc_do_rui_ro']])
        ca_tb = len([ca for ca in st.session_state['database'].values() if "Trung bình" in ca['muc_do_rui_ro']])
        ca_thap = len([ca for ca in st.session_state['database'].values() if "Thấp" in ca['muc_do_rui_ro']])
        ca_cho = tong_ca - ca_khan_cap - ca_tb - ca_thap 
        
        c_a, c_b, c_c = st.columns(3)
        c_a.metric("Tổng số ca đã tiếp nhận", f"{tong_ca} ca")
        c_b.metric("Ca Khẩn cấp (Cần BGH chú ý)", f"{ca_khan_cap} ca", delta="Nguy hiểm", delta_color="inverse")
        danh_sach_tai_khoan_gv = [k for k, v in st.session_state['users'].items() if v['role'] == 'teacher']
        c_c.metric("Số lượng GV tham gia", f"{len(danh_sach_tai_khoan_gv)} người")
        
        if tong_ca > 0:
            st.markdown("**Biểu đồ Phân bổ Mức độ Rủi ro Tâm lý toàn trường:**")
            chart_data = pd.DataFrame({
                "Mức độ": ["Cao (Khẩn cấp)", "Trung bình", "Thấp", "Chưa phân tích"],
                "Số lượng ca": [ca_khan_cap, ca_tb, ca_thap, ca_cho]
            })
            st.bar_chart(chart_data.set_index("Mức độ"), color="#ff4b4b")

        with st.expander("🛠 Quản lý Nhân sự & Bảo mật (Thêm/Sửa/Xóa)"):
            st.write("👉 **1. ĐỔI MẬT KHẨU TÀI KHOẢN ADMIN:**")
            admin_id = st.session_state['current_user']
            col_ad1, col_ad2 = st.columns([2, 1])
            admin_new_pass = col_ad1.text_input("Nhập mật khẩu Admin mới:", type="password", key="admin_pw")
            if col_ad2.button("🔑 Cập nhật mật khẩu Admin"):
                if admin_new_pass:
                    st.session_state['users'][admin_id]['pass'] = admin_new_pass
                    luu_du_lieu_len_may()
                    st.success("Đã đổi mật khẩu Admin thành công!")
                else:
                    st.warning("Vui lòng nhập mật khẩu mới!")
            
            st.markdown("---")
            st.write("👉 **2. SỬA THÔNG TIN & RESET MẬT KHẨU GIÁO VIÊN:**")
            if danh_sach_tai_khoan_gv:
                gv_can_sua = st.selectbox("Chọn tài khoản giáo viên để chỉnh sửa:", options=danh_sach_tai_khoan_gv, format_func=lambda x: f"{x} ({st.session_state['users'][x]['name']})")
                c_edit1, c_edit2, c_edit3 = st.columns(3)
                ten_moi = c_edit1.text_input("Tên hiển thị mới:", value=st.session_state['users'][gv_can_sua]['name'])
                pass_moi = c_edit2.text_input("Cấp lại mật khẩu mới:", value=st.session_state['users'][gv_can_sua]['pass'])
                c_btn1, c_btn2 = c_edit3.columns(2)
                if c_btn1.button("💾 Lưu Sửa đổi"):
                    st.session_state['users'][gv_can_sua]['name'] = ten_moi
                    st.session_state['users'][gv_can_sua]['pass'] = pass_moi
                    luu_du_lieu_len_may()
                    st.success(f"Cập nhật thành công tài khoản {gv_can_sua}!")
                    st.rerun()
                if c_btn2.button("🗑️ Xóa GV này"):
                    del st.session_state['users'][gv_can_sua]
                    luu_du_lieu_len_may()
                    st.warning(f"Đã xóa tài khoản {gv_can_sua}!")
                    st.rerun()

            st.markdown("---")
            st.write("👉 **3. THÊM MỚI GIÁO VIÊN TƯ VẤN:**")
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
        
        if tong_ca > 0:
            st.markdown("---")
            st.subheader("📥 Trích xuất Hồ sơ Tư vấn (Phiên bản Chuẩn hóa)")
            du_lieu_xuat = []
            for ma_ca, ca in st.session_state['database'].items():
                lich_su_chat = " | ".join([f"{t['nguoi_gui']}: {t['noi_dung']}" for t in ca['tin_nhan']])
                du_lieu_xuat.append({
                    "Mã Hồ Sơ": ma_ca, 
                    "Thời gian TN": ca['thoi_gian'], 
                    "Khối/Lớp": ca['lop'],
                    "Trạng thái tâm lý đầu vào": ca.get('cam_xuc_ban_dau', 'N/A'),
                    "Hình thức yêu cầu": ca.get('hinh_thuc', 'Gián tiếp'),
                    "Lịch hẹn trực tiếp": ca.get('lich_hen', 'Không có'),
                    "GV Phụ trách": st.session_state['users'][ca['gv_phu_trach']]['name'],
                    "Đánh giá Rủi ro (AI)": ca['muc_do_rui_ro'], 
                    "Kết quả xử lý": ca['trang_thai'],
                    "Nhật ký Trò chuyện": lich_su_chat
                })
            df_export = pd.DataFrame(du_lieu_xuat)
            csv = df_export.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Tải Xuống Phiếu Báo Cáo (File CSV/Excel)", data=csv, file_name="Phieu_Danh_Gia_Tam_Ly_HSP.csv", mime="text/csv", type="primary")

            st.markdown("---")
            st.subheader("🗑️ Dọn dẹp Hệ thống (Xóa ca test)")
            danh_sach_ca = list(st.session_state['database'].keys())
            ca_can_xoa = st.selectbox("Chọn mã ca cần xóa:", options=danh_sach_ca, format_func=lambda x: f"{x} - Lớp: {st.session_state['database'][x]['lop']} ({st.session_state['database'][x]['thoi_gian']})")
            
            if st.button("🚨 Xóa vĩnh viễn ca này"):
                del st.session_state['database'][ca_can_xoa]
                luu_du_lieu_len_may()
                st.success(f"Đã dọn dẹp thành công hồ sơ {ca_can_xoa}!")
                st.rerun()