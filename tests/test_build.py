import pytest
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

from build import SOURCE, build

# Name IDs allowed to mention the original: copyright, trademark notice, description (credit).
CREDIT_IDS = {0, 7, 10}


@pytest.fixture(scope="module")
def paths(tmp_path_factory):
    return build(out=tmp_path_factory.mktemp("fonts"))


@pytest.fixture(scope="module", params=["ttf", "woff2"])
def font(request, paths):
    return TTFont(paths[request.param])


def names(font):
    return {r.nameID: str(r) for r in font["name"].names}


def test_writes_ttf_and_woff2(paths):
    assert paths["ttf"].name == "ReQuizitText-Variable.ttf"
    assert paths["woff2"].name == "ReQuizitText-Variable.woff2"
    assert TTFont(paths["ttf"]).flavor is None
    assert TTFont(paths["woff2"]).flavor == "woff2"


def test_family_names(font):
    n = names(font)
    assert n[1] == "ReQuizit Text"
    assert n[2] == "Regular"
    assert n[3] == "1.000;REQZ;ReQuizitText"
    assert n[4] == "ReQuizit Text"
    assert n[5] == "Version 1.000"
    assert n[6] == "ReQuizitText"
    assert n[25] == "ReQuizitText"


def test_instance_postscript_names_use_the_new_family(font):
    n = names(font)
    ps = [n[i.postscriptNameID] for i in font["fvar"].instances]
    assert ps[0] == "ReQuizitText-Thin"
    assert "ReQuizitText" in ps
    assert all(p.startswith("ReQuizitText") for p in ps)


def test_names_drop_the_original_family_name(font):
    for r in font["name"].names:
        if r.nameID not in CREDIT_IDS:
            assert "Inter" not in str(r), r.nameID


def test_keeps_the_original_copyright_and_trademark(font):
    n = names(font)
    assert n[0] == "Copyright 2016 The Inter Project Authors"
    assert n[7] == "Inter UI and Inter is a trademark of rsms."


def test_credits_the_original_design(font):
    n = names(font)
    assert n[8] == "ReQuizit"
    assert n[9] == "Rasmus Andersson"
    assert "Inter 4.1 by Rasmus Andersson" in n[10]
    assert n[11] == "https://github.com/requizit-is/requizit-text"
    assert n[12] == "https://rsms.me/"
    assert n[14] == "https://openfontlicense.org"


def test_metadata_no_longer_claims_the_original_vendor(font):
    assert font["OS/2"].achVendID == "REQZ"
    assert font["head"].fontRevision == 1.0


def test_keeps_the_variation_axes(font):
    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in font["fvar"].axes}
    assert axes == {"opsz": (14, 14, 32), "wght": (100, 400, 900)}


def test_glyphs_are_unchanged(font):
    source = TTFont(SOURCE)
    assert font.getBestCmap() == source.getBestCmap()
    glyphs, source_glyphs = font.getGlyphSet(), source.getGlyphSet()
    for name in source.getGlyphOrder():
        pen, source_pen = RecordingPen(), RecordingPen()
        glyphs[name].draw(pen)
        source_glyphs[name].draw(source_pen)
        assert pen.value == source_pen.value, name


def test_variations_are_unchanged(paths):
    source = TTFont(SOURCE)
    built = TTFont(paths["ttf"])
    for tag in ("gvar", "avar", "HVAR", "MVAR", "STAT"):
        assert built.reader[tag] == source.reader[tag], tag
