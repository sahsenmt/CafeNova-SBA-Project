from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Define the dynamic menu with item IDs, names, and prices
MENU = {
    'carbonara': {'name': "Chef's Special Pasta Carbonara", 'price': 48.00},
    'truffle_mac': {'name': 'Premium Truffle Macaroni', 'price': 52.00},
    'espresso': {'name': 'Nova Classic Espresso', 'price': 15.00},
    'croissant': {'name': 'Fresh Butter Croissant', 'price': 12.00},
    'tiramisu': {'name': 'Homemade Tiramisu', 'price': 25.00}
}

# In-memory database to store active orders for 3 tables
# Each table holds a dictionary of {item_id: quantity}
tables_data = {
    '1': {},
    '2': {},
    '3': {}
}

# HTML Template with Table Tabs and Action Buttons
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cafe Nova | Multi-Table POS</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #fcf9f2; margin: 0; color: #3e2723; }
        header { background-color: #3e2723; color: #d7ccc8; padding: 1.5rem 0; text-align: center; }
        h1 { margin: 0; font-size: 2.5rem; letter-spacing: 2px; }
        
        /* Table Navigation Tabs */
        .tabs { display: flex; justify-content: center; background-color: #5d4037; padding: 10px 0; }
        .tab-link { 
            color: white; text-decoration: none; padding: 10px 30px; margin: 0 5px; 
            border-radius: 6px; font-weight: bold; transition: 0.3s;
        }
        .tab-link:hover { background-color: #795548; }
        .tab-link.active { background-color: #fcf9f2; color: #3e2723; }
        
        .main-layout { display: flex; max-width: 1100px; margin: 2rem auto; gap: 2rem; padding: 0 1rem; }
        .section { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.06); flex: 1; }
        
        .menu-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        .menu-table th, .menu-table td { padding: 12px; text-align: left; border-bottom: 1px solid #efebe9; }
        .menu-table th { background-color: #efebe9; color: #5d4037; }
        .qty-input { width: 60px; padding: 6px; border-radius: 6px; border: 1px solid #bcaaa4; text-align: center; }
        
        /* Action Buttons */
        .btn-group { display: flex; gap: 10px; margin-top: 1.5rem; }
        .btn-submit { flex: 2; background-color: #5d4037; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-size: 1.1rem; }
        .btn-clear { flex: 1; background-color: #d32f2f; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-size: 1.1rem; }
        .btn-submit:hover { background-color: #3e2723; }
        .btn-clear:hover { background-color: #b71c1c; }
        
        .receipt { font-family: 'Courier New', Courier, monospace; background-color: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; margin-top: 1rem; }
        .receipt-header { text-align: center; font-weight: bold; margin-bottom: 1.5rem; }
        .line-item { display: flex; justify-content: space-between; margin-bottom: 10px; }
        .divider { border-top: 1px dashed #6c757d; margin: 15px 0; }
        .total-line { font-weight: bold; font-size: 1.2rem; }
    </style>
</head>
<body>

    <header>
        <h1>☕ CAFE NOVA POS</h1>
    </header>

    <div class="tabs">
        <a href="/?table=1" class="tab-link {% if active_table == '1' %}active{% endif %}">Table 1</a>
        <a href="/?table=2" class="tab-link {% if active_table == '2' %}active{% endif %}">Table 2</a>
        <a href="/?table=3" class="tab-link {% if active_table == '3' %}active{% endif %}">Table 3</a>
    </div>

    <div class="main-layout">
        <div class="section">
            <h2 style="color: #5d4037; margin-top: 0;">Order for Table {{ active_table }}</h2>
            
            <form method="POST" action="/?table={{ active_table }}">
                <table class="menu-table">
                    <thead>
                        <tr>
                            <th>Item Description</th>
                            <th>Price</th>
                            <th>Qty</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item_id, info in menu.items() %}
                        <tr>
                            <td>{{ info.name }}</td>
                            <td>{{ "%.2f"|format(info.price) }} PLN</td>
                            <td>
                                <input type="number" name="qty_{{ item_id }}" class="qty-input" min="0" 
                                       value="{{ current_quantities.get(item_id, 0) }}">
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <div class="btn-group">
                    <button type="submit" name="action" value="update" class="btn-submit">💾 Save Order</button>
                    <button type="submit" name="action" value="clear" class="btn-clear">🗑️ Clear Table</button>
                </div>
            </form>
        </div>

        <div class="section">
            <h2 style="color: #5d4037; margin-top: 0;">Receipt - Table {{ active_table }}</h2>
            
            {% if ordered_items %}
            <div class="receipt">
                <div class="receipt-header">
                    CAFE NOVA<br>
                    Table: {{ active_table }}<br>
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
                Table {{ active_table }} is currently empty.
            </p>
            {% endif %}
        </div>
    </div>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    # Identify which table is currently active (default to Table 1)
    active_table = request.args.get('table', '1')
    if active_table not in tables_data:
        active_table = '1'
        
    # Handle form submission (Update Order OR Clear Table)
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'clear':
            # Reset the data for the active table
            tables_data[active_table] = {}
        
        elif action == 'update':
            # Save new quantities to the active table
            for item_id in MENU.keys():
                qty_str = request.form.get(f'qty_{item_id}', '0')
                qty = int(qty_str) if qty_str.isdigit() else 0
                
                # Only store items with quantity > 0 to save memory
                if qty > 0:
                    tables_data[active_table][item_id] = qty
                elif item_id in tables_data[active_table]:
                    del tables_data[active_table][item_id]
                    
        # Redirect to GET request to prevent double-submission on refresh
        return redirect(url_for('index', table=active_table))

    # --- Calculation Phase for GET request ---
    ordered_items = []
    subtotal = 0.0
    current_quantities = tables_data[active_table]
    
    # Calculate costs based on the active table's stored data
    for item_id, qty in current_quantities.items():
        if qty > 0:
            info = MENU[item_id]
            total_item_price = info['price'] * qty
            subtotal += total_item_price
            ordered_items.append({
                'name': info['name'],
                'qty': qty,
                'total_item_price': total_item_price
            })
            
    tax = subtotal * 0.08
    total = subtotal + tax

    # Render UI with active table context
    return render_template_string(
        HTML_CONTENT,
        menu=MENU,
        active_table=active_table,
        current_quantities=current_quantities,
        ordered_items=ordered_items,
        subtotal=subtotal,
        tax=tax,
        total=total
    )

if __name__ == '__main__':
    app.run()