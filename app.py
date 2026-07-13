from flask import Flask

# Create the Flask application
app = Flask(__name__)

# Home page
@app.route("/")
def home():
    return """
    <h1>👶 Welcome, Mom & Dad!</h1>
    <h3>BabyCare Management System</h3>
    <p>Built by Asus using Flask 🚀</p>
    """

# Run the application
if __name__ == "__main__":
    app.run(debug=True)