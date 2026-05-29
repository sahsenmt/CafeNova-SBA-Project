from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Welcome to Cafe Nova!</h1><p>Frontend Web App is running perfectly on Azure.</p>"

if __name__ == '__main__':
    app.run()
    