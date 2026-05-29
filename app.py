from flask import Flask, render_template_string, request

app = Flask(__name__)

# Define the dynamic menu with item IDs, names, and prices
MENU = {
    'carbonara': {'name': "Chef's Special Pasta Carbonara", 'price': 48.00},
    'truffle_mac': {'name': 'Premium Truffle Macaroni', 'price': 52.00},
    'espresso': {'name': 'Nova Classic Espresso', 'price': 15.00},
    'croissant': {'name': 'Fresh Butter Croissant', 'price': 12.00},
    'tiramisu': {'name': 'Homemade Tiramisu', 'price': 25.00}
}

# HTML Template with combined CSS and POS interface logic
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cafe Nova | Waiter POS System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #fcf9f2;
            color: #3e2723;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #3e2723;
            color: #d7ccc8;
            padding: 2rem 0;
            text-align: center;
        }
        h1 { margin: 0; font-size: 2.8rem; letter-spacing: 2px; }
        .main-layout {
            display: flex;
            max-width: 1100px;
            margin: 2rem auto;
            gap: 2rem;
            padding: 0 1rem;
        }
        .section {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.06);
            flex: 1;
        }
        .menu-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        .menu-table th, .menu-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #efebe9;
        }
        .menu-table th { background-color: #efebe9; color: #5d4037; }
        .qty-input {
            width: 60px;
            padding: 6px;
            border-radius: 6px;
            border: 1px solid #bcaaa4;
            text-align: center;
            font-size: 1rem;
        }
        .btn-submit {
            background-color: #5d4037;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 1.1rem;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            margin-top: 1.5rem;
            transition: background 0.2s;
        }
        .btn-submit:hover { background-color: #3e2723; }
        .receipt {
            font-family: 'Courier New', Courier, monospace;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
            margin-top: 1rem;
        }
        .receipt-header { text-align: center; font-weight: bold; margin-bottom: 1.5rem; }
        .line-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 1rem;
        }
        .divider { border-top: 1px dashed #6c757d; margin: 15px 0; }
        .total-line { font-weight: bold; font-size: 1.2rem; }
    </style>
</head>
<body>

    <header>
        <h1>☕ CAFE NOVA</h1>
        <p>Waiter Live Order POS System</p>
    </header>

    <div class="main-layout">
        <div class="section">
            <h2 style="color: #5d4037; margin-top: 0;">Take New Order</h2>
            <p>Select quantities below to simulate a real-time waiter entry:</p>
            
            <form method="POST" action="/">
                <table class="menu-table">
                    <thead>
                        <tr>
                            <th>Item Description</th>
                            <th>Price</th>
                            <th>Quantity</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item_id, info in menu.items() %}
                        <tr>
                            <td>{{ info.name }}</td>
                            <td>{{ "%.2f"|format(info.price) }} PLN</td>
                            <td>
                                <input type="number" name="qty_{{ item_id }}" class="qty-input" min="0" value="{{ current_quantities.get(item_id, 0) }}">
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <button type="submit" class="btn-submit">🛒 Calculate & Generate Receipt</button>
            </form>
        </div>

        <div class="section">
            <h2 style="color: #5d4037; margin-top: 0;">Live Bill / Receipt</h2>
            
            {% if ordered_items %}
            <div class="receipt">
                <div class="receipt-header">
                    CAFE NOVA RECEIPT<br>
                    -------------------------
                </div>
                
                {% for item in ordered_items %}
                <div class="line-item">
                    <span>{{ item.qty }}x {{ item.name }}</span>
                    <span>{{ "%.2f"|format(item.total_item_price) }} PLN</span>
                </div>
                {% endfor %}
                
                <div class="divider"></div>
                
                <div class="line-item">
                    <span>Subtotal:</span>
                    <span>{{ "%.2f"|format(subtotal) }} PLN</span>
                </div>
                <div class="line-item">
                    <span>VAT (8%):</span>
                    <span>{{ "%.2f"|format(tax) }} PLN</span>
                </div>
                
                <div class="divider"></div>
                
                <div class="line-item total-line">
                    <span>TOTAL DUE:</span>
                    <span>{{ "%.2f"|format(total) }} PLN</span>
                </div>
            </div>
            {% else %}
            <p style="color: #757575; font-style: italic; text-align: center; margin-top: 4rem;">
                No active order. Select items on the left to compute the bill.
            </p>
            {% endif %}
        </div>
    </div>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    ordered_items = []
    current_quantities = {}
    subtotal = 0.0
    
    # Process the form submission data
    if request.method == 'POST':
        for item_id, info in MENU.items():
            # Retrieve quantity from input field, default to 0 if empty or invalid
            qty_str = request.form.get(f'qty_{item_id}', '0')
            qty = int(qty_str) if qty_str.isdigit() else 0
            
            current_quantities[item_id] = qty
            
            # If item is selected, calculate costs and add to active receipt
            if qty > 0:
                total_item_price = info['price'] * qty
                subtotal += total_item_price
                ordered_items.append({
                    'name': info['name'],
                    'qty': qty,
                    'total_item_price': total_item_price
                })
                
    # Compute dynamic taxation (8% standard catering VAT) and grand total
    tax = subtotal * 0.08
    total = subtotal + tax

    # Render template with variables back to the UI context
    return render_template_string(
        HTML_CONTENT,
        menu=MENU,
        ordered_items=ordered_items,
        current_quantities=current_quantities,
        subtotal=subtotal,
        tax=tax,
        total=total
    )

if __name__ == '__main__':
    # Start the application server
    app.run()