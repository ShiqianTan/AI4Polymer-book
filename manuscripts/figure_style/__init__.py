"""Book-size vector drawings; geometry is designed at its final reading size.

Follows the Hands-On Large Language Models figure style: white background, light
fills, dark thin outlines, large labels. Every exported figure is checked for a
11 pt minimum label size and for text spilling outside the canvas.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.transforms import Bbox

from .typography import configure_font

COL = dict(ink='#252525', line='#454545', blue='#CBE3F3', green='#CFE8DB',
           orange='#F9DEC0', purple='#DDCDE8', gray='#EEEEEE', white='#FFFFFF')

FONT_PATH, FONT_FAMILY = configure_font()

STYLE = {'font.family': 'sans-serif', 'font.sans-serif': [FONT_FAMILY, 'DejaVu Sans'],
         'font.size': 12, 'font.weight': 'normal', 'axes.titleweight': 'medium',
         'text.color': COL['ink'], 'axes.labelcolor': COL['ink'],
         'axes.edgecolor': COL['line'], 'xtick.color': COL['ink'], 'ytick.color': COL['ink'],
         'axes.labelsize': 12, 'axes.titlesize': 14, 'xtick.labelsize': 11,
         'ytick.labelsize': 11, 'legend.fontsize': 11, 'svg.fonttype': 'path',
         'pdf.fonttype': 42, 'figure.facecolor': 'white', 'savefig.facecolor': 'white',
         'axes.unicode_minus': False}

plt.rcParams.update(STYLE)


def canvas(height=3.6):
    fig, ax = plt.subplots(figsize=(420 / 72, height))
    fig.subplots_adjust(left=.035, right=.965, bottom=.035, top=.965)
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')
    return fig, ax


def plot(height=3.6, left=.17, bottom=.20):
    fig, ax = plt.subplots(figsize=(420 / 72, height))
    fig.subplots_adjust(left=left, right=.95, bottom=bottom, top=.93)
    ax.spines[['top', 'right']].set_visible(False)
    return fig, ax


def text(ax, x, y, label, size=12, ha='left', **kw):
    return ax.text(x, y, label, fontsize=size, ha=ha, va='center',
                   linespacing=1.4, **kw)


def box(ax, x, y, w, h, label='', color='blue', size=12, edge=None):
    patch = FancyBboxPatch((x, y), w, h,
                           boxstyle='round,pad=0.002,rounding_size=0.008',
                           facecolor=COL[color], edgecolor=edge or COL['line'],
                           linewidth=.9)
    ax.add_patch(patch)
    if label:
        text(ax, x + w / 2, y + h / 2, label, size, ha='center')
    return patch


def arrow(ax, start, end, kind='data'):
    # Dashed edges denote control; solid edges carry data. Explain locally in captions.
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=11,
                                 linewidth=1, color=COL['line'],
                                 linestyle='--' if kind == 'control' else '-',
                                 shrinkA=3, shrinkB=3))


BADGE_KINDS = ('DATA', 'LIT', 'CALC', 'SCHEMATIC')
BADGE_LABEL = {'DATA': '数据结果图', 'LIT': '文献统计图',
               'CALC': '复算结果图', 'SCHEMATIC': '示意图'}
BADGE_FILL = {'DATA': 'green', 'LIT': 'blue', 'CALC': 'orange',
              'SCHEMATIC': 'gray'}


def draw_badge(fig, kind, size=11, pad=4.0, margin=5.0, zorder=1000):
    """Draw an evidence badge in the top-right corner of a figure.

    kind is one of BADGE_KINDS. The badge is a light rounded rectangle with a
    dark thin edge and a label at no less than 11 pt; it is added last so it
    sits above the artwork. Returns the display-space bounding box so callers
    can test it against the text they have already placed.
    """
    if kind not in BADGE_KINDS:
        raise ValueError(f'unknown badge kind: {kind!r}; expected one of '
                         f'{BADGE_KINDS}')
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    label = fig.text(0.0, 0.0, BADGE_LABEL[kind], fontsize=size, ha='left',
                     va='bottom', color=COL['ink'], zorder=zorder + 1)
    fig.canvas.draw()
    tb = label.get_window_extent(renderer)
    box_w = tb.width + 2 * pad
    box_h = tb.height + 2 * pad
    x1 = fig.bbox.width - margin
    y1 = fig.bbox.height - margin
    x0, y0 = x1 - box_w, y1 - box_h
    inv = fig.transFigure.inverted()
    fx0, fy0 = inv.transform((x0, y0))
    fx1, fy1 = inv.transform((x1, y1))
    patch = FancyBboxPatch((fx0, fy0), fx1 - fx0, fy1 - fy0,
                           boxstyle='round,pad=0,rounding_size=0.008',
                           facecolor=COL[BADGE_FILL[kind]],
                           edgecolor=COL['line'], linewidth=.9,
                           transform=fig.transFigure, clip_on=False,
                           zorder=zorder)
    fig.add_artist(patch)
    label.set_position(((fx0 + fx1) / 2, (fy0 + fy1) / 2))
    label.set_ha('center')
    label.set_va('center')
    fig.canvas.draw()
    return Bbox.from_extents(x0, y0, x1, y1)


badge = draw_badge


def _text_artists(fig):
    """Every visible text object the layout checks consider, in draw order."""
    labels = list(fig.texts)
    for ax in fig.axes:
        labels.extend(ax.texts)
        legend = ax.get_legend()
        if legend is not None:
            labels.extend(legend.get_texts())
        if ax.axison:
            labels.extend([ax.title, ax.xaxis.label, ax.yaxis.label])
            for axis in [ax.xaxis, ax.yaxis]:
                lo, hi = sorted(axis.get_view_interval())
                for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                    if lo <= tick.get_loc() <= hi:
                        labels.extend([tick.label1, tick.label2])
                labels.append(axis.get_offset_text())
    return labels


class Exporter:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.outputs = []
        self.checks = []

    def save(self, fig, name, badge=None):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        placed = [t for t in _text_artists(fig)
                  if t.get_visible() and t.get_text()]
        if badge:
            box = draw_badge(fig, badge)
            clashes = [t.get_text() for t in placed
                       if box.overlaps(t.get_window_extent(renderer))]
            if clashes:
                raise ValueError(
                    f'{name}: badge {badge} overlaps text: {clashes}')
        warnings = []
        sizes = []
        for t in _text_artists(fig):
            if not t.get_visible() or not t.get_text():
                continue
            bb = t.get_window_extent(renderer)
            sizes.append(t.get_fontsize())
            if bb.x0 < 0 or bb.y0 < 0 or bb.x1 > fig.bbox.width or bb.y1 > fig.bbox.height:
                warnings.append(t.get_text())
        record = dict(figure=name, width_pt=round(fig.get_figwidth() * 72, 4),
                      min_label_pt=min(sizes), text_extent_warnings=warnings)
        self.checks.append(record)
        if warnings:
            raise ValueError(f'{name}: labels outside canvas: {warnings}')
        if min(sizes) < 11:
            raise ValueError(f'{name}: label smaller than 11 pt')
        for ext in ['svg', 'png', 'pdf']:
            path = self.directory / f'{name}.{ext}'
            fig.savefig(path, dpi=240)
            self.outputs.append(path)
        plt.close(fig)

    def finish(self):
        (self.directory / 'teaching-layout-validation.json').write_text(
            json.dumps(self.checks, ensure_ascii=False, indent=2) + '\n')
        return self.outputs
