# Fuel App Project

## Overview
The Fuel App is a Flask-based web application designed to process and analyze multiple Excel files containing fuel transaction records. It allows users to upload Excel files, clean and standardize the data, apply filters (specifically by Vehicle Number), view a data preview and filtered results, and download the filtered data as a CSV file.

## Key Features
- Upload multiple Excel files with different structures.
- Clean and standardize vehicle numbers and column names.
- Auto-detect missing or mismatched columns.
- Apply filters based on Vehicle Number, Date, and Station.
- Display data preview and filtered data in tabular format.
- Show a summary box with total price and total records after filtering.
- Download filtered data as a CSV file named after the Vehicle Number.

## Technologies Used
- Python (Flask)
- JavaScript (jQuery & AJAX)
- HTML5 & CSS3 (Bootstrap for UI styling)
- DataTables.js (for interactive tables)
- Pandas (for data processing)

## Folder Structure
```
project-root/
├── app.py                # Flask backend
├── templates/
│   └── index.html        # Main HTML file
├── static/
│   ├── styles.css        # Custom styles
│   └── script.js         # JavaScript logic
├── uploads/              # Folder to store uploaded Excel files
├── processed/            # Folder to store processed and filtered CSV files
└── README.md             # Project documentation
```

## Installation & Setup
1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/fuel-app.git
cd fuel-app
```

2. **Create a virtual environment and activate it:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install flask pandas openpyxl rapidfuzz
```

4. **Run the Flask server:**
```bash
python app.py
```

5. **Access the app:**
Open your browser and go to `http://127.0.0.1:5000/`

## Usage
1. Upload one or more Excel files (must be `.xlsx` format).
2. The app validates column names and displays a preview.
3. Enter a Vehicle Number and click **Apply Filter**.
4. The filtered data will appear along with a summary box showing total price and total records.
5. Optionally, download the filtered data as a CSV file using the **Download CSV** button.

## Customization
- You can adjust the `REQUIRED_COLUMNS` list in `app.py` to match your specific column requirements.
- Modify `styles.css` for custom UI styling.
- Expand filter functionality in `script.js` to include more conditions.

## License
This project is licensed under the MIT License.

## Author
Developed by Aaiydh.

---
Feel free to customize or expand the app based on your business needs!

