document.addEventListener('DOMContentLoaded', () => {
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    const cartCountElement = document.getElementById('cart-count');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();

            const buttonElement = event.target.closest('.add-to-cart-btn');
            if (!buttonElement) return;

            const url = buttonElement.dataset.url;
            const originalButtonText = buttonElement.textContent;

            const loginLink = document.querySelector('a[href*="/login"]');
            const isLoggedIn = !loginLink;

            if (!isLoggedIn) {
                const loginUrl = `/login/?next=${encodeURIComponent(window.location.pathname + window.location.search)}`;
                console.log("User not logged in. Redirecting to:", loginUrl);
                window.location.href = loginUrl;
                return;
            }
            console.log("User logged in. Proceeding with fetch to:", url);
            buttonElement.textContent = 'Adding...';
            buttonElement.disabled = true;

            fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest' 
                }
            })
            .then(response => {
                if (!response.ok) {
                    const contentType = response.headers.get("content-type");
                    if (contentType && contentType.indexOf("application/json") !== -1) {
                       return response.json().then(errData => {
                           throw new Error(errData.message || `Server error: ${response.status}`);
                       });
                    } else {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                }
                const contentType = response.headers.get("content-type");
                 if (contentType && contentType.indexOf("application/json") !== -1) {
                    return response.json();
                 } else {
                    console.warn("Received non-JSON response even though status was OK:", response);
                    throw new Error("Unexpected response format from server.");
                 }
            })
            .then(data => {
                if (data.status === 'success') {
                    console.log("Successfully added to cart:", data);
                    buttonElement.textContent = '✓ Added!';
                    if (cartCountElement && data.cart_count !== undefined) {
                        cartCountElement.textContent = data.cart_count;
                        cartCountElement.style.transform = 'scale(1.3)';
                        setTimeout(() => { cartCountElement.style.transform = 'scale(1)'; }, 150);
                    }
                    setTimeout(() => {
                        if (document.body.contains(buttonElement)) {
                           buttonElement.textContent = originalButtonText;
                           buttonElement.disabled = false;
                        }
                    }, 1500);
                } else {
                    console.error('Error adding to cart (from JSON):', data.message);
                    alert(`Error: ${data.message || 'Could not add item.'}`);
                    if (!window.location.href.includes('/login/')) {
                        buttonElement.textContent = originalButtonText;
                        buttonElement.disabled = false;
                    }
                }
            })
            .catch(error => {
                console.error('Add to Cart Fetch Error:', error);
                alert(`Could not add item to cart. ${error.message}`);
                 if (!window.location.href.includes('/login/')) {
                    if (document.body.contains(buttonElement)) {
                       buttonElement.textContent = originalButtonText;
                       buttonElement.disabled = false;
                    }
                 }
            });
        });
    });
    const passwordToggles = document.querySelectorAll('.password-toggle-icon');

    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const passwordInput = toggle.previousElementSibling;

            if (passwordInput && (passwordInput.type === 'password' || passwordInput.type === 'text')) {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    toggle.classList.remove('fa-eye');
                    toggle.classList.add('fa-eye-slash');
                } else {
                    passwordInput.type = 'password';
                    toggle.classList.remove('fa-eye-slash');
                    toggle.classList.add('fa-eye');
                }
            } else {
                console.error("Could not find password input for toggle:", toggle);
            }
        });
    });


});
document.addEventListener('DOMContentLoaded', () => {

    const uploadButton = document.getElementById('upload_pic_button');
    const hiddenFileInput = document.getElementById('id_profile_pic_input');
    const filenameSpan = document.getElementById('selected_filename');

    if (uploadButton && hiddenFileInput && filenameSpan) {

        uploadButton.addEventListener('click', () => {
            hiddenFileInput.click();
        });

        hiddenFileInput.addEventListener('change', () => {
            if (hiddenFileInput.files && hiddenFileInput.files.length > 0) {
                filenameSpan.textContent = hiddenFileInput.files[0].name;
            } else {
                filenameSpan.textContent = '';
            }
        });

    } else {
        if (!uploadButton) console.error("Custom upload button not found.");
        if (!hiddenFileInput) console.error("Hidden file input not found.");
        if (!filenameSpan) console.error("Filename display span not found.");
    }

});