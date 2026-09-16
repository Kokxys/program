# T-COPIER PRO – aktualizace

Tento veřejný repozitář slouží pouze k distribuci oficiálních aktualizací T-COPIER PRO.

- Zdrojový kód aplikace zde není zveřejněný.
- Nejsou zde Telegram session, konfigurace, historie ani přihlašovací údaje.
- Instalační soubory budou dostupné v části **Releases**.

Aplikace kontroluje tento stálý manifest:

`https://github.com/Kokxys/program/releases/latest/download/latest.json`

Každé vydání musí obsahovat dva soubory:

1. `T_COPIER_PRO_Setup_<verze>.exe`
2. `latest.json`

Nejdřív se nahraje instalátor a až potom `latest.json`. Copier nabídne jen verzi vyšší než tu, která je právě nainstalovaná, a před dokončením stažení ověří velikost a SHA-256 instalátoru.
