<div align=center>

  ![Banner](https://github.com/user-attachments/assets/d024bf6d-7a58-4f61-8a29-681e076995cf)
  
  [![GitHub License](https://img.shields.io/github/license/CheapNightbot/yutify?style=for-the-badge&color=%23dfebfc)](LICENSE)
  [![Website Status](https://img.shields.io/website?url=https%3A%2F%2Fyutify.onrender.com%2F&style=for-the-badge&color=%23dfebfc)](https://yutify.onrender.com/)
  [![Read Docs](https://img.shields.io/badge/READ-DOCS-blue?style=for-the-badge&color=%23dfebfc)](https://yutify.onrender.com/docs)

</div>

# yutify <img src="static/favicon.svg" width="50px">

<details>
  <summary>SCREENSHOTS</summary>
  
  ![image](https://github.com/user-attachments/assets/b8d09c15-1ed5-48d2-b03d-4cb54bffa98a)

</details>

**yutifiy** is a simple RESTful API (wrapper) for retrieving music info for various steaming platforms written in Flask (Python). Using the artist name and song name, you can get various information about the song including the streaming link(s) for various music streaming platforms. To prevent the abuse of the API, there is a ratelimit of 60 requests per minute for every user.

Right now, it only retrieves streaming links for Spotify & YouTube Music. If you would like me to add any other streaming platforms or more metadata about the song(s), feel free to open an issue. You can visit the website to playaround [here](https://yutify.onrender.com/) or maybe check simple [examples](/examples) on how get started and make sure to read [docs](https://yutify.onrender.com/docs).

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

→ For retrieving information from YouTube Music, it uses [ytmusicapi](https://github.com/sigma67/ytmusicapi) and OAuth for authenticated requests. Please check the [docs](https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html) on how to setup OAuth. You just need to authenticate and save the "oauth.json" in the root directory of the project. The authentication is not required, so you can change [this line](https://github.com/CheapNightbot/yutify/blob/b449e4352b34f6efea5c299fbb258efb0ab347f3/yutify/musicyt.py#L37) inside [yutify/musicyt.py](/yutify/musicyt.py) slightly to not use OAuth:

```python
ytmusic = YTMusic()
```

→ And regarding ratelimit:

- For ratelimiting, it uses **Flask-Limiter** and for storage, **redis**.
- So, first, you will have to have a redis instance up and running.
- You can, at this point, just copy and paste the URL where the redis instance is running into the variable `redis_uri` at [line `16`](https://github.com/CheapNightbot/yutify/blob/b449e4352b34f6efea5c299fbb258efb0ab347f3/api.py#L16) inside `api.py` and run yutify again with `python api.py` and NOW, it should work.
- OR, better, create a file `.env` in the root folder of project and create a variable `REDIS_URI` inside it and paste the redis instace url after it (after `=` sign!) and without changing any other file like before, run `python api.py` command, and everything will work as expected.
- Alternatively (optional, only for testing purposes), you can change the Flask-Limiter's config to not use redis at all. Change the [`storage_uri=redis_uri`](https://github.com/CheapNightbot/yutify/blob/b449e4352b34f6efea5c299fbb258efb0ab347f3/api.py#L33) to `storage_uri="memory:///"` to use the memory (RAM!) instead and run `python api.py` again. Do not use it for production.

<details>
  <summary>If you do not want to use ratelimiting at all, you have to change (or really remove) few lines of code inside `api.py`:</summary>
<br>

- [Remove imports](https://github.com/CheapNightbot/yutify/blob/b449e4352b34f6efea5c299fbb258efb0ab347f3/api.py#L8-L9):

```python
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address
```

- [Remove Flask-Limiter config](https://github.com/CheapNightbot/yutify/blob/b449e4352b34f6efea5c299fbb258efb0ab347f3/api.py#L30-L36):

```python
redis_uri = os.environ["REDIS_URI"]

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=redis_uri,
    strategy="fixed-window-elastic-expiry",
    on_breach=default_error_responder,
)
```

- [Remove the ratelimit decorator from the endpoint](https://github.com/CheapNightbot/yutify/blob/b449e4352b34f6efea5c299fbb258efb0ab347f3/api.py#L40):

```python
@limiter.limit("60 per minute")
```

- Finally, [remove the ratelimit error handling function](https://github.com/CheapNightbot/yutify/blob/b449e4352b34f6efea5c299fbb258efb0ab347f3/api.py#L24-L27):

```python
def default_error_responder(request_limit: RequestLimit):
    limit = str(request_limit.limit)
    limit = re.sub(r"(\d+)\s+per", r"\1 request(s) per", limit)
    return make_response(jsonify(error=f"ratelimit exceeded {limit}"), 429)
```

You can run `python api.py` again, and everything should work as expected.

</details>

# Contributing 🤝

## Users

If you don't know programming, you can still contribute to this project by opening an issue for suggestions, improvements or really for an issue.

## Developers

- Just fork the repository.
- Create a new branch for your changes and make changes in that (separate) branch.
- Open a pull request.

# Acknowledgement // End Note

- Powered by [Render](https://render.com/register). 🚀
- Logos/Icons provided by [SVG REPO](https://www.svgrepo.com/). 🧑‍🎨
- Using [Spotify Web API](https://developer.spotify.com/documentation/web-api). 🛠️
- Thanks to [sigma67](https://github.com/sigma67) for [ytmusicapi](https://github.com/sigma67/ytmusicapi). 🫂
- Thanks to [OhaJoq](https://github.com/Joqnix) for motivation behind this project. ✨
