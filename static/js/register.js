document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');

    const usernameError = document.getElementById('usernameError');
    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');
    const confirmPasswordError = document.getElementById('confirmPasswordError');

    const usernameRegex = /^[a-zA-Z0-9_]{3,15}$/; // Only letters, numbers, and underscores (3-15 chars)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Basic email format
    const passwordRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,20}$/; // At least one number, one uppercase and lowercase letter, and between 6-20 chars

    // Function to validate username
    function validateUsername() {
        if (!usernameRegex.test(username.value)) {
            usernameError.textContent = "Username must be 3-15 characters long, with no special symbols.";
            return false;
        } else {
            usernameError.textContent = '';
            return true;
        }
    }

    // Function to validate email
    function validateEmail() {
        if (!emailRegex.test(email.value)) {
            emailError.textContent = "Please enter a valid email address.";
            return false;
        } else {
            emailError.textContent = '';
            return true;
        }
    }

    // Function to validate password
    function validatePassword() {
        if (!passwordRegex.test(password.value)) {
            passwordError.textContent = "Password must be 6-20 characters long, include a number, an uppercase, and a lowercase letter.";
            return false;
        } else {
            passwordError.textContent = '';
            return true;
        }
    }

    // Function to validate password match
    function validateConfirmPassword() {
        if (password.value !== confirmPassword.value) {
            confirmPasswordError.textContent = "Passwords do not match.";
            return false;
        } else {
            confirmPasswordError.textContent = '';
            return true;
        }
    }

    // Add event listeners for real-time validation
    username.addEventListener('input', validateUsername);
    email.addEventListener('input', validateEmail);
    password.addEventListener('input', validatePassword);
    confirmPassword.addEventListener('input', validateConfirmPassword);

    // Form submission validation
    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Prevent form submission for validation

        const isValidUsername = validateUsername();
        const isValidEmail = validateEmail();
        const isValidPassword = validatePassword();
        const isPasswordsMatch = validateConfirmPassword();

        if (isValidUsername && isValidEmail && isValidPassword && isPasswordsMatch) {
            form.submit(); // If all validations pass, submit the form
        }
    });
});
