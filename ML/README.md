# AI-Based Government Scheme Eligibility and Recommendation System

Scheme Finder is a college ML microproject for discovering Indian welfare schemes.
It addresses a practical problem: titles and benefits are searchable, but conditions,
documents and application links are often spread across official sites.

## Run in VS Code on Windows

Open `C:\Users\PRANAV\OneDrive\Documents\ML MICROPROJECT` using **File → Open Folder**.
In the VS Code PowerShell terminal, launch the installed app.

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501). Press **Ctrl+C** to stop the server.
In VS Code, use **Python: Select Interpreter** and choose `.venv\Scripts\python.exe`.

### Recreate the environment or retrain

Tested on Windows with Python 3.14.2. You can call the venv Python directly without
changing PowerShell execution policy. With the VS Code Python and Python Debugger extensions installed, you can also launch **Run Scheme Finder** from **Run and Debug**.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.data_loader
.\.venv\Scripts\python.exe -m src.train_model
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Data and methods

- [Indian Government Welfare Schemes](https://www.kaggle.com/datasets/premsargara/indian-government-beneficiary-schemes) supplies 4,702 catalog records with 29 fields.
- [Indian government central sector scheme](https://www.kaggle.com/datasets/mrsumitjha/indian-government-central-sector-scheme) supplies 772 historical fiscal rows with 16 fields.
- Official rule sources, downloaded paths and dataset limitations are detailed in [Dataset sources](docs/dataset_sources.md). See `data/processed/raw_audit.json` for missing counts.
- Simulated candidate pairs support Logistic Regression, Decision Tree, Random Forest and k-NN. GridSearchCV tunes the four algorithms using five profile-grouped folds. Profiles in the holdout are kept out of training and CV. Imputation, encoding and scaling run inside each fold.
- The selected model and actual evaluation results are in `models/`. K-Means and PCA use the synthetic profiles for exploratory analysis.

Python, Streamlit, Pandas, NumPy, scikit-learn, Plotly and Joblib power the app.
The confusion matrix uses Matplotlib and Seaborn. Storage uses CSV and JSON.

## Demonstration

1. Open **Home** to explore categories, regions and the searchable catalog.
2. Use **Recommendations** with a fictional profile. The app orders results by rule status and displayed relevance score within each status.
3. Under **Eligibility checker**, use PM Ujjwala with all fields blank to see the missing-information status. Enter age 17 and submit again to see the age condition fail.
4. Check **Compare schemes**, **Model performance** and **Applicant patterns**.
5. To capture screenshots for a report, press **Win+Shift+S** on each page and use fictional values in form screenshots.

## Scope and responsible use

The catalog has broad coverage. Rule checks, rankings and side-by-side comparisons
cover the three reviewed schemes. Confirm current requirements and eligibility
on the official portals. Machine learning ranks simplified initial matches and
the rule checker explains self-reported answers. There is no real applicant
validation or fairness certification. Gender is collected only to check PM
Ujjwala and excluded from training. The app does not request Aadhaar numbers,
account numbers or document uploads. Form inputs stay in the active session.

See [Curriculum mapping](docs/curriculum_mapping.md) for full unit coverage.