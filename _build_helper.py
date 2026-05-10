"""
_build_helper.py - Wird von build_lokal.bat und build_release.bat aufgerufen
Ersetzt SERVER_HOST in config.py temporaer fuer den Build
"""
import sys

LOKAL_HOST = "localhost"
RELEASE_HOST = "klingeundgelinge.duckdns.org"

def set_host(host):
    with open("config.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Ersetze jede SERVER_HOST Zeile
    lines = content.splitlines()
    neue_lines = []
    for line in lines:
        if line.strip().startswith("SERVER_HOST"):
            neue_lines.append(f'SERVER_HOST = "{host}"')
        else:
            neue_lines.append(line)

    with open("config.py", "w", encoding="utf-8") as f:
        f.write("\n".join(neue_lines))

    print(f"SERVER_HOST gesetzt auf: {host}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung: python _build_helper.py lokal|release")
        sys.exit(1)

    modus = sys.argv[1].lower()
    if modus == "lokal":
        set_host(LOKAL_HOST)
    elif modus == "release":
        set_host(RELEASE_HOST)
    else:
        print(f"Unbekannter Modus: {modus}")
        sys.exit(1)
