from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

sketches = os.path.join(os.getcwd(), "sketches")
os.makedirs(sketches, exist_ok = True)

@app.route("/save_sketch", methods = ['POST'])
def save_sketch():
    data = request.json
    code = data.get("code", "")

    if not code.strip():
        return jsonify({"error": "Code cannot be empty!"}), 400

    file_path = os.path.join(sketches, "sketch.ino")
    
    with open(file_path, "w") as f:
        f.write(code)

    return jsonify({"message": "Sketch saved successfully!", "path": file_path})

@app.route("/")
def homepage():
    return render_template("main.html")

if __name__ == "__main__":
    app.run("0.0.0.0", port = 80)
