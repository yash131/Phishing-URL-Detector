from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory, jsonify
from featureExtractor import featureExtraction
from pycaret.classification import load_model, predict_model
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key'  # Secure this in production

# Load phishing detection model
model = load_model('model/phishingdetection')

# Predict function
def predict(url):
    data = featureExtraction(url)
    result = predict_model(model, data=data)
    return {
        'prediction_label': int(result['prediction_label'][0]),
        'prediction_score': float(result['prediction_score'][0]) * 100
    }

# Static files handler
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == "user@example.com" and password == "1":
            session['logged_in'] = True
            return redirect(url_for('url_check'))
        return "Invalid credentials, please try again!"
    return render_template('login_page.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# URL checker route
@app.route('/check-url', methods=['GET', 'POST'])
def url_check():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        url = request.form['url']
        data = predict(url)
        return render_template('url_check.html', url=url, data=data)

    return render_template('url_check.html')

# Chatbot UI
@app.route('/chatbot')
def chatbot():
    return '''
    <html>
    <head>
        <title>Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
            .chatbox { width: 100%; height: 400px; border: 1px solid #ccc; overflow-y: auto; padding: 10px; }
            .input-box { width: 80%; padding: 10px; margin-top: 10px; }
            .send-btn { padding: 10px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>Chatbot</h2>
        <div class="chatbox" id="chatbox"></div>
        <input type="text" class="input-box" id="userInput" placeholder="Type a message...">
        <button class="send-btn" onclick="sendMessage()">Send</button>

        <script>
            function sendMessage() {
                let input = document.getElementById('userInput').value;
                if (input.trim() === '') return;

                let chatbox = document.getElementById('chatbox');
                chatbox.innerHTML += "<p><b>You:</b> " + input + "</p>";

                fetch('/chatbot-response', {
                    method: 'POST',
                    body: JSON.stringify({ message: input }),
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    chatbox.innerHTML += "<p><b>Bot:</b> " + data.response + "</p>";
                });

                document.getElementById('userInput').value = '';
            }
        </script>
    </body>
    </html>
    '''

# Chatbot response logic
@app.route('/chatbot-response', methods=['POST'])
def chatbot_response():
    user_message = request.json.get("message")
    bot_reply = f"You said: {user_message}"  # Replace with actual logic
    return jsonify({"response": bot_reply})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
