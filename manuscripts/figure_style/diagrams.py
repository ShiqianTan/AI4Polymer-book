"""Reusable teaching-diagram primitives for the AI4Polymer figures.

Every helper draws into a `figure_style.canvas` axes whose coordinates are the
unit square, so a layout can be reasoned about in fractions of the 420 pt column.
The primitives keep the shared palette and never set a label below 11 pt.

Conventions shared with `figure_style`:
  * light fills, dark thin outlines, one emphasis object per figure;
  * solid arrows carry data, dashed arrows denote control or feedback;
  * data figures keep real axes and units and use `plot()`, not `canvas()`.
"""
import math

from matplotlib.patches import Circle, Polygon, Rectangle

from . import COL, arrow, box, text


def layers(ax, items, x=0.06, w=0.80, y0=0.10, step=0.155, h=0.12,
           name_x=0.125, desc_x=0.21, tag_x=0.83, arrow_x=0.46,
           name_size=13, size=11):
    """Stack items bottom-to-top with upward data arrows.

    items: (name, description, right_tag, color); right_tag may be ''.
    """
    for i, (name, desc, tag, color) in enumerate(items):
        y = y0 + i * step
        box(ax, x, y, w, h, '', color)
        text(ax, name_x, y + h / 2, name, size=name_size, ha='center', weight='bold')
        text(ax, desc_x, y + h / 2, desc, size=size)
        if tag:
            text(ax, tag_x, y + h / 2, tag, size=size, ha='right')
        if i:
            arrow(ax, (arrow_x, y - (step - h)), (arrow_x, y))


def pipeline(ax, steps, y=0.58, h=0.15, color='blue', size=11,
             x0=0.03, x1=0.97, gap=0.02, back=None):
    """Left-to-right flow of boxes joined by data arrows.

    steps: labels. back: iterable of (from_index, to_index) drawn as a dashed
    control arrow below the flow, used for a fallback or feedback edge.
    """
    n = len(steps)
    w = (x1 - x0 - gap * (n - 1)) / n
    xs = [x0 + i * (w + gap) for i in range(n)]
    for i, label in enumerate(steps):
        box(ax, xs[i], y - h / 2, w, h, label, color, size=size)
        if i:
            arrow(ax, (xs[i - 1] + w, y), (xs[i], y))
    for a, b in (back or []):
        ya = y - h / 2 - 0.13
        for i in (a, b):
            ax.plot([xs[i] + w / 2] * 2, [y - h / 2, ya], color=COL['line'], lw=1)
        arrow(ax, (xs[b] + w / 2, ya), (xs[a] + w / 2, ya), kind='control')


def cycle(ax, items, center=(0.5, 0.5), rx=0.30, ry=0.28, w=0.24, h=0.12,
          color='blue', size=11, start=90.0, offset=0.40):
    """Ring of boxes joined by arrows.

    items: (label, note) with note optional, drawn just below the box.
    Arrows are drawn first so the boxes sit on top of their ends.
    """
    n = len(items)
    pts = []
    for k in range(n):
        a = math.radians(start - 360.0 * k / n)
        pts.append((center[0] + rx * math.cos(a), center[1] + ry * math.sin(a)))
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        arrow(ax, (a[0] + (b[0] - a[0]) * offset, a[1] + (b[1] - a[1]) * offset),
              (b[0] + (a[0] - b[0]) * offset, b[1] + (a[1] - b[1]) * offset))
    for (label, note), (cx, cy) in zip(items, pts):
        box(ax, cx - w / 2, cy - h / 2, w, h, label, color, size=size)
        if note:
            text(ax, cx, cy - h / 2 - 0.05, note, size=11, ha='center')


def funnel(ax, stages, cx=0.34, w_top=0.56, y_top=0.90, h=0.15, gap=0.012,
           shrink=0.17, size=11, colors=None):
    """Stacked narrowing trapezoids; stages are (label, value), value optional."""
    palette = colors or ['blue', 'green', 'orange', 'purple', 'gray']
    for i, (label, value) in enumerate(stages):
        y = y_top - i * (h + gap)
        w0 = w_top * (1 - shrink * i)
        w1 = w_top * (1 - shrink * (i + 1))
        verts = [(cx - w0 / 2, y), (cx + w0 / 2, y),
                 (cx + w1 / 2, y - h), (cx - w1 / 2, y - h)]
        ax.add_patch(Polygon(verts, closed=True,
                             facecolor=COL[palette[i % len(palette)]],
                             edgecolor=COL['line'], linewidth=.9))
        text(ax, cx, y - h / 2, label, size=size, ha='center')
        if value:
            text(ax, cx + w0 / 2 + 0.015, y - h / 2, value, size=11)


def spectrum(ax, items, y=0.58, h=0.16, color='blue', size=11,
             x0=0.04, x1=0.96, gap=0.014, left_label='', right_label=''):
    """Horizontal family axis: ordered boxes over a right-pointing axis."""
    n = len(items)
    w = (x1 - x0 - gap * (n - 1)) / n
    for i, label in enumerate(items):
        box(ax, x0 + i * (w + gap), y - h / 2, w, h, label, color, size=size)
    arrow(ax, (x0, y - h / 2 - 0.12), (x1, y - h / 2 - 0.12))
    if left_label:
        text(ax, x0, y + h / 2 + 0.08, left_label, size=11)
    if right_label:
        text(ax, x1, y + h / 2 + 0.08, right_label, size=11, ha='right')


def pyramid(ax, tiers, cx=0.38, w_top=0.20, y_top=0.90, h=0.15, gap=0.012,
            widen=0.11, size=11, colors=None):
    """Top-to-bottom widening trapezoids; tiers are (label, note)."""
    palette = colors or ['purple', 'orange', 'green', 'blue', 'gray']
    for i, (label, note) in enumerate(tiers):
        y = y_top - i * (h + gap)
        w0 = w_top + widen * i
        w1 = w_top + widen * (i + 1)
        verts = [(cx - w0 / 2, y), (cx + w0 / 2, y),
                 (cx + w1 / 2, y - h), (cx - w1 / 2, y - h)]
        ax.add_patch(Polygon(verts, closed=True,
                             facecolor=COL[palette[i % len(palette)]],
                             edgecolor=COL['line'], linewidth=.9))
        text(ax, cx, y - h / 2, label, size=size, ha='center')
        if note:
            text(ax, cx + w1 / 2 + 0.015, y - h / 2, note, size=11)


def tree(ax, root, branches, root_xy=(0.5, 0.86), branch_y=0.40, w=0.24, h=0.13,
         root_color='gray', color='blue', size=11):
    """Root box above a row of branch boxes, joined by data arrows."""
    n = len(branches)
    box(ax, root_xy[0] - w / 2, root_xy[1] - h / 2, w, h, root, root_color, size=size)
    for i, label in enumerate(branches):
        x = 0.05 + 0.90 * (i + 0.5) / n
        box(ax, x - w / 2, branch_y - h / 2, w, h, label, color, size=size)
        arrow(ax, (root_xy[0], root_xy[1] - h / 2), (x, branch_y + h / 2))


def graph(ax, nodes, edges, w=0.22, h=0.12, size=11, color='blue'):
    """Free node/edge diagram.

    nodes: {name: (x, y, label[, color])}; edges: (a, b[, kind]) where kind is
    'data' (solid, default) or 'control' (dashed).
    """
    for name, spec in nodes.items():
        x, y, label = spec[0], spec[1], spec[2]
        c = spec[3] if len(spec) > 3 else color
        box(ax, x - w / 2, y - h / 2, w, h, label, c, size=size)
    for e in edges:
        a, b = e[0], e[1]
        kind = e[2] if len(e) > 2 else 'data'
        arrow(ax, (nodes[a][0], nodes[a][1]), (nodes[b][0], nodes[b][1]), kind=kind)


def venn(ax, left, right, overlap, center=(0.5, 0.55), r=0.24, size=11,
         left_color='blue', right_color='green'):
    """Two overlapping discs with a shared middle label."""
    ax.add_patch(Circle((center[0] - r * 0.62, center[1]), r,
                        facecolor=COL[left_color], edgecolor=COL['line'],
                        linewidth=.9, alpha=.8))
    ax.add_patch(Circle((center[0] + r * 0.62, center[1]), r,
                        facecolor=COL[right_color], edgecolor=COL['line'],
                        linewidth=.9, alpha=.8))
    text(ax, center[0] - r * 1.05, center[1], left, size=size, ha='center')
    text(ax, center[0] + r * 1.05, center[1], right, size=size, ha='center')
    text(ax, center[0], center[1], overlap, size=size, ha='center')


def gantt(ax, rows, x0=0.22, x1=0.97, y_top=0.82, row_h=0.13, gap=0.05,
          total=None, size=11, colors=None):
    """Horizontal bars; rows are (label, start, length) in shared data units."""
    palette = colors or ['blue', 'green', 'orange', 'purple', 'gray']
    span = x1 - x0
    total = total or max(s + l for _, s, l in rows)
    for i, (label, start, length) in enumerate(rows):
        y = y_top - i * (row_h + gap)
        text(ax, x0 - 0.015, y - row_h / 2, label, size=size, ha='right')
        ax.add_patch(Rectangle((x0 + span * start / total, y - row_h),
                               span * length / total, row_h,
                               facecolor=COL[palette[i % len(palette)]],
                               edgecolor=COL['line'], linewidth=.9))


def table(ax, headers, rows, y_top=0.86, row_h=0.135, col_x=None, size=11):
    """Light table: bold header row, hairline rules, centred cells."""
    ncol = len(headers)
    if col_x is None:
        col_x = [0.06 + 0.88 * (i + 0.5) / ncol for i in range(ncol)]
    for cx, head in zip(col_x, headers):
        text(ax, cx, y_top, head, size=size, ha='center', weight='bold')
    ax.plot([0.04, 0.96], [y_top - row_h * 0.5] * 2, color=COL['line'], lw=.9)
    for r, row in enumerate(rows):
        y = y_top - row_h * (r + 1)
        for cx, cell in zip(col_x, row):
            text(ax, cx, y, cell, size=size, ha='center')
        if r < len(rows) - 1:
            ax.plot([0.04, 0.96], [y - row_h * 0.5] * 2, color=COL['gray'], lw=.6)
