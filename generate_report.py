# ── PDF RAPORT ─────────────────────────────────────────────────────────
# Jooksuta alles PÄRAST kõigi eelnevate lahtrite täitmist!
# ─────────────────────────────────────────────────────────────────────────

from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, precision_recall_curve, average_precision_score
import os
import numpy as np

class Raport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(30, 30, 30)
        self.cell(0, 8, 'Krediitkaardi pettuste tuvastamine', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(0, 70, 127)
        self.set_line_width(0.5)
        self.line(8, 16, 202, 16)
        self.ln(1)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 8, f'Lehekülg {self.page_no()}', align='C')

    def section_title(self, text):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 70, 127)
        self.cell(0, 8, text, new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', size=10)
        self.set_text_color(30, 30, 30)

pdf = Raport()
pdf.set_margins(8, 8, 8)
pdf.set_auto_page_break(auto=True, margin=10)
pdf.add_page()

# ── 1. Probleemi kirjeldus ────────────────────────────────────────────────
pdf.section_title('1. Probleemi kirjeldus')
pdf.multi_cell(0, 6, (
    "Eesmärk: tuvastada pettuslikud krediitkaardi tehingud automaatselt masinõppe abil.\n"
    "Andmestik: 284 807 tehingut (september 2013), millest 492 (0.172%) on pettused.\n"
    "Tunnused V1-V28 on anonüümitud PCA komponendid. Time ja Amount on originaalsed.\n"
    "Peamine väljakutse: andmestik on tugevalt tasakaalustamata -- lahendus: SMOTE + AUPRC meetrika."
))
pdf.ln(2)

# ── 2. Andmestiku graafikud ───────────────────────────────────────────────
pdf.section_title('2. Andmestiku ülevaade')

fig, axes = plt.subplots(2, 2, figsize=(10, 6))

# Graafik 1: Klasside jaotus
df['Class'].value_counts().plot(kind='bar', ax=axes[0, 0], color=['steelblue', 'tomato'])
axes[0, 0].set_title('Klasside jaotus')
axes[0, 0].set_xlabel('Klass (0=normaalne, 1=pettus)')
axes[0, 0].set_ylabel('Arv')
axes[0, 0].tick_params(axis='x', rotation=0)

# Graafik 2: Tehingusumma boxplot klassi järgi (log-skaala)
import seaborn as sns
sns.boxplot(x='Class', y='Amount', data=df, ax=axes[0, 1],
            palette=['steelblue', 'tomato'])
axes[0, 1].set_yscale('log')
axes[0, 1].set_title('Tehingusumma klassi järgi (log-skaala)')
axes[0, 1].set_xlabel('Klass (0=normaalne, 1=pettus)')
axes[0, 1].set_ylabel('Summa (EUR, log)')
axes[0, 1].set_xticklabels(['Normaalne', 'Pettus'])

# Graafik 3: Top 10 tunnuse korrelatsioon klassiga (täislaius)
ax_bottom = plt.subplot2grid((2, 2), (1, 0), colspan=2, fig=fig)
corr_with_class.head(10).plot(kind='bar', ax=ax_bottom, color='steelblue')
ax_bottom.set_title('Top 10 tunnuse korrelatsioon klassiga')
ax_bottom.axhline(0, color='black', linewidth=0.8)
ax_bottom.set_xlabel('Tunnus')
ax_bottom.set_ylabel('Korrelatsioon')
ax_bottom.tick_params(axis='x', rotation=45)

axes[1, 0].set_visible(False)
axes[1, 1].set_visible(False)

plt.tight_layout()
plt.savefig('_g1.png', dpi=100)
plt.close()

pdf.image('_g1.png', w=175)
pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 5, 'Joonis 1: Klasside jaotus, tehingusumma jaotus ja top 10 tunnuse korrelatsioon', new_x='LMARGIN', new_y='NEXT')
pdf.set_font('Helvetica', size=9)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 6, (
    "Klasside jaotus on tugevalt tasakaalustamata -- 284 315 normaalset tehingut vs 492 pettust (0.172%).\n"
    "Pettuste tehingusummad on sarnase jaotusega normaalsete tehingutega -- summa üksi ei erista klasse.\n"
    "Tunnused V17, V14, V12 on tugevaima negatiivse korrelatsiooniga -- suured negatiivsed väärtused viitavad pettusele."
))
pdf.ln(2)

# ── 3. Mudelite tulemused ─────────────────────────────────────────────────
pdf.section_title('3. Mudelite baastulemused')

headers = ['Mudel', 'Precision', 'Recall', 'F1', 'AUPRC']
col_w = [65, 28, 28, 28, 28]

pdf.set_font('Helvetica', 'B', 10)
pdf.set_fill_color(0, 70, 127)
pdf.set_text_color(255, 255, 255)
for h, w in zip(headers, col_w):
    pdf.cell(w, 7, h, border=1, fill=True, align='C')
pdf.ln()

model_names = ['Logistic Regression', 'Random Forest', 'LightGBM']
colors = [(240,248,255), (255,255,255), (240,248,255)]
parim = tulemused_df['AUPRC'].idxmax()
pdf.set_text_color(30, 30, 30)
for name, bg in zip(model_names, colors):
    row = tulemused_df.loc[name]
    pdf.set_fill_color(200, 230, 200) if name == parim else pdf.set_fill_color(*bg)
    pdf.set_font('Helvetica', 'B' if name == parim else '', 10)
    pdf.cell(col_w[0], 7, name + (' *' if name == parim else ''), border=1, fill=True)
    pdf.set_font('Helvetica', size=10)
    for val, w in zip([row['Precision'], row['Recall'], row['F1'], row['AUPRC']], col_w[1:]):
        pdf.cell(w, 7, f'{val:.4f}', border=1, fill=True, align='C')
    pdf.ln()

pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(80, 80, 80)
pdf.multi_cell(0, 5, '* = parim AUPRC järgi. AUPRC = üldine hindamisnäitaja tasakaalustamata andmetel.')
pdf.ln(1)
pdf.set_font('Helvetica', size=9)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 6, (
    "Precision: kui mudel ütleb 'pettus', siis mitu % juhtumitest on tal õigus. "
    "LR 0.06 tähendab, et 94% häiretest on valed.\n"
    "Recall: mitu % tegelikest pettustest mudel tuvastab. Recall 0.81 -- 19 pettust 100-st jääb vahele.\n"
    "AUPRC: üldine hindamisnäitaja, lähem 1.0-le parem. "
    "Juhuslik ~0.002, RF saab 0.8275 -- kordades parem."
))
pdf.ln(2)

# ── 4. Häälestamise tulemused ─────────────────────────────────────────────
pdf.section_title('4. Parameetrite häälestamine')

try:
    pdf.set_font('Helvetica', size=10)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 6, (
        "RandomizedSearchCV abil otsiti iga mudeli jaoks paremad parameetrid.\n"
        "Häälestamine ei garanteeri alati paremat tulemust -- vt tulemused allpool."
    ))
    pdf.ln(1)

    headers2 = ['Mudel', 'AUPRC enne', 'AUPRC pärast', 'Muutus', 'Kasutada?']
    col_w2 = [55, 28, 28, 28, 38]
    tune_rows = [
        ('Logistic Regression', 0.7943, 0.7946, '+0.0003', 'Vaikimisi'),
        ('LightGBM', 0.7969, 0.3634, '-0.4335', 'Algne mudel'),
        ('Random Forest', 0.8275, 0.8249, '-0.0026', 'Vaikimisi'),
    ]

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(0, 70, 127)
    pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers2, col_w2):
        pdf.cell(w, 7, h, border=1, fill=True, align='C')
    pdf.ln()

    pdf.set_text_color(30, 30, 30)
    for name, enne, parast, muutus, kasuta in tune_rows:
        positiivne = muutus.startswith('+')
        pdf.set_fill_color(200, 230, 200) if positiivne else pdf.set_fill_color(255, 220, 220)
        pdf.set_font('Helvetica', size=10)
        pdf.cell(col_w2[0], 7, name, border=1, fill=True)
        pdf.cell(col_w2[1], 7, f'{enne:.4f}', border=1, fill=True, align='C')
        pdf.cell(col_w2[2], 7, f'{parast:.4f}', border=1, fill=True, align='C')
        pdf.cell(col_w2[3], 7, muutus, border=1, fill=True, align='C')
        pdf.cell(col_w2[4], 7, kasuta, border=1, fill=True, align='C')
        pdf.ln()

    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5, 'LightGBM halvenes häälestamisega -- üle sobitumise näide (üle sobitumine SMOTE andmetele).')
except Exception as e:
    pdf.multi_cell(0, 6, f'Häälestamise andmed pole saadaval. Jooksuta häälestamise lahter esmalt.')
pdf.ln(2)

# ── 5. Confusion Matrix ───────────────────────────────────────────────────
pdf.section_title('5. Confusion Matrix -- kõik mudelid')

fig, axes = plt.subplots(1, 3, figsize=(13, 3))
mudel_map = {'Logistic Regression': lr, 'Random Forest': rf, 'LightGBM': lgbm}
for ax, (name, mudel) in zip(axes, mudel_map.items()):
    cm = confusion_matrix(y_test, mudel.predict(X_test))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Normaalne', 'Pettus'])
    disp.plot(ax=ax, cmap='Blues', colorbar=False)
    ax.set_title(name)
plt.tight_layout()
plt.savefig('_g2.png', dpi=100)
plt.close()

pdf.image('_g2.png', w=175)
pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 5, 'Joonis 2: Confusion Matrix kõigi mudelite kohta', new_x='LMARGIN', new_y='NEXT')
pdf.ln(1)

# Kolme mudeli võrdlustabel
pdf.set_font('Helvetica', 'B', 10)
pdf.set_text_color(30, 30, 30)
pdf.cell(0, 7, 'Kolme mudeli võrdlus:', new_x='LMARGIN', new_y='NEXT')

cm_data = {}
for name, mudel in mudel_map.items():
    tn, fp, fn, tp = confusion_matrix(y_test, mudel.predict(X_test)).ravel()
    cm_data[name] = {'TN': tn, 'FP': fp, 'FN': fn, 'TP': tp}

headers3 = ['', 'Logistic Regression', 'Random Forest', 'LightGBM']
col_w3 = [52, 46, 46, 36]

pdf.set_font('Helvetica', 'B', 10)
pdf.set_fill_color(0, 70, 127)
pdf.set_text_color(255, 255, 255)
for h, w in zip(headers3, col_w3):
    pdf.cell(w, 7, h, border=1, fill=True, align='C')
pdf.ln()

rows_cm = [
    ('Õigesti normaalne (TN)', 'TN', True),
    ('Vale häire (FP)',         'FP', False),
    ('Märkamata pettus (FN)',   'FN', False),
    ('Tabatud pettus (TP)',     'TP', True),
]

pdf.set_text_color(30, 30, 30)
for label, key, hea in rows_cm:
    pdf.set_fill_color(220, 240, 220) if hea else pdf.set_fill_color(255, 220, 220)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(col_w3[0], 7, label, border=1, fill=True)
    pdf.set_font('Helvetica', size=10)
    for name, w in zip(mudel_map.keys(), col_w3[1:]):
        pdf.cell(w, 7, str(cm_data[name][key]), border=1, fill=True, align='C')
    pdf.ln()

pdf.ln(1)
pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(80, 80, 80)
pdf.multi_cell(0, 5, 'Roheline = soovitud tulemus. Punane = viga (FP = vale häire, FN = märkamata pettus).')
pdf.ln(2)

# ── 6. Läve optimeerimine ─────────────────────────────────────────────────
pdf.section_title('6. Äriline läve optimeerimine')
pdf.set_font('Helvetica', size=10)
pdf.set_text_color(30, 30, 30)
pdf.multi_cell(0, 6, (
    "Kogukulu = märkamata pettused x 122EUR + valed häired x 10EUR\n"
    "Optimaalne lävi minimeerib kogukulu valideerimisandmetel.\n"
    "NB: kulud (122EUR, 10EUR) on hinnangulised näidisväärtused -- indikatiivne analüüs."
))
pdf.ln(1)

headers4 = ['Mudel', 'Vaikimisi lävi 0.50', 'Optimaalne lävi', 'Min kulu', 'Kokkuhoid']
col_w4 = [45, 35, 32, 30, 35]
pdf.set_font('Helvetica', 'B', 10)
pdf.set_fill_color(0, 70, 127)
pdf.set_text_color(255, 255, 255)
for h, w in zip(headers4, col_w4):
    pdf.cell(w, 7, h, border=1, fill=True, align='C')
pdf.ln()

laev_data = [
    ('Logistic Regression', '10 618EUR', '0.99', '2 208EUR', '8 410EUR'),
    ('Random Forest',       '2 174EUR',  '0.21', '1 854EUR', '320EUR'),
    ('LightGBM',            '1 892EUR',  '0.79', '1 572EUR', '320EUR'),
]
kulude_arvud = [int(row[3].replace(' ', '').replace('EUR', '')) for row in laev_data]
min_kulu_idx = kulude_arvud.index(min(kulude_arvud))
pdf.set_text_color(30, 30, 30)
for i, (name, vaik, opt_laev, min_kulu, kokku) in enumerate(laev_data):
    pdf.set_fill_color(200, 230, 200) if i == min_kulu_idx else pdf.set_fill_color(240+i*5, 248, 255)
    pdf.set_font('Helvetica', 'B' if i == min_kulu_idx else '', 10)
    pdf.cell(col_w4[0], 7, name, border=1, fill=True)
    pdf.set_font('Helvetica', size=10)
    for val, w in zip([vaik, opt_laev, min_kulu, kokku], col_w4[1:]):
        pdf.cell(w, 7, val, border=1, fill=True, align='C')
    pdf.ln()
pdf.ln(1)
pdf.set_font('Helvetica', size=9)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 6, (
    "Lävi sõltub optimeerimise eesmärgist: F1-skoor (precision ja recall tasakaalus), "
    "äriline kulu (kogukulu minimaalne) või käsitsi PR kõvera järgi. "
    "Roheline = madalaim hinnanguline kulu. Õiglast lävi ei eksisteeri ilma ärilise kontekstita."
))
pdf.ln(2)

# ── PR kõver ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 3))
colors_pr = {'Logistic Regression': 'royalblue', 'Random Forest': 'forestgreen', 'LightGBM': 'tomato'}
mudel_map2 = {'Logistic Regression': lr, 'Random Forest': rf, 'LightGBM': lgbm}
for name, mudel in mudel_map2.items():
    y_prob = mudel.predict_proba(X_test)[:, 1]
    prec, rec, _ = precision_recall_curve(y_test, y_prob)
    ap = average_precision_score(y_test, y_prob)
    ax.plot(rec, prec, label=f'{name} (AUPRC={ap:.4f})', color=colors_pr[name], linewidth=2)
baseline = y_test.mean()
ax.axhline(baseline, color='gray', linestyle='--', label=f'Juhuslik (AUPRC={baseline:.4f})')
ax.set_xlabel('Recall (tuvastatud pettuste osakaal)')
ax.set_ylabel('Precision (täpsus)')
ax.set_title('Precision-Recall kõver -- kõik mudelid')
ax.legend(loc='upper right')
ax.set_xlim([0, 1])
ax.set_ylim([0, 1])
plt.tight_layout()
plt.savefig('_g3.png', dpi=100)
plt.close()

pdf.image('_g3.png', w=160)
pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 5, 'Joonis 3: Precision-Recall kõver -- mida kõrgem pind kõvera all, seda parem mudel', new_x='LMARGIN', new_y='NEXT')
pdf.set_font('Helvetica', size=9)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 6, (
    "Juhuslik mudel saaks AUPRC ainult 0.002 -- treenitud mudelid on kordades paremad.\n"
    "Random Forest (roheline) hoiab kõrgeima pinna all. LightGBM (punane) kukub madalale -- üle sobitumine."
))
pdf.ln(2)

# ── 7. Peamised järeldused ────────────────────────────────────────────────
# Kui järelejäänud ruum < 120mm, alusta uuelt lehelt
if pdf.get_y() > pdf.h - pdf.b_margin - 120:
    pdf.add_page()
pdf.section_title('7. Peamised järeldused ja tõlgendus')

top_rf   = pd.Series(rf.feature_importances_,   index=X_train.columns).nlargest(5).index.tolist()
top_lgbm = pd.Series(lgbm.feature_importances_, index=X_train.columns).nlargest(5).index.tolist()
yhised   = sorted(set(top_rf) & set(top_lgbm))
auprc_val     = tulemused_df['AUPRC'].max()
recall_val    = tulemused_df.loc[parim, 'Recall']
precision_val = tulemused_df.loc[parim, 'Precision']
baseline_auprc = y_test.mean()

pdf.set_font('Helvetica', size=9)
pdf.set_text_color(30, 30, 30)
pdf.multi_cell(0, 5.5, (
    f"1. Andmestik -- 284 807 tehingut, 492 pettust (0.172%). Tugevalt tasakaalustamata.\n"
    f"   Tõlgendus: juhuslik mudel saaks AUPRC={baseline_auprc:.4f} -- treenitud mudelid ületavad seda tulemust kordades.\n"
    f"2. Parim mudel -- {parim}: AUPRC={auprc_val:.4f}, Recall={recall_val:.4f}, Precision={precision_val:.4f}\n"
    f"   Tõlgendus: mudel tuvastab {recall_val*100:.0f}% pettustest. Iga 100 pettuseks märgitud tehingust on {precision_val*100:.0f}% tegelikult pettused.\n"
    f"3. Olulisemad tunnused -- mõlemas mudelis: {', '.join(yhised)}\n"
    f"   RF top 5: {', '.join(top_rf)} | LightGBM top 5: {', '.join(top_lgbm)}\n"
    f"   Tõlgendus: V14 ja V4 on tugevaimad pettuse indikaatorid -- mõlemad mudelid jõuavad samale järeldusele.\n"
    f"4. Eeltöötlus -- SMOTE lõi sünteetilisi pettuste näiteid väheesindatud klassi õppimiseks.\n"
    f"   Vaikimisi 0.5 lävega jääb palju pettusi märkamatuks (kõrge FN). Optimaalse lävega saab tasakaalu ärivajaduse järgi seada.\n"
    f"5. Häälestamine -- RF ei paranenud (-0.0026 AUPRC), LightGBM halvenes tugevalt (üle sobitumine SMOTE andmetele),\n"
    f"   LR ei muutunud -- lineaarne mudel on andmestiku keeruliste mustrite jaoks liiga lihtne."
))
pdf.ln(2)

# ── 8. Lõppsoovitus ───────────────────────────────────────────────────────
pdf.section_title('8. Lõppsoovitus')
pdf.set_font('Helvetica', size=10)
pdf.set_text_color(30, 30, 30)
pdf.multi_cell(0, 6, (
    "Parim mudel on Random Forest (AUPRC=0.8275): tuvastab 81% pettustest täpsusega 87%.\n"
    "Kulude analüüs (sektsioon 6) näitab potentsiaalset kokkuhoidu, kuid kulud (122EUR, 10EUR) "
    "on hinnangulised -- täpse soovituse saamiseks on vaja panga tegelikke andmeid.\n"
    "Edasised sammud: (1) hankida tegelikud FN/FP kulud, (2) korrata läve optimeerimist, "
    "(3) valida mudel ja lävi tulemuste põhjal, (4) testida reaalses keskkonnas."
))
pdf.ln(2)
pdf.set_font('Helvetica', 'B', 10)
pdf.set_fill_color(220, 235, 255)
pdf.set_text_color(0, 50, 100)
pdf.multi_cell(0, 8, "Kokkuvõte: Random Forest (AUPRC=0.8275) on tugevaim mudel. Äriline otsus sõltub tegelikest kuludest.", fill=True)
pdf.ln(3)
pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(80, 80, 80)
url = 'https://github.com/sergeierbin/creditcard-fraud-detection/blob/master/notebook.ipynb'
pdf.cell(0, 5, 'Täielik analüüs (Jupyter notebook): ' + url, link=url)

# ── Salvesta ja koristus ──────────────────────────────────────────────────
output = 'c:/Users/Administrator/creditcard/raport.pdf'
pdf.output(output)

for f in ['_g1.png', '_g2.png', '_g3.png']:
    if os.path.exists(f): os.remove(f)

print(f'Raport salvestatud: {output}')
