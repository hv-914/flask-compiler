import os
import subprocess
import re
from flask import Flask, request, jsonify, render_template, send_from_directory, send_file

app = Flask(__name__)

# Define the path of the directories
sketches = os.path.join(os.getcwd(), "sketches")
os.makedirs(sketches, exist_ok = True)
outputs = os.path.join(os.getcwd(), "outputs")
os.makedirs(outputs, exist_ok = True)

fqbn = "esp32:esp32:esp32"

# Default decorator
@app.route("/")
def homepage():
    ssid = ip = "Unknown"
    networks = subprocess.run(
        ["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True
    )
    for line in networks.stdout.split("\n"):
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":")[1].strip()
    result = subprocess.run(
            ["ipconfig"], capture_output=True, text=True
        )
    match = re.search(r"Default Gateway[ .]*: ([\d.]+)", result.stdout)
    if match:
        ip = match.group(1)
         
    return render_template("main.html", ssid=ssid, ip=ip)

# Decorator for the compile_sketch button
@app.route("/compile_sketch", methods = ["POST"])
def compile_sketch():
    data = request.json
    code = data.get("code", "")

    if not code.strip():
        return jsonify({"error": "Code cannot be empty"}), 400
    
    file_path = os.path.join(sketches, "sketches.ino")

    with open(file_path, "w") as f:
        f.write(code)

    compile_cmd = [
        "arduino-cli", "compile", "-b", fqbn,
        "--output-dir", outputs, sketches
    ]
    
    try:
        result = subprocess.run(compile_cmd, capture_output=True, text=True, check=True, cwd=sketches)
        bin_files = [f for f in os.listdir(outputs) if f.endswith(".bin")]
        bin_filepath = os.path.join(outputs, bin_files[0])

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
            "bin_filename": bin_files[0],
            "bin_filepath": bin_filepath
        }), 200
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Compilation failed",
            "stdout": e.stdout,
            "stderr": e.stderr
        }), 500

# Decorator to download the .ino.bin file
@app.route("/download/<filename>", methods = ['GET'])
def downloads(filename):
    binpath = os.path.join(os.path.abspath("outputs"), filename)
    if os.path.exists(binpath):
        return send_from_directory("outputs", filename, as_attachment = True)
    else:
        return jsonify({"Error": "File not found"}), 404
    
if __name__ == "__main__":
    app.run("0.0.0.0", port = 80, debug = True)