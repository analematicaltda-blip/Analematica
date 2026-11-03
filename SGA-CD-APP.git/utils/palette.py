"""Normalize legacy white controls without changing their actions or contents."""
SKY = "#38BDF8"
SURFACE = "#0D1424"
PALE_COLORS = {"white", "white70", "white54", "white60", "white24", "#fff", "#ffffff", "#e2e8f0", "#f8fafc", "#f7f9f9", "#efefef"}

def apply_sky_palette(control, seen=None):
    if control is None:
        return
    if seen is None:
        seen = set()
    if id(control) in seen:
        return
    seen.add(id(control))
    for attr in ("color", "bgcolor"):
        value = getattr(control, attr, None)
        if isinstance(value, str) and value.lower() in PALE_COLORS:
            setattr(control, attr, SURFACE if attr == "bgcolor" else SKY)
    for attr in ("controls", "content", "actions", "title", "subtitle", "leading", "trailing", "appbar", "drawer", "navigation_bar", "floating_action_button", "spans", "tabs"):
        children = getattr(control, attr, None)
        if isinstance(children, (list, tuple)):
            for child in children:
                apply_sky_palette(child, seen)
        elif children is not None and not isinstance(children, (str, int, float, bool)):
            apply_sky_palette(children, seen)


def fit_view_widths(control, available_width, seen=None):
    """Constrain fixed-width controls and restore their size when space returns."""
    if control is None or not available_width:
        return
    if seen is None:
        seen = set()
    if id(control) in seen:
        return
    seen.add(id(control))
    width = getattr(control, "width", None)
    original = getattr(control, "_sgacd_original_width", width)
    if isinstance(original, (int, float)) and original > 0:
        control._sgacd_original_width = original
        control.width = min(original, max(240, available_width - 32))
    for attr in ("controls", "content", "actions", "appbar", "drawer"):
        child = getattr(control, attr, None)
        if isinstance(child, (list, tuple)):
            for item in child:
                fit_view_widths(item, available_width, seen)
        elif child is not None and not isinstance(child, (str, int, float, bool)):
            fit_view_widths(child, available_width, seen)
