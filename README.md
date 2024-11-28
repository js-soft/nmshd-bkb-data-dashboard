# Dev Setup

Git-Filter für Notebookoutputs aktivieren:

```bash
git config --local include.path "../.gitconfig"
```

## .bacpac SQL Server Backup laden (Linux)

1. SQL Server Datenbankbackup beziehen (.bacpac Datei)
2. SQL Server 2022 im Dockercontainer starten (siehe [Dokumentation](https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker)).

    ```bash
    docker pull mcr.microsoft.com/mssql/server:2022-latest
    docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Bohemian_Rhapsody2024" \
        -p 1433:1433 --name bird_backbone_sql --hostname sql1 \
        mcr.microsoft.com/mssql/server:2022-latest
    ```
3. `sqlpackage` installieren (z.B. via [AUR Package](https://aur.archlinux.org/packages/sqlpackage)).
4. Backup mittels `sqlpackage` importieren.

    ```bash
    sqlpackage /a:Import /tsn:localhost /tdn:bird_backbone /tu:sa /tp:Bohemian_Rhapsody2024 /TargetEncryptConnection:false /sf:sql-bird-backup.bacpac
    ```

5. Microsoft's ODBC SQL Driver Installieren (z.B. via [AUR Package](https://aur.archlinux.org/packages/msodbcsql))


# TODOs (To be specified)

- Landing Page mit Cards für einzelne Tabs
- Datumscutoff für alle geeigneten Plots via Schieberegler
- Alle (relevanten) Plots: Filtern von Daten bezüglich ClientId
- Identities: Identityzuwachsraten
- Identities: Dropoffraten (identity deletion, Grund evlt aufnehmen)
- Number of XYZ per Identity: Click soll einzelne Identitäten anzeigen (wie?)
    - alternativ: Datenabzug per CSV (Button im Plot-Kontextmenü)
-  Frequenz Buckets / Histogramme mit click on balken aufspalten
    - alternativ: Wechsel zwischen Scatterplot und Histogram mittels Button im Plot-Kontextmenü für alle Plots
- Größenangaben verschlüsselter Payloads sollten skaliert werden (Verschlüsselung, Base64, Json-Boilerplate)
- Animationen für geeignete Plots evaluieren https://plotly.com/python/animations/
- "Number of XYZ per Identity" mit Nutzungsdauer skalieren. Die reine Anzahl ist nicht informativ, da sie im Laufe der gewöhnlichen Nutzung steigt und dadurch mit der Nutzungsdauer skaliert.
- Definition von Testconnector-IDs statisch konfigurierbar machen (z.B. Umgebungsvariable, die Regex definiert)
- Lookup Tabellen (z.B. RelationshipStatus {20: Pending, ...}) statisch generieren (C# Code Anbindung/Einpflegung in DB)
- Aktivität der Nutzer, z.B. über Zeit des letzten Logins (siehe Devices.AspNetUsers)
- anzahl Nachrichten wochen/monatsweise aggregieren? (bessere übersicht)
    - zusätzlicher Plot; siehe Identityzuwachsraten, gleiches Problem
- Absolutanzahl Fehler in Abhängigkeit von Zeitintervall
    - eigener Plot/Tabelle oder in existierenden Plot eingliedern
- Integrationstests
