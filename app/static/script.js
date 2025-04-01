document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.querySelector('#search-form');
    const showLyrics = document.querySelector("#show-lyrics");
    const closeLyrics = document.querySelector("#close-lyrics");
    const lyricsModal = document.querySelector("#lyrics");
    const themeBtn = document.querySelector('#themeBtn');
    const themeBtnIcon = document.querySelector('#theme-btn');
    const brandHeading = document.querySelector('#brand');
    const brandHeaderText = document.querySelector('.brand');
    const registerForm = document.querySelector('#register-form');
    const usernameInput = document.querySelector('#username');
    const emailInput = document.querySelector('#email');
    const passwordInput = document.querySelector('#password');
    const password2Input = document.querySelector('#password2');
    const passwordStrength = document.querySelector('#password-strength');
    const passwordConfirm = document.querySelector('#password-confirm');
    const showProfileEditor = document.querySelector('#edit-profile-btn');
    const closeProfileEditor = document.querySelector('#close-edit-profile');
    const editProfileModal = document.querySelector('#edit-profile-modal');
    const passResetForm = document.querySelector('#reset_password');

    themeBtn.addEventListener("click", () => {
        const currentIcon = themeBtnIcon.innerText;
        themeBtnIcon.innerText = 'light_mode' === currentIcon ? 'dark_mode' : 'light_mode';
        document.documentElement.setAttribute('data-theme', document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light')
    });

    let fadeTimeout;

    function closeFlashMessage() {
        const flashMessage = document.getElementById('flashMessage');
        if (flashMessage) {
            flashMessage.style.opacity = '0'; // Start fading out

            // Wait for the transition to finish before removing the element
            setTimeout(() => {
                flashMessage.remove(); // Remove the element from the DOM
            }, 500); // Match this duration with the CSS transition duration
        }
    }

    function startFadeOut() {
        fadeTimeout = setTimeout(closeFlashMessage, 5000); // Start fade out after 5 seconds
    }

    function stopFadeOut() {
        clearTimeout(fadeTimeout); // Stop the fade out
    }

    // Add event listeners for mouse hover
    const flashMessage = document.getElementById('flashMessage');
    if (flashMessage) {
        flashMessage.addEventListener('mouseenter', stopFadeOut);
        flashMessage.addEventListener('mouseleave', startFadeOut);

        // Add event listener for the close button
        const flashCloseBtn = flashMessage.querySelector('.flash-close-btn');
        if (flashCloseBtn) {
            flashCloseBtn.addEventListener('click', closeFlashMessage);
        }

        // Start the fade out when the page loads
        startFadeOut();
    }


    if (brandHeading) {
        document.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                brandHeading.style.opacity = '0';
                brandHeaderText.style.visibility = 'visible';
                brandHeaderText.style.opacity = '1';
            } else {
                brandHeaderText.style.opacity = '0';
                brandHeaderText.style.visibility = 'hidden';
                brandHeading.style.opacity = '1';
            }
        });
    }

    if (brandHeaderText) {
        brandHeaderText.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }


    if (searchForm) {
        searchForm.addEventListener('submit', function () {
            let searchButton = document.querySelector('#search');
            searchButton.setAttribute('aria-busy', 'true');
            searchButton.innerHTML = 'Searching...'
        });

        const artistName = document.querySelector('#artist');
        const songName = document.querySelector('#song');

        if (artistName.getAttribute('aria-invalid') === 'true') {
            artistName.addEventListener('input', () => {
                artistName.setAttribute('aria-invalid', 'false');
                document.querySelector('#artist-helper').innerText = '';
            });
        }

        if (songName.getAttribute('aria-invalid') === 'true')
            songName.addEventListener('input', () => {
                songName.setAttribute('aria-invalid', 'false');
                document.querySelector('#song-helper').innerText = '';
            });


        artistName.addEventListener('blur', () => {
            if (artistName.getAttribute('aria-invalid') === 'false') {
                artistName.removeAttribute('aria-invalid');
            }
        });

        songName.addEventListener('blur', () => {
            if (songName.getAttribute('aria-invalid') === 'false') {
                songName.removeAttribute('aria-invalid');
            }
        });
    }


    // Config
    const isOpenClass = "modal-is-open";
    const openingClass = "modal-is-opening";
    const closingClass = "modal-is-closing";
    const scrollbarWidthCssVar = "--pico-scrollbar-width";
    const animationDuration = 400; // ms
    let visibleModal = null;

    // Toggle modal
    const toggleModal = (event) => {
        event.preventDefault();
        const modal = document.getElementById(event.currentTarget.dataset.target);
        if (!modal) return;
        modal && (modal.open ? closeModal(modal) : openModal(modal));
    };

    // Open modal
    const openModal = (modal) => {
        const { documentElement: html } = document;
        const scrollbarWidth = getScrollbarWidth();
        if (scrollbarWidth) {
            html.style.setProperty(scrollbarWidthCssVar, `${scrollbarWidth}px`);
        }
        html.classList.add(isOpenClass, openingClass);
        setTimeout(() => {
            visibleModal = modal;
            html.classList.remove(openingClass);
        }, animationDuration);
        modal.showModal();
    };

    // Close modal
    const closeModal = (modal) => {
        visibleModal = null;
        const { documentElement: html } = document;
        html.classList.add(closingClass);
        setTimeout(() => {
            html.classList.remove(closingClass, isOpenClass);
            html.style.removeProperty(scrollbarWidthCssVar);
            modal.close();
        }, animationDuration);
    };

    // Close with a click outside
    document.addEventListener("click", (event) => {
        if (visibleModal === null) return;
        const modalContent = visibleModal.querySelector("article");
        const isClickInside = modalContent.contains(event.target);
        !isClickInside && closeModal(visibleModal);
    });

    // Close with Esc key
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && visibleModal) {
            closeModal(visibleModal);
        }
    });

    // Get scrollbar width
    const getScrollbarWidth = () => {
        const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
        return scrollbarWidth;
    };

    if (lyricsModal) {
        showLyrics.addEventListener('click', toggleModal);
        closeLyrics.addEventListener('click', toggleModal);
    }

    if (editProfileModal) {
        showProfileEditor.addEventListener('click', toggleModal);
        closeProfileEditor.addEventListener('click', toggleModal);
    }


    if (registerForm) {
        ; (function () {
            // all package will be available under zxcvbnts
            const options = {
                translations: zxcvbnts['language-en'].translations,
                graphs: zxcvbnts['language-common'].adjacencyGraphs,
                dictionary: {
                    ...zxcvbnts['language-common'].dictionary,
                    ...zxcvbnts['language-en'].dictionary,
                },
            }
            zxcvbnts.core.zxcvbnOptions.setOptions(options)

            passwordInput.addEventListener('input', () => {
                let result = zxcvbnts.core.zxcvbn(passwordInput.value, [usernameInput.value, emailInput.value]);
                passwordStrength.textContent = result.feedback.suggestions[0] || '' + ' ' + result.feedback.warning;

                if (result.score >= 3) {
                    passwordInput.setAttribute('aria-invalid', 'false');
                } else {
                    passwordInput.setAttribute('aria-invalid', 'true');
                }
            });

            passwordInput.addEventListener('blur', () => {
                if (passwordInput.getAttribute('aria-invalid') === 'false') {
                    passwordInput.removeAttribute('aria-invalid');
                }
            });

            password2Input.addEventListener('input', () => {
                if (password2Input.value === passwordInput.value) {
                    password2Input.setAttribute('aria-invalid', 'false');
                    passwordConfirm.textContent = '';
                    if (result.score >= 3) {
                        passwordInput.setAttribute('aria-invalid', 'false');
                        password2Input.setAttribute('aria-invalid', 'false');
                    } else {
                        passwordInput.setAttribute('aria-invalid', 'true');
                        password2Input.setAttribute('aria-invalid', 'true');
                    }

                } else {
                    password2Input.setAttribute('aria-invalid', 'true');
                    passwordConfirm.textContent = 'Passwords do not match!';
                }
            });

            password2Input.addEventListener('blur', () => {
                if (password2Input.getAttribute('aria-invalid') === 'false') {
                    password2Input.removeAttribute('aria-invalid');
                }
            });
        })()
    }

    if (passResetForm) {
        ; (function () {
            // all package will be available under zxcvbnts
            const options = {
                translations: zxcvbnts['language-en'].translations,
                graphs: zxcvbnts['language-common'].adjacencyGraphs,
                dictionary: {
                    ...zxcvbnts['language-common'].dictionary,
                    ...zxcvbnts['language-en'].dictionary,
                },
            }
            zxcvbnts.core.zxcvbnOptions.setOptions(options)

            passwordInput.addEventListener('input', () => {
                let result = zxcvbnts.core.zxcvbn(passwordInput.value);
                passwordStrength.textContent = result.feedback.suggestions[0] || '' + ' ' + result.feedback.warning;

                if (result.score >= 3) {
                    passwordInput.setAttribute('aria-invalid', 'false');
                } else {
                    passwordInput.setAttribute('aria-invalid', 'true');
                }
            });

            passwordInput.addEventListener('blur', () => {
                if (passwordInput.getAttribute('aria-invalid') === 'false') {
                    passwordInput.removeAttribute('aria-invalid');
                }
            });

            password2Input.addEventListener('input', () => {
                if (password2Input.value === passwordInput.value) {
                    password2Input.setAttribute('aria-invalid', 'false');
                    passwordConfirm.textContent = '';
                    if (result.score >= 3) {
                        passwordInput.setAttribute('aria-invalid', 'false');
                        password2Input.setAttribute('aria-invalid', 'false');
                    } else {
                        passwordInput.setAttribute('aria-invalid', 'true');
                        password2Input.setAttribute('aria-invalid', 'true');
                    }

                } else {
                    password2Input.setAttribute('aria-invalid', 'true');
                    passwordConfirm.textContent = 'Passwords do not match!';
                }
            });

            password2Input.addEventListener('blur', () => {
                if (password2Input.getAttribute('aria-invalid') === 'false') {
                    password2Input.removeAttribute('aria-invalid');
                }
            });
        })()
    }
});
