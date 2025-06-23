<div align=center>

![Banner](https://github.com/user-attachments/assets/ce43c4c7-5716-472d-b834-588f6559048d)

[![GitHub License](https://img.shields.io/github/license/CheapNightbot/yutify?style=for-the-badge&color=%236f6cc7)](LICENSE)
[![Website Status](https://img.shields.io/website?url=https%3A%2F%2Fyutify.cheapnightbot.me%2F&style=for-the-badge&color=%236f6cc7)](https://yutify.cheapnightbot.me/)
[![Read Docs](https://img.shields.io/badge/READ-DOCS-blue?style=for-the-badge&color=%236f6cc7)](https://yutify.onrender.com/docs)

</div>

# yutify <img src="app/static/favicon.svg" width="40px">

<details>
  <summary>✨ TABLE OF CONTENTS</summary>

- [yutify <img src="app/static/favicon.svg" width="20px">](#yutify) ← you're here..
  - [Features ™️](#features-️)
  - [Available Music Platforms 📻](#available-music-platforms-)
  - [Running yutify 🧑‍💻](#running-yutify-)
    - [Environment Variables 🔐](#environment-variables)
  - [Contributing 🤝](#contributing-)
  - [Disclaimer ⚠️](#disclaimer-️)
  - [Acknowledgement // End Note 🙃](#acknowledgement--end-note-)

</details>

<details>
  <summary>✨ SCREENSHOTS</summary>

  <span align="center">

| OwO                                                                                                              |
| ---------------------------------------------------------------------------------------------------------------- |
| ![home page](https://github.com/user-attachments/assets/d01e69f2-f8cb-4290-8190-cf8542086b6f)                    |
| ![home page with seach results](https://github.com/user-attachments/assets/efc0a37d-d58c-4a99-830d-448e1b6fdfdd) |
| ![api search response](https://github.com/user-attachments/assets/d536a7b0-642a-44ff-989b-87d4a1e23972)          |
| ![user profile page](https://github.com/user-attachments/assets/87b7badf-b281-451c-bc9c-31244e459659)            |
| ![user settings page](https://github.com/user-attachments/assets/7aae2377-bc29-4f93-b954-5359daad1219)           |

  </span>

</details>

**yutify** is a simple RESTful API for retrieving music info from various streaming platforms. Using the artist name and song name, you can get various information about the song, including streaming link(s) for multiple music platforms. To prevent abuse, the API enforces a rate limit of 20 requests per minute per user.

Right now, it only retrieves streaming links for [these music platforms](#available-music-platforms-). If you'd like to suggest additional platforms or metadata, feel free to open an issue. You can visit the website to explore [here](https://yutify.onrender.com/) and make sure to read the [docs](https://yutify.onrender.com/docs) as well.

### Features ™️

- Get streaming links for [various streaming platforms](#available-music-platforms-). ♪(´▽ ｀)
- Retrieve detailed music information OwO ~ artists, album, lyrics, release date, etc.!
- Retrieve music metadata for your currently playing tracks from Last.fm and/or Spotify.
- Request information for a specific streaming platform. Read the [docs](https://yutify.onrender.com/docs) for more info.
- Use API endpoints to search for music programmatically or explore directly on the [website](https://yutify.onrender.com/). ヾ(⌐■_■)ノ ♪
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

## Environment Variables 🔐

For certain configurations, it relies on environment variables that must be set before running yutify. Here's a brief overview:

> [!TIP]
> There is a `.env_example` file in the root directory of the project. Rename it to `.env` and replace placeholder values with actual values when running the project locally.
> When using a hosting provider, set the respective values in the environment variable settings provided by them.

### Required: These environment variables are mandatory!

- `SECRET_KEY`: Used by Flask for session management and security. To generate a secure key, you may run the following command:

  ```bash
  python -c "import secrets; print(secrets.token_hex())"
  ```

- `ENCRYPTION_KEY`: A URL-safe base64-encoded 32-byte key used for encrypting access token information (for the services that require authorization like Spotify & KKBox for searching music) and to encrypt the (2FA) recovery codes at rest (i.e. in the database). To generate an encryption key, run the following command after installing dependencies:

  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

  - **Important**: Once used to encrypt, changing or losing this key will prevent decryption of previously encrypted data. Handle with care!

- `SECURITY_PASSWORD_SALT`: Specifies the HMAC salt. This is used for double hashing the password. A good salt can be generated using the following command:

  ```bash
  python -c "import secrets; print(secrets.SystemRandom().getrandbits(128))"
  ```

- `SECURITY_TOTP_SECRETS`: Secret used to encrypt the totp_password both into DB and into the session cookie. You should run the following command to generate one after installing dependencies:

  ```bash
  python  -c "from passlib import totp; print(totp.generate_secret());"
  ```

### Optional: These environment variables are optional!

- `SERVICE`: The service / application name. Default to `"yutify"`. You may set it to anything you want. It will be used / shown in various places like, home/index page, meta tags, email, etc.
- `SERVICE_EMAIL`: An email address which will be used in privacy policy and terms of service pages at the bottom (after obfuscating).
- `HOST_URL`: The URL where the application itself is currently running. It will be used in meta tags and just used for sending logging emails (error and above) to the admin email. The default is `localhost`, so the email "from" field will look like this: `From: <no-reply@localhost>`
- `PORT`: The port number on which the application will serve HTTP requests. Defaults to `5000`.
- `LOG_TO_STDOUT`: Whether to use file based logging or log to the console. Set this variable to `1` to enable console logging and `0` or omit it to use file based logging.
- `DATABASE_URL`: SQL Database URL. If not set, a file-based SQLite database (`app.db`) will be used in the root directory.
- `YUTIFY_MAIL_ERROR_LOGS`: If set to `1`, logs for error and above level will be sent to the email set in the `ADMIN_EMAIL` variable. To disable sending logs to email, set it to `0` or simply omit it.
- `YUTIFY_ACCOUNT_DELETE_EMAIL`: Whether to send account deletion confirmation email to the user when they decide to delete their account. Set this to `0` to disable it. Default to `1` (will send email).
- `SECURITY_REGISTERABLE`: Whether to allow user registration / sign up or not. Set this variable to `1` to enable user sign up and `0` or omit it to disable user sign up.
- `SECURITY_CONFIRMABLE`: Whether users are required to confirm their email address when registering a new account. If set to `1` (default), a confirmation email will sent to the user's email and they can't login without confirming their account. Set it to `0` to disable it.
- `RETURN_GENERIC_RESPONSES`: Whether to return generic responses for auth endpoints. Set it to `0` to disable it. Default to enabled (i.e. `1`).
- `CHECK_EMAIL_DELIVERABILITY`: When user signup, check if email address exists (or is fake) and whether emails can be sent to that address. Set it to `1` to enable it or `0` to disable it. By default it is enabled.
- For retrieving music information from Spotify, KKBox, and Last.fm, client IDs, client secrets, or API keys are required. Thankfully, [yutipy](https://pypi.org/project/yutipy/) provides a command-line utility to obtain these values. Run `yutipy-config` in your terminal after installing dependencies. The wizard will guide you through obtaining and setting up API keys for supported services like KKBOX, Last.fm, and Spotify. These values are automatically saved in the `.env` file.
  - `KKBOX_CLIENT_ID`, `KKBOX_CLIENT_SECRET`, `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI`, `LASTFM_API_KEY`
  - Without these variables, interaction with these platforms will be unavailable.
- Variables for sending emails (used for error logs and password resets):
  - `MAIL_SERVER`: The mail server address (e.g., `smtp.gmail.com`).
  - `MAIL_PORT`: The port to use for the mail server (e.g., `587` for TLS).
  - `MAIL_USE_TLS`: Whether to use TLS for secure email communication. Set this variable to `1` to enable TLS and `0` or omit it to disable TLS.
  - `MAIL_USERNAME`: The email address to use for sending emails.
  - `MAIL_PASSWORD`: The password or app-specific password for the email account.
  - `ADMIN_EMAIL`: The administrator's email address to receive error logs or notifications. It will also be used to create a defult admin user when first running yutify (see below "**Run the application**"!).
- `RATELIMIT`: Enables rate-limiting on all API routes (`/api/*`). For valid values, refer to the [Flask-Limiter Docs](https://flask-limiter.readthedocs.io/en/stable/configuration.html#rate-limit-string-notation).
- `REDIS_URI`: URI for Redis (used for rate-limiting and caching). If not set:
  - With `FLASK_DEBUG=1` (development mode), in-memory caching will be used.
  - Without `FLASK_DEBUG` (production mode), caching will be disabled.
- `ENABLE_CAPTCHA`: Whether to enable captcha on login and signup forms or not. Set this to `1` to enable captcha and `0` or omit it to disable captcha.
- For captcha, yutify uses Flask-WTF. Which comes with default configs for reCaptcha. However, if you want to use different captcha (e.g. hCaptcha), you may set these variables in environment variable (or `.env` file):
  - `CUSTOM_CAPTCHA`: Set to `1` if using different captcha than the Flask-WTF comes with and `0` or omit it to use default configs. (`ENABLE_CAPTCHA` should also be set to `1` otherwise this variable will be ignored and no captcha will be enabled).
  - Following variables define the configs for custom captcha. Please consult the [Flask-WTF Docs](https://flask-wtf.readthedocs.io/en/latest/config/#recaptcha). `CUSTOM_CAPTCHA` must be set to `1` else, these will be ignored:
  - `RECAPTCHA_PUBLIC_KEY`, `RECAPTCHA_PRIVATE_KEY`, `RECAPTCHA_SCRIPT`, `RECAPTCHA_DIV_CLASS`, `RECAPTCHA_VERIFY_SERVER`

**3. Run the application**:

> [!IMPORTANT]
> Make sure you are at the root of the project directory before running commands below!
>
> Visit the application locally at: `http://localhost:<PORT>` or `http://127.0.0.1:<PORT>` ~
> Replace the `<PORT>` with the port number you defined in environment variable (or `.env` file) Or the default `5000`.
>
> When using a hosting provider, use the link provided by them for your deployed project.

```bash
flask db upgrade
```

```bash
python yutify.py
```

> [!WARNING]
> Regardless of the user registeration / signup is enabled or disabled, a default admin user with the email set in the `ADMIN_EMAIL` environment variable will be created when you will run the project. It will be created only if a user with that email does not exist in the database. You must change the username and password for it after logging in as this user. Please check the default values below:
>
> - `name`: "Admin"
> - `userrname`: "admin"
> - `email`: value set in `ADMIN_EMAIL` envrionment variable
> - `password`: "senpai-likes-small-potatoes"

# Contributing 🤝

We welcome contributions from everyone! Here's how you can help:

- **Open Issues**: If you have suggestions, improvements, or bug reports, feel free to open an issue.
- **Fork and Develop**: Fork the repository, create a new branch for your changes, and make modifications in that branch.
- **Submit Pull Requests**: Once your changes are ready, open a pull request for review.

Whether you're a user or a developer, your contributions are valuable and appreciated!

# Disclaimer ⚠️

All trademarks, logos, and content displayed in this project are the property of their respective owners.

This project is open-source and is not affiliated with, endorsed by, or associated with any of the mentioned services or platforms, including but not limited to Apple Music, Spotify, KKBox, Last.fm, Deezer, and YouTube Music.
The use of their names, trademarks, or logos is solely to indicate compatibility or integration with these platforms and to enhance the user experience.

Any logos or trademarks displayed in this project and/or on the website remain the property of their respective owners.

# Acknowledgement // End Note 🙃

- Uses [yutipy](https://pypi.org/project/yutipy/) 🎶
- Uses [Pico CSS](https://picocss.com/) 🎨
- Powered by [Render](https://render.com/register) 🚀
- User Profile Icons by <a href="https://www.figma.com/@rrgraph?ref=svgrepo.com" target="_blank">Rrgraph</a> in CC Attribution License via <a href="https://www.svgrepo.com/" target="_blank">SVG Repo</a> 🧑‍🎨
- Thanks to [OhaJoq](https://github.com/Joqnix) for inspiring this project ✨
- Thanks to everyone who starred the repo—it means a lot! 🫂
- Uses [Foundation for Emails](https://github.com/foundation/foundation-emails) for responsive email templates ✉️
