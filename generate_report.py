import json

code = '''from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

class Raport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, 'Krediitkaardi pettuste tuvastamine', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Lehekülg {self.page_no()}', align='C')

pdf = Raport()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# 1. Probleemi kirjeldus
pdf.set_font('Helvetica', 'B', 13)
pdf.set_text_color(0, 70, 127)
pdf.cell(0, 10, '1. Probleemi kirjeldus', new_x='LMARGIN', new_y='NEXT')
pdf.set_font('Helvetica', size=10)
pdf.set_text_color(30, 30, 30)
pdf.multi_cell(0, 7, (
    "Eesmark: tuvastada pettuslikud krediitkaardi tehingud automaatselt.\\n"
    "Andmestik: 284 807 tehingut (septembrist 2013), millest 492 (0.172%) on pettused.\\n"
    "Andmestik on tugevalt tasakaalustamata - peamine tehniline valjakutse.\\n"
    "Tunnused V1-V28 on anuumitud (PCA), Time ja Amount on originaalsed."
))
pdf.ln(3)

# 2. Olulisemad graafikud
pdf.set_font('Helvetica', 'B', 13)
pdf.set_text_color(0, 70, 127)
pdf.cell(0, 10, '2. Olulisemad graafikud', new_x='LMARGIN', new_y='NEXT')

fig, ax = plt.subplots(figsize=(5, 3))
df['Class'].value_counts().plot(kind='bar', ax=ax, color=['steelblue', 'tomato'])
ax.set_title('Klasside jaotus')
ax.set_xlabel('Klass (0=normaalne, 1=pettus)')
ax.set_ylabel('Arv')
ax.tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.savefig('_g1.png', dpi=100)
plt.close()

fig, ax = plt.subplots(figsize=(6, 3))
corr_with_class.head(10).plot(kind='bar', ax=ax, color='steelblue')
ax.set_title('Top 10 tunnuse korrelatsioon klassiga')
ax.axhline(0, color='black', linewidth=0.8)
plt.tight_layout()
plt.savefig('_g2.png', dpi=100)
plt.close()

pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 6, 'Joonis 1: Klasside jaotus', new_x='LMARGIN', new_y='NEXT')
pdf.image('_g1.png', w=90)
y_pos = pdf.get_y()
pdf.set_xy(105, y_pos - 55)
pdf.image('_g2.png', w=95)
pdf.ln(5)

# 3. Mudelite tulemused
pdf.set_font('Helvetica', 'B', 13)
pdf.set_text_color(0, 70, 127)
pdf.cell(0, 10, '3. Mudelite tulemuste tabel', new_x='LMARGIN', new_y='NEXT')

headers = ['Mudel', 'Precision', 'Recall', 'F1', 'AUPRC']
col_w = [60, 30, 30, 30, 30]

pdf.set_font('Helvetica', 'B', 10)
pdf.set_fill_color(0, 70, 127)
pdf.set_text_color(255, 255, 255)
for h, w in zip(headers, col_w):
    pdf.cell(w, 8, h, border=1, fill=True, align='C')
pdf.ln()

model_names = ['Logistic Regression', 'Random Forest', 'LightGBM']
colors = [(240,248,255), (255,255,255), (240,248,255)]
pdf.set_text_color(30, 30, 30)
for name, bg in zip(model_names, colors):
    row = tulemused_df.loc[name]
    pdf.set_fill_color(*bg)
    pdf.set_font('Helvetica', size=10)
    pdf.cell(col_w[0], 8, name, border=1, fill=True)
    for val, w in zip([row['Precision'], row['Recall'], row['F1'], row['AUPRC']], col_w[1:]):
        pdf.cell(w, 8, f'{val:.4f}', border=1, fill=True, align='C')
    pdf.ln()

pdf.ln(5)

# 4. Peamised jareldused
pdf.set_font('Helvetica', 'B', 13)
pdf.set_text_color(0, 70, 127)
pdf.cell(0, 10, '4. Peamised jareldused', new_x='LMARGIN', new_y='NEXT')
pdf.set_font('Helvetica', size=10)
pdf.set_text_color(30, 30, 30)

parim = tulemused_df['AUPRC'].idxmax()
auprc_val = tulemused_df['AUPRC'].max()
recall_val = tulemused_df.loc[parim, 'Recall']
precision_val = tulemused_df.loc[parim, 'Precision']

pdf.multi_cell(0, 7, (
    f"Parim mudel: {parim} (AUPRC={auprc_val:.4f})\\n"
    f"  - Tabab {recall_val*100:.1f}% tegelikest pettustest\\n"
    f"  - {precision_val*100:.1f}% pettuseks margitud tehingutest on tegelikult pettused\\n\\n"
    "Olulisemad tunnused: V14, V4, V12, V17 (molemal mudelil yhised)\\n\\n"
    "Suurim valjakutse: klasside tasakaalustamatus (0.172% pettusi)\\n"
    "Lahendus: SMOTE + AUPRC meetrika (mitte tavaline tapsus)\\n\\n"
    "Ariline moju: Random Forest optimaalse lavega (0.34) saastab ~612 eurot\\n"
    "vorreldus vaikimisi lavega (0.5)."
))

output = 'c:/Users/Administrator/creditcard/raport.pdf'
pdf.output(output)

for f in ['_g1.png', '_g2.png']:
    if os.path.exists(f): os.remove(f)

print(f"Raport salvestatud: {output}")
'''

with open('c:/Users/Administrator/creditcard/notebook.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

nb['cells'].append({
    'cell_type': 'markdown',
    'id': 'raport_md',
    'metadata': {},
    'source': ['## Raport (PDF)']
})

nb['cells'].append({
    'cell_type': 'code',
    'id': 'raport_code',
    'metadata': {},
    'outputs': [],
    'execution_count': None,
    'source': [code]
})

with open('c:/Users/Administrator/creditcard/notebook.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print('Lisatud notebook.ipynb-i')
