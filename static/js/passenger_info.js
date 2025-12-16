// passenger_info.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('passenger-form');

    form.addEventListener('submit', function(event) {
        let isValid = true;

        // Clear previous errors
        document.querySelectorAll('.error-message').forEach(el => el.textContent = '');

        // Validate Full Name
        const fullName = document.getElementById('full_name').value.trim();
        if (fullName.length < 2) {
            document.getElementById('name-error').textContent = 'Name must be at least 2 characters long.';
            isValid = false;
        }

        // Validate Age
        const age = document.getElementById('age').value;
        if (age < 18) {
            document.getElementById('age-error').textContent = 'Passenger must be at least 18 years old.';
            isValid = false;
        }

        // Validate Gender
        const gender = document.getElementById('gender').value;
        if (!gender) {
            document.getElementById('gender-error').textContent = 'Please select a gender.';
            isValid = false;
        }

        // Validate Email
        const email = document.getElementById('email').value.trim();
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            document.getElementById('email-error').textContent = 'Invalid email address.';
            isValid = false;
        }

        // Validate Phone Number
        const phone = document.getElementById('phone').value.trim();
        if (phone.length < 10) {
            document.getElementById('phone-error').textContent = 'Phone number must be at least 10 digits long.';
            isValid = false;
        }

        // Validate ID Proof Number
        const idProof = document.getElementById('id_proof').value.trim();
        if (idProof.length < 5) {
            document.getElementById('id-proof-error').textContent = 'ID Proof number must be valid.';
            isValid = false;
        }

        // Validate Address
        const address = document.getElementById('address').value.trim();
        if (address.length < 10) {
            document.getElementById('address-error').textContent = 'Address must be at least 10 characters long.';
            isValid = false;
        }

        // Validate Date of Birth
        const dob = new Date(document.getElementById('dob').value);
        const today = new Date();
        if (dob > today) {
            document.getElementById('dob-error').textContent = 'Date of Birth cannot be in the future.';
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault(); // Prevent form submission if invalid
        }
    });
});
