import json
import subprocess
import sys
from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = 'tizia.db'


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            badge_name TEXT,
            UNIQUE(user_id, badge_name)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS role_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role_id TEXT,
            mission_id TEXT,
            content TEXT,
            ai_score INTEGER DEFAULT NULL,
            ai_feedback TEXT DEFAULT NULL,
            status TEXT DEFAULT 'pending',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT,
            difficulty TEXT,
            description TEXT,
            boilerplate_code TEXT,
            expected_output TEXT,
            xp_reward INTEGER DEFAULT 150
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_id TEXT,
            code TEXT,
            status TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO tasks VALUES (
            'TIZIA_PY_001',
            'Bài 1: Tính tổng dãy số',
            'Easy',
            'Viết hàm sum_range(n) trả về tổng các số từ 1 đến n.\n\nVí dụ:\n  Input: n=5\n  Output: 15',
            'def sum_range(n):\n    # Viết code của bạn ở đây\n    pass\n\nprint(sum_range(5))\nprint(sum_range(10))\nprint(sum_range(1))',
            '15\n55\n1',
            80
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO tasks VALUES (
            'TIZIA_PY_002',
            'Bài 2: Đếm số chẵn',
            'Easy',
            'Viết hàm count_even(arr) trả về số lượng số chẵn trong mảng.\n\nVí dụ:\n  Input: [1,2,3,4,5,6]\n  Output: 3',
            'def count_even(arr):\n    # Viết code của bạn ở đây\n    pass\n\nprint(count_even([1,2,3,4,5,6]))\nprint(count_even([1,3,5]))\nprint(count_even([]))',
            '3\n0\n0',
            80
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO tasks VALUES (
            'TIZIA_ALGO_002',
            'Kiểm tra số nguyên tố',
            'Medium',
            'Viết hàm is_prime(n) trả về True nếu n là số nguyên tố, ngược lại trả về False.\n\nVí dụ:\n  Input: n=7 -> True\n  Input: n=10 -> False',
            'def is_prime(n):\n    # Viết code của bạn ở đây\n    pass\n\nprint(is_prime(7))\nprint(is_prime(10))\nprint(is_prime(1))',
            'True\nFalse\nFalse',
            200
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO tasks VALUES (
            'TIZIA_ALGO_003',
            'Đảo chuỗi (Reverse String)',
            'Easy',
            'Viết hàm reverse_str(s) trả về chuỗi s bị đảo ngược.\n\nVí dụ:\n  Input: "tizia" -> "aizit"',
            'def reverse_str(s):\n    # Viết code của bạn ở đây\n    pass\n\nprint(reverse_str("tizia"))\nprint(reverse_str("hello"))',
            'aizit\nolleh',
            120
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO tasks VALUES (
            'TIZIA_ALGO_004',
            'Fibonacci thứ N',
            'Medium',
            'Viết hàm fibonacci(n) trả về số Fibonacci thứ n (bắt đầu từ 0).\n\nVí dụ:\n  Input: n=6 -> Output: 8\n  (Dãy: 0,1,1,2,3,5,8...)',
            'def fibonacci(n):\n    # Viết code của bạn ở đây\n    pass\n\nprint(fibonacci(6))\nprint(fibonacci(0))\nprint(fibonacci(10))',
            '8\n0\n55',
            220
        )
    ''')
    # Seed user mẫu
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username, xp, level) VALUES (1, 'hoc_vien_demo', 250, 3)"
    )

    # Seed task mẫu
    cursor.execute('''
        INSERT OR IGNORE INTO tasks VALUES (
            'TIZIA_ALGO_001',
            'Tìm số lớn nhất trong mảng',
            'Easy',
            'Viết hàm find_max(arr) nhận vào mảng số nguyên và trả về số lớn nhất. Nếu mảng trống, trả về None.\n\nVí dụ:\n  Input: [1, 5, 3, 9, 2]\n  Output: 9',
            'def find_max(arr):\n    # Viết code của bạn ở đây\n    pass\n\nprint(find_max([1, 5, 3, 9, 2]))\nprint(find_max([-10, -5, -20, -1]))\nprint(find_max([]))',
            '9\n-1\nNone',
            150
        )
    ''')

    # Seed badge mẫu
    cursor.execute(
        "INSERT OR IGNORE INTO badges (user_id, badge_name) VALUES (1, 'Định hướng nghề CNTT')"
    )

    conn.commit()
    conn.close()
    print("✅ Database sẵn sàng!")


def calculate_level(xp):
    thresholds = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500]
    level = 1
    for i, threshold in enumerate(thresholds):
        if xp >= threshold:
            level = i + 1
    return level
CAREER_HANDBOOK = [
    {
        "id": "developer",
        "icon": "fa-code",
        "color": "orange",
        "title": "Lập trình viên (Developer)",
        "summary": "Người xây dựng phần mềm — biến ý tưởng thành sản phẩm chạy được.",
        "daily_tasks": [
            "Viết code theo yêu cầu (feature) từ Product Manager",
            "Tham gia Code Review — đọc và góp ý code của đồng nghiệp",
            "Sửa lỗi (bug fix) được báo cáo từ Tester",
            "Daily standup meeting — báo cáo tiến độ 15 phút mỗi sáng"
        ],
        "skills": ["Một ngôn ngữ lập trình (Python, JS, Java...)", "Git/GitHub", "Đọc hiểu tài liệu API", "Tư duy logic & debug"],
        "salary_range": "8 - 25 triệu (Junior) → 25 - 60 triệu (Senior)"
    },
    {
        "id": "tester",
        "icon": "fa-bug",
        "color": "pink",
        "title": "Kiểm thử viên (QA/QC Tester)",
        "summary": "Người 'phá' sản phẩm trước khi người dùng thật phá nó — tìm lỗi có hệ thống.",
        "daily_tasks": [
            "Viết test case dựa trên yêu cầu sản phẩm",
            "Thực hiện kiểm thử thủ công (manual test) hoặc tự động (automation)",
            "Báo cáo bug chi tiết: bước tái hiện, kết quả mong đợi vs thực tế",
            "Retest sau khi Developer fix xong"
        ],
        "skills": ["Tư duy phản biện, tỉ mỉ", "Hiểu quy trình SDLC", "Công cụ quản lý bug (Jira)", "Cơ bản về automation testing"],
        "salary_range": "7 - 18 triệu (Junior) → 18 - 40 triệu (Senior)"
    },
    {
        "id": "cybersecurity",
        "icon": "fa-shield-halved",
        "color": "red",
        "title": "Kỹ sư Bảo mật (Cybersecurity)",
        "summary": "Người bảo vệ hệ thống khỏi tấn công — vừa là người phòng thủ, vừa hiểu cách tấn công.",
        "daily_tasks": [
            "Quét lỗ hổng bảo mật (vulnerability scanning)",
            "Phân tích log để phát hiện hành vi bất thường",
            "Viết báo cáo Pentest (kiểm thử xâm nhập)",
            "Cập nhật chính sách bảo mật, đào tạo nhân viên về an toàn thông tin"
        ],
        "skills": ["Mạng máy tính (TCP/IP, DNS)", "Linux command line", "OWASP Top 10", "Tư duy của hacker (ethical)"],
        "salary_range": "10 - 25 triệu (Junior) → 30 - 70 triệu (Senior)"
    },
    {
        "id": "data_analyst",
        "icon": "fa-chart-pie",
        "color": "yellow",
        "title": "Nhà phân tích dữ liệu (Data Analyst)",
        "summary": "Người biến dữ liệu thô thành insight giúp doanh nghiệp ra quyết định.",
        "daily_tasks": [
            "Viết truy vấn SQL để lấy dữ liệu từ database",
            "Làm sạch và xử lý dữ liệu (data cleaning)",
            "Xây dựng dashboard trực quan (Power BI, Tableau)",
            "Trình bày kết quả phân tích cho team kinh doanh"
        ],
        "skills": ["SQL", "Excel/Google Sheets nâng cao", "Python (Pandas) hoặc R", "Tư duy thống kê cơ bản"],
        "salary_range": "8 - 20 triệu (Junior) → 20 - 45 triệu (Senior)"
    }
]
ROLE_MISSIONS = {
    "developer": {
        "mission_id": "DEV_FIX_001",
        "title": "Nhiệm vụ: Sửa lỗi nút Đăng nhập bị lệch",
        "brief": (
            "VinaApp báo lỗi: nút 'Đăng nhập' trên trang chủ bị lệch sang trái, "
            "không nằm giữa khung chứa. Dưới đây là đoạn CSS gốc đang lỗi:\n\n"
            ".login-btn {\n"
            "    display: block;\n"
            "    width: 200px;\n"
            "    /* margin bị thiếu auto để center */\n"
            "}\n\n"
            "Hãy viết lại đoạn CSS đúng để nút được căn giữa theo chiều ngang trong container."
        ),
        "input_type": "code",
        "placeholder": ".login-btn {\n    display: block;\n    width: 200px;\n    /* Viết code sửa lỗi của bạn ở đây */\n}",
        "submit_label": "Nộp đoạn CSS đã sửa"
    },
    "cybersecurity": {
        "mission_id": "SEC_LOG_001",
        "title": "Nhiệm vụ: Phân tích Log truy cập đáng nghi",
        "brief": (
            "Dưới đây là log truy cập server trong 1 phút của VinaApp:\n\n"
            "10:00:01 - IP 113.22.1.5 - GET /login - 200 OK\n"
            "10:00:02 - IP 192.168.1.40 - POST /login - 401 Unauthorized\n"
            "10:00:02 - IP 192.168.1.40 - POST /login - 401 Unauthorized\n"
            "10:00:03 - IP 192.168.1.40 - POST /login - 401 Unauthorized\n"
            "10:00:03 - IP 192.168.1.40 - POST /login - 401 Unauthorized\n"
            "10:00:04 - IP 192.168.1.40 - POST /login - 200 OK\n"
            "10:00:05 - IP 113.22.1.5 - GET /profile - 200 OK\n\n"
            "Hãy chỉ ra IP nào đáng nghi, kiểu tấn công có thể đang xảy ra là gì, "
            "và bạn sẽ đề xuất biện pháp phòng chống nào."
        ),
        "input_type": "text",
        "placeholder": "Ví dụ: IP ... đáng nghi vì... Kiểu tấn công có thể là... Đề xuất biện pháp...",
        "submit_label": "Nộp báo cáo phân tích"
    },
    "data_analyst": {
        "mission_id": "DATA_SALES_001",
        "title": "Nhiệm vụ: Phân tích doanh số sụt giảm",
        "brief": (
            "Bảng doanh số VinaApp theo tháng (đơn vị: triệu VNĐ):\n\n"
            "Tháng 1: 120 | Tháng 2: 135 | Tháng 3: 90 | Tháng 4: 60\n\n"
            "Ghi chú thêm: Tháng 3 công ty tăng giá sản phẩm 20%. "
            "Tháng 4 đối thủ ra mắt app cạnh tranh có giá rẻ hơn.\n\n"
            "Hãy viết nhận định về nguyên nhân sụt giảm doanh số và đề xuất "
            "1-2 hành động cụ thể để cải thiện."
        ),
        "input_type": "text",
        "placeholder": "Ví dụ: Doanh số giảm mạnh từ tháng 3 trùng với thời điểm... Đề xuất...",
        "submit_label": "Nộp báo cáo phân tích"
    }
}
# ── PAGE ROUTES ──────────────────────────────────────
CASE_STUDIES = [
    {
        "id": "vinaapp_launch",
        "title": "VinaApp ra mắt: Cuộc đua với thời gian",
        "summary": "Cách 4 vai trò Dev, Tester, Security, Data Analyst phối hợp trong 1 sprint thực tế.",
        "timeline": [
            {"role": "Data Analyst", "color": "yellow", "action": "Phân tích feedback người dùng từ bản beta, phát hiện 68% phàn nàn về tốc độ load trang."},
            {"role": "Developer", "color": "orange", "action": "Tối ưu code, thêm lazy-loading cho hình ảnh, giảm thời gian load từ 4s xuống 1.2s."},
            {"role": "Tester", "color": "pink", "action": "Kiểm thử lại toàn bộ luồng thanh toán sau khi code thay đổi, phát hiện thêm 2 bug mới phát sinh."},
            {"role": "Cybersecurity", "color": "red", "action": "Quét lại bảo mật sau khi Dev sửa code, đảm bảo không có lỗ hổng mới bị mở ra."},
            {"role": "Developer", "color": "orange", "action": "Fix 2 bug Tester báo cáo, merge code vào nhánh chính (main branch)."},
            {"role": "Data Analyst", "color": "yellow", "action": "Theo dõi số liệu sau khi ra mắt: tỷ lệ giữ chân người dùng tăng 23% sau 1 tuần."}
        ],
        "lesson": "Bài học: Không có vai trò nào làm việc độc lập — mọi quyết định kỹ thuật đều xuất phát từ dữ liệu thực tế, và mọi thay đổi code đều cần được kiểm thử + bảo mật lại từ đầu."
    }
]

DEBUG_SCENARIOS = [
    {
        "id": "scenario_1",
        "bug_code": 'def calculate_discount(price, percent):\n    return price - percent\n\nprint(calculate_discount(100, 20))  # Mong đợi: 80',
        "question": "Hàm này tính giảm giá bị sai. Lỗi nằm ở đâu?",
        "options": [
            {"text": "Tên hàm sai", "correct": False},
            {"text": "Thiếu chuyển percent thành tỷ lệ (price * percent / 100)", "correct": True},
            {"text": "Thiếu kiểu dữ liệu float", "correct": False}
        ],
        "explanation": "Đúng! Code đang trừ trực tiếp percent (20) vào price, phải tính price - (price * percent / 100) = 100 - 20 = 80 mới đúng công thức giảm giá theo %."
    },
    {
        "id": "scenario_2",
        "bug_code": 'def get_first_item(my_list):\n    return my_list[0]\n\nprint(get_first_item([]))  # Crash!',
        "question": "Đoạn code này bị crash khi nào? Cách debug đúng là gì?",
        "options": [
            {"text": "Luôn crash, không sửa được", "correct": False},
            {"text": "Crash khi list trống — cần kiểm tra len(my_list) > 0 trước khi truy cập [0]", "correct": True},
            {"text": "Lỗi do tên hàm quá dài", "correct": False}
        ],
        "explanation": "Đúng! Đây là lỗi IndexError kinh điển — luôn kiểm tra dữ liệu rỗng trước khi truy cập theo chỉ số (index)."
    }
]


@app.route('/coding/debug-lab')
def debug_lab():
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    conn.close()
    return render_template('debug_lab.html', user=user, scenarios=DEBUG_SCENARIOS)

@app.route('/career/case-study')
def case_study():
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    conn.close()
    return render_template('case_study.html', user=user, cases=CASE_STUDIES)
@app.route('/')
def index():
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    badges = [r['badge_name'] for r in conn.execute(
        'SELECT badge_name FROM badges WHERE user_id = 1').fetchall()]
    conn.close()
    return render_template('index.html', user=user, badges=badges)


@app.route('/career')
def career():
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    badges = [r['badge_name'] for r in conn.execute(
        'SELECT badge_name FROM badges WHERE user_id = 1').fetchall()]
    conn.close()
    return render_template('career.html', user=user, badges=badges)
@app.route('/career/handbook')
def career_handbook():
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    conn.close()
    return render_template('handbook.html', user=user, roles=CAREER_HANDBOOK)
@app.route('/career/play/<role_id>')
def play_role(role_id):
    role = next((r for r in CAREER_HANDBOOK if r['id'] == role_id), None)
    mission = ROLE_MISSIONS.get(role_id)
    if not role or not mission:
        return "Không tìm thấy nhiệm vụ cho role này", 404
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    conn.close()
    return render_template('role_play.html', user=user, role=role, mission=mission)


@app.route('/api/missions/<role_id>/submit', methods=['POST'])
def submit_mission(role_id):
    data = request.get_json()
    user_id = data.get('userId', 1)
    content = data.get('content', '').strip()
    mission = ROLE_MISSIONS.get(role_id)

    if not mission:
        return jsonify({"success": False, "message": "Nhiệm vụ không tồn tại"}), 404
    if not content:
        return jsonify({"success": False, "message": "Bạn chưa nhập nội dung bài nộp!"})

    conn = get_db()
    conn.execute('''
        INSERT INTO role_submissions (user_id, role_id, mission_id, content, status)
        VALUES (?, ?, ?, ?, 'pending')
    ''', (user_id, role_id, mission['mission_id'], content))
    conn.commit()

    # ── PLACEHOLDER ĐÁNH GIÁ TẠM THỜI (sẽ thay bằng AI thật sau) ──
    fake_score, fake_feedback = evaluate_submission_placeholder(role_id, content)

    submission_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.execute('''
        UPDATE role_submissions SET ai_score = ?, ai_feedback = ?, status = 'graded'
        WHERE id = ?
    ''', (fake_score, fake_feedback, submission_id))

    xp_reward = 50 + fake_score  # XP càng cao nếu điểm đánh giá cao
    conn.execute('UPDATE users SET xp = xp + ? WHERE id = ?', (xp_reward, user_id))
    conn.commit()

    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    new_level = calculate_level(user['xp'])
    conn.execute('UPDATE users SET level = ? WHERE id = ?', (new_level, user_id))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "score": fake_score,
        "feedback": fake_feedback,
        "xp_earned": xp_reward,
        "message": f"Đã nộp bài! Điểm đánh giá: {fake_score}/100"
    })


def evaluate_submission_placeholder(role_id, content):
    """
    PLACEHOLDER — đánh giá đơn giản dựa trên độ dài & từ khóa.
    Sau này thay bằng gọi Google Gemini API để chấm thật.
    """
    length_score = min(len(content) // 5, 40)  # tối đa 40 điểm theo độ dài
    base_score = 50 + length_score

    keyword_map = {
        "developer": ["margin", "auto", "center", "flex"],
        "cybersecurity": ["tấn công", "brute", "ip", "đề xuất", "chặn"],
        "data_analyst": ["giá", "đối thủ", "giảm", "đề xuất", "nguyên nhân"]
    }
    keywords = keyword_map.get(role_id, [])
    matched = sum(1 for kw in keywords if kw.lower() in content.lower())
    bonus = matched * 5

    score = min(base_score + bonus, 100)

    feedback = (
        f"Bài nộp đã được ghi nhận. Phát hiện {matched}/{len(keywords)} điểm phân tích quan trọng. "
        f"(Đánh giá tạm thời — hệ thống AI chấm điểm chi tiết sẽ được tích hợp ở phiên bản tiếp theo.)"
    )
    return score, feedback

@app.route('/hitech')
def hitech():
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    conn.close()
    return render_template('hitech.html', user=user)


@app.route('/coding')
def coding():
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    conn.close()
    return render_template('coding.html', user=user)


# ── API ROUTES ───────────────────────────────────────

@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if not user:
        return jsonify({"error": "Không tìm thấy user"}), 404
    return jsonify(dict(user))


@app.route('/api/user/<int:user_id>/add-xp', methods=['POST'])
def add_xp(user_id):
    data = request.get_json()
    xp_amount = data.get('xpAmount', 0)
    conn = get_db()
    conn.execute('UPDATE users SET xp = xp + ? WHERE id = ?', (xp_amount, user_id))
    conn.commit()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    new_level = calculate_level(user['xp'])
    conn.execute('UPDATE users SET level = ? WHERE id = ?', (new_level, user_id))
    conn.commit()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return jsonify({"success": True, "xp": user['xp'], "level": user['level']})


@app.route('/api/user/<int:user_id>/badges', methods=['POST'])
def add_badge(user_id):
    data = request.get_json()
    badge_name = data.get('badgeName', '')
    conn = get_db()
    conn.execute(
        'INSERT OR IGNORE INTO badges (user_id, badge_name) VALUES (?, ?)',
        (user_id, badge_name)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route('/api/tasks')
def get_tasks():
    conn = get_db()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return jsonify([dict(t) for t in tasks])


@app.route('/api/tasks/<task_id>/submit', methods=['POST'])
def submit_task(task_id):
    data = request.get_json()
    code = data.get('code', '')
    user_id = data.get('userId', 1)

    conn = get_db()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if not task:
        conn.close()
        return jsonify({"success": False, "message": "Không tìm thấy bài tập!"})

    # Chặn từ khóa nguy hiểm
    dangerous = ['import os', 'import sys', 'open(', '__import__', 'shutil']
    for keyword in dangerous:
        if keyword in code:
            conn.close()
            return jsonify({"success": False, "message": f"❌ Không được dùng '{keyword}'!"})

    # Chạy code
    try:
        proc = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=5
        )
        actual = proc.stdout.strip()
        expected = task['expected_output'].strip()

        if actual == expected:
            xp_reward = task['xp_reward']
            conn.execute('UPDATE users SET xp = xp + ? WHERE id = ?', (xp_reward, user_id))
            conn.commit()
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            new_level = calculate_level(user['xp'])
            conn.execute('UPDATE users SET level = ? WHERE id = ?', (new_level, user_id))
            conn.commit()
            conn.close()
            return jsonify({"success": True, "message": f"✅ Chính xác! Bạn được cộng {xp_reward} XP!"})
        else:
            conn.close()
            return jsonify({"success": False, "message": f"❌ Sai kết quả. Output của bạn: '{actual}'"})

    except subprocess.TimeoutExpired:
        conn.close()
        return jsonify({"success": False, "message": "⏱️ Code chạy quá 5 giây!"})

init_db()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)