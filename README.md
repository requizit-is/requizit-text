# ReQuizit Text

The text typeface of ReQuizit. One variable font with weights 100 to 900 and optical sizes 14 to 32, plus static files of the four brand weights. Upright only. Latin, Icelandic, Cyrillic and Greek.

ReQuizit Text is a renamed build of [Inter](https://rsms.me/inter/) 4.1 by Rasmus Andersson, licensed under the SIL Open Font License 1.1.

## Files

| File | Use |
| --- | --- |
| `fonts/ttf/ReQuizitText-Variable.ttf` | Desktop apps, print |
| `fonts/webfonts/ReQuizitText-Variable.woff2` | Websites |
| `fonts/ttf/ReQuizitText-{Regular,Medium,Bold,Black}.ttf` | Renderers that need one file per weight, such as resvg in the [poster generator](https://poster.requizit.is) |

The static files are the brand's weights 400, 500, 700 and 900 at optical size 32, the cut for 27 px and up. They carry the brand's character set: Latin with Icelandic, Russian Cyrillic, punctuation, € and №. Everything else takes the variable font.

## Use on a website

```css
@font-face {
  font-family: "ReQuizit Text";
  src: url("ReQuizitText-Variable.woff2") format("woff2");
  font-weight: 100 900;
  font-display: swap;
}
```

Browsers pick the optical size from the font size. Inter's alternate characters work as they are, for example `font-feature-settings: "cv11"` for a single-storey a or `"tnum"` for tabular figures. The full list is on the [Inter site](https://rsms.me/inter/).

## Build

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv run python build.py   # writes fonts/
uv run pytest            # checks the names, axes and glyphs
```

The build takes `sources/InterVariable.ttf` from the Inter 4.1 release, gives it the ReQuizit Text names and writes the files in `fonts/`. It does not change glyphs or variation data. The static files are instances of that renamed font, cut to `CHARSET` in `build.py`. To change glyphs, start from the [Inter sources](https://github.com/rsms/inter/tree/v4.1/src) at tag v4.1.

## Credits and license

- Inter: Rasmus Andersson, [rsms.me/inter](https://rsms.me/inter/).

Licensed under the SIL Open Font License 1.1, see [OFL.txt](OFL.txt). The change history is in [FONTLOG.txt](FONTLOG.txt).

Inter is a trademark of rsms. ReQuizit Text is not affiliated with or endorsed by rsms.
