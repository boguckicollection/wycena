# Wycena Pokémon TCG

This application is a simple Tkinter GUI for checking Pokémon TCG card prices.
It queries a RapidAPI service and displays basic information such as the card
name, image and its 30‑day price trend. The price is taken from the API and the
program calculates your own price (80% of the trend).

## Configuration

The application expects two environment variables so it can connect to RapidAPI:

- `RAPIDAPI_KEY` – your RapidAPI key.
- `RAPIDAPI_HOST` – the RapidAPI host for the card pricing API.

The easiest way to provide them is to create a `.env` file in the project
directory:

```text
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=example-rapidapi-host
```

The `python-dotenv` package is used in `app.py` to load these values at runtime.
You can also export them in your shell before launching the program.

## Installation

This is a regular Python 3 application. Install the required packages with
pip:

```bash
pip install requests pillow python-dotenv
```

`tkinter` is included with most Python installations. If you do not have it,
install the appropriate package for your operating system.

## Usage

Run the application with Python:

```bash
python app.py
```

Enter the card name and number when prompted and the program will display
a matching card with its image and price. If multiple cards are found, a list
will be shown for you to choose from.

