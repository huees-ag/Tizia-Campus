const API_URL = '/api';
const USER_ID = 1;

// ═══════════════════════════════════════════════
// TOAST
// ═══════════════════════════════════════════════
const Toast = {
    show(message, type = 'success', duration = 3500) {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span><span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.4s ease forwards';
            setTimeout(() => toast.remove(), 400);
        }, duration);
    },
    success: (msg) => Toast.show(msg, 'success'),
    error:   (msg) => Toast.show(msg, 'error'),
    info:    (msg) => Toast.show(msg, 'info')
};

// ═══════════════════════════════════════════════
// USER MODULE
// ═══════════════════════════════════════════════
const UserModule = {
    async load() {
        try {
            const res = await fetch(`${API_URL}/user/${USER_ID}`);
            if (!res.ok) throw new Error();
            const user = await res.json();
            this.updateUI(user);
        } catch {
            const el = document.getElementById('user-level-badge');
            if (el) el.textContent = 'Offline';
        }
    },

    updateUI(user) {
        const xp    = document.getElementById('user-xp-badge');
        const level = document.getElementById('user-level-badge');
        if (xp)    xp.innerHTML    = `<i class="fa-solid fa-fire mr-1"></i> ${user.xp} XP`;
        if (level) level.innerHTML = `<i class="fa-solid fa-medal mr-1"></i> Cấp ${user.level}`;
    },

    async addXP(amount) {
        const res = await fetch(`${API_URL}/user/${USER_ID}/add-xp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ xpAmount: amount })
        });
        const data = await res.json();
        this.updateUI(data);
    },

    async addBadge(badgeName) {
        await fetch(`${API_URL}/user/${USER_ID}/badges`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ badgeName })
        });
    }
};

// ═══════════════════════════════════════════════
// QUIZ MODULE
// ═══════════════════════════════════════════════
const QuizModule = {
    step: 1,
    answers: [],

    open() {
        this.step = 1;
        this.answers = [];
        document.getElementById('quiz-modal')?.classList.remove('hidden');
        document.getElementById('quiz-chat-box').innerHTML = `
            <div class="mb-4">
                <span class="text-cyan-400 font-bold text-xs">AI Coach:</span>
                <p class="text-gray-300 mt-1 bg-[#1e2640] p-3 rounded-lg rounded-tl-none">
                    Chào bạn! Hãy trả lời câu hỏi để tôi phân tích thế mạnh của bạn nhé!
                </p>
            </div>
            <div id="quiz-question-zone" class="mt-4"></div>
        `;
        this.showQuestion();
    },

    close() {
        document.getElementById('quiz-modal')?.classList.add('hidden');
    },

    showQuestion() {
        const zone = document.getElementById('quiz-question-zone');
        if (!zone) return;
        const questions = [
            {
                text: 'Câu 1: Bạn thích làm việc với mảng nào nhất?',
                options: [
                    { key: 'A', label: 'Thiết kế giao diện đẹp mắt, tương tác trực quan' },
                    { key: 'B', label: 'Tìm lỗi ẩn, đóng vai thám tử săn lùng Bug' },
                    { key: 'C', label: 'Tấn công và phòng thủ bảo mật hệ thống' }
                ]
            },
            {
                text: 'Câu 2: Phong cách giải quyết vấn đề của bạn?',
                options: [
                    { key: 'X', label: 'Tỉ mỉ, kiên nhẫn, trau chuốt từng chi tiết nhỏ' },
                    { key: 'Y', label: 'Đa nghi, cẩn thận, thích thử thách bảo mật' }
                ]
            }
        ];
        const q = questions[this.step - 1];
        zone.innerHTML = `
            <p class="text-xs text-gray-400 mb-2">${q.text}</p>
            <div class="space-y-2">
                ${q.options.map(o => `
                    <button onclick="QuizModule.answer('${o.key}')"
                            class="w-full text-left bg-[#12182d] hover:bg-cyan-500/20 p-2.5 rounded text-xs border border-[#1f294d] transition-colors">
                        ${o.key}. ${o.label}
                    </button>
                `).join('')}
            </div>
        `;
    },

    async answer(key) {
        this.answers.push(key);
        const chatBox = document.getElementById('quiz-chat-box');
        chatBox.innerHTML += `
            <div class="mb-4 text-right">
                <p class="text-gray-300 mt-1 bg-[#10b981]/20 p-3 rounded-lg rounded-tr-none inline-block">Đã chọn: ${key}</p>
            </div>
        `;
        chatBox.scrollTop = chatBox.scrollHeight;

        if (this.step === 1) {
            this.step = 2;
            this.showQuestion();
        } else {
            await this.showResult();
        }
    },

    async showResult() {
        const zone = document.getElementById('quiz-question-zone');
        zone.innerHTML = '<p class="text-xs text-gray-400 animate-pulse">⏳ AI đang phân tích...</p>';

        let career = 'Lập trình viên (Developer)';
        if (this.answers[0] === 'B') career = 'Kiểm thử viên (QA/QC Tester)';
        if (this.answers[0] === 'C' || this.answers[1] === 'Y') career = 'Kỹ sư Bảo mật (Cybersecurity)';

        await new Promise(r => setTimeout(r, 1200));

        document.getElementById('quiz-chat-box').innerHTML += `
            <div class="mb-4">
                <span class="text-cyan-400 font-bold text-xs">AI Coach:</span>
                <div class="text-gray-300 mt-1 bg-[#1e2640] p-3 rounded-lg rounded-tl-none">
                    <p class="font-bold text-yellow-400 mb-2">🎉 KẾT QUẢ:</p>
                    <p>Bạn phù hợp với: <strong class="text-cyan-400">${career}</strong></p>
                    <p class="mt-2 text-xs text-gray-400">Đã cộng 100 XP!</p>
                </div>
            </div>
        `;

        zone.innerHTML = `<button onclick="QuizModule.close()" class="bg-cyan-600 hover:bg-cyan-700 px-4 py-2 rounded text-xs">Hoàn thành</button>`;

        await UserModule.addXP(100);
        await UserModule.addBadge('Định hướng nghề CNTT');
        Toast.success('Mở khóa badge "Định hướng nghề CNTT" + 100 XP!');
        await UserModule.load();
    }
};

// ═══════════════════════════════════════════════
// TESTER MODULE
// ═══════════════════════════════════════════════
const TesterModule = {
    foundBugs: { 1: false, 2: false, 3: false },

    open() {
        this.foundBugs = { 1: false, 2: false, 3: false };
        document.getElementById('tester-modal')?.classList.remove('hidden');
        document.getElementById('ticket-qty').innerText = '1';
        document.getElementById('ticket-total').innerText = '$15';
        document.getElementById('coupon-input').value = '';
        document.getElementById('coupon-error').classList.add('hidden');
        for (let i = 1; i <= 3; i++) {
            document.getElementById(`bug-task-${i}`).className = 'bg-[#1a203c] p-3 rounded-lg border border-[#1f294d] flex items-center justify-between text-gray-400';
            document.getElementById(`bug-status-${i}`).className = 'text-red-500';
            document.getElementById(`bug-status-${i}`).innerHTML = '<i class="fa-solid fa-circle-question"></i> Chưa tìm ra';
        }
    },

    close() {
        document.getElementById('tester-modal')?.classList.add('hidden');
    },

    changeQty(val) {
        let qty = parseInt(document.getElementById('ticket-qty').innerText);
        qty += val;
        document.getElementById('ticket-qty').innerText = qty;
        document.getElementById('ticket-total').innerText = `$${qty * 15}`;
    },

    applyCoupon() {
        const code = document.getElementById('coupon-input').value;
        const errEl = document.getElementById('coupon-error');
        errEl.classList.remove('hidden');
        if (code === 'GIAM50') {
            errEl.innerText = 'Error 500: Internal Server Crash (Click để báo lỗi)';
        } else {
            errEl.innerText = 'Mã không đúng!';
        }
    },

    async reportBug(bugId) {
        if (bugId === 2) {
            const total = parseInt(document.getElementById('ticket-total').innerText.replace('$', ''));
            if (total >= 0) {
                Toast.info('Chưa có lỗi! Thử nhấn nút trừ xuống dưới 0 xem sao.');
                return;
            }
        }
        if (this.foundBugs[bugId]) return;
        this.foundBugs[bugId] = true;

        Toast.success(`Phát hiện Bug số ${bugId}!`);
        document.getElementById(`bug-task-${bugId}`).className = 'bg-emerald-950/20 p-3 rounded-lg border border-emerald-500/40 flex items-center justify-between text-emerald-400';
        document.getElementById(`bug-status-${bugId}`).className = 'text-emerald-400 font-bold';
        document.getElementById(`bug-status-${bugId}`).innerHTML = '<i class="fa-solid fa-circle-check"></i> Đã phát hiện';

        if (this.foundBugs[1] && this.foundBugs[2] && this.foundBugs[3]) {
            setTimeout(async () => {
                Toast.success('🏆 Tìm đủ 3 lỗi! +200 XP!');
                this.close();
                await UserModule.addXP(200);
                await UserModule.addBadge('Giải quyết vấn đề giả lập');
                await UserModule.load();
            }, 500);
        }
    }
};

// ═══════════════════════════════════════════════
// CODING MODULE
// ═══════════════════════════════════════════════
const CodingModule = {
    currentTaskId: 'TIZIA_ALGO_001',

    async openTask(taskId) {
        this.currentTaskId = taskId;
        await this.open();
    },

    async open() {
        document.getElementById('coding-modal')?.classList.remove('hidden');
        try {
            const res = await fetch(`${API_URL}/tasks`);
            const tasks = await res.json();
            const task = tasks.find(t => t.id === this.currentTaskId);
            if (task) {
                document.getElementById('modal-task-title').textContent     = task.title;
                document.getElementById('modal-task-difficulty').textContent = task.difficulty;
                document.getElementById('modal-task-desc').textContent      = task.description;
                document.getElementById('code-editor').value                = task.boilerplate_code;
                this.setMessage('Sẵn sàng chạy test cases...', 'idle');
            }
        } catch {
            Toast.error('Lỗi tải bài tập!');
        }
    },

    close() {
        document.getElementById('coding-modal')?.classList.add('hidden');
    },

    setMessage(text, state) {
        const el = document.getElementById('compiler-message');
        if (!el) return;
        el.textContent = text;
        el.className = {
            idle:    'text-xs text-gray-400',
            loading: 'text-xs text-yellow-400 animate-pulse',
            success: 'text-xs text-emerald-400 font-bold',
            error:   'text-xs text-red-400 font-bold'
        }[state] || 'text-xs text-gray-400';
    },

    async submit() {
        const code = document.getElementById('code-editor')?.value;
        if (!code) return;
        this.setMessage('⏳ Đang chạy kiểm thử...', 'loading');
        try {
            const res = await fetch(`${API_URL}/tasks/${this.currentTaskId}/submit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId: USER_ID, code })
            });
            const result = await res.json();
            if (result.success) {
                this.setMessage('✓ Đạt 100% test cases!', 'success');
                Toast.success(result.message);
                await UserModule.load();
                setTimeout(() => this.close(), 2000);
            } else {
                this.setMessage('✗ Sai kết quả.', 'error');
                Toast.error(result.message);
            }
        } catch {
            this.setMessage('Lỗi kết nối!', 'error');
            Toast.error('Không thể kết nối server.');
        }
    }
};

// ── Expose ra global ──
window.openQuizModal    = () => QuizModule.open();
window.closeQuizModal   = () => QuizModule.close();
window.openTesterModal  = () => TesterModule.open();
window.closeTesterModal = () => TesterModule.close();
window.changeQty        = (v) => TesterModule.changeQty(v);
window.applyCoupon      = () => TesterModule.applyCoupon();
window.reportBug        = (id) => TesterModule.reportBug(id);
window.openCodingModal  = () => CodingModule.open();
window.closeCodingModal = () => CodingModule.close();
window.submitCode       = () => CodingModule.submit();

// ═══════════════════════════════════════════════
// SORT VISUALIZER MODULE (Bubble Sort / Quick Sort)
// ═══════════════════════════════════════════════
const SortModule = {
    canvas: null,
    ctx: null,
    array: [],
    algorithm: 'bubble',
    isRunning: false,
    shouldStop: false,
    comparisons: 0,
    swaps: 0,

    open() {
        document.getElementById('sort-modal')?.classList.remove('hidden');
        this.canvas = document.getElementById('sort-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.shuffle();
    },

    close() {
        this.shouldStop = true;
        document.getElementById('sort-modal')?.classList.add('hidden');
    },

    setAlgorithm(algo) {
        this.algorithm = algo;
        document.getElementById('algo-bubble').className = algo === 'bubble'
            ? 'px-4 py-2 rounded-lg text-xs font-semibold bg-cyan-500 text-white'
            : 'px-4 py-2 rounded-lg text-xs font-semibold bg-[#1e2640] text-gray-300';
        document.getElementById('algo-quick').className = algo === 'quick'
            ? 'px-4 py-2 rounded-lg text-xs font-semibold bg-cyan-500 text-white'
            : 'px-4 py-2 rounded-lg text-xs font-semibold bg-[#1e2640] text-gray-300';
    },

    shuffle() {
        this.array = Array.from({ length: 30 }, () => Math.floor(Math.random() * 280) + 20);
        this.comparisons = 0;
        this.swaps = 0;
        this.updateStats();
        this.draw();
    },

    updateStats() {
        document.getElementById('sort-comparisons').textContent = this.comparisons;
        document.getElementById('sort-swaps').textContent = this.swaps;
    },

    draw(highlightIndices = [], sortedUpTo = -1) {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        ctx.clearRect(0, 0, w, h);

        const barWidth = w / this.array.length;

        this.array.forEach((val, i) => {
            let color = '#0284c7'; // mặc định
            if (highlightIndices.includes(i)) color = '#f97316'; // đang so sánh
            if (sortedUpTo !== -1 && i >= sortedUpTo) color = '#10b981'; // đã sort xong

            ctx.fillStyle = color;
            ctx.fillRect(i * barWidth + 1, h - val, barWidth - 2, val);
        });
    },

    async sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    getSpeed() {
        const slider = document.getElementById('sort-speed');
        return 210 - parseInt(slider.value); // càng kéo phải, càng nhanh
    },

    async start() {
        if (this.isRunning) return;
        this.isRunning = true;
        this.shouldStop = false;
        this.comparisons = 0;
        this.swaps = 0;

        const btn = document.getElementById('sort-start-btn');
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i>Đang chạy...';

        if (this.algorithm === 'bubble') {
            await this.bubbleSort();
        } else {
            await this.quickSort(0, this.array.length - 1);
        }

        if (!this.shouldStop) {
            this.draw([], this.array.length); // tất cả màu xanh khi xong
            Toast.success('Sắp xếp hoàn tất!');
        }

        this.isRunning = false;
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-play mr-1"></i>Chạy';
    },

    async bubbleSort() {
        const arr = this.array;
        const n = arr.length;
        for (let i = 0; i < n - 1; i++) {
            for (let j = 0; j < n - i - 1; j++) {
                if (this.shouldStop) return;
                this.comparisons++;
                this.draw([j, j + 1], n - i);
                this.updateStats();
                await this.sleep(this.getSpeed());

                if (arr[j] > arr[j + 1]) {
                    [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
                    this.swaps++;
                    this.draw([j, j + 1], n - i);
                    this.updateStats();
                    await this.sleep(this.getSpeed());
                }
            }
        }
    },

    async quickSort(low, high) {
        if (low < high && !this.shouldStop) {
            const pivotIndex = await this.partition(low, high);
            await this.quickSort(low, pivotIndex - 1);
            await this.quickSort(pivotIndex + 1, high);
        }
    },

    async partition(low, high) {
        const arr = this.array;
        const pivot = arr[high];
        let i = low - 1;

        for (let j = low; j < high; j++) {
            if (this.shouldStop) return high;
            this.comparisons++;
            this.draw([j, high]);
            this.updateStats();
            await this.sleep(this.getSpeed());

            if (arr[j] < pivot) {
                i++;
                [arr[i], arr[j]] = [arr[j], arr[i]];
                this.swaps++;
                this.draw([i, j]);
                this.updateStats();
                await this.sleep(this.getSpeed());
            }
        }
        [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
        this.swaps++;
        return i + 1;
    }
};

window.openSortModal  = () => SortModule.open();
window.closeSortModal = () => SortModule.close();

// ═══════════════════════════════════════════════
// COOLING MODULE (Hầm máy chủ)
// ═══════════════════════════════════════════════
const CoolingModule = {
    open() {
        document.getElementById('cooling-modal')?.classList.remove('hidden');
        document.getElementById('cooling-feedback')?.classList.add('hidden');
        this.updatePump(30);
    },
    close() {
        document.getElementById('cooling-modal')?.classList.add('hidden');
    },
    updatePump(pumpPercent) {
        pumpPercent = parseInt(pumpPercent);
        document.getElementById('pump-value').textContent = `${pumpPercent}%`;

        // Công thức mô phỏng: pump cao → nhiệt giảm, nhưng điện tăng
        const temp = Math.round(85 - pumpPercent * 0.55);
        const power = Math.round(20 + pumpPercent * 1.2);

        document.getElementById('temp-display').textContent = `${temp}°C`;
        document.getElementById('power-display').textContent = `${power}W`;

        const rack = document.getElementById('server-rack');
        const tempEl = document.getElementById('temp-display');

        if (temp > 70) {
            rack.className = 'w-20 h-32 bg-gradient-to-b from-orange-500 to-red-600 rounded-lg border-4 border-gray-700 flex items-center justify-center transition-colors duration-500';
            tempEl.className = 'text-3xl font-bold text-red-400 mt-1';
        } else if (temp > 50) {
            rack.className = 'w-20 h-32 bg-gradient-to-b from-yellow-500 to-orange-500 rounded-lg border-4 border-gray-700 flex items-center justify-center transition-colors duration-500';
            tempEl.className = 'text-3xl font-bold text-yellow-400 mt-1';
        } else {
            rack.className = 'w-20 h-32 bg-gradient-to-b from-cyan-400 to-blue-500 rounded-lg border-4 border-gray-700 flex items-center justify-center transition-colors duration-500';
            tempEl.className = 'text-3xl font-bold text-cyan-400 mt-1';
        }

        // Điều kiện thắng: nhiệt < 70 và điện không quá cao (pump <= 70%)
        const feedback = document.getElementById('cooling-feedback');
        if (temp < 70 && pumpPercent <= 70) {
            feedback.classList.remove('hidden');
        } else {
            feedback.classList.add('hidden');
        }
    },
    async complete() {
        await UserModule.addXP(60);
        await UserModule.addBadge('Quản trị hệ thống làm mát');
        Toast.success('+60 XP! Đã làm chủ hệ thống làm mát máy chủ.');
        await UserModule.load();
        this.close();
    }
};

// ═══════════════════════════════════════════════
// LOGIC GATE MODULE (Lab Vi mạch)
// ═══════════════════════════════════════════════
const LogicModule = {
    gate: 'AND',
    inputs: { A: 0, B: 0 },

    open() {
        document.getElementById('logic-modal')?.classList.remove('hidden');
        this.setGate('AND');
    },
    close() {
        document.getElementById('logic-modal')?.classList.add('hidden');
    },
    setGate(gate) {
        this.gate = gate;
        ['AND', 'OR', 'NOT', 'XOR'].forEach(g => {
            const btn = document.getElementById(`gate-${g}`);
            btn.className = g === gate
                ? 'px-4 py-2 rounded-lg text-xs font-bold bg-amber-500 text-white'
                : 'px-4 py-2 rounded-lg text-xs font-bold bg-[#1e2640] text-gray-300';
        });
        document.getElementById('gate-box').textContent = gate;

        // NOT chỉ dùng 1 input — ẩn input B
        const inputB = document.getElementById('input-B');
        inputB.style.opacity = gate === 'NOT' ? '0.3' : '1';
        inputB.disabled = gate === 'NOT';

        this.calculate();
    },
    toggleInput(key) {
        if (key === 'B' && this.gate === 'NOT') return;
        this.inputs[key] = this.inputs[key] === 0 ? 1 : 0;
        document.getElementById(`input-${key}`).textContent = this.inputs[key];
        document.getElementById(`input-${key}`).className = this.inputs[key] === 1
            ? 'w-16 h-16 rounded-full bg-emerald-500 text-2xl font-bold text-white border-2 border-emerald-400'
            : 'w-16 h-16 rounded-full bg-[#2e3a60] text-2xl font-bold text-gray-300 border-2 border-[#1f294d]';
        this.calculate();
    },
    calculate() {
        const { A, B } = this.inputs;
        let output = 0;
        switch (this.gate) {
            case 'AND': output = A && B ? 1 : 0; break;
            case 'OR':  output = A || B ? 1 : 0; break;
            case 'NOT': output = A === 0 ? 1 : 0; break;
            case 'XOR': output = A !== B ? 1 : 0; break;
        }
        const outEl = document.getElementById('output-display');
        outEl.textContent = output;
        outEl.className = output === 1
            ? 'w-16 h-16 rounded-full bg-amber-500 text-2xl font-bold text-white border-2 border-amber-400 flex items-center justify-center'
            : 'w-16 h-16 rounded-full bg-gray-700 text-2xl font-bold text-gray-300 border-2 border-[#1f294d] flex items-center justify-center';
    },
    async complete() {
        await UserModule.addXP(50);
        await UserModule.addBadge('Hiểu cổng logic cơ bản');
        Toast.success('+50 XP! Đã hiểu nguyên lý cổng logic.');
        await UserModule.load();
        this.close();
    }
};

window.openCoolingModal  = () => CoolingModule.open();
window.closeCoolingModal = () => CoolingModule.close();
window.openLogicModal    = () => LogicModule.open();
window.closeLogicModal   = () => LogicModule.close();

window.addEventListener('DOMContentLoaded', () => UserModule.load());