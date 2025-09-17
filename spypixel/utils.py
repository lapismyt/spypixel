from html import escape as html_escape

def generate_svg_badge(text_left: str, text_right: str, color_right: str = "#4c1") -> str:
    text_left_safe = html_escape(text_left)
    text_right_safe = html_escape(text_right)

    CHAR_WIDTH_PX = 6.5
    PADDING_PER_SIDE_PX = 5

    left_content_width_px = len(text_left_safe) * CHAR_WIDTH_PX + PADDING_PER_SIDE_PX * 2
    right_content_width_px = len(text_right_safe) * CHAR_WIDTH_PX + PADDING_PER_SIDE_PX * 2

    left_segment_width_px = max(20, round(left_content_width_px))
    right_segment_width_px = max(20, round(right_content_width_px))

    total_width_px = left_segment_width_px + right_segment_width_px
    height = 20

    left_text_x = round((left_segment_width_px / 2) * 10)
    right_text_x = round((left_segment_width_px + right_segment_width_px / 2) * 10)

    TEXT_PADDING_FOR_TEXTLENGTH = 12
    left_text_length = max(10, round(left_segment_width_px * 10 - TEXT_PADDING_FOR_TEXTLENGTH * 2))
    right_text_length = max(10, round(right_segment_width_px * 10 - TEXT_PADDING_FOR_TEXTLENGTH * 2))

    svg_template = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{total_width_px}" height="{height}" role="img" aria-label="{text_left_safe}: {text_right_safe}">
  <title>{text_left_safe}: {text_right_safe}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width_px}" height="{height}" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{left_segment_width_px}" height="{height}" fill="#555"/>
    <rect x="{left_segment_width_px}" width="{right_segment_width_px}" height="{height}" fill="{color_right}"/>
    <rect width="{total_width_px}" height="{height}" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
    <text aria-hidden="true" x="{left_text_x}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{left_text_length}">
      {text_left_safe}
    </text>
    <text x="{left_text_x}" y="140" transform="scale(.1)" textLength="{left_text_length}">
      {text_left_safe}
    </text>
    <text aria-hidden="true" x="{right_text_x}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{right_text_length}">
      {text_right_safe}
    </text>
    <text x="{right_text_x}" y="140" transform="scale(.1)" textLength="{right_text_length}">
      {text_right_safe}
    </text>
  </g>
</svg>
    """
    return svg_template.strip()