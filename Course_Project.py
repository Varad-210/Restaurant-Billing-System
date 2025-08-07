import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
from fpdf import FPDF
import os
import json

# ------------------ Data ------------------
menu = {
    "Burger": 80,
    "Fries": 40,
    "Coke": 30,
    "Pizza": 150,
    "Pasta": 120,
    "Hot Dog": 60,
    "Chicken Wings": 100,
    "Salad": 70,
    "Ice Cream": 50,
    "Milkshake": 60,
    "Sandwich": 90,
    "Garlic Bread":100,
    "Nachos": 75
}

combos = {
    "Burger": "Recommended Combo: Burger + Coke + Fries (Save ₹30!)",
    "Pizza": "Recommended Combo: Pizza + Coke + Garlic Bread (Save ₹40!)",
    "Pasta": "Recommended Combo: Pasta + Garlic Bread + Coke (Save ₹35!)",
    "Sandwich": "Recommended Combo: Sandwich + Fries + Milkshake (Save ₹45!)",
    "Hot Dog": "Recommended Combo: Hot Dog + Fries + Coke (Save ₹25!)"
}

available_tables = [1, 2, 3, 5, 6]
reservations = []
order = []
customer_orders = {}

# ------------------ Functions ------------------
def view_menu():
    menu_str = "Menu:\n"
    for item, price in menu.items():
        menu_str += f"{item} - Rs.{price}\n"
    messagebox.showinfo("Menu", menu_str)

def table_availability():
    messagebox.showinfo("Available Tables", f"Available Tables: {', '.join(map(str, available_tables))}")

def add_item():
    item = item_entry.get()
    qty = qty_entry.get()

    if item not in menu:
        messagebox.showerror("Error", "Item not in menu.")
        return

    try:
        qty = int(qty)
        if qty <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Enter valid quantity.")
        return

    price = menu[item]
    subtotal = price * qty
    order.append((item, qty, price, subtotal))

    update_order_display()

    if item in combos:
        combo_msg.set(combos[item])

def delete_order():
    if not order:
        messagebox.showerror("Error", "No items to delete.")
        return

    index = simpledialog.askinteger("Delete Item", f"Enter item serial number to delete (1 to {len(order)}):")

    if index is None:
        return

    if 1 <= index <= len(order):
        deleted_item = order.pop(index - 1)
        update_order_display()
        combo_msg.set("")
        totals_label.config(text="")
        messagebox.showinfo("Deleted", f"Item '{deleted_item[0]}' deleted from order.")
    else:
        messagebox.showerror("Error", "Invalid serial number.")

def update_order_display():
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "Sr  Description Qty  Price   Subtotal\n")
    for i, item in enumerate(order, 1):
        output_text.insert(tk.END, f"{i:<3} {item[0]:<10} {item[1]:<4} Rs.{item[2]:<6} Rs.{item[3]}\n")

def generate_bill():
    if not order:
        messagebox.showerror("Error", "No items in order.")
        return

    subtotal = sum(item[3] for item in order)
    discount = 0
    if subtotal > 1000:
        discount = subtotal * 0.15
    elif subtotal > 500:
        discount = subtotal * 0.10

    discounted_subtotal = subtotal - discount
    cgst = sgst = discounted_subtotal * 0.05
    total = discounted_subtotal + cgst + sgst

    bill = f"""
Sub Total : Rs.{subtotal:.2f}
Discount  : Rs.{discount:.2f}
CGST (5%) : Rs.{cgst:.2f}
SGST (5%) : Rs.{sgst:.2f}
Total     : Rs.{total:.2f}
"""
    totals_label.config(text=bill)
    return total, discount, cgst, sgst, subtotal

def save_receipt():
    if not order:
        messagebox.showerror("Error", "No items in order. Generate bill first.")
        return

    customer_id = simpledialog.askstring("Receipt", "Enter customer ID:")
    if not customer_id:
        return

    total_details = generate_bill()
    if not total_details:
        return

    total, discount, cgst, sgst, subtotal = total_details

    # Load existing orders if the file exists
    try:
        with open("customer_orders.json") as f:
            existing_orders = json.load(f)
    except FileNotFoundError:
        existing_orders = {}

    existing_orders[customer_id] = order[:]  # Add/overwrite this customer's order

    # Now save back to the file
    with open("customer_orders.json", "w") as f:
        json.dump(existing_orders, f, indent=4)
    
    # ... rest of your PDF generation code ...


    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_fill_color(200, 220, 255)

    pdf.cell(190, 10, "VIT CANTEEN", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(95, 10, f"Date: {datetime.now().strftime('%d-%m-%Y')}", border=1)
    pdf.cell(95, 10, f"Time: {datetime.now().strftime('%H:%M:%S')}", border=1, ln=True)
    pdf.cell(190, 10, f"Customer ID: {customer_id}", border=1, ln=True)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, "Item Details", ln=True, align='C')

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 10, "Item", 1)
    pdf.cell(30, 10, "Price", 1)
    pdf.cell(30, 10, "Qty", 1)
    pdf.cell(30, 10, "Total", 1, ln=True)

    pdf.set_font("Arial", '', 10)
    for item in order:
        item_name, qty, price, item_subtotal = item
        pdf.cell(100, 10, item_name, 1)
        pdf.cell(30, 10, f"Rs.{price}", 1)
        pdf.cell(30, 10, str(qty), 1)
        pdf.cell(30, 10, f"Rs.{item_subtotal}", 1, ln=True)

    pdf.cell(160, 10, "Sub Total", 1)
    pdf.cell(30, 10, f"Rs.{subtotal:.2f}", 1, ln=True)

    pdf.cell(160, 10, f"Discount ({discount/subtotal*100:.0f}%)", 1)
    pdf.cell(30, 10, f"-Rs.{discount:.2f}", 1, ln=True)

    pdf.cell(160, 10, "CGST (5%)", 1)
    pdf.cell(30, 10, f"Rs.{cgst:.2f}", 1, ln=True)

    pdf.cell(160, 10, "SGST (5%)", 1)
    pdf.cell(30, 10, f"Rs.{sgst:.2f}", 1, ln=True)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(160, 10, "Total Bill", 1)
    pdf.cell(30, 10, f"Rs.{total:.2f}", 1, ln=True)

    filename = f"receipt_{customer_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(filename)
    messagebox.showinfo("Saved", f"Receipt saved as {filename}")

def repeat_last_order():
    customer_id = simpledialog.askstring("Repeat Order", "Enter your customer ID:")
    if not customer_id:
        return

    try:
        with open("customer_orders.json") as f:
            saved_orders = json.load(f)
            previous_order = saved_orders.get(customer_id)
            if previous_order:
                global order
                order = previous_order
                update_order_display()
                messagebox.showinfo("Order Loaded", "Previous order loaded successfully.")
            else:
                messagebox.showerror("Not Found", "No previous order found for this ID.")
    except FileNotFoundError:
        messagebox.showerror("Error", "Order history file not found.")

def reserve_table():
    name = simpledialog.askstring("Reservation", "Enter your name:")
    table = simpledialog.askinteger("Reservation", "Enter table number:")
    date = simpledialog.askstring("Reservation", "Enter date (DD-MM-YYYY):")

    slot1 = "7PM - 9PM"
    slot2 = "9PM - 11PM"
    time_slot = simpledialog.askstring("Reservation", f"Enter time slot (Suggested: {slot1} or {slot2}):")

    if table not in available_tables:
        messagebox.showerror("Unavailable", "Table not available.")
        return

    reservations.append((name, table, date, time_slot))
    available_tables.remove(table)
    messagebox.showinfo("Reserved", f"Table {table} reserved for {name} on {date} at {time_slot}.")

# ------------------ Main Screen ------------------
# Main window
root = tk.Tk()
root.title("🍔 Restaurant Order Management System 🍟")
root.config(bg="#e6f7ff")

# Root column weights for responsiveness
for i in range(3):
    root.grid_columnconfigure(i, weight=1)

# Title
tk.Label(root, text="🍽️ VIT CANTEEN BILL SYSTEM  🍽️",
         font=("Arial", 16, "bold"), fg="#003366", bg="#e6f7ff").grid(row=0, column=0, columnspan=3, pady=10)

# Entry Frame
entry_frame = tk.Frame(root, bg="#cceeff")
entry_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
for i in range(3):
    entry_frame.grid_columnconfigure(i, weight=1)

tk.Label(entry_frame, text="Item:", bg="#cceeff", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
item_entry = tk.Entry(entry_frame, bg="#ffffff")
item_entry.grid(row=0, column=1, sticky="ew", padx=5)

tk.Label(entry_frame, text="Qty:", bg="#cceeff", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w")
qty_entry = tk.Entry(entry_frame, bg="#ffffff")
qty_entry.grid(row=1, column=1, sticky="ew", padx=5)

tk.Button(entry_frame, text="➕ Add Item", command=add_item, bg="#66cc99", fg="white", width=15).grid(row=0, column=2, padx=5)
tk.Button(entry_frame, text="💰 Generate Bill", command=generate_bill, bg="#3399ff", fg="white", width=15).grid(row=1, column=2, padx=5)

# Buttons Frame
buttons_frame = tk.Frame(root, bg="#e6f7ff")
buttons_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
for i in range(3):
    buttons_frame.grid_columnconfigure(i, weight=1)

tk.Button(buttons_frame, text="📋 Table Availability", command=table_availability, bg="#66ccff", fg="black", width=18).grid(row=0, column=0, padx=5)
tk.Button(buttons_frame, text="📝 Reserve Table", command=reserve_table, bg="#ffcc66", fg="black", width=18).grid(row=0, column=1, padx=5)
tk.Button(buttons_frame, text="📖 View Menu", command=view_menu, bg="#ff9999", fg="black", width=18).grid(row=0, column=2, padx=5)

tk.Button(buttons_frame, text="⭐ Order (Recommendation)", command=lambda: combo_msg.set("Add an item for suggestions ↓"),
          bg="#cc99ff", fg="white", width=20).grid(row=1, column=0, pady=5)
tk.Button(buttons_frame, text="❌ Delete Item", command=delete_order, bg="#ff6666", fg="white", width=15).grid(row=1, column=1, pady=5)
tk.Button(buttons_frame, text="📥 Save Receipt", command=save_receipt, bg="#00cc99", fg="white", width=15).grid(row=1, column=2, pady=5)
tk.Button(buttons_frame, text="🔄 Repeat Last Order", command=repeat_last_order, bg="#3399ff", fg="white", width=20).grid(row=2, column=1, pady=5)

# Order Display Textbox
output_text = tk.Text(root, height=10, width=60, bg="#f2f2f2", font=("Courier New", 10))
output_text.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
output_text.insert(tk.END, "Sr  Description    Qty   Price   Subtotal\n")

# Combo Recommendation Label
combo_msg = tk.StringVar()
tk.Label(root, textvariable=combo_msg, fg="#cc3300", bg="#e6f7ff", font=("Arial", 10, "italic")).grid(row=4, column=0, columnspan=3)

# Totals Label
totals_label = tk.Label(root, text="", font=("Arial", 11, "bold"), fg="#333333", bg="#e6f7ff")
totals_label.grid(row=5, column=0, columnspan=3, pady=10)

# Footer Note
tk.Label(root, text="SAVE PAPER SAVE NATURE!!\nTHANK YOU FOR A DELICIOUS MEAL.",
         bg="#e6f7ff", pady=10).grid(row=6, column=0, columnspan=3)

# Make row 3 expandable
root.grid_rowconfigure(3, weight=1)

root.mainloop()