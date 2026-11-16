# Saison-Themes für Home Assistant

Saisonale Themes mit eigener Primärfarbe und Hintergrundbild, die sich automatisch nach einstellbaren Zeiträumen umschalten. Gedacht für Wand-Dashboards wie das Shelly Wall Display, funktioniert aber in jedem Home-Assistant-Frontend.

Enthaltene Themes:

| Theme | Standard-Zeitraum | Primärfarbe |
|---|---|---|
| Saison Halloween | 15.10. bis 02.11. | Kürbis-Orange |
| Saison Weihnachten | 30.11. bis 06.01. | Weihnachtsrot |
| Saison Silvester | 31.12. | Champagner-Gold |
| Saison Ostern | 14 Tage vor bis 7 Tage nach Ostersonntag (automatisch berechnet) | Frühlingsgrün |
| Saison Geburtstag | an jedem eingetragenen Geburtstag | Himbeer-Pink |
| Saison Standard | außerhalb aller Zeiträume | frei wählbar |

Bei Überschneidungen gilt: Geburtstag, Silvester, Halloween, Weihnachten, Ostern.

## Installation über HACS

1. HACS öffnen, oben rechts auf die drei Punkte und dann auf **Benutzerdefinierte Repositories**.
2. `https://github.com/yannick80/ha_saison_themes` eintragen, Typ **Integration**, hinzufügen.
3. **Saison-Themes** suchen und herunterladen.
4. Home Assistant neu starten.
5. **Einstellungen → Geräte & Dienste → Integration hinzufügen → Saison-Themes**.

## Einrichtung

Die Integration legt die Datei `themes/saison_themes.yaml` in deinem Konfigurationsordner an und lädt die Themes über den offiziellen Dienst `frontend.reload_themes`. Damit das funktioniert, muss deine `configuration.yaml` den Ordner `themes` einlesen. Bei neueren Installationen ist das meist schon der Fall:

```yaml
frontend:
  themes: !include_dir_merge_named themes
```

Fehlt die Zeile, erscheint unter **Einstellungen → Reparaturen** ein Hinweis.

Auf jedem Dashboard-Gerät einmal das Profil öffnen (unten links auf den Benutzernamen) und das Theme auf **Backend-ausgewählt** stellen. Nur dann übernimmt das Gerät das automatisch gesetzte Theme.

## Einstellungen

**Einstellungen → Geräte & Dienste → Saison-Themes → Konfigurieren**

- Primärfarbe für jedes Theme
- Zeiträume für Halloween, Weihnachten und Silvester im Format `TT.MM` (dürfen über den Jahreswechsel gehen)
- Tage vor und nach Ostersonntag
- Geburtstage, z. B. `Anna 14.03, Ben 02.07` (Name optional, 29.02. wird in Nicht-Schaltjahren am 28.02. gefeiert)
- Jedes Theme lässt sich einzeln deaktivieren

## Entitäten

| Entität | Bedeutung |
|---|---|
| `select.saison_themes_modus` | Automatisch oder ein Theme fest erzwingen |
| `sensor.saison_themes_aktive_saison` | Aktive Saison, Attribut `theme` mit dem Theme-Namen |
| `sensor.saison_themes_geburtstag_heute` | Wer heute Geburtstag hat, sonst `keiner` |
| `sensor.saison_themes_ostersonntag` | Ostersonntag des aktuellen Jahres |

Die Entity-IDs hängen von der Sprache bei der Einrichtung ab.

## Umstieg vom YAML-Paket

Wer vorher das YAML-Paket genutzt hat, entfernt es, damit sich beides nicht in die Quere kommt:

- `packages/saison_themes.yaml`
- `themes/saison.yaml`
- optional `www/themes/*.svg`

Danach Home Assistant neu starten. Die Einträge unter `homeassistant: packages:` und `frontend: themes:` in der `configuration.yaml` können bleiben.

## Deinstallation

Beim Löschen der Integration wird `themes/saison_themes.yaml` wieder entfernt und Home Assistant fällt auf das Standard-Theme zurück.
