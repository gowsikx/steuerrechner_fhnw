\# Steuerrechner – Kanton Solothurn

# Interaktive Steuerberechnung

## 📝 Analyse

**Problem**


Viele Steuerzahler wissen nicht genau, wie hoch ihre Abgaben an Gemeinde, Kanton, Bund oder Religionsgemeinschaft sind. Die Berechnung erfolgt oft manuell mit Tabellen oder groben Schätzungen, was zu Fehlern und Unsicherheiten führt. Unterschiedliche Steuerarten (Gemeinde, Kanton, Bund, Religion) machen die Übersicht besonders schwierig.

Bisher fehlte eine einfache, interaktive Möglichkeit, Steuerberechnungen direkt einzugeben, zu sehen und bei Bedarf zu speichern (z. B. in einer GUI). Das erschwert die langfristige Finanzplanung, da Nutzer jedes Jahr ihre Berechnungen wiederholen müssen.

**Ziel**


Die Anwendung MeineSteuer soll Nutzern ermöglichen, ihre Steuerlast einfach zu berechneN und eine Übersicht für Gemeinde-, Kanton-, Bundes- und Religionssteuer zu erhalten.

**Scenario**

Der Nutzer gibt seine persönlichen Daten ein (Geburtsdatum, Religion, Wohnort) und erhält eine Übersicht seiner Steuerlast nach Kategorien. Alle Berechnungen erfolgen interaktiv in der GUI.

**User stories:**
1. Als User möchte ich wissen, wie viel meine Gemeinde-Steuern sind.
2. Als User möchte ich wissen, wie viel meine Bundes-Steuern sind.
3. Als User möchte ich wissen, wie viel meine Kanton-Steuern sind.
4. Als User möchte ich meine Religion auswählen.
5. Als User möchte ich wissen, wie hoch meine Religionssteuer ist.
6. Als User möchte ich wissen, wie hoch meine Gesamtsteuerlast pro Jahr ist.
7. Als User möchte ich mein Geburtsdatum eingeben.
8. Als User möchte ich haben, dass ein Alter automatisch berechnet wird und im PDF sichtbar ist.
9. Als User möchte ich eine einfache Desktop-GUI verwenden,
um meine Daten bequem eingeben und Ergebnisse direkt sehen zu können.

**Use cases:**
- Kanton anzeigen (aus .csv)
- Gemeinde anzaigen
- Religion anzeigen
- Aktuelle Steuerberechnung und Total anzeigen

---

## ✅ Projektanforderungen

Jede App muss die folgenden drei Kriterien erfuellen, um akzeptiert zu werden (vgl. Projektrichtlinien auf Moodle):

- Interaktive App (Konsole oder GUI)
- Datenvalidierung (z. B. Eingaben pruefen)
- Dateiverarbeitung (Lesen/Schreiben)
---

### 1. Interaktive App
 
---

Die Anwendung interagiert über Konsole oder eine GUI mit den Nutzern. 
- Steuerwerte für Gemeinde, Kanton, Bund und Religion eingeben/auswählen
- Geburtsdatum eingeben → Alter wird berechnet
- Steuerübersicht anzeigen

---

### 2. Datenvalidierung

Alle Eingaben werden überprüft, um Fehler zu vermeiden:
- Numerische Eingaben: nur gültige Zahlen akzeptieren
- Geburtsdatum: korrekte Eingabe prüfen
- Religion: aus vorgegebener Liste auswählen


### 3. Dateiverarbeitung

Eingabedateien:
- gemeinde.txt (Gemeinden)

## ⚙️ Implementation

### Technology
- Python 3.x
- Environment: GitHub Codespaces
- Bibliothek fuer PDF-Erstellung: reportlab

### 📂 Repository Structure
```text
MeineSteuer/
├── main.py             # Hauptlogik (Konsole + GUI)
├── religion.txt        # Eingabedatei Religionen
└── README.md           # Projektdoku

```

## 👥 Team & Beiträge


| Name           | Aufgabeverteilung                                              |
|----------------|----------------------------------------------                  |
| Arti Rechi     | Implementierung und Entwicklung der GUI                        |
| Gowsi Kanesan  | Implementierung der Berechnungslogik und Steuerformeln         |
| Rusa Kandiah   | Auswahl der Steuersätze und umfassende Softwaretest            |


## Beiträge
- Repository importieren und in eigenem Fork arbeiten
- Regelmässig committen, um Fortschritte zu dokumentieren
- Änderungen nur im eigenen Fork pushen

## 📝 License

This project is provided for **educational use only** as part of the Programming Foundations module.  
[MIT License](LICENSE)



