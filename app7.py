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

/* Global font size slightly smaller for GitHub deployment */
html, body, [class*="css"] {
    font-size: 22px !important;
}
h1, h2, h3 {
    font-weight: 800 !important;
}

/* TOOLBOX PANEL */
.toolbox-panel {
    background-color: rgba(25, 25, 35, 0.92);
    padding: 1.8rem;
    border-radius: 1.4rem;
    border: 1px solid rgba(255,255,255,0.18);
}

/* BUTTONS */
div.stButton > button {
    width: 100% !important;
    height: 60px !important;
    font-size: 23px !important;
    font-weight: 750 !important;
    border-radius: 14px !important;
}

/* FIX FOR GITHUB ZOOMING */
img[data-testid="stImage"] {
    object-fit: contain !important;
    max-width: 800px !important;     /* <— SIMULATION FIXED SIZE */
    height: auto !important;
    margin-left: auto !important;
    margin-right: auto !important;
    display: block !important;
}

/* Toolbox icons allowed to be larger */
.toolbox-icon img {
    max-width: 260px !important;
    width: 100% !important;
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
    "astrocyte": None,
    "scaffold": None,
    "molecules": set(),
    "cell_overlay": None,
    "astrocyte_overlay": None,
    "scaffold_overlay": None,
    "last_outcome": None,
    "last_success": None,
    "queued_animation": None
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

    if st.session_state.astrocyte_overlay:
        base.alpha_composite(load_rgba(st.session_state.astrocyte_overlay))

    if st.session_state.scaffold_overlay:
        base.alpha_composite(load_rgba(st.session_state.scaffold_overlay))

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
        canvas.image(anim)
        time.sleep(1.0)
        canvas.image(render_canvas())


# ================================================
# LAYOUT — GitHub-friendly spacing
# ================================================
canvas_col, toolbox_col = st.columns([1.0, 1.0])


# ================================================
# LEFT — SIMULATION WINDOW
# ================================================
with canvas_col:
    st.header("🧪 Regeneration Simulation")

    canvas = st.empty()
    play_if_queued(canvas)

    if st.session_state.last_outcome is None:
        canvas.image(render_canvas())
    else:
        if st.session_state.last_outcome:
            canvas.image(gif("axon_success_gif.png"))
        else:
            canvas.image(gif("axon_failure_gif.png"))

    if st.button("Run Simulation 🚀"):
        success = 0.05

        if st.session_state.intrinsic:
            success += random.uniform(0.25, 0.45)
        if st.session_state.support:
            success += random.uniform(0.20, 0.40)
        if st.session_state.astrocyte:
            success += random.uniform(0.05, 0.15)
        if st.session_state.scaffold:
            success += random.uniform(0.10, 0.25)
        if st.session_state.molecules:
            success += random.uniform(0.05, 0.15)

        success = min(success, 0.95)
        st.session_state.last_success = success

        outcome = random.random() < success
        st.session_state.last_outcome = outcome

        st.markdown(f"### Success Probability: **{success*100:.1f}%**")

        if outcome:
            st.success("Regeneration Successful 🎉")
            canvas.image(gif("axon_success_gif.png"))
        else:
            st.error("Regeneration Failed ❌")
            canvas.image(gif("axon_failure_gif.png"))

    if st.button("Reset ❌"):
        st.session_state.clear()
        st.rerun()



# ================================================
# RIGHT — TOOLBOX
# ================================================
with toolbox_col:
    st.markdown('<div class="toolbox-panel">', unsafe_allow_html=True)
    st.header("🧰 Toolbox")

    ICON_SIZE = 230

    def play_animation(path):
        queue_animation(path)
        st.rerun()

    # -------- INTRINSIC --------
    st.subheader("Intrinsic Growth Programs")
    ig1, ig2 = st.columns(2)

    with ig1:
        st.markdown('<div class="toolbox-icon">', unsafe_allow_html=True)
        st.image(icon("KLF7.png"))
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Use KLF7"):
            st.session_state.intrinsic.add("KLF7")
            play_animation(gif("AAV_gif.png"))

    with ig2:
        st.markdown('<div class="toolbox-icon">', unsafe_allow_html=True)
        st.image(icon("GAP-43_BASP1.png"))
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Use GAP-43/BASP1"):
            st.session_state.intrinsic.add("GAP43")
            play_animation(gif("AAV_gif.png"))

    ig3, ig4 = st.columns(2)
    with ig3:
        st.image(icon("CAMP_Elevation.png"))
        if st.button("Use cAMP"):
            st.session_state.intrinsic.add("cAMP")
            play_animation(gif("AAV_gif.png"))

    with ig4:
        st.image(icon("ATF3CREB.png"))
        if st.button("Use ATF3/CREB"):
            st.session_state.intrinsic.add("CREB")
            play_animation(gif("AAV_gif.png"))

    st.markdown("---")

    # -------- SUPPORT CELLS --------
    st.subheader("Support Cells")
    support_locked = st.session_state.support is not None

    sc1, sc2 = st.columns(2)
    with sc1:
        st.image(icon("SchwannCell.png"))
        if st.button("Use Schwann", disabled=support_locked and st.session_state.support!="Schwann"):
            st.session_state.support = "Schwann"
            st.session_state.cell_overlay = gif("schwann_cell_overlay.png")
            play_animation(gif("schwann_cell_gif.png"))

    with sc2:
        st.image(icon("SchwannLikeCell.png"))
        if st.button("Use Schwann-like", disabled=support_locked and st.session_state.support!="SchwannLike"):
            st.session_state.support = "SchwannLike"
            st.session_state.cell_overlay = gif("schwann_like_cells_overlay.png")
            play_animation(gif("schwann_like_cell_gif.png"))

    st.markdown("---")

    # -------- ASTROCYTES --------
    st.subheader("Astrocytes")
    ac1 = st.container()

    with ac1:
        st.image(icon("astrocyte.png"))
        if st.button("Add Astrocyte"):
            st.session_state.astrocyte = True
            st.session_state.astrocyte_overlay = gif("astrocyte_overlay.png")
            play_animation(gif("astrocyte_fadein_gif.png"))

    st.markdown("---")

    # -------- SCAFFOLDS --------
    st.subheader("Physical Scaffolds")
    scaffold_locked = st.session_state.scaffold is not None

    pf1, pf2 = st.columns(2)
    with pf1:
        st.image(icon("aligned_fibers.png"))
        if st.button("Use Aligned Fibers", disabled=scaffold_locked and st.session_state.scaffold!="Aligned"):
            st.session_state.scaffold = "Aligned"
            st.session_state.scaffold_overlay = gif("aligned_fibers_overlay.png")
            play_animation(gif("scaffold_fadein_gif.png"))

    with pf2:
        st.image(icon("laminin.png"))
        if st.button("Use Laminin", disabled=scaffold_locked and st.session_state.scaffold!="Laminin"):
            st.session_state.scaffold = "Laminin"
            st.session_state.scaffold_overlay = gif("laminin_overlay.png")
            play_animation(gif("scaffold_fadein_gif.png"))

    pf3, pf4 = st.columns(2)
    with pf3:
        st.image(icon("hydrogel_tube.png"))
        if st.button("Use Hydrogel", disabled=scaffold_locked and st.session_state.scaffold!="Hydrogel"):
            st.session_state.scaffold = "Hydrogel"
            st.session_state.scaffold_overlay = gif("hydrogel_overlay.png")
            play_animation(gif("scaffold_fadein_gif.png"))

    with pf4:
        st.image(icon("BDNF_gradient.png"))
        if st.button("Use BDNF Gradient", disabled=scaffold_locked and st.session_state.scaffold!="BDNF"):
            st.session_state.scaffold = "BDNF"
            st.session_state.scaffold_overlay = gif("BDNF_overlay.png")
            play_animation(gif("scaffold_fadein_gif.png"))

    st.markdown("---")

    # -------- SMALL MOLECULES --------
    st.subheader("Small Molecules")
    sm1, sm2 = st.columns(2)

    with sm1:
        st.image(icon("M1.png"))
        if st.button("Use M1"):
            st.session_state.molecules.add("M1")
            play_animation(gif("small_molecule_diffusion_gif.png"))

    with sm2:
        st.image(icon("SB216763.png"))
        if st.button("Use SB216763"):
            st.session_state.molecules.add("SB216763")
            play_animation(gif("small_molecule_diffusion_gif.png"))

    sm3, sm4 = st.columns(2)
    with sm3:
        st.image(icon("7,8-DHF.png"))
        if st.button("Use 7,8-DHF"):
            st.session_state.molecules.add("7,8-DHF")
            play_animation(gif("small_molecule_diffusion_gif.png"))

    with sm4:
        st.image(icon("Mexiletine.png"))
        if st.button("Use Mexiletine"):
            st.session_state.molecules.add("Mexiletine")
            play_animation(gif("small_molecule_diffusion_gif.png"))

    st.markdown("</div>", unsafe_allow_html=True)
