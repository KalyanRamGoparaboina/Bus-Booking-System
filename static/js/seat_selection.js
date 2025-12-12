<script>
document.addEventListener('DOMContentLoaded', function() {
    const seatElements = document.querySelectorAll('.seat');
    const totalPriceElement = document.getElementById('total-price');
    const selectedSeatsInput = document.getElementById('selected_seats');
    const totalAmountInput = document.getElementById('total_amount');
    const pickupLocationSelect = document.getElementById('pickup-location');
    const dropLocationSelect = document.getElementById('drop-location');
    const formPickupLocation = document.getElementById('form_pickup_location');
    const formDropLocation = document.getElementById('form_drop_location');

    let totalPrice = 0;
    let selectedSeats = [];

    // Seat click logic
    seatElements.forEach(seat => {
        const price = parseInt(seat.getAttribute('data-price')) || 0;

        seat.addEventListener('click', function() {
            const seatNumber = this.getAttribute('data-seat');

            if (this.classList.contains('available')) {
                this.classList.add('selected');
                this.classList.remove('available');
                totalPrice += price;
                selectedSeats.push(seatNumber);
            } else if (this.classList.contains('selected')) {
                this.classList.add('available');
                this.classList.remove('selected');
                totalPrice -= price;
                selectedSeats = selectedSeats.filter(s => s !== seatNumber);
            }

            totalPriceElement.textContent = totalPrice;
            selectedSeatsInput.value = selectedSeats.join(',');
            totalAmountInput.value = totalPrice;
        });
    });

    // Filter buttons logic
    document.querySelectorAll('.filter-btn').forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            seatElements.forEach(seat => {
                if (filter === 'all' || seat.getAttribute('data-type') === filter) {
                    seat.style.display = 'block';
                } else {
                    seat.style.display = 'none';
                }
            });
        });
    });

    // Pickup and drop location updates
    if (pickupLocationSelect && formPickupLocation) {
        pickupLocationSelect.addEventListener('change', function() {
            formPickupLocation.value = this.value;
        });
    }

    if (dropLocationSelect && formDropLocation) {
        dropLocationSelect.addEventListener('change', function() {
            formDropLocation.value = this.value;
        });
    }
});
</script>
