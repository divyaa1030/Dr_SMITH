// Dr. SMITH - JavaScript

document.addEventListener('DOMContentLoaded', function() {

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Active sidebar link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(link => {
        if (link.getAttribute('href') === currentPath || 
            currentPath.includes(link.getAttribute('href'))) {
            link.classList.add('active');
        }
    });

    // Fake Medicine Reminder Notification
    function showReminder() {
        if (Math.random() > 0.7) {
            const notification = document.createElement('div');
            notification.style.position = 'fixed';
            notification.style.bottom = '20px';
            notification.style.right = '20px';
            notification.style.background = '#22D3EE';
            notification.style.color = '#0F172A';
            notification.style.padding = '15px 20px';
            notification.style.borderRadius = '10px';
            notification.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
            notification.style.zIndex = '9999';
            notification.innerHTML = `
                <strong>🔔 Medicine Reminder</strong><br>
                Take Paracetamol 500mg now
            `;
            document.body.appendChild(notification);

            setTimeout(() => {
                notification.style.transition = 'all 0.5s';
                notification.style.opacity = '0';
                notification.style.transform = 'translateY(20px)';
                setTimeout(() => notification.remove(), 500);
            }, 6000);
        }
    }

    // Show random reminder every 25 seconds (demo)
    setInterval(showReminder, 25000);
    showReminder(); // Show one immediately

    console.log("%cDr. SMITH - Smart Medical Intelligence Loaded Successfully ✅", 
                "color: #1E3A8A; font-weight: bold; font-size: 14px;");
});