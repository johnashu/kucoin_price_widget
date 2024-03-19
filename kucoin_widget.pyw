import tkinter as tk
import threading
import time
import requests
from config import START_POSITION, URL, TOKENS, DELAY, AVERAGE_CHAR_WIDTH, MIN_WIDTH

previous_prices = {}

def fetch_all_token_prices():
    """Fetches the current prices for all tokens and calculates price changes."""
    global previous_prices
    all_prices_text = []
    for token in TOKENS:
        try:
            response = requests.get(f"{URL}/api/v1/market/orderbook/level1?symbol={token}-USDT")
            response_data = response.json()
            current_price = float(response_data["data"]["bestAsk"])
            price_change = calculate_price_change(token, current_price)
            previous_prices[token] = current_price
            all_prices_text.append((f"{token}: ${current_price} ", price_change))
        except Exception as e:
            all_prices_text.append((f"{token}: Error ", ("-", "white")))
    return all_prices_text

def calculate_price_change(token, current_price):
    """Calculates the price change direction."""
    if token in previous_prices:
        if current_price > previous_prices[token]:
            return ("↑", "green")
        elif current_price < previous_prices[token]:
            return ("↓", "red")
        else:
            return ("-", "white")
    else:
        return ("-", "white")

def update_price_label(text_widget, root):
    """Updates the price label with the latest prices."""
    while True:
        all_prices_text = fetch_all_token_prices()
        total_length = 1

        # Buffer to hold new content
        new_content = []
        for i, (token_text, (change_symbol, color)) in enumerate(all_prices_text):
            pipe = '' if i == len(all_prices_text) - 1 else '  |'
            text_with_symbol = f"  {token_text}{change_symbol}{pipe}"
            new_content.append((text_with_symbol, color))
            total_length += len(text_with_symbol) + 1

        # Update the widget in one operation to minimize flashing
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)

        for text_with_symbol, color in new_content:
            insert_point = text_widget.index(tk.END)
            text_widget.insert(insert_point, text_with_symbol)
            # Apply color to the change symbol
            symbol_start = f"{insert_point}-{len(text_with_symbol)}c"
            symbol_end = f"{symbol_start}+{len(text_with_symbol)}c"
            text_widget.tag_add(color, symbol_start, symbol_end)

        text_widget.config(state=tk.DISABLED)
        adjust_window_size(root, total_length)
        time.sleep(DELAY)

def adjust_window_size(root, total_length):
    """Adjusts the main window size based on the total length of the text."""
    new_width = int(max(MIN_WIDTH, total_length * AVERAGE_CHAR_WIDTH))
    root.geometry(f"{new_width}x30")

def setup_gui():
    """Sets up the GUI components."""
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.geometry(START_POSITION)
    root.resizable(False, False)

    price_text_widget = tk.Text(root, height=1, bg="black", fg="white", font=("Helvetica", 14, "bold"), wrap=tk.NONE)
    price_text_widget.tag_configure("green", foreground="green")
    price_text_widget.tag_configure("red", foreground="red")
    price_text_widget.tag_configure("black", foreground="black")
    price_text_widget.pack(fill=tk.BOTH, expand=True)
    price_text_widget.config(state=tk.DISABLED)
    price_text_widget.pack_propagate(False)

    setup_bindings(root)
    threading.Thread(target=lambda: update_price_label(price_text_widget, root), daemon=True).start()
    return root

def setup_bindings(root):
    """Sets up event bindings for the application."""
    root.bind("<Button-3>", lambda event: root.destroy())
    root.bind("<Button-1>", lambda event: setattr(root, "drag_start", (event.x, event.y)))
    root.bind("<ButtonRelease-1>", lambda event: setattr(root, "drag_start", None))
    root.bind("<B1-Motion>", lambda event: move_and_log_position(root, event))

def move_and_log_position(root, event):
    """Moves the window and logs its new position."""
    new_x = root.winfo_x() + event.x - root.drag_start[0]
    new_y = root.winfo_y() + event.y - root.drag_start[1]
    root.geometry(f"+{new_x}+{new_y}")
    new_position = f"+{new_x}+{new_y}"
    update_start_position_in_config(new_position)

def update_start_position_in_config(new_position):
    """Updates the START_POSITION in config.py with the new position."""
    config_path = 'config.py'
    with open(config_path, 'r') as file:
        lines = file.readlines()
    
    with open(config_path, 'w') as file:
        for line in lines:
            if line.strip().startswith('START_POSITION'):
                line = f'START_POSITION = "{new_position}"\n'
            file.write(line)

if __name__ == "__main__":
    root = setup_gui()
    root.mainloop()