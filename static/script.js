document.addEventListener('DOMContentLoaded', function() {
    let form = document.querySelector('form');

    form.addEventListener('submit', function() {
        let searchButton = document.querySelector('#search');
        searchButton.innerHTML = '<div class="loader"></div>'
    });

    const backgrouondImage = document.createElement('div');
    const backgrouondOverlay = document.createElement('div');
    backgrouondImage.classList.add('background-image');
    backgrouondOverlay.classList.add('background-overlay');
    document.documentElement.prepend(backgrouondOverlay)
    document.documentElement.appendChild(backgrouondImage);
});
