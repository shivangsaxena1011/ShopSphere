// ShopSphere Global Client-Side Interactions

document.addEventListener('DOMContentLoaded', function () {
  initAjaxCart();
});

function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const isSuccess = type === 'success';
  const bgColor = isSuccess ? 'bg-emerald-600' : 'bg-red-600';
  const icon = isSuccess ? 'check_circle' : 'error';

  toast.className = `${bgColor} text-white px-5 py-3 rounded-2xl shadow-lg flex items-center gap-3 text-xs font-semibold pointer-events-auto transform translate-y-2 opacity-0 transition-all duration-300 z-50`;
  toast.innerHTML = `
    <span class="material-symbols-outlined text-[18px]">${icon}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  // Trigger enter animation
  setTimeout(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');
  }, 10);

  // Auto remove after 3.5s
  setTimeout(() => {
    toast.classList.remove('translate-y-0', 'opacity-100');
    toast.classList.add('translate-y-2', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function initAjaxCart() {
  document.querySelectorAll('.ajax-cart-form').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalHTML = submitBtn ? submitBtn.innerHTML : '';

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
          <svg class="animate-spin h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <span>Adding...</span>
        `;
      }

      const formData = new FormData(form);

      fetch(form.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      })
      .then(response => {
        if (!response.ok) throw new Error('Network error');
        return response.json();
      })
      .then(data => {
        if (data.status === 'success') {
          // Update navbar cart badge
          const badge = document.getElementById('nav-cart-badge');
          if (badge && data.cart_count !== undefined) {
            badge.innerText = data.cart_count;
            badge.classList.add('scale-125');
            setTimeout(() => badge.classList.remove('scale-125'), 300);
          }
          showToast(data.message || 'Product added to your cart!', 'success');
        } else {
          showToast(data.message || 'Could not add product', 'error');
        }
      })
      .catch(error => {
        console.error('Add to cart error:', error);
        form.submit(); // fallback to standard POST
      })
      .finally(() => {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalHTML;
        }
      });
    });
  });
}
