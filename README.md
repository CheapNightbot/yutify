<div align=center>

  ![Banner](https://github.com/user-attachments/assets/6423bf5a-29d9-42b4-90a5-8851d701def7)

  [![GitHub License](https://img.shields.io/github/license/CheapNightbot/yutify?style=for-the-badge&color=%23dfebfc)](LICENSE)
  [![Website Status](https://img.shields.io/website?url=https%3A%2F%2Fyutify.onrender.com%2F&style=for-the-badge&color=%23dfebfc)](https://yutify.onrender.com/)
  [![Read Docs](https://img.shields.io/badge/READ-DOCS-blue?style=for-the-badge&color=%23dfebfc)](https://yutify.onrender.com/docs)

</div>

# yutify <img src="static/favicon.svg" width="50px">

<details>
  <summary>✨ TABLE OF CONTENTS</summary>

- [yutify <img src="static/favicon.svg" width="20px">](#yutify) ← you're here..
  - [Features ™️](#features-️)
  - [Available Music Platforms](#available-music-platforms-)
- [Run Locally 🧑‍💻](#run-locally-)
  - [Additional Notes On Running yutify 📝](#additional-notes-on-running-yutify-)
- [Contributing 🤝](#contributing-)
  - [Users](#users)
  - [Developers](#developers)
- [Acknowledgement // End Note 🙃](#acknowledgement--end-note-)

</details>

<details>
  <summary>✨ SCREENSHOTS</summary>

  <span align="center">

  |                                           OwO                                             |
  | ----------------------------------------------------------------------------------------- |
  | ![image](https://github.com/user-attachments/assets/0f8c5bf8-e081-4679-b1fb-3cd12d6096ed) |
  | ![image](https://github.com/user-attachments/assets/6d08624b-37cc-4bac-987a-dea34bb7f541) |
  | ![image](https://github.com/user-attachments/assets/223d9fb6-6a86-4edb-8934-d2a038b257a3) |

  </span>

</details>

**yutifiy** is a simple RESTful API for retrieving music info for various streaming platforms. Using the artist name and song name, you can get various information about the song including the streaming link(s) for various music streaming platforms. To prevent the abuse of the API, there is a ratelimit of 30 requests per minute for every user.

Right now, it only retrieves streaming links for [these music platforms](#available-music-platforms-). If you would like me to add any other streaming platforms or more metadata about the song(s), feel free to open an issue. You can visit the website to playaround [here](https://yutify.onrender.com/) or maybe check simple [examples](/examples) on how get started and make sure to read [docs](https://yutify.onrender.com/docs).

### Features ™️

- Retrieve various information about music OwO ~!
  - Some of the noticable information that can be retrieved:
  - [x] Album Art
  - [x] Album Type
  - [x] Genre
  - [x] Lyrics
  - [x] Release Date
  - [x] Many More ™ ヾ(⌐■_■)ノ♪
- Get streaming link for [various streaming platforms](#available-music-platforms-). ♪(´▽｀)
- Request for information only for a particular streaming platform. Read the [docs](https://yutify.onrender.com/docs) for more info.
- Use API endpoint to search for music in code or play around directly on [website](https://yutify.onrender.com/). ヾ(⌐■_■)ノ♪
- It's FREE. \_(:з)∠)\_

### TODO

- Unified responses!
    - Right now, the response for individual platforms and default response etc., there are a lot of differences in data. Like, there is no guarantee that a key will available or not.
    - So, me will make sure to standardize the responses. No matter what, all the responses will have same keys, although the data might be `null` (cause of music platforms, not me !!).

### Available Music Platforms 📻

> Alphabetically sorted

- [x] [Apple Music](https://music.apple.com/)
- [x] [Deezer](https://www.deezer.com/)
- [x] [Spotify](https://spotify.com/)
- [x] [YouTube Music](https://music.youtube.com/)

# Run Locally 🧑‍💻

Run yutify locally in only three steps. Alright, ready? Go:

1. Clone the repository:

```bash
git clone https://github.com/CheapNightbot/yutify.git
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python api.py
```

> [!IMPORTANT]
> Visit locahost at port 8000: http://localhost:8000/

## Additional Notes On Running yutify 📝

Okay, doing above *three* steps didn't work, right >.< ? Because there are few other steps required to be considered while running yutify:
> By the way, I assume you already had Python installed. You have, right?

<br>

→ For retrieving information from Spotify, it uses official Spotify API endpoint, which requires authentication. So, you will have to signup for **Spotify for Developers** account (it's free) and follow the steps below:

- Go to your dashboard at https://developer.spotify.com/
- Create a new app and fill `localhost/callback` in "Redirect URIs" field.
- Select "Web API" for "Which API/SDKs are you planning to use?".
- Next, create `.env` file inside [yutify/](yutify/) directory.
  - Create a variable inside this `.env` file called `CLIENT_ID` and paste the Client ID from Spotify Dashboard after it (after `=` sign. no space).
  - Then, create new variable `CLIENT_SECRET` and paste Client secret from Spotify Dashboard. You may have to click on "View client secret".

→ And regarding ratelimit:

- For ratelimiting, it uses **Flask-Limiter** and for storage, **redis**.
- So, first, you will have to have a redis instance up and running.
  - You can, at this point, just copy and paste the URL where the redis instance is running into the `.env` file in the project root directory (check the `.env_example` file!).
- Run `python api.py` command, and everything will work as expected.
- If no `.env` file exists or it fails to get `"REDIS_URI"`, it will use the memory for ratelimiting instead of redis. It is good for running in development environment, do not use it for production.
- If you do not want to use ratelimiting at all, you can change the global `RATELIMIT` variable in `api.py` to `False`:
  - `RATELIMIT = False`
  - You can run `python api.py` again, and everything should work as expected.

# Contributing 🤝

## Users

If you don't know programming, you can still contribute to this project by opening an issue for suggestions, improvements or really for an issue.

## Developers

- Just fork the repository.
- Create a new branch for your changes and make changes in that (separate) branch.
- Open a pull request.

# Acknowledgement // End Note 🙃

- Powered by [Render](https://render.com/register). 🚀
- Logos/Icons provided by [SVG REPO](https://www.svgrepo.com/). 🧑‍🎨
- Using [Spotify Web API](https://developer.spotify.com/documentation/web-api). 🛠️
- Using [Deezer API](https://developers.deezer.com/api). 🛠️
- Thanks to [sigma67](https://github.com/sigma67) for [ytmusicapi](https://github.com/sigma67/ytmusicapi). 🫂
- Thanks to [OhaJoq](https://github.com/Joqnix) for motivation behind this project. ✨
