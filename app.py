from flask import Flask, render_template_string

app = Flask(__name__)

# HTML template with embedded CSS and Jinja2 variables for dynamic rendering
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cafe Nova | Live Order</title>
    <style>
        /* Simple and elegant styling for the cafe app */
        body { 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
            background-color: #fcf9f2; 
            color: #3e2723; 
            text-align: center; 
            margin: 0; 
        }
        header { 
            background-color: #3e2723; 
            color: #d7ccc8; 
            padding: 2.5rem 0; 
        }
        h1 { margin: 0; font-size: 3rem; letter-spacing: 2px; }
        .container { 
            max-width: 650px; 
            margin: 3rem auto; 
            background: white; 
            padding: 2.5rem; 
            border-radius: 12px; 
            box-shadow: 0 8px 20px rgba(0,0,0,0.08); 
        }
        .receipt { 
            background-color: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            text-align: left; 
            margin-top: 25px; 
            font-family: 'Courier New', Courier, monospace; 
            font-size: 1.1rem; 
            border: 1px solid #dee2e6;
        }
        .line-item { 
            display: flex; 
            justify-content: space-between; 
            border-bottom: 1px dashed #adb5bd; 
            margin-bottom: 12px; 
            padding-bottom: 8px; 
        }
        .total { 
            font-weight: bold; 
            font-size: 1.4rem; 
            border-bottom: none; 
            border-top: 2px solid #343a40; 
            padding-top: 15px; 
            margin-top: 10px;
            color: #212529;
        }
    </style>
</head>
<body>
    <header>
        <h1>☕ CAFE NOVA</h1>
        <p>Cloud-Powered Culinary Experience</p>
    </header>
    
    <div class="container">
        <h2>Live Order Calculation</h2>
        <p>This section demonstrates dynamic backend calculation using Python Flask before rendering the HTML.</p>
        
        <div class="receipt">
            <div class="line-item">
                <span>Chef's Special Macaroni</span> 
                <span>{{ "%.2f"|format(pasta_price) }} PLN</span>
            </div>
            <div class="line-item">
                <span>Nova Classic Espresso</span> 
                <span>{{ "%.2f"|format(coffee_price) }} PLN</span>
            </div>
            <br>
            <div class="line-item">
                <span>Subtotal</span> 
                <span>{{ "%.2f"|format(subtotal) }} PLN</span>
            </div>
            <div class="line-item">
                <span>Tax (8% VAT)</span> 
                <span>{{ "%.2f"|format(tax) }} PLN</span>
            </div>
            <div class="line-item total">
                <span>TOTAL DUE</span> 
                <span>{{ "%.2f"|format(total) }} PLN</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Define prices for the menu items
    pasta_price = 45.00
    coffee_price = 15.00
    
    # Calculate subtotal, tax (8% food VAT), and final total
    subtotal = pasta_price + coffee_price
    tax = subtotal * 0.08
    total = subtotal + tax
    
    # Pass the calculated values to the HTML template dynamically
    return render_template_string(
        HTML_CONTENT, 
        pasta_price=pasta_price, 
        coffee_price=coffee_price, 
        subtotal=subtotal, 
        tax=tax, 
        total=total
    )

if __name__ == '__main__':
    # Run the Flask development server
    app.run()