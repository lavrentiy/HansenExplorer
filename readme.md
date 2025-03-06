# Solubility Calculator

A Flask-based web application for predicting solubility using **Hansen Solubility Parameters (HSP)**. The tool calculates Hansen distances, **RED values**, and visualizes solubility in a **3D interactive plot**.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/lavrentiy/HansenExplorer.git
cd HansenExplorer
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
The app will be available at **http://127.0.0.1:5000/** in your browser.

## Dependencies
- Python 3.8+
- Flask
- NumPy
- Pandas
- Plotly

To install missing dependencies manually, run:
```bash
pip install flask numpy pandas plotly
```

## License
This project is licensed under the **MIT License**.

## DISCLAIMER: This tool uses Hansen Solubility Parameters (HSP) as a theoretical model to estimate solubility.
It does NOT account for temperature effects, solvent mixtures, pH variations, or experimental data. Real-life solubility may differ significantly. For laboratory or industrial applications, consult empirical solubility data.
