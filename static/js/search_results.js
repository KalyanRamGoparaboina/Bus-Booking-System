document.addEventListener('DOMContentLoaded', () => {
    // Handling live tracking updates
    setInterval(updateLiveTracking, 60000); // Update every minute

    // Handling seat selection
    const busCards = document.querySelectorAll('.bus-card');
    const modal = document.getElementById('seat-modal');
    const closeBtn = document.querySelector('.close-btn');

    busCards.forEach(card => {
        const trackingElement = card.querySelector('.tracking');
        const busId = card.dataset.busId;

        trackingElement.addEventListener('click', () => {
            alert(`Live tracking for bus ID ${busId}`);
        });

        const selectSeatsBtn = card.querySelector('.select-seats-btn');
        selectSeatsBtn.addEventListener('click', (e) => {
            e.preventDefault();
            // Ensure URL is valid
            const url = selectSeatsBtn.href;
            if (url) {
                window.location.href = url;
            } else {
                console.error('Select seats button has no href attribute');
            }
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    function updateLiveTracking() {
        console.log('Live tracking update');
        // Add real tracking update logic here if needed
    }
});
