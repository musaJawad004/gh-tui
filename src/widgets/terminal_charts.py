"""Large, terminal-native charts built from Rich text primitives."""

from __future__ import annotations

from math import atan2, pi, sqrt

from rich.text import Text


def line_plot(
    values: tuple[int, ...],
    summary: str,
    color: str,
    *,
    width: int = 34,
    height: int = 7,
) -> Text:
    """Render a connected multi-row plot with readable Y and X axes."""
    if not values:
        values = (0,)
    width = max(len(values), width)
    height = max(4, height)
    low, high = min(values), max(values)
    spread = max(1, high - low)
    positions = [round(index * (width - 1) / max(1, len(values) - 1)) for index in range(len(values))]
    rows = [height - 1 - round((value - low) / spread * (height - 1)) for value in values]
    canvas = [[" " for _ in range(width)] for _ in range(height)]

    for index in range(len(values) - 1):
        x1, x2 = positions[index], positions[index + 1]
        y1, y2 = rows[index], rows[index + 1]
        for x in range(x1, x2 + 1):
            amount = (x - x1) / max(1, x2 - x1)
            y = round(y1 + (y2 - y1) * amount)
            canvas[y][x] = "·"
    for x, y in zip(positions, rows, strict=True):
        canvas[y][x] = "●"

    result = Text(no_wrap=True)
    label_width = max(3, len(str(high)), len(str(low)))
    midpoint = round((high + low) / 2)
    for row, cells in enumerate(canvas):
        label = high if row == 0 else midpoint if row == height // 2 else low if row == height - 1 else None
        result.append(f"{label:>{label_width}} " if label is not None else " " * (label_width + 1), style="dim")
        result.append("┼" if row == height - 1 else "┤", style="dim")
        result.append("".join(cells), style=color)
        result.append("\n")
    result.append(" " * (label_width + 1) + "└" + "─" * width, style="dim")
    result.append(f"\n{' ' * (label_width + 2)}old{' ' * max(1, width - 9)}now", style="dim")
    result.append(f"\n{summary}", style=f"bold {color}")
    return result


def donut_chart(
    values: tuple[int, ...],
    summary: str,
    colors: tuple[str, ...],
    *,
    width: int = 21,
    height: int = 9,
) -> Text:
    """Render a proportional, colored ASCII donut with a centered total."""
    values = values or (0,)
    total = sum(max(0, value) for value in values) or 1
    colors = colors or ("white",)
    cumulative: list[float] = []
    running = 0.0
    for value in values:
        running += max(0, value) / total
        cumulative.append(running)

    width = max(13, width | 1)
    height = max(7, height | 1)
    center_x, center_y = width // 2, height // 2
    center_label = str(total)
    result = Text()
    for y in range(height):
        for x in range(width):
            nx = (x - center_x) / max(1, center_x)
            ny = (y - center_y) / max(1, center_y)
            radius = sqrt(nx * nx + ny * ny)
            if 0.58 <= radius <= 1.04:
                angle = (atan2(ny, nx) + pi) / (2 * pi)
                segment = next(
                    (index for index, boundary in enumerate(cumulative) if angle <= boundary),
                    len(cumulative) - 1,
                )
                result.append("●", style=colors[segment % len(colors)])
            elif y == center_y and center_x - len(center_label) // 2 <= x < center_x + (len(center_label) + 1) // 2:
                offset = x - (center_x - len(center_label) // 2)
                result.append(center_label[offset], style="bold")
            else:
                result.append(" ")
        result.append("\n")
    result.append(summary, style="dim")
    return result
