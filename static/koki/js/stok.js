// =========================================
// TERRALOG KOKI - Stok Menu
// =========================================

// menuData di-inject dari template via <script> di stok_menu.html

let stokKatFilter = 'Semua';
let stokSearchQ   = '';

// ── Kategori Badge Color ──────────────────
const katColor = {
    'Coffee':     'bg-purple-100 text-purple-700',
    'Non Coffee': 'bg-pink-100 text-pink-700',
    'Food':       'bg-blue-100 text-blue-700',
    'Snack':      'bg-yellow-100 text-yellow-700',
};

// ── Render Table ──────────────────────────
function renderStokTable() {
    const tbody = document.getElementById('stokTableBody');
    const filtered = menuData.filter(m => {
        const matchKat    = stokKatFilter === 'Semua' || m.kategori === stokKatFilter;
        const matchSearch = m.nama.toLowerCase().includes(stokSearchQ.toLowerCase());
        return matchKat && matchSearch;
    });

    if (!filtered.length) {
        tbody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center py-14 text-gray-300">
                <i class="fa-solid fa-magnifying-glass text-4xl mb-3 block"></i>
                <p class="text-sm font-semibold">Menu tidak ditemukan</p>
            </td>
        </tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(m => {
        const stokColor = m.stok === 0 ? 'text-red-500' : m.stok <= 5 ? 'text-orange-500' : 'text-gray-800';
        const stokLabel = m.stok === 0
            ? '<span class="block text-[10px] text-red-400 font-bold">HABIS</span>'
            : m.stok <= 5
                ? '<span class="block text-[10px] text-orange-400 font-bold">HAMPIR HABIS</span>'
                : '';

        return `
        <tr class="border-b border-gray-100 hover:bg-blue-50/30 transition-colors">
            <!-- Nama -->
            <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-lg bg-[#1B2FAA]/10 flex items-center justify-center flex-shrink-0">
                        <i class="fa-solid fa-utensils text-[#1B2FAA] text-xs"></i>
                    </div>
                    <span class="font-semibold text-gray-800">${m.nama}</span>
                </div>
            </td>
            <!-- Kategori -->
            <td class="px-6 py-4 text-center">
                <span class="px-3 py-1 rounded-full text-xs font-bold ${katColor[m.kategori] || 'bg-gray-100 text-gray-600'}">
                    ${m.kategori}
                </span>
            </td>
            <!-- Stok Saat Ini -->
            <td class="px-6 py-4 text-center">
                <span class="text-lg font-extrabold ${stokColor}">${m.stok}</span>
                ${stokLabel}
            </td>
            <!-- Update Stok -->
            <td class="px-6 py-4">
                <div class="flex items-center justify-center gap-2">
                    <button onclick="adjustStok(${m.id}, -1)"
                            class="w-8 h-8 rounded-lg border-2 border-gray-200 text-gray-500
                                   hover:border-red-300 hover:text-red-500 hover:bg-red-50
                                   font-bold text-lg transition-all flex items-center justify-center">
                        −
                    </button>
                    <input type="number" id="stok-${m.id}" value="${m.stok}" min="0"
                           class="w-16 text-center px-2 py-1.5 border border-gray-200 rounded-lg
                                  text-sm font-bold outline-none focus:border-[#1B2FAA] transition-colors">
                    <button onclick="adjustStok(${m.id}, 1)"
                            class="w-8 h-8 rounded-lg border-2 border-gray-200 text-gray-500
                                   hover:border-green-300 hover:text-green-500 hover:bg-green-50
                                   font-bold text-lg transition-all flex items-center justify-center">
                        +
                    </button>
                    <button onclick="simpanStok(${m.id})"
                            class="px-3 py-1.5 rounded-lg bg-[#1B2FAA] text-white text-xs font-bold
                                   hover:bg-[#1E3ACC] transition-all">
                        Simpan
                    </button>
                </div>
            </td>
            <!-- Toggle Status -->
            <td class="px-6 py-4 text-center">
                <label class="toggle-switch relative inline-block w-[46px] h-6 cursor-pointer">
                    <input type="checkbox" ${m.status ? 'checked' : ''}
                           onchange="toggleMenuStatus(${m.id}, this)">
                    <span class="toggle-slider"></span>
                </label>
            </td>
        </tr>`;
    }).join('');
}

// ── Filter Kategori ───────────────────────
function filterStokKat(kat, btn) {
    stokKatFilter = kat;
    document.querySelectorAll('.stok-kat-btn').forEach(b => {
        b.classList.remove('bg-[#1B2FAA]', 'text-white');
        b.classList.add('border-2', 'border-[#1B2FAA]', 'text-[#1B2FAA]');
    });
    btn.classList.add('bg-[#1B2FAA]', 'text-white');
    btn.classList.remove('border-2', 'border-[#1B2FAA]', 'text-[#1B2FAA]');
    renderStokTable();
}

// ── Filter Search ─────────────────────────
function filterStokSearch() {
    stokSearchQ = document.getElementById('searchMenu').value;
    renderStokTable();
}

// ── Adjust Stok ───────────────────────────
function adjustStok(menuId, delta) {
    const input  = document.getElementById(`stok-${menuId}`);
    const newVal = Math.max(0, parseInt(input.value || 0) + delta);
    input.value  = newVal;
    const m = menuData.find(x => x.id === menuId);
    if (m) m.stok = newVal;
}

// ── Simpan Stok ───────────────────────────
function simpanStok(menuId) {
    const stok = parseInt(document.getElementById(`stok-${menuId}`).value || 0);
    const m    = menuData.find(x => x.id === menuId);
    if (!m) return;

    fetch(`/api/koki/update-stok/${menuId}`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ stok })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            m.stok = stok;
            if (stok === 0) m.status = false;
            renderStokTable();
            showToast(`Stok "${m.nama}" diperbarui → ${stok}`);
        }
    });
}

// ── Toggle Status ─────────────────────────
function toggleMenuStatus(menuId, checkbox) {
    const m = menuData.find(x => x.id === menuId);
    if (m) m.status = checkbox.checked;

    fetch(`/api/toggle-menu-status/${menuId}`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ status: checkbox.checked })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) showToast('Status menu diperbarui!');
    });
}

// ── Init ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    renderStokTable();
});