function showNotification(message, category) {
    var notificationContainer = document.getElementById('notification-container');

    var alertDiv = document.createElement('div');
    alertDiv.classList.add('alert', 'alert-' + category, 'text-center', 'alert-dismissible', 'fade', 'show', 'm-auto');
    alertDiv.textContent = message;

    var closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.classList.add('btn-close');
    closeButton.setAttribute('data-bs-dismiss', 'alert');
    closeButton.setAttribute('aria-label', 'Close');

    alertDiv.appendChild(closeButton);
    notificationContainer.appendChild(alertDiv);

    setTimeout(function () {
        alertDiv.remove();
    }, 5000);
}