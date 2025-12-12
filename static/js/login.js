document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');
    const loginMessage = document.getElementById('loginMessage');

    const usernameRegex = /^[a-zA-Z0-9_]{3,15}$/; // Username rules

    // Username validation
    function validateUsername() {
        if (!usernameRegex.test(username.value)) {
            usernameError.textContent = "Username must be 3-15 characters long.";
            return false;
        } else {
            usernameError.textContent = '';
            return true;
        }
    }

    // Password validation (basic check, you can enhance based on your requirements)
    function validatePassword() {
        if (password.value.length < 6) {
            passwordError.textContent = "Password must be at least 6 characters long.";
            return false;
        } else {
            passwordError.textContent = '';
            return true;
        }
    }

    // Form submit handler
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const isValidUsername = validateUsername();
        const isValidPassword = validatePassword();

        if (isValidUsername && isValidPassword) {
            loginMessage.textContent = "Logging in..."; // Simulating successful submission
            loginMessage.style.color = 'green';
            form.submit();
        } else {
            loginMessage.textContent = "Please fix the errors and try again.";
            loginMessage.style.color = 'red';
        }
    });

    username.addEventListener('input', validateUsername);
    password.addEventListener('input', validatePassword);
});
