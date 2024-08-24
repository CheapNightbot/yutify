// Function to fetch data from the API
async function fetchSongInfo(artist_name, song_name) {
    const url = `https://yutify.onrender.com/api/${artist_name}:${song_name}`;

    const response = await fetch(url);
    const data = await response.json();

    // Do anything with `data`, here log to console
    console.log(data);
}

// Call the function with arguments
fetchSongInfo("Artist Name", "Song Name");
