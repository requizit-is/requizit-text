"""Build ReQuizit Text from the Inter 4.1 variable font."""

from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).parent
SOURCE = ROOT / "sources" / "InterVariable.ttf"
OUT = ROOT / "fonts"

FAMILY = "ReQuizit Text"
PS_FAMILY = "ReQuizitText"
SOURCE_PS_FAMILY = "InterVariable"
FILE_NAME = f"{PS_FAMILY}-Variable"
VERSION = "1.000"
VENDOR = "REQZ"
OFL_URL = "https://openfontlicense.org"

NAMES = {
    1: FAMILY,
    3: f"{VERSION};{VENDOR};{PS_FAMILY}",
    4: FAMILY,
    5: f"Version {VERSION}",
    6: PS_FAMILY,
    8: "ReQuizit",
    10: "Renamed build of Inter 4.1 by Rasmus Andersson (https://rsms.me/inter/) for ReQuizit.",
    11: "https://github.com/requizit-is/requizit-text",
    13: (
        "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
        f"This license is available with a FAQ at: {OFL_URL}"
    ),
    14: OFL_URL,
    25: PS_FAMILY,
}


def rename(font: TTFont) -> None:
    name = font["name"]
    name.names = [r for r in name.names if r.platformID == 3]
    for record in name.names:
        text = str(record)
        if SOURCE_PS_FAMILY in text:
            record.string = text.replace(SOURCE_PS_FAMILY, PS_FAMILY)
    for name_id, text in NAMES.items():
        name.setName(text, name_id, 3, 1, 0x409)

    font["OS/2"].achVendID = VENDOR
    font["head"].fontRevision = float(VERSION)


def build(source: Path = SOURCE, out: Path = OUT) -> dict[str, Path]:
    font = TTFont(source)
    rename(font)
    paths = {
        "ttf": out / "ttf" / f"{FILE_NAME}.ttf",
        "woff2": out / "webfonts" / f"{FILE_NAME}.woff2",
    }
    for flavor, path in paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        font.flavor = "woff2" if flavor == "woff2" else None
        font.save(path)
    return paths


if __name__ == "__main__":
    for path in build().values():
        print(path.relative_to(ROOT))
