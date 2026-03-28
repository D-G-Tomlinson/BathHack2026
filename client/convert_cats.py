"""Run once to convert SVG cat images to PNGs for pygame."""
import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
CATS = ["Brown_cat", "Grey_cat", "Orange_cat", "White_cat"]

# Block cairocffi so rlPyCairo falls back to pycairo
import importlib, types
bad = types.ModuleType("cairocffi")
bad.__spec__ = importlib.util.spec_from_loader("cairocffi", loader=None)
sys.modules["cairocffi"] = bad  # makes 'import cairocffi' succeed but it's empty

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM

    for name in CATS:
        src = os.path.join(HERE, "Images", f"{name}.svg")
        dst = os.path.join(HERE, "Images", f"{name}.png")
        drawing = svg2rlg(src)
        renderPM.drawToFile(drawing, dst, fmt="PNG")
        print(f"Saved {dst}")
    print("Done!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback; traceback.print_exc()
