document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.querySelector('#search-form');
    const themeBtn = document.querySelector('#themeBtn');
    const themeBtnIcon = document.querySelector('#theme-btn');
    const navTitle = document.querySelector('#nav-title');
    const headerTitle = document.querySelector('#header-title');
    const loginForm = document.querySelector('#login_user_form');
    const usernameInput = document.querySelector('#username');
    const usernameHelper = document.querySelector('#username-helper');
    const passwordInput = document.querySelector('#password');
    const passwordHelper = document.querySelector('#password-helper');
    const passwordConfirmInput = document.querySelector('#password_confirm');
    const passwordConfirm = document.querySelector('#password-confirm');
    const editProfileModal = document.querySelector('#edit-profile-modal');
    const lastfmLinkModal = document.querySelector('#lastfm-link-modal')
    const accountDelBtm = document.querySelector('.delete-account');
    const editRoleForm = document.querySelector('[name="edit_role_form"]');
    const editServicesForm = document.querySelector('[name="edit_service_form"]');
    const manageUserAccountForm = document.querySelector('[name="manage_user_account_form"]');
    const tabControl = document.querySelector('[role="tab-control"]');
    const togglePasswordContainer = document.querySelector(".password-toggle-icon");
    const togglePassword = document.querySelector(".password-toggle-icon i");
    const addURIBtn = document.querySelector('#add-redirect-uri');
    const endpointSelect = document.getElementById('endpoint-select');
    const appiMeDocs = document.getElementById('appi-me-docs');
    const activitySvgDocs = document.getElementById('activity-svg-docs');

    // Accordion: only one <details> open at a time
    document.querySelectorAll('.faq-section details').forEach((detail) => {
        detail.addEventListener('toggle', function () {
            if (this.open) {
                document.querySelectorAll('.faq-section details').forEach((otherDetail) => {
                    if (otherDetail !== this) otherDetail.removeAttribute('open');
                });
            }
        });
    });

    if (endpointSelect && appiMeDocs && activitySvgDocs) {
        function updateDocsDisplay() {
            if (endpointSelect.value === '/api/activity.svg') {
                appiMeDocs.style.display = 'none';
                activitySvgDocs.style.display = 'initial';
            } else {
                appiMeDocs.style.display = '';
                activitySvgDocs.style.display = 'none';
            }
        }
        endpointSelect.addEventListener('change', updateDocsDisplay);
        // Set initial state on page load
        updateDocsDisplay();
    }

    function convertToUserTimezone(datetimeString) {
        // Get the parts
        const [Y, M, D, H, m] = datetimeString.split(/\D/);
        // Create a Date object from the datetime string
        const date = new Date(Date.UTC(Y, M - 1, D, H, m));
        let hours = date.getHours();
        const minutes = date.getMinutes();

        // Convert hours from 24-hour to 12-hour format
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'

        // Format minutes to always be two digits
        const formattedMinutes = minutes < 10 ? '0' + minutes : minutes;

        // Get month name
        const options = { month: 'long' };
        const month = new Intl.DateTimeFormat('en-US', options).format(date);

        // Construct the final formatted string
        const formattedDate = `${date.getFullYear()}, ${date.getDate()} ${month}`;
        const formattedTime = `${hours}:${minutes} ${ampm}`
        return [formattedDate, formattedTime];
    }

    // Get the datetime from the element or data-tooltip attribute
    const datatimeElements = document.querySelectorAll('.datetime');
    if (datatimeElements) {
        datatimeElements.forEach(datatimeElement => {
            // Convert and display the formatted date
            const formattedDateTime = convertToUserTimezone(datatimeElement.innerText);
            datatimeElement.innerText = formattedDateTime[0];
            datatimeElement.setAttribute('data-tooltip', 'at ' + formattedDateTime[1])
        });
    }

    function isValidUsername(username) {
        // Regular expression to match the criteria
        const regex = /^[A-Za-z0-9-]*$/; // Allows letters, numbers, and hyphen (-)
        // const hyphenCount = (username.match(/-/g) || []).length; // Count hyphens

        // Check if the input matches the regex and contains at most one hyphen
        return regex.test(username) // && hyphenCount <= 1;
    }


    themeBtn.addEventListener("click", () => {
        const currentIcon = themeBtnIcon.innerText;
        themeBtnIcon.innerText = 'light_mode' === currentIcon ? 'dark_mode' : 'light_mode';
        document.documentElement.setAttribute('data-theme', document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
    });

    let fadeTimeout;

    function closeFlashMessage(flashMessage) {
        if (flashMessage) {
            flashMessage.classList.add('fade-out'); // Add fade-out class

            // Wait for the transition to finish before removing the element
            setTimeout(() => {
                flashMessage.remove(); // Remove the element from the DOM
            }, 500); // Match this duration with the CSS transition duration
        }
    }

    function startFadeOut(flashMessage) {
        fadeTimeout = setTimeout(() => closeFlashMessage(flashMessage), 5000); // Start fade out after 5 seconds
    }

    function stopFadeOut(flashMessage) {
        clearTimeout(fadeTimeout); // Stop the fade out
        flashMessage.classList.remove('fade-out'); // Remove fade-out class to restore opacity
    }

    // Add event listeners for mouse hover
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(flashMessage => {
        if (flashMessage) {
            flashMessage.addEventListener('mouseenter', () => stopFadeOut(flashMessage));
            flashMessage.addEventListener('mouseleave', () => startFadeOut(flashMessage));

            // Add event listener for the close button
            const flashCloseBtns = flashMessage.querySelectorAll('.flash-close-btn');
            flashCloseBtns.forEach(flashCloseBtn => {
                if (flashCloseBtn) {
                    flashCloseBtn.addEventListener('click', () => closeFlashMessage(flashMessage));
                }
            });

            // Start the fade out when the page loads
            startFadeOut(flashMessage);
        }
    });


    if (headerTitle && navTitle) {
        document.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                headerTitle.style.opacity = '0';
                navTitle.style.visibility = 'visible';
                navTitle.style.opacity = '1';
            } else {
                navTitle.style.opacity = '0';
                navTitle.style.visibility = 'hidden';
                headerTitle.style.opacity = '1';
            }
        });
    } else {
        navTitle.style.visibility = 'visible';
        navTitle.style.opacity = '1';
    }

    if (navTitle) {
        navTitle.addEventListener('click', () => {
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
        const songName = document.querySelector('[name="song"]');

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

    // Attach event listeners for lyrics modal after dynamic content load
    function attachLyricsModalListeners() {
        const lyricsModal = document.querySelector("#lyrics");
        const showLyrics = document.querySelector("#show-lyrics");
        const closeLyrics = document.querySelector("#close-lyrics");
        if (lyricsModal && showLyrics && closeLyrics) {
            showLyrics.addEventListener('click', toggleModal);
            closeLyrics.addEventListener('click', toggleModal);
        }
    }

    // Ensure lyrics modal listeners are attached on initial page load (for static content like index.html)
    attachLyricsModalListeners();

    if (editProfileModal) {
        const showProfileEditor = document.querySelector('#edit-profile-btn');
        const closeProfileEditor = document.querySelector('#close-edit-profile');
        showProfileEditor.addEventListener('click', toggleModal);
        closeProfileEditor.addEventListener('click', toggleModal);
    }

    const validateUsername = () => {
        if (usernameInput && !loginForm) {
            usernameInput.addEventListener('input', () => {
                if (usernameInput.value.length < 4) {
                    usernameInput.setAttribute('aria-invalid', true);
                    usernameHelper.textContent = 'Username must be at least 4 characters long!';
                } else if (!isValidUsername(usernameInput.value)) {
                    usernameInput.setAttribute('aria-invalid', true);
                    usernameHelper.textContent = 'Username can contain only letters, numbers and hyphen (-)';
                } else {
                    usernameInput.setAttribute('aria-invalid', false);
                    usernameHelper.textContent = '';
                }
            });

            usernameInput.addEventListener('blur', () => {
                usernameInput.removeAttribute('aria-invalid');
                usernameHelper.textContent = '';
            });
        }
    }

    const confirmPassword = () => {
        if (passwordInput && passwordConfirmInput) {
            passwordInput.addEventListener('input', () => {
                if (passwordInput.value.length < 16) {
                    passwordInput.setAttribute('aria-invalid', true);
                    passwordHelper.textContent = 'Password must be at least 16 characters long!';
                } else {
                    passwordInput.setAttribute('aria-invalid', false);
                    passwordHelper.textContent = '';
                }
            });

            passwordConfirmInput.addEventListener('input', () => {
                if (passwordConfirmInput.value !== passwordInput.value) {
                    passwordConfirmInput.setAttribute('aria-invalid', 'true');
                    passwordConfirm.textContent = 'Passwords do not match!';
                } else {
                    passwordConfirm.textContent = '';
                    if (!passwordInput.getAttribute('aria-invalid') && passwordInput.value.length >= 16) {
                        passwordInput.type = 'password';
                        togglePasswordContainer.style.opacity = '0';
                        setTimeout(() => {
                            togglePasswordContainer.style.display = 'none';
                        }, 50);
                        passwordConfirmInput.setAttribute('aria-invalid', 'false');
                    }
                }
            });

            passwordInput.addEventListener('blur', () => {
                if (passwordInput.getAttribute('aria-invalid') === 'false') {
                    passwordInput.removeAttribute('aria-invalid');
                    passwordHelper.textContent = '';
                }
            });

            passwordConfirmInput.addEventListener('blur', () => {
                if (passwordConfirmInput.getAttribute('aria-invalid') === 'false') {
                    passwordConfirmInput.removeAttribute('aria-invalid');
                }
            });
        }

        if (loginForm) {
            if (passwordInput.getAttribute('aria-invalid') === 'true') {
                passwordInput.addEventListener("input", () => {
                    if (passwordHelper) {
                        passwordHelper.innerHTML = '<a href="/reset-password">Forgot Password?</a>';
                    }
                    passwordInput.removeAttribute('aria-invalid');
                });
            }
        }
    }


    validateUsername();
    confirmPassword();


    if (togglePasswordContainer) {
        togglePasswordContainer.style.pointerEvents = 'initial';
        togglePasswordContainer.style.opacity = '1';
        const passwordField = document.querySelector("#password, #auth-key");
        togglePassword.addEventListener("click", () => {
            if (passwordField.type === "password") {
                passwordField.type = "text";
                togglePassword.classList.remove("fa-eye");
                togglePassword.classList.add("fa-eye-slash");
            } else {
                passwordField.type = "password";
                togglePassword.classList.remove("fa-eye-slash");
                togglePassword.classList.add("fa-eye");
            }
        });
    }



    if (lastfmLinkModal) {
        const lastfmLinkButton = document.querySelector('.link[data-service="lastfm"]');
        const closeLastfmModal = document.querySelector('#close-lastfm-modal');
        lastfmLinkButton.addEventListener('click', toggleModal);
        closeLastfmModal.addEventListener('click', toggleModal);
    }

    async function fetchActivity() {
        const activityContainer = document.querySelector('.user-activity-container') || document.querySelector('#user-activity');

        if (!activityContainer) {
            return;
        }

        let url = '/api/me?type=html';
        const username = document.getElementById('username').getAttribute('data-username');
        if (username) {
            url += `&username=${encodeURIComponent(username)}`;
        }

        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            activityContainer.removeAttribute('aria-busy');
            const errorData = await response.json();
            const img = '<img src="/static/errors/no.gif" alt="shiroi-suna-no-aquatop" width="404px">'
            activityContainer.innerHTML = `<div class="error-container"><p class="text-in-article">${errorData.error}</p>${img}</div>`;
            throw new Error();
        }

        if (response.ok) {
            const html = await response.text();

            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;

            const newContent = tempDiv.querySelector('#user-activity');
            if (newContent) {
                // Extract relevant data from the current and new activity
                const currentStatusTxt = activityContainer.querySelector('.user-activity-header h4')?.textContent.trim();
                const newStatusTxt = newContent.querySelector('.user-activity-header h4')?.textContent.trim();

                const currentTitle = activityContainer.querySelector('.music-info span.ellipsis')?.textContent.trim();
                const newTitle = newContent.querySelector('.music-info span.ellipsis')?.textContent.trim();

                const currentArtists = activityContainer.querySelector('.music-info:nth-child(3) span.ellipsis')?.textContent.trim();
                const newArtists = newContent.querySelector('.music-info:nth-child(3) span.ellipsis')?.textContent.trim();

                // Compare relevant fields to avoid unnecessary updates
                if (currentStatusTxt !== newStatusTxt) {
                    const currentStatusEl = activityContainer.querySelector('.user-activity-header');
                    if (currentStatusEl) {
                        currentStatusEl.replaceWith(newContent.querySelector('.user-activity-header'));
                    }
                }

                if (currentTitle !== newTitle || currentArtists !== newArtists) {
                    // Add fade-out effect before replacing content
                    activityContainer.style.opacity = '0';
                    setTimeout(() => {
                        activityContainer.replaceWith(newContent);
                        newContent.style.opacity = '0';
                        setTimeout(() => {
                            newContent.style.opacity = '1';
                            attachLyricsModalListeners(); // Attach lyrics modal listeners after DOM update
                        }, 50); // Delay to trigger fade-in
                    }, 300); // Match fade-out duration
                } else {
                    // If not replaced, still try to attach listeners (for initial load)
                    attachLyricsModalListeners();
                }
            }
        }
    }

    // Fetch activity every 10 seconds normally, but retry in 60 seconds if an error occurs
    let fetchInterval = 10000; // Normal interval is 10 seconds

    function startFetchingActivity() {
        fetchActivity()
            .then(() => {
                // Reset interval to normal after a successful fetch
                fetchInterval = 10000;
            })
            .catch(() => {
                // Increase interval to 60 seconds on error
                fetchInterval = 60000;
            })
            .finally(() => {
                // Schedule the next fetch
                setTimeout(startFetchingActivity, fetchInterval);
            });
    }

    // Start the fetching process
    startFetchingActivity();

    if (accountDelBtm) {
        const showDelAccount = document.querySelector('#show-account-del');
        const closeDelAccount = document.querySelector('#close-account-del');
        showDelAccount.addEventListener('click', toggleModal);
        closeDelAccount.addEventListener('click', toggleModal);
    }

    if (editRoleForm || editServicesForm || manageUserAccountForm) {
        let currentlyEditingRow = null; // Track the currently editing row

        document.querySelectorAll(".edit-btn").forEach(button => {
            button.addEventListener("click", (event) => {
                const row = event.target.parentElement.parentElement;

                // If another row is being edited, reset it
                if (currentlyEditingRow && currentlyEditingRow !== row) {
                    resetRow(currentlyEditingRow);
                }

                const inputs = row.querySelectorAll("input[type='text'], input[type='url'], input[type='checkbox']");
                const saveButton = row.querySelector("input[name='edit_service'], input[name='edit_user'], input[name='edit_role'], input[class='save-btn'");
                const editButton = event.target;
                const cancelButton = row.querySelector(".cancel-btn");
                const deleteButton = row.querySelector(".delete-btn");

                // Toggle edit mode
                inputs.forEach(input => { if (input.hasAttribute('readonly')) { input.readOnly = false; } });
                inputs.forEach(input => { if (input.hasAttribute('disabled')) { input.disabled = false; } });

                // Toggle button visibility
                if (saveButton) saveButton.style.display = "inline-block";
                if (cancelButton) cancelButton.style.display = "inline-block";
                if (editButton) editButton.style.display = "none";
                if (deleteButton) deleteButton.style.display = "none";

                // Set focus to the first input field
                const firstInput = row.querySelector("input[type='text'], input[type='url']");
                if (firstInput) {
                    firstInput.focus();
                }

                // Track the currently editing row
                currentlyEditingRow = row;
            });
        });

        document.querySelectorAll(".cancel-btn").forEach(button => {
            button.addEventListener("click", (event) => {
                const row = event.target.parentElement.parentElement;
                resetRow(row);

                // Clear the currently editing row
                currentlyEditingRow = null;
            });
        });

        document.querySelectorAll(".secondary.delete-btn").forEach(button => {
            button.addEventListener("click", (event) => {
                const name = editRoleForm ? "role" : editServicesForm ? "service" : "user";
                const confirmation = confirm(`Are you sure you want to delete this ${name}?`);

                if (confirmation && manageUserAccountForm) {
                    event.preventDefault();
                    const modal = document.getElementById(button.dataset.target);
                    if (!modal) return;
                    modal && (modal.open ? closeModal(modal) : openModal(modal));
                }

                if (!confirmation) {
                    event.preventDefault(); // Prevent form submission if the user cancels
                }
            });
        });

        function resetRow(row) {
            const inputs = row.querySelectorAll("input[type='text'], input[type='url'], input[type='checkbox']");
            const saveButton = row.querySelector("input[name='edit_service'], input[name='edit_user'], input[name='edit_role']");
            const editButton = row.querySelector(".edit-btn");
            const cancelButton = row.querySelector(".cancel-btn");
            const deleteButton = row.querySelector(".delete-btn");

            // Revert inputs to readonly/disabled
            inputs.forEach(input => {
                if (input.type === 'text' || input.type === 'url') { input.readOnly = true; }
                if (input.type === 'checkbox') { input.disabled = true; }
            });

            // Toggle button visibility
            if (saveButton) saveButton.style.display = "none";
            if (cancelButton) cancelButton.style.display = "none";
            if (editButton) editButton.style.display = "inline-block";
            if (deleteButton) deleteButton.style.display = "inline-block";
        }

        const userNotifyOnDelete = document.querySelectorAll("input[name='notify_deletion'");
        userNotifyOnDelete.forEach(notifyDeletion => {
            notifyDeletion.addEventListener('change', function () {
                if (this.checked) {
                    this.nextElementSibling.nextElementSibling.disabled = false;
                } else {
                    this.nextElementSibling.nextElementSibling.value = '';
                    this.nextElementSibling.nextElementSibling.disabled = true;
                }
            });
        });
    }

    // source/credit: https://codepen.io/vardumper/pen/VwdJoyE
    if (tabControl) {
        const nodeList = document.querySelectorAll('nav[role="tab-control"] label');
        const eventListenerCallback = setActiveState.bind(null, nodeList);

        nodeList[0].classList.add('active-tab'); /** add active class to first node  */

        nodeList.forEach((node) => {
            node.addEventListener("click", eventListenerCallback); /** add click event listener to all nodes */
        });

        /** the click handler */
        function setActiveState(nodeList, event) {
            nodeList.forEach((node) => {
                node.classList.remove("active-tab"); /** remove active class from all nodes */
            });
            event.target.classList.add("active-tab"); /* set active class on current node */
        }
    }

    if (addURIBtn) {
        const redirectURIsContainer = document.getElementById('redirectURIs');
        if (redirectURIsContainer && addURIBtn) {
            // Initially disable the add button
            addURIBtn.disabled = true;

            function updateRemoveButtons() {
                const removeBtns = document.querySelectorAll('.remove-redirect_uri');
                if (removeBtns.length > 1) {
                    removeBtns.forEach(btn => {
                        btn.style.opacity = '1';
                        btn.style.pointerEvents = 'auto';
                    });
                } else {
                    removeBtns.forEach(btn => {
                        btn.style.opacity = '0';
                        btn.style.pointerEvents = 'none';
                    });
                }
            }

            function updateAddBtnState() {
                const lastInput = redirectURIsContainer.querySelector('.redirectURI:last-child input');
                const uriDivs = redirectURIsContainer.querySelectorAll('.redirectURI');
                const helper = document.getElementById('redirect-uri-helper-two');
                if (uriDivs.length >= 10) {
                    if (helper) helper.textContent = 'You have reached the maximum of 10 redirect URIs.';
                    addURIBtn.style.display = 'none';
                } else {
                    if (helper) helper.textContent = '';
                    addURIBtn.style.display = '';
                }
                if (lastInput && lastInput.value.length > 8 && uriDivs.length < 10) {
                    addURIBtn.disabled = false;
                } else {
                    addURIBtn.disabled = true;
                }
            }

            function updateInputIndices() {
                const uriDivs = redirectURIsContainer.querySelectorAll('.redirectURI');
                uriDivs.forEach((div, idx) => {
                    const input = div.querySelector('input');
                    if (input) {
                        input.id = `redirect_uris-${idx}-redirect_uri`;
                        input.name = `redirect_uris-${idx}-redirect_uri`;
                    }
                });
            }

            // Attach input listeners to all current inputs
            function attachInputListeners() {
                const uriDivs = redirectURIsContainer.querySelectorAll('.redirectURI');
                uriDivs.forEach((div, idx) => {
                    const input = div.querySelector('input');
                    if (input) {
                        input.removeEventListener('input', updateAddBtnState);
                        input.addEventListener('input', updateAddBtnState);
                    }
                });
            }

            // Initial setup
            updateRemoveButtons();
            updateInputIndices();
            attachInputListeners();
            updateAddBtnState();

            addURIBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const uriDivs = redirectURIsContainer.querySelectorAll('.redirectURI');
                if (uriDivs.length >= 10) return; // Prevent adding more than 10
                const lastURI = redirectURIsContainer.querySelector('.redirectURI:last-child');
                const newURI = lastURI.cloneNode(true);
                // Clear the input value
                const input = newURI.querySelector('input');
                if (input) input.value = '';
                // Remove any error messages
                const error = newURI.querySelector('small');
                if (error) error.innerText = '';
                redirectURIsContainer.appendChild(newURI);
                updateInputIndices();
                attachInputListeners();
                updateRemoveButtons();
                updateAddBtnState();
                // Focus new input
                const lastInput = redirectURIsContainer.querySelector('.redirectURI:last-child input');
                if (lastInput) lastInput.focus();
            });

            // Remove URI
            redirectURIsContainer.addEventListener('click', (e) => {
                if (e.target.closest('.remove-redirect_uri')) {
                    const allURIs = redirectURIsContainer.querySelectorAll('.redirectURI');
                    if (allURIs.length > 1) {
                        e.target.closest('.redirectURI').remove();
                        updateInputIndices();
                        attachInputListeners();
                        updateRemoveButtons();
                        updateAddBtnState();
                    }
                }
            });
        }
    }
});
