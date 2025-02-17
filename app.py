from flask import Flask, render_template, request, jsonify, send_file
import os
import pandas as pd
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
ALLOWED_EXTENSIONS = {"xlsx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

REQUIRED_COLUMNS = ["Vehicle Number", "Total Price", "Fuel Type", "Date", "Station"]

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_vehicle_number(value):
    """Cleans vehicle numbers by removing letters, dashes, spaces, and unnecessary characters."""
    if pd.isna(value):
        return ""

    value = str(value).strip()
    value = re.sub(r'\s+', '', value)
    value = re.sub(r'-', '', value)
    value = re.sub(r'[a-zA-Z]+', '', value)

    return value

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded!"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file!"})

    if file and allowed_file(file.filename):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        try:
            df = pd.read_excel(file_path, dtype=str)
            df.columns = df.columns.str.strip()

            if not all(col in df.columns for col in REQUIRED_COLUMNS):
                return jsonify({"error": "Invalid file format! Ensure correct column names."})

            df["Vehicle Number"] = df["Vehicle Number"].apply(clean_vehicle_number)

            preview_data = df.head(10).to_dict(orient="records")
            return jsonify({"success": True, "preview": preview_data, "filename": file.filename})

        except Exception as e:
            return jsonify({"error": f"File processing failed: {str(e)}"})

    return jsonify({"error": "Invalid file format! Please upload an Excel file."})

@app.route("/filter", methods=["POST"])
def filter_data():
    data = request.get_json()
    filename = data.get("filename")
    filter_conditions = data.get("filters", {})

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found!"})

    df = pd.read_excel(file_path, dtype=str)
    df["Vehicle Number"] = df["Vehicle Number"].astype(str).str.strip().apply(clean_vehicle_number)

    for column, value in filter_conditions.items():
        if value and column in df.columns:
            df = df[df[column].astype(str).str.contains(value, na=False, case=False)]

    csv_path = os.path.join(PROCESSED_FOLDER, "filtered_vehicle_data.csv")
    df.to_csv(csv_path, index=False)

    return jsonify({"success": True, "filtered_data": df.to_dict(orient="records")})



@app.route("/download")
def download_file():
    return send_file(os.path.join(PROCESSED_FOLDER, "filtered_vehicle_data.csv"), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
