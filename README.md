<p align="center">
  <a href="https://my.home-assistant.io/redirect/marketplace_repository/?owner=yannick80&repository=ha-saison-themes&category=integration">
    <img alt="Open in the Home Assistant Marketplace" src="https://my.home-assistant.io/badges/marketplace_repository.svg"/>
  </a>
</p>
<p align="center">
  <a href="https://github.com/yannick80/ha-saison-themes/releases/latest">
    <img alt="Latest release" src="https://img.shields.io/github/v/release/yannick80/ha-saison-themes?label=release"/>
  </a>
  <a href="https://www.home-assistant.io">
    <img alt="HA 2025.1+" src="https://img.shields.io/badge/HA-2025.1%2B-blue.svg"/>
  </a>
  <a href="https://github.com/yannick80/ha-saison-themes/actions/workflows/validate.yml">
    <img alt="Validate" src="https://img.shields.io/github/actions/workflow/status/yannick80/ha-saison-themes/validate.yml?branch=main&label=validate"/>
  </a>
  <a href="LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/yannick80/ha-saison-themes.svg"/>
  </a>
</p>

# Saison-Themes

Saison-Themes gives your Home Assistant dashboards a seasonal look: each season has its own primary colour and background image, and Home Assistant switches between them on its own, based on date ranges you can change.
Made for wall dashboards such as the Shelly Wall Display, but it works in every Home Assistant frontend.

<!-- ha-marketplace:exclude-start -->
**Contents:**
[What you get](#what-you-get) ·
[Before you start](#before-you-start) ·
[Installation](#installation) ·
[Set up](#set-up) ·
[Options](#options) ·
[Entities](#entities) ·
[Troubleshooting & FAQ](#troubleshooting--faq) ·
[For developers](#for-developers)
<!-- ha-marketplace:exclude-end -->

## What you get

- **Six themes that switch by themselves:**

  | Theme | Default period | Primary colour |
  |---|---|---|
  | Saison Halloween | 15 Oct to 2 Nov | pumpkin orange |
  | Saison Weihnachten (Christmas) | 30 Nov to 6 Jan | Christmas red |
  | Saison Silvester (New Year's Eve) | 31 Dec | champagne gold |
  | Saison Ostern (Easter) | 14 days before to 7 days after Easter Sunday, calculated every year | spring green |
  | Saison Geburtstag (Birthday) | on every birthday you enter | raspberry pink |
  | Saison Standard | outside all periods | your choice |

  When periods overlap, the first one wins: Birthday, New Year's Eve, Halloween, Christmas, Easter.
- **Everything in the user interface.** Colours, periods and birthdays are set under **Configure**; no YAML to edit.
- **A mode switch** to keep one theme for a while, for example for a party.
- **Sensors** for the active season, today's birthday and this year's Easter Sunday, for your own automations.
- **Cleans up after itself.** Removing the integration also removes its theme file.
- **English and German** user interface.

## Before you start

- [ ] **Home Assistant 2025.1 or newer.**
- [ ] **Your `configuration.yaml` loads the `themes` folder.** Newer installations usually have this already:

  ```yaml
  frontend:
    themes: !include_dir_merge_named themes
  ```

  If the line is missing, the integration tells you under **Settings** > **Repairs**.

<!-- ha-marketplace:exclude-start -->
## Installation

### Home Assistant 2026.11 and newer (Marketplace)

**One click:** select this button, then confirm in your Home Assistant.

[![Open Marketplace repository on My Home Assistant](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=yannick80&repository=ha-saison-themes&category=integration)

**Or by hand:**

1. In Home Assistant, go to **Settings** > **Marketplace**.
2. In the upper-right corner, select **Add from link**.
3. Under **GitHub link**, enter `https://github.com/yannick80/ha-saison-themes`. If Home Assistant asks for the type, choose **Integration**.
4. Open Saison-Themes and select **Install**.
5. Restart Home Assistant.

### Home Assistant 2026.10 and older (HACS)

[![Open in HACS on My Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=yannick80&repository=ha-saison-themes&category=integration)

1. Open **HACS** in the sidebar.
2. Select the three dots in the upper-right corner, then **Custom repositories**.
3. Enter `https://github.com/yannick80/ha-saison-themes`, choose the type **Integration**, and select **Add**.
4. Open Saison-Themes and select **Download**.
5. Restart Home Assistant.

### Manual installation

1. Download the source code of this repository.
2. Copy the folder `custom_components/saison_themes` to `config/custom_components/` (create the folder if it does not exist).
3. Restart Home Assistant.
<!-- ha-marketplace:exclude-end -->

## Set up

1. Go to **Settings** > **Devices & services** > **Add integration** and search for **Saison-Themes**.
   The integration writes `themes/saison_themes.yaml` into your configuration folder and reloads the themes.
2. On **every dashboard device**, open your profile (your user name at the bottom left) and set the theme to **Backend-selected**.
   Only then does the device follow the theme the integration sets.

## Options

**Settings** > **Devices & services** > **Saison-Themes** > **Configure**:

- the primary colour of every theme;
- the periods for Halloween, Christmas and New Year's Eve, as `DD.MM` (they may span the turn of the year);
- the days before and after Easter Sunday;
- birthdays, for example `Anna 14.03, Ben 02.07` (the name is optional; 29.02 is celebrated on 28.02 in non-leap years);
- every theme can be turned off on its own.

## Entities

| Entity | Meaning |
|---|---|
| `select.saison_themes_mode` | *Automatic*, or keep one theme |
| `sensor.saison_themes_active_season` | the active season; attribute `theme` holds the theme name |
| `sensor.saison_themes_birthday_today` | whose birthday it is today |
| `sensor.saison_themes_easter_sunday` | Easter Sunday of the current year |

The entity IDs depend on the language Home Assistant had when you set up the integration; in German they are `select.saison_themes_modus`, `sensor.saison_themes_aktive_saison`, `sensor.saison_themes_geburtstag_heute` and `sensor.saison_themes_ostersonntag`.

## Troubleshooting & FAQ

### A device does not change its theme

Open the profile on that device and set the theme to **Backend-selected**. A theme picked on the device itself always wins.

### "Saison-Themes are not loaded" under Repairs

Your `configuration.yaml` does not load the `themes` folder. Add the lines from [Before you start](#before-you-start) and restart Home Assistant. The notice disappears on its own.

### "Themes could not be reloaded" under Repairs

Usually caused by an error in another theme file or in `configuration.yaml`. The notice shows the error message.

### I used the Saison-Themes YAML package before

Remove it, so the two do not get in each other's way, then restart Home Assistant:

- `packages/saison_themes.yaml`
- `themes/saison.yaml`
- optionally `www/themes/*.svg`

The entries under `homeassistant: packages:` and `frontend: themes:` in `configuration.yaml` can stay.

### What happens when I remove the integration?

`themes/saison_themes.yaml` is deleted again and Home Assistant falls back to the default theme.

## For developers

The integration has no dependencies outside Home Assistant. CI runs the HACS validation and hassfest; see [CHANGELOG.md](CHANGELOG.md) for what changed.

**Releasing:** bump `version` in `custom_components/saison_themes/manifest.json` and `VERSION` in `const.py`, move the CHANGELOG entry to the new version, then publish a GitHub release with the tag `vX.Y.Z`.

## License

[MIT](LICENSE)
