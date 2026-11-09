# Wunderground PWS (dashboard) – Home Assistant integrace

Vložíš URL stanice (`https://www.wunderground.com/dashboard/pws/IOBORA10`) nebo jen ID, nastavíš
interval a dostaneš zařízení se senzory: teplota, pocitová teplota, rosný bod, vlhkost, vítr,
nárazy, směr větru, tlak, intenzita a denní úhrn srážek, UV, sluneční záření.

Žádné CSS selektory ani scrape senzory – integrace stáhne stránku a přečte `data-*` atributy widgetů.
Jednotky se čtou ze stránky a HA je převede podle tvého nastavení jednotek.

## Instalace
1. Zkopíruj složku `custom_components/wunderground_pws` do `<config>/custom_components/`.
2. Restartuj Home Assistant.
3. Nastavení → Zařízení a služby → Přidat integraci → **Wunderground PWS (dashboard)**.
4. Pro každou stanici přidej integraci znovu. Interval změníš v „Konfigurovat“ u dané stanice.

## Poznámky
- Výchozí interval je 5 minut (min. 1). Wunderground stanice se většinou obnovují po pár minutách, častější dotazy nemají smysl.
- Integrace čte HTML stránky; pokud Wunderground změní layout, parser (`parser.py`) je třeba upravit.

## Instalace přes HACS
HACS → Integrace → menu (⋮) → Vlastní repozitáře → URL `https://github.com/LadasFaras/wg-homeassistant`, kategorie **Integration** → stáhnout → restart HA.
