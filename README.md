# Item Catalog

<!-- MarkdownTOC levels="1" autolink=true autoanchor=false bracket="round" -->

- [Installation](#installation)
    - [Set up Google OAuth2](#set-up-google-oauth2)

<!-- /MarkdownTOC -->

## Installation

Install the dependencies:

```sh
pip install -r requirements.txt
```

Setup the SQLite-DB:

```sh
python database_setup.py [-h] [--with-example-content] [--purge]
```

Then start your flask-application server:

```sh
python application.py
```

### Set up Google OAuth2

- Create a new app in the [Google Cloud Console](https://console.cloud.google.com/)
- Go to "API's and Services" => "Credentials" and create a new `OAuth client ID`
- Download the Client-Secret JSON and place it within this folder with the name `google_secrets.json`
