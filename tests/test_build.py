import pytest
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from build import SOURCE, STATIC_WEIGHTS, build, build_static

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


@pytest.fixture(scope="module")
def static_paths(tmp_path_factory):
    return build_static(out=tmp_path_factory.mktemp("fonts"))


@pytest.fixture(scope="module", params=[400, 500, 700, 900])
def static(request, static_paths):
    return request.param, TTFont(static_paths[request.param])


def advance(font, char):
    return font["hmtx"][font.getBestCmap()[ord(char)]][0]


def test_writes_the_four_brand_weights_as_static_ttf(static_paths):
    assert {w: p.name for w, p in static_paths.items()} == {
        400: "ReQuizitText-Regular.ttf",
        500: "ReQuizitText-Medium.ttf",
        700: "ReQuizitText-Bold.ttf",
        900: "ReQuizitText-Black.ttf",
    }
    assert {p.parent.name for p in static_paths.values()} == {"ttf"}


def test_static_fonts_have_no_variations(static):
    _, font = static
    for tag in ("fvar", "gvar", "avar", "HVAR", "MVAR", "STAT"):
        assert tag not in font, tag


def test_static_names_keep_one_family_with_the_weight_as_style(static):
    weight, font = static
    style = STATIC_WEIGHTS[weight]
    n = names(font)
    assert n[1] == "ReQuizit Text"
    assert n[2] == style
    assert n[3] == f"1.000;REQZ;ReQuizitText-{style}"
    assert n[4] == f"ReQuizit Text {style}"
    assert n[5] == "Version 1.000"
    assert n[6] == f"ReQuizitText-{style}"
    assert not {16, 17, 25} & n.keys()


def test_static_names_drop_the_original_family_name_and_keep_the_credits(static):
    _, font = static
    n = names(font)
    for name_id, text in n.items():
        if name_id not in CREDIT_IDS:
            assert "Inter" not in text, name_id
    assert n[0] == "Copyright 2016 The Inter Project Authors"
    assert "Inter 4.1 by Rasmus Andersson" in n[10]


def test_static_weight_metadata(static):
    weight, font = static
    os2 = font["OS/2"]
    assert os2.usWeightClass == weight
    assert bool(os2.fsSelection & 0b100000) == (weight == 700)
    assert bool(os2.fsSelection & 0b1000000) == (weight == 400)
    assert not os2.fsSelection & 0b1
    assert font["head"].macStyle == (1 if weight == 700 else 0)


def test_static_fonts_cover_the_brand_character_set(static):
    _, font = static
    cmap = set(font.getBestCmap())
    assert len(cmap) == 499
    for char in "AzÞþÐðÆæÖöŐőЁёЖжЯя№€™−→«»—…":
        assert ord(char) in cmap, char
    assert ord("α") not in cmap
    assert cmap <= set(TTFont(SOURCE).getBestCmap())


def test_static_weights_grow_heavier(static_paths):
    widths = [advance(TTFont(static_paths[w]), "H") for w in (400, 500, 700, 900)]
    assert widths == sorted(set(widths))


def test_static_fonts_take_the_display_optical_size(static_paths):
    def cut(opsz):
        return advance(instantiateVariableFont(TTFont(SOURCE), {"wght": 400, "opsz": opsz}), "n")

    assert advance(TTFont(static_paths[400]), "n") == cut(32) != cut(14)
