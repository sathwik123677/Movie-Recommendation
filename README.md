# Movie Recommendation

A clean, modern, and personalized movie recommendation wizard app. Built with Flask, vanilla CSS, and JavaScript.

## Features
- **Preferences Wizard**: Filter movies by genres, preferred language, minimum IMDb rating, and runtime.
- **Taste Profile matching**: Extracts directors, cast members, and genres from movies you like to build an affinity profile.
- **Structural 4-Column Grid**: View recommended movie cards side-by-side on desktop screen dimensions.
- **Explainable Matches**: See exactly why each movie is recommended under "Match Insights".
- **Clickable Posters**: Click on any movie poster image to open its IMDb link in a new tab.

---

## Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3** (version 3.8 or newer) installed.

### 2. Install Dependencies
Run the following command in your terminal to install Flask:
```bash
pip install Flask requests
```

*(Optional: If you also want to run the Jupyter SVD machine learning model prototype `movies.ipynb`):*
```bash
pip install pandas scikit-surprise ipywidgets notebook
```

### 3. Run the Web Server
Start the Flask application server:
```bash
python app.py
```

### 4. Access the App
Open your web browser and go to:
👉 **http://127.0.0.1:5000**

---

## Technical Details

For detailed analysis on how the recommendation logic assigns weights and scores, or how the machine learning prototype `movies.ipynb` is structured, view the [notes.txt](notes.txt) file.