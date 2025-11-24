import streamlit as st
import random
import os
import time
from PIL import Image

# ================================================
# PAGE CONFIG + STYLE
# ================================================
st.set_page_config(page_title="Axon Regeneration Simulator", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 22px !important;
}
h1, h2, h3 {
    font-weight: 800 !important;
}
.toolbox-panel {
    background-color: rgba(25, 25, 35, 0.92);
    padding: 1.5rem;
    border-radius: 1rem;
    border: 1px solid rgba(255,255,255,0.12);
}
div.stButton > button {
    width: 100% !important;
    height: 60px !important;
    font-size: 22px !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# ================================================
# PATH HELPERS
# ================================================
def icon(name): return os.path.join("icons", name)
def gif(name): return os.path.join("gifs", name)

BASE_IMAGE = icon("injured_axon_gap.png")

# ================================================
# SESSION STATE INIT (exclusive logic)
# ================================================
if "intrinsic" not in st.session_state:
    st.session_state.intrinsic = set()

if "support" not in st.session_state:
    st.session_state.support = None

if "scaffold" not in st.session_state:
    st.session_state.scaffold = None

if "molecules" not in st.session_state:
    st.session_state.molecules = set()

if "cell_overlay" not in st.session_state:
    st.session_state.cell_overlay = None

if "scaffold_overlay" not in st.session_state:
    st.session_state.scaffold_overlay = None

if "last_outcome" not in st.session_state:
    st.session_state.last_outcome = None

if "last_success" not in st.session_state:
    st.session_state.last_success = None

# ================================================
# CANVAS RENDER
# ================================================
def load_rgba(path):
    return Image.open(path).convert("RGBA")

def render_canvas():
    base = load_rgba(BASE_IMAGE)

    if st.session_state.cell_overlay:
        base.alpha_composite(load_rgba(st.session_state.cell_overlay))

    if st.session_state.scaffold_overlay:
        base.alpha_composite(load_rgba(st.session_state.scaffold_overlay))

    return base

# ================================================
# LAYOUT
# ================================================
canvas_col, toolbox_col = st.columns([1, 1])

# ================================================
# LEFT — MAIN SIMULATION WINDOW
# ================================================
with canvas_col:
    st.header("🧪 Regeneration Simulation")

    canvas = st.empty()

    # Startup
    if st.session_state.last_outcome is None:
        canvas.image(render_canvas(), width=1100)
    else:
        if st.session_state.last_outcome:
            canvas.image(gif("axon_success_gif.png"), width=1100)
        else:
            canvas.image(gif("axon_failure_gif.png"), width=1100)

    # ---- RUN SIMULATION ----
    if st.button("Run Simulation 🚀"):
        success = 0.05
        if st.session_state.intrinsic:
            success += random.uniform(0.25, 0.45)
        if st.session_state.support:
            success += random.uniform(0.20, 0.40)
        if st.session_state.scaffold:
            success += random.uniform(0.10, 0.25)
        if st.session_state.molecules:
            success += random.uniform(0.05, 0.15)

        success = min(success, 0.95)
        st.session_state.last_success = success
        st.markdown(f"### Success Probability: **{success*100:.1f}%**")

        outcome = random.random() < success
        st.session_state.last_outcome = outcome

        if outcome:
            st.success("Regeneration Successful 🎉")
            canvas.image(gif("axon_success_gif.png"), width=1100)
        else:
            st.error("Regeneration Failed ❌")
            canvas.image(gif("axon_failure_gif.png"), width=1100)

    # ---- RESET ----
    if st.button("Reset ❌"):
        st.session_state.clear()
        st.stop()

# ================================================
# RIGHT — TOOLBOX
# ================================================
with toolbox_col:
    st.markdown('<div class="toolbox-panel">', unsafe_allow_html=True)
    st.header("🧰 Toolbox")

    ICON_SIZE = 160

    # ======================================================
    # INSTANT ANIMATION FUNCTION (fixes lag completely)
    # ======================================================
    def play_animation(animation_path):
        """Instantly show animation in canvas, then return to overlays."""
        canvas.image(animation_path, width=1100)
        time.sleep(1.0)
        canvas.image(render_canvas(), width=1100)
        st.stop()

    # ======================================================
    # INTRINSIC GROWTH
    # ======================================================
    st.subheader("Intrinsic Growth Programs")

    ig1, ig2 = st.columns(2)
    with ig1:
        st.image(icon("KLF7.png"), width=ICON_SIZE)
        if st.button("Use KLF7"):
            st.session_state.intrinsic.add("KLF7")
            play_animation(gif("AAV_gif.png"))

    with ig2:
        st.image(icon("GAP-43_BASP1.png"), width=ICON_SIZE)
        if st.button("Use GAP-43/BASP1"):
            st.session_state.intrinsic.add("GAP43")
            play_animation(gif("AAV_gif.png"))

    ig3, ig4 = st.columns(2)
    with ig3:
        st.image(icon("CAMP_Elevation.png"), width=ICON_SIZE)
        if st.button("Use cAMP"):
            st.session_state.intrinsic.add("cAMP")
            play_animation(gif("AAV_gif.png"))

    with ig4:
        st.image(icon("ATF3CREB.png"), width=ICON_SIZE)
        if st.button("Use ATF3/CREB"):
            st.session_state.intrinsic.add("CREB")
            play_animation(gif("AAV_gif.png"))

    st.markdown("---")

    # ======================================================
    # SUPPORT CELLS (EXCLUSIVE)
    # ======================================================
    st.subheader("Support Cells")
    disabled_support = st.session_state.support is not None

    sc1, sc2 = st.columns(2)
    with sc1:
        st.image(icon("SchwannCell.png"), width=ICON_SIZE)
        if st.button("Use Schwann", disabled=disabled_support and st.session_state.support!="Schwann"):
            st.session_state.support = "Schwann"
            st.session_state.cell_overlay = gif("schwann_cell_overlay.png")
            play_animation(gif("schwann_cell_gif.png"))

    with sc2:
        st.image(icon("SchwannLikeCell.png"), width=ICON_SIZE)
        if st.button("Use Schwann-like", disabled=disabled_support and st.session_state.support!="SchwannLike"):
            st.session_state.support = "SchwannLike"
            st.session_state.cell_overlay = gif("schwann_like_cells_overlay.png")
            play_animation(gif("schwann_like_cell_gif.png"))

    st.markdown("---")

    # ======================================================
    # PHYSICAL SCAFFOLDS (EXCLUSIVE)
    # ======================================================
    st.subheader("Physical Scaffolds")
    disabled_scaffold = st.session_state.scaffold is not None

    pf1, pf2 = st.columns(2)
    with pf1:
        st.image(icon("aligned_fibers.png"), width=ICON_SIZE)
        if st.button("Use Aligned Fibers", disabled=disabled_scaffold and st.session_state.scaffold!="Aligned"):
            st.session_state.scaffold = "Aligned"
            st.session_state.scaffold_overlay = gif("aligned_fibers_overlay.png")
            play_animation(gif("scaffold_fadein_gif.png"))

    with pf2:
        st.image(icon("laminin.png"), width=ICON_SIZE)
        if st.button("Use Laminin", disabled=disabled_scaffold and st.session_state.scaffold!="Laminin"):
            st.session_state.scaffold = "Laminin"
            st.session_state.scaffold_overlay = gif("scaffold_fadein_gif.png")
            play_animation(gif("scaffold_fadein_gif.png"))

    pf3, pf4 = st.columns(2)
    with pf3:
        st.image(icon("hydrogel_tube.png"), width=ICON_SIZE)
        if st.button("Use Hydrogel", disabled=disabled_scaffold and st.session_state.scaffold!="Hydrogel"):
            st.session_state.scaffold = "Hydrogel"
            st.session_state.scaffold_overlay = gif("hydrogel_overlay.png")
            play_animation(gif("scaffold_fadein_gif.png"))

    with pf4:
        st.image(icon("BDNF_gradient.png"), width=ICON_SIZE)
        if st.button("Use BDNF Gradient", disabled=disabled_scaffold and st.session_state.scaffold!="BDNF"):
            st.session_state.scaffold = "BDNF"
            st.session_state.scaffold_overlay = gif("scaffold_fadein_gif.png")
            play_animation(gif("scaffold_fadein_gif.png"))

    st.markdown("---")

    # ======================================================
    # SMALL MOLECULES (NOT EXCLUSIVE)
    # ======================================================
    st.subheader("Small Molecules")

    sm1, sm2 = st.columns(2)
    with sm1:
        st.image(icon("M1.png"), width=ICON_SIZE)
        if st.button("Use M1"):
            st.session_state.molecules.add("M1")
            play_animation(gif("small_molecule_diffusion_gif.png"))

    with sm2:
        st.image(icon("SB216763.png"), width=ICON_SIZE)
        if st.button("Use SB216763"):
            st.session_state.molecules.add("SB216763")
            play_animation(gif("small_molecule_diffusion_gif.png"))

    sm3, sm4 = st.columns(2)
    with sm3:
        st.image(icon("7,8-DHF.png"), width=ICON_SIZE)
        if st.button("Use 7,8-DHF"):
            st.session_state.molecules.add("7,8-DHF")
            play_animation(gif("small_molecule_diffusion_gif.png"))

    with sm4:
        st.image(icon("Mexiletine.png"), width=ICON_SIZE)
        if st.button("Use Mexiletine"):
            st.session_state.molecules.add("Mexiletine")
            play_animation(gif("small_molecule_diffusion_gif.png"))

    st.markdown("</div>", unsafe_allow_html=True)
