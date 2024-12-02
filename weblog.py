import flask
import os

# serves logs/mail.log in Browser

app = flask.Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
    <head>
        <script>
            function getLog() {
                fetch('/get_log')
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('log-content').textContent = data;
                    });
            }
            getLog(); // immediately after page load
            setInterval(getLog, 10000); // every 10 seconds
        </script>
    </head>
    <body>
        <pre id="log-content"></pre>
    </body>
    </html>
    """

@app.route('/get_log')
def get_log():
    if not os.path.exists('logs/mail.log'):
        return 'No log file'
    with open('logs/mail.log') as f:
        return f.read()

app.run(debug=True, host='0.0.0.0', port=5001)
