document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const showLyrics = document.querySelector("#show-lyrics");
    const closeLyrics = document.querySelector("#close-lyrics");
    const lyricsModal = document.querySelector("#lyrics");

    form.addEventListener('submit', function () {
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
});
