"""
Steuerrechner (Kanton Solothurn)

"""

import sys
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from datetime import datetime
except Exception as e:
    print("Fehlende Bibliotheken oder Import-Fehler:", e)
    print("Bitte installiere: pandas, matplotlib, openpyxl")
    raise


# Relligion und Kirchensteuer

list_religion = ["Römisch-katholisch", "Reformiert", "Christkatholisch", "Andere/Keine"]
list_zivilstand = ["Ledig", "Verheiratet", "eingetragene Partnerschaft", "Konkubinat"]

kirchensteuer_saetze = {
    "Römisch-katholisch": 0.12,
    "Reformiert": 0.10,
    "Christkatholisch": 0.08,
    "Andere/Keine": 0.0,
}

# Steuerfunktionen

def kantonssteuer_solothurn(einkommen, kinder):
    """Kanton Solothurn: Kinderabzug 9'000 CHF pro Kind"""
    e = max(0, einkommen - kinder * 9000)
    if e > 310000:
        return e * 0.115
    stufen = [(12000, 0), (4000, 0.045), (4000, 0.05), (3000, 0.065),
        (2000, 0.08), (3000, 0.09), (11000, 0.095), (15000, 0.1),
        (44000, 0.105), (212000, 0.115)]
    steuer = 0
    for b, s in stufen:
        if e <= 0:
            break
        t = min(e, b)
        steuer += t * s
        e -= t
    return steuer

def bundessteuer(e, zivilstand, kinder):
    """Bundessteuer (vereinfachter Tarif)"""
    e = max(0, e - kinder * 6600)
    tarif = [(18500, 0, 0), (33200, 0, 0.0077), (43500, 138.6, 0.0088),
        (58000, 229.2, 0.0264), (76100, 612, 0.0297),
        (82000, 1149.55, 0.0594), (108800, 1500, 0.066),
        (141500, 3268.8, 0.088), (184900, 6146.4, 0.11),
        (793400, 10920.4, 0.132),]
    x = e if zivilstand == "Ledig" else e / 2
    steuer = 0
    for g, b, s in tarif:
        if x <= g:
            prev = tarif[tarif.index((g, b, s)) - 1][0] if tarif.index((g, b, s)) > 0 else 18500
            steuer = b + (x - prev) * s
            break
    else:
        steuer = x * 0.115
    if zivilstand != "Ledig":
        steuer *= 2
    return max(steuer, 0)


# Excel Loader

def lade_gemeindesteuern_dialog():
    """Öffnet Dialog, liest Excel ein, gibt dict zurück: {Gemeinde: Steuerfuss}"""
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(
        title="Bitte Gemeindesteuer-Excel auswählen",
        filetypes=[("Excel Dateien", "*.xlsx *.xls")]
    )
    if not filename:
        raise FileNotFoundError("Keine Datei gewählt.")

    df_raw = pd.read_excel(filename, header=None)
    
    if df_raw.shape[0] < 4:
        raise ValueError("Excel-Datei scheint nicht die erwartete Struktur zu haben (zu wenige Zeilen).")
    headers_row_idx = 2 if df_raw.shape[0] > 3 else 0
    headers = df_raw.iloc[headers_row_idx].tolist()
 
    clean_headers = []
    for i, h in enumerate(headers):
        if pd.isna(h):
            clean_headers.append(f"col{i}")
        else:
            clean_headers.append(str(h).strip())
    df_raw.columns = clean_headers
  
    df = df_raw.iloc[headers_row_idx + 1 :].reset_index(drop=True)
    
    gemeinde_col = None
    for col in df.columns:
        
        if df[col].dtype == object or df[col].apply(lambda x: isinstance(x, str)).all():
           
            if df[col].dropna().astype(str).str.strip().replace("", pd.NA).dropna().shape[0] > 0:
                gemeinde_col = col
                break
    steuer_col = None
    for col in df.columns:
        
        try:
            col_series = pd.to_numeric(df[col], errors='coerce').dropna()
            if not col_series.empty and col_series.max() < 2000:
                steuer_col = col
                break
        except Exception:
            continue
    if gemeinde_col is None or steuer_col is None:
        
        if len(df.columns) >= 3:
            gemeinde_col = df.columns[0]
            steuer_col = df.columns[2]
        else:
            raise ValueError("Konnte Gemeinde- oder Steuerfuss-Spalte nicht erkennen.")
    # Bereinige Gemeindennamen
    def clean_name(n):
        s = str(n).strip()
        # z.B. Aeschi (SO) -> Aeschi
        if s.endswith(" (SO)"):
            s = s.rsplit(" (SO)", 1)[0].strip()
        return s
    gemeinde_steuern = {}
    for _, row in df.iterrows():
        name = row.get(gemeinde_col)
        val = row.get(steuer_col)
        if pd.isna(name) or pd.isna(val):
            continue
        try:
            name_clean = clean_name(name)
            val_int = int(float(val))
            gemeinde_steuern[name_clean] = val_int
        except Exception:
            
            continue
    if not gemeinde_steuern:
        raise ValueError("Keine gültigen Gemeinde- / Steuerfuss-Daten gefunden.")
    # Normalisierte Suche
    normalised = {k.lower(): k for k in gemeinde_steuern.keys()}
    return gemeinde_steuern, normalised


# GUI Aufbau

class SteuerApp:
    def __init__(self, master):
        self.master = master
        master.title("Steuerrechner - Kanton Solothurn")
        master.geometry("900x700")

        # Variablen
        self.gemeinden = {}
        self.normalised = {}
        self.selected_gemeinde = tk.StringVar()
        self.name_var = tk.StringVar()
        self.geb_var = tk.StringVar()
        self.religion_var = tk.StringVar(value=list_religion[0])
        self.ziv_var = tk.StringVar(value=list_zivilstand[0])
        self.kinder_var = tk.IntVar(value=0)
        self.gehalt_var = tk.StringVar(value="0")
        self.km_var = tk.StringVar(value="0")
        # Widgets
        top = ttk.Frame(master, padding=10)
        top.pack(fill="x")

        btn_load = ttk.Button(top, text="Excel laden (Gemeinden)", command=self.load_excel)
        btn_load.grid(row=0, column=0, padx=5, sticky="w")

        ttk.Label(top, text="Name:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(top, textvariable=self.name_var, width=25).grid(row=1, column=1, sticky="w")

        ttk.Label(top, text="Geburtstag (TT.MM.JJJJ):").grid(row=2, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.geb_var, width=20).grid(row=2, column=1, sticky="w")

        ttk.Label(top, text="Gemeinde:").grid(row=3, column=0, sticky="w", pady=4)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top, textvariable=self.search_var, width=30)
        search_entry.grid(row=3, column=1, sticky="w")
        search_entry.bind("<KeyRelease>", self.update_suggestions)

        self.listbox = tk.Listbox(top, height=6, width=40)
        self.listbox.grid(row=4, column=0, columnspan=2, sticky="w")
        self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        ttk.Label(top, text="Religion:").grid(row=1, column=2, sticky="w")
        ttk.Combobox(top, values=list_religion, state="readonly", textvariable=self.religion_var).grid(row=1, column=3, sticky="w")

        ttk.Label(top, text="Zivilstand:").grid(row=2, column=2, sticky="w")
        ttk.Combobox(top, values=list_zivilstand, state="readonly", textvariable=self.ziv_var).grid(row=2, column=3, sticky="w")

        ttk.Label(top, text="Kinder:").grid(row=3, column=2, sticky="w")
        ttk.Spinbox(top, from_=0, to=10, textvariable=self.kinder_var, width=5).grid(row=3, column=3, sticky="w")

        ttk.Label(top, text="Nettojahresgehalt (CHF):").grid(row=5, column=0, sticky="w", pady=6)
        ttk.Entry(top, textvariable=self.gehalt_var, width=20).grid(row=5, column=1, sticky="w")

        ttk.Label(top, text="Pendeldistanz einfach (km):").grid(row=6, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.km_var, width=10).grid(row=6, column=1, sticky="w")

        btn_calc = ttk.Button(top, text="Berechnen", command=self.berechnen)
        btn_calc.grid(row=7, column=0, pady=10, sticky="w")

        btn_clear = ttk.Button(top, text="Zurücksetzen", command=self.reset_fields)
        btn_clear.grid(row=7, column=1, sticky="w", padx=6)

        # Ergebnis-Frame
        bottom = ttk.Frame(master, padding=10)
        bottom.pack(fill="both", expand=True)

        self.result_box = tk.Text(bottom, height=10, font=("Courier", 11))
        self.result_box.pack(fill="x", pady=(0,10))

        # Diagramm-Canvas
        self.fig = plt.Figure(figsize=(5,4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=bottom)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Status
        self.status = ttk.Label(master, text="Bitte Excel laden (Knopf oben).", relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")


    # Funktionen GUI
 
    def load_excel(self):
        try:
            gemeinden, normalised = lade_gemeindesteuern_dialog()
            # sortiere alphabetisch
            self.gemeinden = dict(sorted(gemeinden.items(), key=lambda x: x[0].lower()))
            self.normalised = normalised
            self.update_listbox(list(self.gemeinden.keys()))
            self.status.config(text=f"{len(self.gemeinden)} Gemeinden geladen.")
        except Exception as e:
            messagebox.showerror("Fehler beim Laden", str(e))
            self.status.config(text="Fehler beim Laden der Excel-Datei.")

    def update_listbox(self, items):
        self.listbox.delete(0, tk.END)
        for it in items:
            self.listbox.insert(tk.END, it)

    def update_suggestions(self, event=None):
        q = self.search_var.get().strip().lower()
        if not q:
            self.update_listbox(list(self.gemeinden.keys()))
            return
        matches = [g for g in self.gemeinden.keys() if q in g.lower()]
        self.update_listbox(matches[:200])  # safety cap

    def on_listbox_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        val = self.listbox.get(sel[0])
        self.selected_gemeinde.set(val)
       
        self.search_var.set(val)

    def validate_name(self, s):
        return s.strip().isalpha() and len(s.strip()) >= 2

    def berechnen(self):
        # Validierung
        name = self.name_var.get().strip()
        if not name.isalpha() or len(name) < 3:
            messagebox.showerror(
                "Fehler",
                "Name muss mindestens 3 Buchstaben lang sein und darf nur Buchstaben enthalten."
            )
            return
        
        geb = self.geb_var.get().strip()
        gemeinde_input = self.search_var.get().strip()
        try:
            geb_d = datetime.strptime(geb, "%d.%m.%Y")
            alter = datetime.now().year - geb_d.year - ((datetime.now().month, datetime.now().day) < (geb_d.month, geb_d.day))
        except Exception:
            messagebox.showerror("Fehler", "Geburtsdatum ungültig. Format TT.MM.JJJJ")
            return

        if not gemeinde_input:
            messagebox.showerror("Fehler", "Bitte Gemeinde wählen.")
            return

        # Gemeinde lookup (normalize)
        key = gemeinde_input.strip().lower()
        if key in self.normalised:
            gemeinde = self.normalised[key]
            steuerfuss = self.gemeinden[gemeinde]
        else:
            messagebox.showerror("Fehler", "Gemeinde nicht in Liste gefunden.")
            return

        try:
            gehalt = float(self.gehalt_var.get().replace(",", "."))
            km = float(self.km_var.get().replace(",", "."))
        except Exception:
            messagebox.showerror("Fehler", "Bitte Zahlen korrekt eingeben (Gehalt, km).")
            return
        
        if gehalt < 0:
            messagebox.showerror("Fehler", "Das Einkommen darf nicht negativ sein.")
            return

        if km < 0:
            messagebox.showerror("Fehler", "Die Pendeldistanz darf nicht negativ sein.")
            return

        religion = self.religion_var.get()
        ziv = self.ziv_var.get()
        kinder = int(self.kinder_var.get())

        krankenkassen_abzug = 1700 if ziv in ["Ledig", "Konkubinat"] else 3500
        pendlerabzug = min(km * 2 * 220 * 0.7, 7000)
        steuerbares = max(0, gehalt - (krankenkassen_abzug + pendlerabzug))

        kanton = kantonssteuer_solothurn(steuerbares, kinder) * 1.04
        gemeindesteuer = kantonssteuer_solothurn(steuerbares, kinder) * (steuerfuss / 100)
        kirchensteuer = 0 if religion == "Andere/Keine" else gemeindesteuer * kirchensteuer_saetze[religion]
        bundes = bundessteuer(steuerbares, ziv, kinder)
        gesamt = kanton + gemeindesteuer + kirchensteuer + bundes

        # Ausgabe
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, f"Name: {name}\n")
        self.result_box.insert(tk.END, f"Alter: {alter}\n")
        self.result_box.insert(tk.END, f"Wohngemeinde: {gemeinde} (Steuerfuss {steuerfuss}%)\n")
        self.result_box.insert(tk.END, f"Zivilstand: {ziv}\n")
        self.result_box.insert(tk.END, f"Religion: {religion}\n")
        self.result_box.insert(tk.END, f"Nettojahresgehalt: CHF {gehalt:,.2f}\n")
        self.result_box.insert(tk.END, f"Pendlerabzug: CHF {pendlerabzug:,.2f} (max 7'000)\n")
        self.result_box.insert(tk.END, f"Kinder: {kinder}\n")
        self.result_box.insert(tk.END, "-" * 40 + "\n")
        self.result_box.insert(tk.END, f"Gemeindesteuer:  CHF {gemeindesteuer:,.2f}\n")
        self.result_box.insert(tk.END, f"Kantonssteuer:   CHF {kanton:,.2f}\n")
        self.result_box.insert(tk.END, f"Bundessteuer:    CHF {bundes:,.2f}\n")
        self.result_box.insert(tk.END, f"Kirchensteuer:   CHF {kirchensteuer:,.2f}\n")
        self.result_box.insert(tk.END, "-" * 40 + "\n")
        self.result_box.insert(tk.END, f"GESAMTSTEUER:    CHF {gesamt:,.2f}\n")
        self.result_box.insert(tk.END, "-" * 40 + "\n")

        # Diagramm zeichnen
        self.zeichne_diagramm(gemeindesteuer, kanton, bundes, kirchensteuer)

    def zeichne_diagramm(self, g, k, b, ki):
        self.ax.clear()
        labels = ["Gemeinde", "Kanton", "Bund", "Kirche"]
        values = [g if g>0 else 0.001, k if k>0 else 0.001, b if b>0 else 0.001, ki if ki>0 else 0.001]
        self.ax.pie(values, labels=labels, autopct="%1.1f%%")
        self.ax.set_title("Steuerverteilung")
        self.canvas.draw()

    def reset_fields(self):
        self.name_var.set("")
        self.geb_var.set("")
        self.search_var.set("")
        self.update_listbox(list(self.gemeinden.keys()) if self.gemeinden else [])
        self.religion_var.set(list_religion[0])
        self.ziv_var.set(list_zivilstand[0])
        self.kinder_var.set(0)
        self.gehalt_var.set("0")
        self.km_var.set("0")
        self.result_box.delete("1.0", tk.END)
        self.ax.clear()
        self.canvas.draw()
        self.status.config(text="Zurückgesetzt.")


# App starten

def main():
    root = tk.Tk()
    app = SteuerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
