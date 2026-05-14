// =========================================
// TERRALOG KOKI - Antrean Order
// =========================================

// ordersData di-inject dari template via tag <script> di antrian_order.html

// ── Helpers ───────────────────────────────
function getElapsedMin(waktuStr) {
    const [h, m] = waktuStr.split(':').map(Number);
    const now = new Date();
    const orderTime = new Date();
    orderTime.setHours(h, m, 0, 0);
    return Math.max(0, Math.floor((now - orderTime) / 60000));
}

function updateCounters() {
    const pending   = ordersData.filter(o => o.status === 'pending').length;
    const preparing = ordersData.filter(o => o.status === 'preparing').length;
    const ready     = ordersData.filter(o => o.status === 'ready').length;

    document.getElementById('count-pending').textContent   = pending;
    document.getElementById('count-preparing').textContent = preparing;
    document.getElementById('count-ready').textContent     = ready;
    document.getElementById('count-total').textContent     = ordersData.length;

    // Update sidebar badge
    const badge = document.getElementById('badge-pending');
    if (badge) badge.textContent = pending;
}

// ── Empty State ───────────────────────────
function emptyCol(msg) {
    return `
    <div class="flex flex-col items-center justify-center py-16 text-center opacity-50">
        <i class="fa-solid fa-bowl-food text-4xl text-gray-300 mb-3"></i>
        <p class="text-xs font-semibold text-gray-400">${msg}</p>
    </div>`;
}

// ── Card: PENDING ─────────────────────────
function buildCardPending(order) {
    const elapsed  = getElapsedMin(order.waktu);
    const isUrgent = elapsed >= 10;

    const itemsHtml = order.items.map(item => `
        <div class="flex items-center justify-between">
            <span class="text-sm text-gray-700">${item.qty}x ${item.nama}</span>
            <button onclick="startItem(${order.id}, '${item.nama}', this)"
                    class="start-item-btn flex items-center gap-1 px-3 py-1 rounded-lg
                           bg-[#1B2FAA] text-white text-xs font-bold
                           hover:bg-[#1E3ACC] transition-all">
                <i class="fa-solid fa-play text-[9px]"></i> Start
            </button>
        </div>
    `).join('');

    return `
    <div class="bg-white rounded-xl border-2 border-red-200 p-4 shadow-sm" id="order-card-${order.id}">
        <div class="flex items-center justify-between mb-1">
            <span class="font-extrabold text-gray-900 text-base">${order.id_display}</span>
            <span class="flex items-center gap-1 text-xs font-semibold ${isUrgent ? 'timer-urgent' : 'text-gray-400'}">
                <i class="fa-regular fa-clock text-[10px]"></i> ${elapsed} min
            </span>
        </div>
        <p class="text-xs text-gray-400 mb-3">${order.meja}</p>
        <div class="flex flex-col gap-2.5 mb-4">${itemsHtml}</div>
        <button onclick="prosesSemuaOrder(${order.id})"
                class="w-full py-2 rounded-lg bg-[#1B2FAA] text-white text-sm font-bold
                       hover:bg-[#1E3ACC] transition-all">
            Proses Semua
        </button>
    </div>`;
}

// ── Card: PREPARING ───────────────────────
function buildCardPreparing(order) {
    const elapsed = getElapsedMin(order.waktu);

    const itemsHtml = order.items.map((item, idx) => {
        const done = item.done || false;
        return `
        <div class="flex items-center justify-between">
            <span class="text-sm ${done ? 'text-gray-300 line-through' : 'text-gray-700'}">
                ${item.qty}x ${item.nama}
            </span>
            ${done
                ? `<i class="fa-solid fa-circle-check text-green-500 text-lg"></i>`
                : `<button onclick="finishItem(${order.id}, ${idx})"
                           class="flex items-center gap-1 px-3 py-1 rounded-lg
                                  bg-orange-500 text-white text-xs font-bold
                                  hover:bg-orange-600 transition-all">
                        <i class="fa-solid fa-flag-checkered text-[9px]"></i> Finish
                   </button>`
            }
        </div>`;
    }).join('');

    return `
    <div class="bg-white rounded-xl border-2 border-yellow-300 p-4 shadow-sm" id="order-card-${order.id}">
        <div class="flex items-center justify-between mb-1">
            <span class="font-extrabold text-gray-900 text-base">${order.id_display}</span>
            <span class="flex items-center gap-1 text-xs font-semibold text-gray-400">
                <i class="fa-regular fa-clock text-[10px]"></i> ${elapsed} min
            </span>
        </div>
        <p class="text-xs text-gray-400 mb-3">${order.meja}</p>
        <div class="flex flex-col gap-2.5 mb-4">${itemsHtml}</div>
        <button onclick="selesaikanOrder(${order.id})"
                class="w-full py-2 rounded-lg bg-[#1B2FAA] text-white text-sm font-bold
                       hover:bg-[#1E3ACC] transition-all">
            Selesaikan Semua
        </button>
    </div>`;
}

// ── Card: READY ───────────────────────────
function buildCardReady(order) {
    const elapsed = getElapsedMin(order.waktu);

    const itemsHtml = order.items.map(item => `
        <div class="flex items-center justify-between">
            <span class="text-sm text-gray-400 line-through">${item.qty}x ${item.nama}</span>
            <i class="fa-solid fa-circle-check text-green-500 text-lg"></i>
        </div>
    `).join('');

    return `
    <div class="bg-white rounded-xl border-2 border-green-300 p-4 shadow-sm" id="order-card-${order.id}">
        <div class="flex items-center justify-between mb-1">
            <span class="font-extrabold text-gray-900 text-base">${order.id_display}</span>
            <span class="flex items-center gap-1 text-xs font-semibold text-gray-400">
                <i class="fa-regular fa-clock text-[10px]"></i> ${elapsed} min
            </span>
        </div>
        <p class="text-xs text-gray-400 mb-3">${order.meja}</p>
        <div class="flex flex-col gap-2.5 mb-4">${itemsHtml}</div>
        <button disabled
                class="w-full py-2 rounded-lg bg-gray-200 text-gray-500 text-sm font-bold cursor-not-allowed">
            Menunggu Pengambilan
        </button>
    </div>`;
}

// ── Render Kanban ─────────────────────────
function renderKanban() {
    const pending   = ordersData.filter(o => o.status === 'pending');
    const preparing = ordersData.filter(o => o.status === 'preparing');
    const ready     = ordersData.filter(o => o.status === 'ready');

    document.getElementById('col-pending').innerHTML =
        pending.length   ? pending.map(buildCardPending).join('')     : emptyCol('Tidak ada order menunggu');
    document.getElementById('col-preparing').innerHTML =
        preparing.length ? preparing.map(buildCardPreparing).join('') : emptyCol('Tidak ada order diproses');
    document.getElementById('col-ready').innerHTML =
        ready.length     ? ready.map(buildCardReady).join('')         : emptyCol('Tidak ada order siap');

    updateCounters();
}

// ── Actions ───────────────────────────────

// Start satu item (cek apakah semua sudah distart)
function startItem(orderId, itemNama, btn) {
    btn.innerHTML = '<i class="fa-solid fa-check text-[9px]"></i> Started';
    btn.disabled  = true;
    btn.className = 'flex items-center gap-1 px-3 py-1 rounded-lg bg-green-500 text-white text-xs font-bold cursor-not-allowed';

    // Cek apakah semua item sudah di-start
    const card       = btn.closest(`#order-card-${orderId}`);
    const remaining  = card.querySelectorAll('.start-item-btn:not([disabled])');
    if (remaining.length === 0) {
        setTimeout(() => prosesSemuaOrder(orderId), 400);
    }
}

// Pindah ke Preparing
function prosesSemuaOrder(orderId) {
    const order = ordersData.find(o => o.id === orderId);
    if (!order) return;
    order.status = 'preparing';
    order.items  = order.items.map(i => ({ ...i, done: false }));

    fetch(`/api/koki/update-order-status/${orderId}`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ status: 'preparing' })
    })
    .then(r => r.json())
    .then(() => {
        renderKanban();
        showToast(`${order.id_display} dipindah ke Preparing 🔥`, 'preparing');
    });
}

// Finish satu item di Preparing
function finishItem(orderId, itemIdx) {
    const order = ordersData.find(o => o.id === orderId);
    if (!order) return;
    order.items[itemIdx].done = true;

    const allDone = order.items.every(i => i.done);
    if (allDone) {
        setTimeout(() => selesaikanOrder(orderId), 400);
    } else {
        renderKanban();
    }
}

// Pindah ke Ready
function selesaikanOrder(orderId) {
    const order = ordersData.find(o => o.id === orderId);
    if (!order) return;
    order.status = 'ready';
    order.items  = order.items.map(i => ({ ...i, done: true }));

    fetch(`/api/koki/update-order-status/${orderId}`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ status: 'ready' })
    })
    .then(r => r.json())
    .then(() => {
        renderKanban();
        showToast(`${order.id_display} siap disajikan! ✅`, 'ready');
    });
}

// ── Init ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    renderKanban();
    // Auto-refresh timer setiap 60 detik (update elapsed time)
    setInterval(renderKanban, 60000);
});