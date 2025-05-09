import { createApp, ref, computed } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
const inputArtist = document.querySelector("#artist");
const inputSong = document.querySelector("#song");

const copyEndpointUrl = (e) => {
    e.preventDefault();
    const endpointUrl = document.querySelector(".endpoint")?.href;
    navigator.clipboard.writeText(endpointUrl).then(() => {
        alert('URL Copied to clipboard!');
    });
}

createApp({
    setup() {
        const artist = ref(inputArtist.value || '');
        const song = ref(inputSong.value || '');
        const endpoint = '/api/search';
        const computedEndpoint = computed(() => {
            return `${endpoint}/${artist.value || '<artist>'}:${song.value || '<song>'}`;
        });

        return {
            artist,
            song,
            computedEndpoint,
            copyEndpointUrl
        }
    },
    delimiters: ['${', '}']
}).mount('#app')
