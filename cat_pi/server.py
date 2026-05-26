from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/buzz")
def buzz():
    subprocess.run(["python3", "/home/stacy/buzzer.py"])
    return "Buzzing!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
