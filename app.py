from flask import Flask, render_template, request, jsonify, send_file
import os
import pandas as pd
import re
from rapidfuzz import process

app = Flask(__name__, template_folder="templates")

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
ALLOWED_EXTENSIONS = {"xlsx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# ✅ Move `app.run(debug=True)` to the bottom

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Define the required columns in the desired order
REQUIRED_COLUMNS = ["Vehicle Number", "Total Price", "Station", "Date"]

# Possible alternative names for the required columns
COLUMN_ALIASES = {
    "Vehicle No.": "Vehicle Number",
    "Total Cost": "Total Price",
    "Gas Station": "Station",
    "Transaction Date": "Date",
    "Amount Paid": "Total Price",
    "Fuel Station": "Station"
}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_vehicle_number(value):
    """Cleans and standardizes vehicle numbers."""
    if pd.isna(value):
        return ""
    value = str(value).strip()
    value = re.sub(r'\s+', '', value)  # Remove spaces
    value = re.sub(r'-', '', value)  # Remove dashes
    return value

def standardize_columns(df):
    """Ensure all required columns are present, renaming and filling missing ones."""
    actual_columns = list(df.columns)
    column_map = {}
    missing_columns = []

    print(f"🔹 Original columns: {actual_columns}")  # Debugging

    for required_col in REQUIRED_COLUMNS:
        if required_col in actual_columns:
            column_map[required_col] = required_col
        else:
            match = process.extractOne(required_col, actual_columns)
            if match and match[1] > 80:
                column_map[match[0]] = required_col
            elif required_col in COLUMN_ALIASES.values():
                column_map[required_col] = required_col
            else:
                missing_columns.append(required_col)

    df.rename(columns=column_map, inplace=True)
    
    print(f"✅ Final columns after renaming: {list(df.columns)}")  # Debugging
    print(f"⚠️ Missing columns: {missing_columns}")  # Debugging

    # Fill missing columns before reordering
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = "N/A" if col in ["Vehicle Number", "Station", "Date"] else "0"

    # ✅ Ensure columns exist before reordering
    available_columns = [col for col in REQUIRED_COLUMNS if col in df.columns]
    df = df[available_columns]

    return df, missing_columns


@app.route("/upload", methods=["POST"])
def upload():
    if "files" not in request.files:
        return jsonify({"error": "No files uploaded!"})

    files = request.files.getlist("files")
    all_data = []

    for file in files:
        if file and allowed_file(file.filename):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            try:
                df = pd.read_excel(file_path, dtype=str)
                df.columns = df.columns.str.strip()

                df, missing_columns = standardize_columns(df)

                if missing_columns:
                    return jsonify({
                        "error": f"File {file.filename} has missing columns",
                        "missing_columns": missing_columns
                    })

                df["Vehicle Number"] = df["Vehicle Number"].apply(clean_vehicle_number)

                # ✅ Assign Station Name from Filename
                station_name = file.filename.split(".")[0]  # Extract name before `.xlsx`
                df["Station"] = station_name  # Assign the extracted station name

                all_data.append(df)

            except Exception as e:
                return jsonify({"error": f"File processing failed for {file.filename}: {str(e)}"})

    if all_data:
        merged_df = pd.concat(all_data, ignore_index=True)
        merged_df = merged_df.fillna("N/A")

        # ✅ Ensure correct order
        merged_df = merged_df[["Vehicle Number", "Total Price", "Station", "Date"]]

        csv_path = os.path.join(PROCESSED_FOLDER, "merged_vehicle_data.csv")
        merged_df.to_csv(csv_path, index=False)

        preview_data = merged_df.head(10).to_dict(orient="records")

        return jsonify({"success": True, "preview": preview_data, "filename": "merged_vehicle_data.csv"})

    return jsonify({"error": "No valid files processed."})


@app.route("/filter", methods=["POST"])
def filter_data():
    """Filters the merged data based on Vehicle Number and calculates total price."""
    data = request.get_json()
    filename = "merged_vehicle_data.csv"
    filter_vehicle = data.get("filters", {}).get("Vehicle Number", "").strip()

    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "No data available. Please upload files first."})

    df = pd.read_csv(file_path, dtype=str)

    if filter_vehicle:
        df = df[df["Vehicle Number"].astype(str).str.contains(filter_vehicle, na=False, case=False)]

    if df.empty:
        return jsonify({"error": "No matching records found."})

    df["Total Price"] = pd.to_numeric(df["Total Price"], errors="coerce").fillna(0)
    total_price = df["Total Price"].sum()

    df = df.fillna("N/A")

    return jsonify({
        "success": True,
        "filtered_data": df.to_dict(orient="records"),
        "total_price": total_price
    })

@app.route("/download")
def download_file():
    """Download filtered data as CSV based on Vehicle Number."""
    vehicle_number = request.args.get("vehicle")

    if not vehicle_number:
        return jsonify({"error": "No vehicle number provided for download!"})

    file_path = os.path.join(PROCESSED_FOLDER, "merged_vehicle_data.csv")

    if not os.path.exists(file_path):
        return jsonify({"error": "No data available. Please upload files first."})

    df = pd.read_csv(file_path, dtype=str)

    # ✅ Filter by Vehicle Number
    df = df[df["Vehicle Number"].astype(str).str.contains(vehicle_number, na=False, case=False)]

    if df.empty:
        return jsonify({"error": "No matching records found for download!"})

    # ✅ Save the filtered data with Vehicle Number as filename
    filtered_csv_path = os.path.join(PROCESSED_FOLDER, f"{vehicle_number}.csv")
    df.to_csv(filtered_csv_path, index=False)

    return send_file(filtered_csv_path, as_attachment=True)

# ✅ Move `app.run(debug=True)` to the bottom
if __name__ == "__main__":
    app.run(debug=True)


