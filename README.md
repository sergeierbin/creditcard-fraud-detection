# Krediitkaardi pettuste tuvastamine

Masinõppe projekt, mis tuvastab pettuslikke krediitkaardi tehinguid automaatselt.

## Projekti failid

| Fail | Kirjeldus |
|------|-----------|
| [notebook.ipynb](notebook.ipynb) | Põhianalüüs koos tulemustega (EDA, mudelid, graafikud) |
| [raport.pdf](raport.pdf) | Lühike PDF-kokkuvõte (2 lk) |
| [generate_report.py](generate_report.py) | PDF-raporti generaator |

## Projekti kirjeldus

Andmestik sisaldab **284 807 tehingut** (september 2013), millest ainult **0,172% on pettused** — see teeb ülesande keeruliseks, sest andmestik on tugevalt tasakaalustamata.

Mudel vaatab iga tehingut ja vastab küsimusele: **kas see tehing on pettus või normaalne?**

## Mudelid

| Mudel | Põhimõte |
|-------|----------|
| Logistic Regression | Lihtne baasmudel — arvutab iga tunnuse kaalu |
| Random Forest | Palju otsusepuid koos — stabiilne ja täpne |
| LightGBM | Kiire gradient boosting — parim tulemus |

## Peamised tulemused

- **Parim mudel:** Random Forest / LightGBM (AUPRC > 0.85)
- **Meetrika:** AUPRC (mitte accuracy) — sobib tasakaalustamata andmetele
- **Klasside tasakaalustamine:** SMOTE (sünteetilised näited treeningandmetesse)
- **Läve optimeerimine:** F1-põhine ja kulupõhine (FN=122€, FP=10€)

## Andmestik

Andmestik pole repasse lisatud (liiga suur). Lae alla Kaggle'ist:

[Credit Card Fraud Detection — Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)

Pane `creditcard.csv` projekti kausta ja käivita notebook.

## Käivitamine

```bash
pip install pandas numpy matplotlib seaborn scikit-learn lightgbm imbalanced-learn fpdf2
jupyter notebook notebook.ipynb
```

## Tehnoloogiad

`Python` `pandas` `scikit-learn` `LightGBM` `imbalanced-learn` `matplotlib` `seaborn` `fpdf2`
