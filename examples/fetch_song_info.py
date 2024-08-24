import requests


def fetch_song_info(artist_name, song_name):
    url = f"https://yutify.onrender.com/api/{artist_name}:{song_name}"

    response = requests.get(url)
    data = response.json()

    # Do anything with `data`, here print in the terminal
    print(data)


# Call the function with arguments
fetch_song_info("Artist Name", "song Name")
