import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST")

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST
}

BANNED_WORDS = ["box", "booster", "bundle", "blister", "etb", "case", "pack"]

def is_valid_card(card):
    if "card_number" not in card:
        return False  # to nie pojedyncza karta
    name = card.get("name", "").lower()
    return not any(bad in name for bad in BANNED_WORDS)


def find_matching_card(name, number=None):
    """Search for a card using the API and return the best match."""
    # The new API endpoint expects a single ``search`` parameter.
    search_query = f"{name} {number}" if number else name
    params = {"search": search_query}

    logger.debug("Requesting card search with params: %s", params)
    response = requests.get(
        f"https://{API_HOST}/cards/search", headers=HEADERS, params=params
    )

    logger.debug("API response status: %s", response.status_code)
    logger.debug("Requested URL: %s", response.url)
    if response.status_code != 200:
        raise Exception("Błąd pobierania danych z API.")

    data = response.json()
    # The new endpoint may return cards either in ``data`` or ``cards``
    # property.  Handle both cases gracefully.
    products = data.get("data") or data.get("cards") or []
    if isinstance(products, dict):
        products = products.get("cards") or products.get("data") or []

    logger.debug("API returned %d products", len(products))

    # Filtrowanie tylko singli
    valid_cards = [c for c in products if is_valid_card(c)]

    # Jeśli podano numer – dopasuj dokładnie po części przed '/'
    if number:
        # Użytkownik może podać numer w formie np. "206/198". Bierzemy tylko
        # pierwszą część i porównujemy w postaci uppercase, ignorując białe znaki.
        user_num = number.split("/")[0].strip().upper()

        for card in valid_cards:
            card_num = (
                str(card.get("card_number", "")).split("/")[0].strip().upper()
            )
            tcgid = str(card.get("tcgid", "")).strip().upper()

            # Najpierw próba dokładnego dopasowania po numerze karty
            if user_num == card_num:
                return card, []

            # Jeśli nie – dopuszczamy częściowe dopasowanie po tcgid
            if user_num in tcgid:
                return card, []

    # Jeśli nie znaleziono dokładnego dopasowania – zwróć listę do wyboru
    return None, valid_cards



def search_card():
    name = entry_name.get().strip()
    number = entry_number.get().strip()
    logger.debug("Searching for name='%s', number='%s'", name, number)

    if not name or not number:
        messagebox.showerror("Błąd", "Podaj nazwę i numer karty.")
        return

    try:
        card, alternatives = find_matching_card(name, number)
        if card:
            logger.debug("Found exact card match")
            display_card(card)
        else:
            if not alternatives:
                logger.debug("No cards found")
                messagebox.showerror("Nie znaleziono", "Nie znaleziono żadnych kart.")
                return
            logger.debug("Showing alternative selection")
            show_alternative_list(alternatives)

    except Exception as e:
        logger.exception("Error while searching for card")
        messagebox.showerror("Błąd", str(e))


def display_card(card):
    logger.debug("Displaying card: %s (%s)", card.get('name'), card.get('card_number'))
    label_result.config(text=f"{card.get('name')} ({card.get('card_number')})")

    # Obrazek
    image_url = card.get("image")
    if image_url:
        try:
            resp = requests.get(image_url)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content))
            img = img.resize((250, 350))
            img_tk = ImageTk.PhotoImage(img)
            label_image.config(image=img_tk)
            label_image.image = img_tk
        except Exception:
            logger.exception("Failed to load card image")
            label_image.config(image=None)
            label_image.image = None
    else:
        label_image.config(image=None)
        label_image.image = None

    # Cena
    price = card.get("prices", {}).get("cardmarket", {}).get("30d_average")
    if price:
        price = round(float(price), 2)
        your_price = round(price * 0.8, 2)
        label_price.config(text=f"Cena trend (30d): {price:.2f} EUR\nTwoja cena (80%): {your_price:.2f} EUR")
    else:
        label_price.config(text="Brak danych o cenie trend.")


def show_alternative_list(cards):
    window = tk.Toplevel(root)
    window.title("Wybierz kartę z listy")
    logger.debug("Showing %d alternative cards", len(cards))

    tk.Label(window, text="Nie znaleziono podanego numeru.\nWybierz kartę z listy:").pack(pady=5)

    listbox = tk.Listbox(window, width=60, height=10)
    for i, card in enumerate(cards):
        label = f"{card.get('name')} ({card.get('card_number')})"
        listbox.insert(tk.END, label)
    listbox.pack()

    def on_select():
        index = listbox.curselection()
        if not index:
            return
        selected_card = cards[index[0]]
        logger.debug("Selected alternative card: %s (%s)", selected_card.get('name'), selected_card.get('card_number'))
        display_card(selected_card)
        window.destroy()

    btn_ok = tk.Button(window, text="Wybierz", command=on_select)
    btn_ok.pack(pady=5)


# GUI
root = tk.Tk()
root.title("Wyceniarka kart Pokémon TCG")
root.geometry("600x650")

frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="Nazwa karty:").grid(row=0, column=0, sticky="e")
entry_name = tk.Entry(frame_input, width=30)
entry_name.grid(row=0, column=1)

tk.Label(frame_input, text="Numer karty:").grid(row=1, column=0, sticky="e")
entry_number = tk.Entry(frame_input, width=30)
entry_number.grid(row=1, column=1)

btn_search = tk.Button(root, text="Szukaj", command=search_card)
btn_search.pack(pady=10)

label_result = tk.Label(root, text="", font=("Helvetica", 14))
label_result.pack()

label_image = tk.Label(root)
label_image.pack(pady=10)

label_price = tk.Label(root, text="", font=("Helvetica", 12))
label_price.pack(pady=10)

root.mainloop()
