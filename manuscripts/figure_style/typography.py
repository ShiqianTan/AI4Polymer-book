"""Repository-pinned Chinese typography for every chapter figure.

The book ships Source Han Sans CN under ``fonts/`` as Git LFS objects. When those
files are absent (for example in a fresh checkout that has not run ``git lfs
pull``), figure building falls back to a system CJK sans face so that the
geometry and layout checks still run.

Fallbacks avoid ``.ttc`` font collections: XeLaTeX's ``xdvipdfmx`` silently
drops their subsetted CID fonts when a figure PDF is included in the book, which
leaves the figure labels blank. A single-face ``.ttf`` keeps its glyphs.
"""
from pathlib import Path

from matplotlib import font_manager

FONT_DIR = Path(__file__).resolve().parent / 'fonts'
PINNED = FONT_DIR / 'SourceHanSansCN-Regular.ttf'
SYSTEM_FALLBACKS = ('Arial Unicode MS', 'Songti SC', 'STHeiti',
                    'PingFang HK', 'Hiragino Sans GB', 'Noto Sans CJK SC')


def configure_font(override=None):
    """Register the pinned faces when present; otherwise return a system face."""
    for weight in ('Regular', 'Medium', 'Bold'):
        path = FONT_DIR / f'SourceHanSansCN-{weight}.ttf'
        if path.exists():
            font_manager.fontManager.addfont(str(path))
    if override:
        path = Path(override).expanduser().resolve()
        font_manager.fontManager.addfont(str(path))
        return path, font_manager.FontProperties(fname=str(path)).get_name()
    if PINNED.exists():
        return PINNED, font_manager.FontProperties(fname=str(PINNED)).get_name()
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in SYSTEM_FALLBACKS:
        if name in available:
            return None, name
    raise FileNotFoundError('No CJK figure font available; pass --font or add '
                            'manuscripts/figure_style/fonts/SourceHanSansCN-*.ttf')
