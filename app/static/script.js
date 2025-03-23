document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.querySelector('search-form');
    const showLyrics = document.querySelector("#show-lyrics");
    const closeLyrics = document.querySelector("#close-lyrics");
    const lyricsModal = document.querySelector("#lyrics");
    const themeBtn = document.querySelector('#themeBtn');
    const themeBtnIcon = document.querySelector('#theme-btn');
    const brandHeading = document.querySelector('#brand');
    const brandHeaderText = document.querySelector('.brand');


    themeBtn.addEventListener("click", () => {
        const currentIcon = themeBtnIcon.classList[1];
        themeBtnIcon.classList.remove(currentIcon);
        themeBtnIcon.classList.add('fa-sun' === currentIcon ? 'fa-moon' : 'fa-sun');
        document.documentElement.setAttribute('data-theme', document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light')
    });


    if (brandHeading) {
        document.addEventListener('scroll', () => {
            if (window.scrollY > 111) {
                brandHeading.style.opacity = '0';
                brandHeaderText.style.visibility = 'visible';
                brandHeaderText.style.opacity = '1';
            } else {
                brandHeaderText.style.opacity = '0';
                brandHeaderText.style.visibility = 'hidden';
                brandHeading.style.opacity = '1';
            }
        });
    } else {
        brandHeaderText.style.visibility = 'visible';
        brandHeaderText.style.opacity = '1';
    }

    if (searchForm) {

        searchForm.addEventListener('submit', function () {
            let searchButton = document.querySelector('#search');
            searchButton.setAttribute('aria-busy', 'true');
            searchButton.innerHTML = 'Searching...'
        });


        showLyrics.addEventListener("click", () => {
            document.documentElement.classList.add("modal-is-open", "modal-is-opening");
            lyricsModal.setAttribute("open", "");
        });


        closeLyrics.addEventListener("click", () => {
            document.documentElement.classList.remove("modal-is-open", "modal-is-closing");
            lyricsModal.removeAttribute("open");
        });
    }
});
