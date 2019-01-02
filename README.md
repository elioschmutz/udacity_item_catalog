# Item Catalog

<!-- MarkdownTOC levels="1" autolink=true autoanchor=false bracket="round" -->

- [Installation](#installation)

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
