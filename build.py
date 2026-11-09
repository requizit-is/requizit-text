"""Build ReQuizit Text from the Inter 4.1 variable font."""

from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

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

# Static instances serve renderers that need one file per weight, such as resvg. They take the
# brand's four weights at the largest optical size and the brand's web character set.
STATIC_WEIGHTS = {400: "Regular", 500: "Medium", 700: "Bold", 900: "Black"}
STATIC_OPSZ = 32
# Latin with Icelandic and Latin Extended-A, Russian Cyrillic, punctuation, the euro, numero and
# trademark signs, arrows and the minus. U+0000 stays because Inter maps it.
CHARSET = [
    (0x0000, 0x0000), (0x0020, 0x007E), (0x00A0, 0x00AC), (0x00AE, 0x0148), (0x014A, 0x017F),
    (0x0400, 0x045F), (0x2000, 0x200B), (0x2010, 0x2027), (0x202F, 0x2055), (0x2057, 0x2057),
    (0x205F, 0x205F), (0x20AC, 0x20AC), (0x2116, 0x2116), (0x2122, 0x2122), (0x2190, 0x2193),
    (0x2212, 0x2212),
]


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


def static_instance(variable: TTFont, weight: int) -> TTFont:
    style = STATIC_WEIGHTS[weight]
    font = instantiateVariableFont(variable, {"wght": weight, "opsz": STATIC_OPSZ})

    options = subset.Options()
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.notdef_outline = True
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=[c for first, last in CHARSET for c in range(first, last + 1)])
    subsetter.subset(font)

    name = font["name"]
    for name_id in (16, 17, 25):
        name.removeNames(nameID=name_id)
    for name_id, text in {
        2: style,
        3: f"{VERSION};{VENDOR};{PS_FAMILY}-{style}",
        4: f"{FAMILY} {style}",
        6: f"{PS_FAMILY}-{style}",
    }.items():
        name.setName(text, name_id, 3, 1, 0x409)
    if "STAT" in font:
        del font["STAT"]

    os2 = font["OS/2"]
    os2.usWeightClass = weight
    # fsSelection: ITALIC 0, BOLD 5, REGULAR 6.
    os2.fsSelection = (os2.fsSelection & ~0b1100001) | {700: 0b100000, 400: 0b1000000}.get(weight, 0)
    font["head"].macStyle = 1 if weight == 700 else 0
    return font


def build_static(source: Path = SOURCE, out: Path = OUT) -> dict[int, Path]:
    variable = TTFont(source)
    rename(variable)
    paths = {}
    for weight, style in STATIC_WEIGHTS.items():
        path = out / "ttf" / f"{PS_FAMILY}-{style}.ttf"
        path.parent.mkdir(parents=True, exist_ok=True)
        static_instance(variable, weight).save(path)
        paths[weight] = path
    return paths


if __name__ == "__main__":
    for path in [*build().values(), *build_static().values()]:
        print(path.relative_to(ROOT))
