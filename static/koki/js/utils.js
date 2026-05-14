// =========================================
// TERRALOG KOKI - Utilities
// =========================================

// ── Toast ─────────────────────────────────
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const msg   = document.getElementById('toast-message');
    const icon  = document.getElementById('toast-icon');

    const cfg = {
        success:   { border: '#10B981', cls: 'fa-circle-check text-green-500' },
        preparing: { border: '#F59E0B', cls: 'fa-fire-burner text-yellow-500' },
        ready:     { border: '#10B981', cls: 'fa-check-circle text-green-500' },
        error:     { border: '#EF4444', cls: 'fa-circle-xmark text-red-500' },
    };
    const c = cfg[type] || cfg.success;
    toast.style.borderLeftColor = c.border;
    icon.className = `fa-solid ${c.cls} text-base`;
    msg.textContent = message;
    toast.classList.remove('hide');
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hide');
    }, 3000);
}

// ── Modal ─────────────────────────────────
function openModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('hidden');
    el.classList.add('active');
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.add('hidden');
    el.classList.remove('active');
}

// Tutup modal saat klik backdrop
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) closeModal(this.id);
        });
    });
});

// ── Toggle Password ───────────────────────
function togglePwd(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
    btn.querySelector('i').className =
        input.type === 'password' ? 'fa-regular fa-eye' : 'fa-regular fa-eye-slash';
}

// ── Logout ────────────────────────────────
function prosesLogout() {
    showToast('Berhasil logout. Sampai jumpa!', 'success');
    closeModal('modalLogout');
    setTimeout(() => { window.location.href = '/login'; }, 1500);
}