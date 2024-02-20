function togglePasswordVisibility() {
    var passwordInput = document.querySelector('[name="password"]');
    var toggleIcon = document.getElementById('toggleIcon');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.name = 'eye-slash'; // Change the icon to 'eye-slash'
    } else {
        passwordInput.type = 'password';
        toggleIcon.name = 'eye'; // Change the icon back to 'eye'
    }
}