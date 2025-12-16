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

        // Set price data from server to seats
        seatElements.forEach(seat => {
            const price = parseInt(seat.getAttribute('data-price'));
            seat.addEventListener('click', function() {
                if (this.classList.contains('available')) {
                    this.classList.add('selected');
                    this.classList.remove('available');
                    totalPrice += price;
                    selectedSeats.push(this.getAttribute('data-seat'));
                } else if (this.classList.contains('selected')) {
                    this.classList.add('available');
                    this.classList.remove('selected');
                    totalPrice -= price;
                    selectedSeats = selectedSeats.filter(seat => seat !== this.getAttribute('data-seat'));
                }
                totalPriceElement.textContent = totalPrice;
                selectedSeatsInput.value = selectedSeats.join(',');
                totalAmountInput.value = totalPrice;
            });
        });

        // Event listener for filter buttons
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

        // Update hidden inputs with selected pickup and drop locations
        pickupLocationSelect.addEventListener('change', function() {
            formPickupLocation.value = this.value;
        });

        dropLocationSelect.addEventListener('change', function() {
            formDropLocation.value = this.value;
        });
    });
</script>
