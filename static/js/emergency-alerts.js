// static/js/emergency-alerts.js
document.addEventListener('DOMContentLoaded', function() {
    const emergencyMessage = document.getElementById('emergency-message');
    const notificationsList = document.getElementById('notifications-list');
    const languageFilter = document.getElementById('language-filter');

    // Sample emergency alerts data
    const emergencyAlerts = [
        {
            id: 1,
            message: {
                en: "Heavy rainfall warning for Mumbai region. Please stay indoors.",
                mr: "मुंबई परिसरात जोरदार पावसाचा इशारा. कृपया घरात रहा.",
                hi: "मुंबई क्षेत्र के लिए भारी वर्षा की चेतावनी। कृपया घर के अंदर रहें।"
            },
            level: "emergency",
            timestamp: new Date()
        },
        // Add more sample alerts
    ];

    // Sample notifications data
    const notifications = [
        {
            id: 1,
            title: {
                en: "COVID-19 Vaccination Drive Update",
                mr: "कोविड-१९ लसीकरण मोहीम अपडेट",
                hi: "कोविड-१९ टीकाकरण अभियान अपडेट"
            },
            message: {
                en: "New vaccination centers opened in Pune district",
                mr: "पुणे जिल्ह्यात नवीन लसीकरण केंद्रे सुरू",
                hi: "पुणे जिले में नए टीकाकरण केंद्र खुले"
            },
            timestamp: new Date()
        },
        // Add more sample notifications
    ];

    function updateEmergencyMessage(lang) {
        if (emergencyAlerts.length > 0) {
            const latestAlert = emergencyAlerts[0];
            emergencyMessage.textContent = latestAlert.message[lang];
        }
    }

    function updateNotificationsList(lang) {
        notificationsList.innerHTML = '';
        notifications.forEach(notification => {
            const notificationDiv = document.createElement('div');
            notificationDiv.className = 'bg-gray-100 p-4 rounded-lg';
            notificationDiv.innerHTML = `
                <h4 class="font-bold text-gray-800">${notification.title[lang]}</h4>
                <p class="text-gray-600 mt-2">${notification.message[lang]}</p>
                <p class="text-sm text-gray-500 mt-2">${notification.timestamp.toLocaleString()}</p>
            `;
            notificationsList.appendChild(notificationDiv);
        });
    }

    // Initialize with default language
    const defaultLang = 'mr';
    updateEmergencyMessage(defaultLang);
    updateNotificationsList(defaultLang);

    // Language filter change handler
    languageFilter.addEventListener('change', (e) => {
        const selectedLang = e.target.value;
        updateEmergencyMessage(selectedLang);
        updateNotificationsList(selectedLang);
    });

    // Simulated real-time updates
    setInterval(() => {
        const selectedLang = languageFilter.value;
        updateEmergencyMessage(selectedLang);
    }, 30000);
});