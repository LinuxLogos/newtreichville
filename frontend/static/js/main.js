document.addEventListener('DOMContentLoaded', function() {
    // Update current year in footer
    const yearSpan = document.getElementById('currentYear');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // Placeholder for reservation form submission
    const reservationForm = document.getElementById('reservationForm');
    if (reservationForm) {
        reservationForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const messagesDiv = document.getElementById('reservationMessages');
            messagesDiv.textContent = 'Traitement de la réservation...';
            messagesDiv.className = 'text-blue-600';
            // TODO: Implement actual form submission logic to backend
            console.log('Reservation form submitted (not yet sending to backend)');

            // Simulate API call
            setTimeout(() => {
                // Simulate success
                // messagesDiv.textContent = 'Réservation envoyée avec succès !';
                // messagesDiv.className = 'text-green-600';
                // reservationForm.reset();

                // Simulate error
                 messagesDiv.textContent = 'Erreur lors de la réservation. Veuillez réessayer.';
                 messagesDiv.className = 'text-red-600';
            }, 2000);
        });
    }

    // Placeholder for contact form submission
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const messagesDiv = document.getElementById('contactMessages');
            messagesDiv.textContent = 'Envoi du message...';
            messagesDiv.className = 'text-blue-600';
            // TODO: Implement actual form submission logic to backend
            console.log('Contact form submitted (not yet sending to backend)');

            // Simulate API call
            setTimeout(() => {
                // Simulate success
                messagesDiv.textContent = 'Message envoyé avec succès !';
                messagesDiv.className = 'text-green-600';
                contactForm.reset();

                // Simulate error
                // messagesDiv.textContent = 'Erreur lors de l\'envoi du message. Veuillez réessayer.';
                // messagesDiv.className = 'text-red-600';
            }, 2000);
        });
    }

    console.log('New Treichville main.js loaded.');
});
