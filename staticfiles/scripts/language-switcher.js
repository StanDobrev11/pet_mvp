// Language switcher functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get all language switcher buttons
    const languageSwitchers = document.querySelectorAll('.language-switcher');

    // Add click event listener to each button
    languageSwitchers.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            // Get the language code from the data attribute
            const languageCode = this.getAttribute('data-language');

            // Store the language preference in localStorage
            localStorage.setItem('django_language', languageCode);

            // Set the cookie for Django to use on the server side
            document.cookie = `django_language=${languageCode}; path=/; max-age=31536000`;

            // Reload the current page to apply the language change
            // This avoids the redirect to login page by not using Django's set_language view
            window.location.reload();
        });
    });
});
