document.addEventListener('DOMContentLoaded', function() {
    let form = document.querySelector('form');

    form.addEventListener('submit', function() {
        document.body.style.cursor = 'wait';
        document.querySelector('#search').style.cursor = 'wait';
    });

    const backgrouondImage = document.createElement('div');
    const backgrouondOverlay = document.createElement('div');
    backgrouondImage.classList.add('background-image');
    backgrouondOverlay.classList.add('background-overlay');
    document.documentElement.prepend(backgrouondOverlay)
    document.documentElement.appendChild(backgrouondImage);
});
