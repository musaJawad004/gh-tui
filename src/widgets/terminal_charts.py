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
    legend: str = "observed",
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
            canvas[y][x] = "∙"
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
    result.append("\n● ", style=f"bold {color}")
    result.append(legend, style="dim")
    result.append("   ∙ line", style="dim")
    result.append(f"\n{summary}", style=f"bold {color}")
    return result


def donut_chart(
    values: tuple[int, ...],
    summary: str,
    colors: tuple[str, ...],
    *,
    width: int = 21,
    height: int = 9,
    labels: tuple[str, ...] = (),
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

    height = max(7, height | 1)
    # Terminal cells are approximately twice as tall as they are wide. Keeping the
    # character-grid width near 2× height produces a visually round ring on screen.
    width = max(13, min(width | 1, height * 2 + 1))
    center_x, center_y = width // 2, height // 2
    center_label = str(total)
    result = Text()
    for y in range(height):
        for x in range(width):
            nx = (x - center_x) / max(1, center_x)
            ny = (y - center_y) / max(1, center_y)
            radius = sqrt(nx * nx + ny * ny)
            if 0.66 <= radius <= 1.04:
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
    if labels:
        for index, label in enumerate(labels):
            if index:
                result.append("   ")
            result.append("● ", style=f"bold {colors[index % len(colors)]}")
            value = values[index] if index < len(values) else 0
            result.append(f"{label} {value}", style="dim")
        result.append("\n")
    result.append(summary, style="bold")
    return result


def contribution_calendar(
    summary: str,
    color: str,
    *,
    width: int = 42,
    height: int = 11,
) -> Text:
    """Render a GitHub-style contribution calendar that expands with its panel."""
    labels = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    all_months = ("Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug")
    label_width = 4
    weeks = max(12, min(52, (width - label_width) // 2))
    graph_width = weeks * 2

    month_count = max(3, min(len(all_months), graph_width // 4))
    months = tuple(
        all_months[round(index * (len(all_months) - 1) / (month_count - 1))]
        for index in range(month_count)
    )
    header = [" "] * graph_width
    for index, month in enumerate(months):
        position = round(index * max(0, graph_width - len(month)) / (len(months) - 1))
        for offset, character in enumerate(month):
            if position + offset < graph_width:
                header[position + offset] = character

    result = Text(no_wrap=True)
    result.append(" " * label_width + "".join(header).rstrip() + "\n", style="dim")
    gap_rows = max(0, (height - 9) // 6)
    for day, label in enumerate(labels):
        result.append(f"{label:<{label_width}}", style="dim")
        for week in range(weeks):
            score = (week * 11 + day * 7 + week * day * 3 + (week // 5) * 2) % 17
            if score < 6:
                result.append("· ", style="dim")
            elif score < 10:
                result.append("▪ ", style=f"dim {color}")
            elif score < 14:
                result.append("■ ", style=color)
            else:
                result.append("■ ", style=f"bold {color}")
        result.append("\n")
        if gap_rows and day < len(labels) - 1:
            result.append("\n" * gap_rows)
    result.append(" " * label_width, style="dim")
    result.append("Less  ·  ▪  ■  ", style="dim")
    result.append("■", style=f"bold {color}")
    result.append("  More", style="dim")
    result.append(f"   │   {summary}", style=f"bold {color}")
    return result


def horizontal_bars(
    labels: tuple[str, ...],
    values: tuple[int, ...],
    colors: tuple[str, ...],
    summary: str,
    *,
    width: int = 42,
    row_spacing: int = 0,
) -> Text:
    """Render labeled proportional bars with exact values and a compact legend."""
    peak = max(values, default=1) or 1
    label_width = max((len(label) for label in labels), default=4)
    bar_width = max(8, width - label_width - 9)
    result = Text(no_wrap=True)
    rows = tuple(zip(labels, values, strict=False))
    for index, (label, value) in enumerate(rows):
        filled = round(value / peak * bar_width)
        color = colors[index % len(colors)]
        result.append(f"{label:<{label_width}}  ", style="dim")
        result.append("█" * filled, style=f"bold {color}")
        result.append("░" * (bar_width - filled), style="dim")
        result.append(f"  {value:>3}\n", style=color)
        if row_spacing and index < len(rows) - 1:
            result.append("\n" * row_spacing)
    result.append(summary, style="bold")
    return result


def vertical_bars(
    values: tuple[int, ...],
    labels: tuple[str, ...],
    summary: str,
    color: str,
    *,
    width: int = 42,
    height: int = 7,
) -> Text:
    """Render a full-width vertical histogram with category labels."""
    peak = max(values, default=1) or 1
    height = max(4, height)
    count = max(1, len(values))
    slot_width = max(3, width // count)
    bar_width = max(1, slot_width - 2)
    result = Text(no_wrap=True)
    for row in range(height, 0, -1):
        threshold = row / height
        for value in values:
            filled = value / peak >= threshold
            result.append(" " + ("█" * bar_width if filled else " " * bar_width) + " ", style=color)
        result.append("\n")
    result.append("─" * min(width, slot_width * count), style="dim")
    result.append("\n")
    for label in labels:
        result.append(f"{label:^{slot_width}}"[:slot_width], style="dim")
    result.append(f"\n{summary}", style=f"bold {color}")
    return result
