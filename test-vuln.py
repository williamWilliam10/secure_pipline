import os

app = Flask(__name__)


@app.route("/run")
def run_command():
    
    user_input = request.args.get("host")
    os.system("ping " + user_input)