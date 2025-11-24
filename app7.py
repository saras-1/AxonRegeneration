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
    font-size: 27px !important;
}
h1, h2, h3 {
    font-weight: 800 !important;
}
.toolbox-panel {
    background-color: rgba(25, 25, 35, 0.92);
    padding: 2rem;
    border-radius: 1.4rem;
    border: 1px solid rgba(255,255,255,0.18);
}

/* BUTTONS */
div.stButton > button {
    width: 100% !important;
    height: 66px !important;
    font-size: 27px !important;
    font-weight: 750 !important;
    border-radius: 14px !important;
}

/* FIXED CANVAS SIZE — prevents GitHub zoom */
img[data-testid="stImage"] {
    width: 900px !important;
    max-width: 900px !important;
    height: auto !important;
    object-fit: contain !important;
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
# SESSION STATE DEFAULTS
# ================================================
defaults = {
    "intrinsic": set(),
    "support": None,
    "scaffold": None,
    "molecules": set(),
    "astrocyte": False,
    "cell_overlay": None,
    "scaffold_overlay": None,
    "astrocyte_overlay": None,
    "queued_animation": None,
    "last_outcome": None,
    "last_success": None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================================================
# IMAGE HANDLING
# ================================================
def load_rgba(path):
    return Image.open(path).convert("RGBA")

def render_canvas():
    base = load_rgba(BASE_IMAGE)

    if st.session_state.cell_overlay:
        base.alpha_composite(load_rgba(st.session_state.cell_overlay))

    if st.session_state.scaffold_overlay:
        base.alpha_composite(load_rgga(st.session_state.scaffold_overlay))

    if st.session_state.astrocyte_overlay:
        base.alpha_composite(load_rgba(st.session_state.astrocyte_overlay))

    return base

# ================================================
# ANIMATIONS
# ================================================
def queue_animation(path):
    st.session_state.queued_animation = path

def play_if_queued(canvas):
    if st.session_state.queued_animation:
        anim = st.session_state.queued_animation
        st.session_state.queued_animation = None
        canvas.image(anim, width=900)
        time.sleep(1.0)
        canvas.image(render_canvas(), width=900)

# ================================================
# LAYOUT
# ================================================
canvas_col, toolbox_col = st.columns([1.1, 0.9])

# ================================================
# LEFT — SIMULATION
# ================================================
with canvas_col:
    st.header("🧪 Regeneration Simulation")

    canvas = st.empty()
    play_if_queued(canvas)

    if st.session_state.last_outcome is None:
        canvas.image(render_canvas(), width=900)
    else:
        outcome_img = "axon_success_gif.png" if st.session_state.last_outcome else "axon_failure_gif.png"
        canvas.image(gif(outcome_img), width=900)

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
        if st.session_state.astrocyte:
            success -= random.uniform(0.10, 0.20)

        success = max(min(success, 0.95), 0.01)

        st.session_state.last_success = success
        st.markdown(f"### Success Probability: **{success*100:.1f}%**")

        result = random.random() < success
        st.session_state.last_outcome = result

        canvas.image(gif("axon_success_gif.png" if result else "axon_failure_gif.png"), width=900)

    if st.button("Reset ❌"):
        st.session_state.clear()
        st.rerun()

# ================================================
# RIGHT — TOOLBOX WITH TABS
# ================================================
with toolbox_col:
    st.markdown('<div class="toolbox-panel">', unsafe_allow_html=True)
    st.header("🧰 Toolbox")

    ICON_SIZE = 250
    def play_animation(path):
        queue_animation(path)
        st.rerun()

    # All tabs
    tab_intrinsic, tab_support, tab_scaffold, tab_molecules = st.tabs(
        ["Intrinsic Growth Programs", "Support Cells", "Physical Scaffolds", "Small Molecules"]
    )

    # ----------------------------------------------------
    # INTRINSIC TAB
    # ----------------------------------------------------
    with tab_intrinsic:
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

    # ----------------------------------------------------
    # SUPPORT CELLS TAB  (Astrocytes moved here)
    # ----------------------------------------------------
with tab_support:

    support_locked = st.session_state.support is not None

    sc1, sc2 = st.columns(2)

    with sc1:
        st.image(icon("SchwannCell.png"), width=ICON_SIZE)
        if st.button("Use Schwann", disabled=support_locked and st.session_state.support!="Schwann"):
            st.session_state.support = "Schwann"
            st.session_state.cell_overlay = gif("schwann_cell_overlay.png")
            play_animation(gif("schwann_cell_gif.png"))

    with sc2:
        st.image(icon("SchwannLikeCell.png"), width=ICON_SIZE)
        if st.button("Use Schwann-like", disabled=support_locked and st.session_state.support!="SchwannLike"):
            st.session_state.support = "SchwannLike"
            st.session_state.cell_overlay = gif("schwann_like_cells_overlay.png")
            play_animation(gif("schwann_like_cell_gif.png"))

    # ⭐ ASTROCYTES GO HERE — still inside tab_support ⭐
    ac1, ac2 = st.columns(2)

    with ac1:
        st.image(icon("astrocyte.png"), width=ICON_SIZE)

    with ac2:
        if st.button("Use Astrocytes", disabled=support_locked and st.session_state.support!="Astrocytes"):
            st.session_state.support = "Astrocytes"
            st.session_state.cell_overlay = gif("astrocyte_overlay.png")
            play_animation(gif("astrocyte_fadein_gif.png"))



    # ----------------------------------------------------
    # SCAFFOLDS TAB
    # ----------------------------------------------------
    with tab_scaffold:
        scaffold_locked = st.session_state.scaffold is not None

        pf1, pf2 = st.columns(2)

        with pf1:
            st.image(icon("aligned_fibers.png"), width=ICON_SIZE)
            if st.button("Use Aligned Fibers", disabled=scaffold_locked and st.session_state.scaffold!="Aligned"):
                st.session_state.scaffold = "Aligned"
                st.session_state.scaffold_overlay = gif("aligned_fibers_overlay.png")
                play_animation(gif("scaffold_fadein_gif.png"))

        with pf2:
            st.image(icon("laminin.png"), width=ICON_SIZE)
            if st.button("Use Laminin", disabled=scaffold_locked and st.session_state.scaffold!="Laminin"):
                st.session_state.scaffold = "Laminin"
                st.session_state.scaffold_overlay = gif("laminin_overlay.png")
                play_animation(gif("scaffold_fadein_gif.png"))

        pf3, pf4 = st.columns(2)

        with pf3:
            st.image(icon("hydrogel_tube.png"), width=ICON_SIZE)
            if st.button("Use Hydrogel", disabled=scaffold_locked and st.session_state.scaffold!="Hydrogel"):
                st.session_state.scaffold = "Hydrogel"
                st.session_state.scaffold_overlay = gif("hydrogel_overlay.png")
                play_animation(gif("scaffold_fadein_gif.png"))

        with pf4:
            st.image(icon("BDNF_gradient.png"), width=ICON_SIZE)
            if st.button("Use BDNF Gradient", disabled=scaffold_locked and st.session_state.scaffold!="BDNF"):
                st.session_state.scaffold = "BDNF"
                st.session_state.scaffold_overlay = gif("BDNF_overlay.png")
                play_animation(gif("scaffold_fadein_gif.png"))

    # ----------------------------------------------------
    # SMALL MOLECULES TAB
    # ----------------------------------------------------
    with tab_molecules:
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
