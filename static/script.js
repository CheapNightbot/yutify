document.addEventListener('DOMContentLoaded', function() {
    let form = document.querySelector('form');

    form.addEventListener('submit', function() {
        document.body.style.cursor = 'wait';
        document.querySelector('#search').style.cursor = 'wait';
    });
});
