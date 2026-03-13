import streamlit as st
import datetime
import random
import pandas as pd
import requests

# ==========================================
# CẤU HÌNH HỆ THỐNG & BẢO MẬT
# ==========================================
try:
    API_KEY = st.secrets["API_KEY"]
except:
    st.error("❌ Chưa cấu hình API_KEY trong mục Secrets của Streamlit!")
    st.stop()

st.set_page_config(page_title="Trạm Lắng Nghe AI", page_icon="🏫", layout="wide")

# ==========================================
# KẾT NỐI DATABASE (FIREBASE)
# ==========================================
FIREBASE_URL = "https://tram-lang-nghe-data-default-rtdb.firebaseio.com"

def tai_du_lieu():
    try:
        r = requests.get(f"{FIREBASE_URL}/he_thong.json")
        if r.status_code == 200 and r.json(): return r.json()
    except: pass
    return None

def luu_du_lieu():
    data = {'users': st.session_state['users'], 'database': st.session_state['database']}
    try: requests.put(f"{FIREBASE_URL}/he_thong.json", json=data)
    except: pass

# ==========================================
# HÀM GỌI AI TỰ ĐỘNG (CHỐNG LỖI 404)
# ==========================================
def tu_dong_goi_ai(prompt, api_key):
    try:
        # 1. Quét danh sách AI được phép dùng trên API Key này
        url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res_list = requests.get(url_list)
        if res_list.status_code != 200:
            return f"Lỗi kiểm tra model: {res_list.text}"
            
        danh_sach = res_list.json().get('models', [])
        models_hop_le = [m['name'] for m in danh_sach if 'generateContent' in m.get('supportedGenerationMethods', [])]
        
        # 2. Tự động chọn AI tốt nhất hiện có
        model_chon = None
        uu_tien = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-2.0-flash', 'models/gemini-pro', 'models/gemini-1.0-pro']
        for m in uu_tien:
            if m in models_hop_le:
                model_chon = m
                break
                
        if not model_chon and len(models_hop_le) > 0:
            model_chon = models_hop_le[0] # Lấy đại model đầu tiên nếu các model trên bị ẩn
            
        if not model_chon:
            return "Lỗi: Tài khoản API của bạn không hỗ trợ tạo văn bản."

        # 3. Tiến hành gọi AI
        url_chat = f"https://generativelanguage.googleapis.com/v1beta/{model_chon}:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {'Content-Type': 'application/json'}
        
        res_chat = requests.post(url_chat, json=payload, headers=headers)
        if res_chat.status_code == 200:
            return res_chat.json()['candidates'][0]['content']['parts'][0]['text']
        elif res_chat.status_code == 429:
            # Bắt luôn lỗi hết lượt dùng miễn phí
            return "Lỗi 429: Tài khoản API của bạn đã hết lượt dùng miễn phí (Quota Exceeded). Hãy tạo API Key bằng một tài khoản Gmail khác."
        else:
            return f"Lỗi gọi AI: {res_chat.text}"
    except Exception as e:
        return f"Lỗi hệ thống AI: {str(e)}"

# ==========================================
# KHỞI TẠO DỮ LIỆU
# ==========================================
if 'init' not in st.session_state:
    cloud_data = tai_du_lieu()
    if cloud_data:
        st.session_state['users'] = cloud_data.get('users', {})
        st.session_state['database'] = cloud_data.get('database', {})
    else:
        st.session_state['users'] = {
            'admin': {'pass': 'admin123', 'role': 'admin', 'name': 'Ban Giám Hiệu'},
            'gv01': {'pass': '1111', 'role': 'teacher', 'name': 'Thầy Hoàng Anh'}
        }
        st.session_state['database'] = {}
    st.session_state['init'] = True

if 'current_user' not in st.session_state: st.session_state['current_user'] = None

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
st.title("🏫 TRẠM LẮNG NGHE - AI HỖ TRỢ TÂM LÝ HỌC ĐƯỜNG")
t1, t2, t3 = st.tabs(["🎓 Học Sinh", "👨‍🏫 Giáo Viên", "⚙️ Quản Lý"])

# --- TAB 1: HỌC SINH ---
with t1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("💌 Gửi tâm tư")
        gv_list = {k: v['name'] for k, v in st.session_state['users'].items() if v['role'] == 'teacher'}
        chon_gv = st.selectbox("Gửi đến thầy/cô:", options=list(gv_list.keys()), format_func=lambda x: gv_list[x])
        noidung = st.text_area("Câu chuyện của em:", height=150)
        if st.button("🚀 Gửi đi"):
            if noidung:
                ma = f"HS-{random.randint(1000, 9999)}"
                st.session_state['database'][ma] = {
                    "thoi_gian": datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
                    "lop": "Ẩn danh",
                    "gv_phu_trach": chon_gv,
                    "tin_nhan": [{"nguoi_gui": "Học sinh", "noi_dung": noidung}],
                    "ai_phan_tich": None, "muc_do_rui_ro": "Chờ phân tích", "trang_thai": "Chờ xử lý"
                }
                luu_du_lieu()
                st.success(f"✅ Đã gửi! Mã bí mật của em: **{ma}**")
    with c2:
        st.subheader("💬 Xem phản hồi")
        ma_tra = st.text_input("Nhập mã bí mật:")
        if ma_tra in st.session_state['database']:
            ca = st.session_state['database'][ma_tra]
            for tn in ca['tin_nhan']:
                st.markdown(f"**{tn['nguoi_gui']}:** {tn['noi_dung']}")
            if ca['trang_thai'] == "Đã phản hồi":
                reply = st.text_input("Nhắn lại cho thầy cô:")
                if st.button("Gửi tin nhắn"):
                    ca['tin_nhan'].append({"nguoi_gui": "Học sinh", "noi_dung": reply})
                    ca['trang_thai'] = "Chờ xử lý"
                    luu_du_lieu(); st.rerun()

# --- HÀM LOGIN ---
def login(role):
    if not st.session_state['current_user']:
        u = st.text_input("Tài khoản", key=f"u_{role}")
        p = st.text_input("Mật khẩu", type="password", key=f"p_{role}")
        if st.button("Đăng nhập", key=f"b_{role}"):
            if u in st.session_state['users'] and st.session_state['users'][u]['pass'] == p:
                st.session_state['current_user'] = u; st.rerun()
        return False
    return st.session_state['users'][st.session_state['current_user']]['role'] == role

# --- TAB 2: GIÁO VIÊN ---
with t2:
    if login('teacher'):
        uid = st.session_state['current_user']
        st.write(f"Chào **{st.session_state['users'][uid]['name']}**")
        if st.button("🚪 Đăng xuất"): st.session_state['current_user'] = None; st.rerun()
        
        my_ca = {k: v for k, v in st.session_state['database'].items() if v['gv_phu_trach'] == uid}
        for ma, ca in my_ca.items():
            with st.expander(f"Ca {ma} - Trạng thái: {ca['trang_thai']}"):
                for tn in ca['tin_nhan']: st.write(f"{tn['nguoi_gui']}: {tn['noi_dung']}")
                
                if st.button("🧠 AI Phân tích & Gợi ý", key=f"ai_{ma}"):
                    with st.spinner("Đang dò tìm bộ não AI tương thích nhất..."):
                        chat_history = "\n".join([f"{t['nguoi_gui']}: {t['noi_dung']}" for t in ca['tin_nhan']])
                        prompt = f"Phân tích tâm lý học sinh từ nội dung sau:\n{chat_history}\nĐưa ra: 1.Mức độ rủi ro (Thấp/Trung bình/Cao) 2.Lời khuyên cho GV 3.Mẫu tin nhắn trả lời."
                        
                        # GỌI HÀM AI TỰ ĐỘNG
                        ket_qua = tu_dong_goi_ai(prompt, API_KEY)
                        ca['ai_phan_tich'] = ket_qua
                        
                        if "Lỗi" not in ket_qua:
                            if "Cao" in ket_qua[:100]: ca['muc_do_rui_ro'] = "Cao (Khẩn cấp)"
                            elif "Trung bình" in ket_qua[:100]: ca['muc_do_rui_ro'] = "Trung bình"
                            else: ca['muc_do_rui_ro'] = "Thấp"
                        
                        luu_du_lieu(); st.rerun()
                
                if ca.get('ai_phan_tich'):
                    if "Lỗi" in ca['ai_phan_tich']: st.error(ca['ai_phan_tich'])
                    else: st.info(ca['ai_phan_tich'])
                    
                    gv_msg = st.text_area("Gửi tin nhắn cho HS:", key=f"gv_{ma}")
                    if st.button("Gửi phản hồi", key=f"btn_{ma}"):
                        ca['tin_nhan'].append({"nguoi_gui": "Giáo viên", "noi_dung": gv_msg})
                        ca['trang_thai'] = "Đã phản hồi"
                        luu_du_lieu(); st.rerun()

# --- TAB 3: ADMIN ---
with t3:
    if login('admin'):
        st.subheader("Quản lý dữ liệu")
        if st.button("🚪 Đăng xuất Admin"): st.session_state['current_user'] = None; st.rerun()
        
        df = pd.DataFrame([{"Mã": k, "Rủi ro": v['muc_do_rui_ro'], "Trạng thái": v['trang_thai']} for k, v in st.session_state['database'].items()])
        st.table(df)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Tải báo cáo CSV", csv, "bao_cao.csv", "text/csv")