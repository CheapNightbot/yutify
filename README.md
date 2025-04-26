> ⚠️ until the feature is done (along with some security considerations) in the second branch, the yutify website will be down. thank you for your understanding!

<div align=center>

  ![Banner](https://github.com/user-attachments/assets/ce43c4c7-5716-472d-b834-588f6559048d)


  [![GitHub License](https://img.shields.io/github/license/CheapNightbot/yutify?style=for-the-badge&color=%236f6cc7)](LICENSE)
  [![Website Status](https://img.shields.io/website?url=https%3A%2F%2Fyutify.onrender.com%2F&style=for-the-badge&color=%236f6cc7)](https://yutify.onrender.com/)
  [![Read Docs](https://img.shields.io/badge/READ-DOCS-blue?style=for-the-badge&color=%236f6cc7)](https://yutify.onrender.com/docs)

</div>

# yutify <img src="app/static/favicon.svg" width="40px">

<details>
  <summary>✨ TABLE OF CONTENTS</summary>

- [yutify <img src="app/static/favicon.svg" width="20px">](#yutify) ← you're here..
  - [Features ™️](#features-️)
  - [Available Music Platforms 📻](#available-music-platforms-)
  - [Running yutify 🧑‍💻](#running-yutify-)
    - [Environment Variables](#environment-variables)
  - [Contributing 🤝](#contributing-)
  - [Acknowledgement // End Note 🙃](#acknowledgement--end-note-)

</details>

<details>
  <summary>✨ SCREENSHOTS</summary>

  <span align="center">

  |                                           OwO                                             |
  | ----------------------------------------------------------------------------------------- |
  | ![image](https://github.com/user-attachments/assets/5b976d5e-edf4-4701-8591-95ac54cafdf4) |
  | ![image](https://github.com/user-attachments/assets/ca3cd475-b52d-4011-8e96-39ca5280ff1a) |
  | ![image](https://github.com/user-attachments/assets/d536a7b0-642a-44ff-989b-87d4a1e23972) |
  | ![image](https://github.com/user-attachments/assets/2c568977-ae61-4cea-b547-6c863c1aac0f) |
  | ![image](https://github.com/user-attachments/assets/9eab7b03-dcd8-48ea-a53b-2feee19b83fb) |

  </span>

</details>

**yutify** is a simple RESTful API for retrieving music info from various streaming platforms. Using the artist name and song name, you can get various information about the song, including streaming link(s) for multiple music platforms. To prevent abuse, the API enforces a rate limit of 20 requests per minute per user.

Right now, it only retrieves streaming links for [these music platforms](#available-music-platforms-). If you'd like to suggest additional platforms or metadata, feel free to open an issue. You can visit the website to explore [here](https://yutify.onrender.com/) and make sure to read the [docs](https://yutify.onrender.com/docs) as well.

### Features ™️

- Get streaming links for [various streaming platforms](#available-music-platforms-). ♪(´▽｀)
- Retrieve detailed music information OwO ~ artists, album, lyrics, release date, etc.!
- Retrieve music metadata for your currently playing tracks from Last.fm and/or Spotify.
- Request information for a specific streaming platform. Read the [docs](https://yutify.onrender.com/docs) for more info.
- Use API endpoints to search for music programmatically or explore directly on the [website](https://yutify.onrender.com/). ヾ(⌐■_■)ノ♪
- Account sign-up for personalized features like currently playing tracks.
- It's FREE. \_(:з)∠)\_ (but you can always support me on [ko-fi](https://ko-fi.com/cheapnightbot))

### Available Music Platforms 📻

> Alphabetically sorted

- [x] [Apple Music](https://music.apple.com/)
- [x] [Deezer](https://deezer.com/)
- [x] [KKBox](https://kkbox.com/)
- [x] [Last.fm](https://last.fm/)
- [x] [Spotify](https://spotify.com/)
- [x] [YouTube Music](https://music.youtube.com/)

# Running yutify 🧑‍💻

**1. Clone the repository**:

```bash
git clone https://github.com/CheapNightbot/yutify.git
```

**2. Install dependencies**:

```bash
pip install -r requirements.txt
```

Before running yutify, you need to take care of a few things:

## Environment Variables

For certain configurations, it relies on environment variables that must be set before running yutify. Here's a brief overview:

> [!TIP]
> There is a `.env_example` file in the root directory of the project. Rename it to `.env` and replace placeholder values with actual values when running the project locally.
> When using a hosting provider, set the respective values in the environment variable settings provided by them.

### Required: These environment variables are mandatory!

- `SECRET_KEY`: Used by Flask for session management and security. To generate a secure key, you may run either of the following commands:

  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
  OR
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe())"
  ```

- `ENCRYPTION_KEY`: A URL-safe base64-encoded 32-byte key used for encrypting user emails at rest (in the database). To generate an encryption key, run the following command after installing dependencies:

  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

  - **Important**: Once used to encrypt emails, changing or losing this key will prevent decryption of previously saved emails. Handle with care!
- `DATABASE_URL`: SQL Database URL. If not set, a file-based SQLite database (`app.db`) will be used in the root directory.

### Optional: These environment variables are optional!

- `PORT`: The port number on which the application will serve HTTP requests. Defaults to `5000`.
- For retrieving music information from Spotify, KKBox, and Last.fm, client IDs, client secrets, or API keys are required. Thankfully, [yutipy](https://pypi.org/project/yutipy/) provides a command-line utility to obtain these values. Run `yutipy-config` in your terminal after installing dependencies. The wizard will guide you through obtaining and setting up API keys for supported services like KKBOX, Last.fm, and Spotify. These values are automatically saved in the `.env` file.
  - `KKBOX_CLIENT_ID`, `KKBOX_CLIENT_SECRET`, `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI`, `LASTFM_API_KEY`
  - Without these variables, interaction with these platforms will be unavailable.
- Variables for sending emails (used for error logs and password resets):
  - `MAIL_SERVER`: The mail server address (e.g., `smtp.gmail.com`).
  - `MAIL_PORT`: The port to use for the mail server (e.g., `587` for TLS).
  - `MAIL_USE_TLS`: Whether to use TLS for secure email communication. Set this variable to `1` to enable TLS or omit it to disable TLS.
  - `MAIL_USERNAME`: The email address to use for sending emails.
  - `MAIL_PASSWORD`: The password or app-specific password for the email account.
  - `ADMIN_EMAIL`: The administrator's email address to receive error logs or notifications.
- `RATELIMIT`: Enables rate-limiting on all API routes (`/api/*`). For valid values, refer to the [Flask-Limiter Docs](https://flask-limiter.readthedocs.io/en/stable/configuration.html#rate-limit-string-notation).
- `REDIS_URI`: URI for Redis (used for rate-limiting and caching). If not set:
  - With `FLASK_DEBUG=1` (development mode), in-memory caching will be used.
  - Without `FLASK_DEBUG` (production mode), caching will be disabled.

**3. Run the application**:

```bash
flask run
```

> [!IMPORTANT]
> Visit the application locally at: [http://localhost:5000](http://localhost:5000) or [http://127.0.0.1:5000](http://127.0.0.1:5000)

# Contributing 🤝

We welcome contributions from everyone! Here's how you can help:

- **Open Issues**: If you have suggestions, improvements, or bug reports, feel free to open an issue.
- **Fork and Develop**: Fork the repository, create a new branch for your changes, and make modifications in that branch.
- **Submit Pull Requests**: Once your changes are ready, open a pull request for review.

Whether you're a user or a developer, your contributions are valuable and appreciated!

# Acknowledgement // End Note 🙃

- Uses [yutipy](https://pypi.org/project/yutipy/) 🎶
- Uses [Pico CSS](https://picocss.com/) 🎨
- Powered by [Render](https://render.com/register) 🚀
- Thanks to [OhaJoq](https://github.com/Joqnix) for inspiring this project ✨
- Thanks to everyone who starred the repo—it means a lot! 🫂
