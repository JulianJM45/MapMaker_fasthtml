"""The stylesheet now carries behaviour that used to live in JavaScript.

These tests pin the rules that replaced imperative code, so that deleting one
by accident fails here rather than silently in a browser.
"""

import re

RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")


def rules(css):
    """`[(selector, {property: value}), ...]`, comments stripped."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    parsed = []
    for selector, body in RULE.findall(css):
        declarations = {}
        for declaration in body.split(";"):
            if ":" in declaration:
                name, _, value = declaration.partition(":")
                declarations[name.strip()] = value.strip()
        parsed.append((" ".join(selector.split()), declarations))
    return parsed


def declarations_for(css, selector):
    merged = {}
    for parsed_selector, declarations in rules(css):
        if parsed_selector == selector:
            merged.update(declarations)
    return merged


def test_panel_is_hidden_until_the_toggle_is_checked(styles):
    assert declarations_for(styles, "#configuration-form")["display"] == "none"
    assert (
        declarations_for(styles, "#configure-toggle:checked ~ #configuration-form")[
            "display"
        ]
        == "block"
    )


def test_autozoom_blurs_and_disables_the_manual_zoom_row(styles):
    rule = declarations_for(
        styles,
        "#configuration-form:has(#AutoZoom:checked) :is(#zoomLabel, #zoom, #showZoomLevel)",
    )

    assert rule["filter"] == "blur(2px)", "same blur the old JS applied"
    assert rule["pointer-events"] == "none", (
        "replaces the old `element.disabled = true`"
    )


def test_pill_tracks_the_checked_radio(styles):
    assert declarations_for(styles, ".toggle-pill")["transition"] == "left 0.5s"
    assert (
        declarations_for(
            styles, ".button-box:has(.toggle-input:first-of-type:checked) .toggle-pill"
        )["left"]
        == "0"
    )
    assert (
        declarations_for(
            styles, ".button-box:has(.toggle-input:last-of-type:checked) .toggle-pill"
        )["left"]
        == "50%"
    )


def test_pill_colours_and_widths_are_unchanged(styles):
    assert declarations_for(styles, ".button-box")["width"] == "300px"
    assert declarations_for(styles, ".orientation-box")["width"] == "250px"
    # 50% of the two boxes above -- previously hard-coded as 150px and 125px.
    assert declarations_for(styles, ".toggle-pill")["width"] == "50%"
    assert declarations_for(styles, "#btn")["background"] == "var(--pill-format)"
    assert (
        declarations_for(styles, "#orientationBtn")["background"]
        == "var(--pill-orientation)"
    )

    root = declarations_for(styles, ":root")
    assert root["--pill-format"] == "#0fc1ee"
    assert root["--pill-orientation"] == "#28a745"


def test_log_sits_behind_the_map_until_a_render_starts(styles):
    assert declarations_for(styles, "#log")["z-index"] == "0"
    assert declarations_for(styles, "#log.log-active")["z-index"] == "1000"


def test_slope_legend_starts_hidden(styles):
    assert declarations_for(styles, ".slope-legend")["display"] == "none"
    assert declarations_for(styles, ".slope-legend-container")["display"] == "flex"


def test_stacking_order_is_preserved(styles):
    assert declarations_for(styles, "#map")["z-index"] == "1"
    assert declarations_for(styles, ".control-btn")["z-index"] == "800"
    assert declarations_for(styles, "#configuration-form")["z-index"] == "900"


def test_control_buttons_keep_their_positions(styles):
    assert declarations_for(styles, ".control-btn")["top"] == "180px"
    assert declarations_for(styles, "#download-button")["top"] == "220px"

    gpx = declarations_for(styles, "#gpxButton")
    assert gpx["top"] == "290px"
    assert gpx["left"] == "10px"
    assert gpx["right"] == "auto", (
        "the shared rule pins it right; GPX overrides to the left"
    )


def test_hidden_inputs_stay_in_the_accessibility_tree(styles):
    """`display: none` inputs are unreachable by keyboard; clipping is not."""
    hidden = declarations_for(styles, ".visually-hidden")

    assert hidden.get("display") != "none"
    assert hidden["position"] == "absolute"
    assert hidden["clip-path"] == "inset(50%)"
