from flask import Flask, request, jsonify, render_template
import os
import subprocess

app = Flask(__name__)

sketches = os.path.join(os.getcwd(), "sketches")
os.makedirs(sketches, exist_ok = True)

outputs = os.path.join(os.getcwd(), "outputs")
os.makedirs(outputs, exist_ok = True)

fqbn = "esp32:esp32:esp32"

@app.route("/save_sketch", methods = ["POST"])
def save_sketch():
    data = request.json
    code = data.get("code", "")

    if not code.strip():
        return jsonify({"error": "Code cannot be empty"}), 400
    
    file_path = os.path.join(sketches, "sketches.ino")

    with open(file_path, "w") as f:
        f.write(code)

    return jsonify({"message": "Sketch saved successfully", "path": file_path}), 200

@app.route("/compile_sketch", methods = ["POST"])
def compile_sketch():
    compile_cmd = [
        "arduino-cli", "compile", "-b", fqbn,
        "--output-dir", outputs, sketches
    ]
    
    try:
        result = subprocess.run(compile_cmd, capture_output=True, text=True, check=True, cwd=sketches)
        bin_files = [f for f in os.listdir(outputs) if f.endswith(".bin")]

        if not bin_files:
            return jsonify({
                "error": "Compilation succeeded but no .bin file was generated",
                "stdout": result.stdout,
                "stderr": result.stderr
            }), 500

        return jsonify({
            "message": "Compilation successful",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "bin_files": bin_files
        }), 200
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Compilation failed",
            "stdout": e.stdout,
            "stderr": e.stderr
        }), 500

@app.route("/")
def homepage():
    return render_template("main.html")

if __name__ == "__main__":
    app.run("0.0.0.0", port = 80)
