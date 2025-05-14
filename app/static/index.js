const copyEndpointUrl = (e) => {
    e.preventDefault();
    const endpointUrl = document.querySelector(".endpoint")?.href;
    navigator.clipboard.writeText(endpointUrl).then(() => {
        alert('URL Copied to clipboard!');
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const endpoint = '/api/search';
    const endpointUrl = document.querySelector('.endpoint');
    const endpointInput = document.querySelector('.endpoint-url');
    const inputArtist = document.querySelector("#artist");
    const inputSong = document.querySelector("#song");

    let artist = inputArtist.value || '<artist>';
    let song = inputSong.value || '<song>';
    let computedEndpointUrl = `${endpoint}/${artist}:${song}`

    endpointUrl.href = computedEndpointUrl;
    endpointInput.value = computedEndpointUrl;
    endpointUrl.addEventListener('click', copyEndpointUrl);

    inputArtist.addEventListener('input', () => {
        artist = inputArtist.value || '<artist>';
        computedEndpointUrl = `${endpoint}/${artist}:${song}`
        endpointUrl.href = computedEndpointUrl;
        endpointInput.value = computedEndpointUrl;
    });

    inputSong.addEventListener('input', () => {
        song = inputSong.value || '<song>';
        computedEndpointUrl = `${endpoint}/${artist}:${song}`
        endpointUrl.href = computedEndpointUrl;
        endpointInput.value = computedEndpointUrl;
    });
});
