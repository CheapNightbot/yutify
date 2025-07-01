const copyEndpointUrl = (e) => {
    e.preventDefault();
    const endpointUrl = document.querySelector(".endpoint")?.href;
    navigator.clipboard.writeText(endpointUrl).then(() => {
        showFlashMessage('URL Copied to clipboard!', 'info');
    }).catch(() => {
        showFlashMessage('Failed to copy!', 'error');
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const endpoint = '/api/search';
    const endpointUrl = document.querySelector('.endpoint');
    const endpointInput = document.querySelector('.endpoint-url');
    const inputArtist = document.querySelector("#artist");
    const inputSong = document.querySelector("#song");

    let artist = DOMPurify.sanitize(inputArtist.value) || '<artist>';
    let song = DOMPurify.sanitize(inputSong.value) || '<song>';
    let computedEndpointUrl = `${endpoint}/${artist}:${song}`

    endpointUrl.href = computedEndpointUrl;
    endpointInput.value = computedEndpointUrl;
    endpointUrl.addEventListener('click', copyEndpointUrl);

    inputArtist.addEventListener('input', () => {
        artist = DOMPurify.sanitize(inputArtist.value) || '<artist>';
        computedEndpointUrl = `${endpoint}/${artist}:${song}`
        endpointUrl.href = computedEndpointUrl;
        endpointInput.value = computedEndpointUrl;
    });

    inputSong.addEventListener('input', () => {
        song = DOMPurify.sanitize(inputSong.value) || '<song>';
        computedEndpointUrl = `${endpoint}/${artist}:${song}`
        endpointUrl.href = computedEndpointUrl;
        endpointInput.value = computedEndpointUrl;
    });
});
