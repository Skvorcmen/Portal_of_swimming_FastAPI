// Глобальная функция для показа уведомлений
window.showToast = function(message, type = 'success') {
    // Находим или создаем контейнер для тостов
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Определяем цвет и иконку в зависимости от типа
    const config = {
        success: { bg: 'bg-success', icon: 'fa-check-circle' },
        error: { bg: 'bg-danger', icon: 'fa-exclamation-circle' },
        warning: { bg: 'bg-warning', icon: 'fa-exclamation-triangle' },
        info: { bg: 'bg-info', icon: 'fa-info-circle' }
    };
    
    const cfg = config[type] || config.success;
    
    // Создаем тост
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${cfg.bg} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="3000">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${cfg.icon} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();
    
    // Удаляем элемент после скрытия
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
};

// Успешное уведомление
window.showSuccess = function(message) {
    window.showToast(message, 'success');
};

// Ошибка
window.showError = function(message) {
    window.showToast(message, 'error');
};

// Предупреждение
window.showWarning = function(message) {
    window.showToast(message, 'warning');
};

// Информация
window.showInfo = function(message) {
    window.showToast(message, 'info');
};

console.log('✅ Toast notifications loaded');
