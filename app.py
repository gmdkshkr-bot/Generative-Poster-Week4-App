# app.py
import streamlit as st
import random, math, numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io

# --- Utility: Color brightness ---
def luminance(rgb):
    r, g, b = rgb
    return 0.299*r + 0.587*g + 0.114*b

# --- Color Palette ---
def random_palette(style="pastel", k=20):
    if style=="pastel":
        colors = [(0.6+0.4*random.random(), 0.6+0.4*random.random(), 0.6+0.4*random.random()) for _ in range(k)]
    elif style=="neon":
        colors = [(random.uniform(0.5,1), random.uniform(0,1), random.uniform(0.5,1)) for _ in range(k)]
    elif style=="monochrome":
        base = random.random()
        colors = [(base+0.1*random.random(),)*3 for _ in range(k)]
    elif style=="earth":
        earth_tones = [
            (0.42,0.26,0.15),(0.55,0.47,0.37),(0.62,0.74,0.55),
            (0.84,0.78,0.58),(0.40,0.55,0.30)
        ]
        colors = [random.choice(earth_tones) for _ in range(k)]
    elif style=="ocean":
        ocean_tones = [
            (0.0,0.3,0.5),(0.1,0.6,0.8),(0.2,0.8,0.9),
            (0.0,0.5,0.4),(0.4,0.9,1.0)
        ]
        colors = [random.choice(ocean_tones) for _ in range(k)]
    elif style=="sunset":
        sunset_tones = [
            (1.0,0.5,0.0),(1.0,0.2,0.3),(0.8,0.3,0.6),
            (0.6,0.2,0.8),(0.9,0.7,0.3)
        ]
        colors = [random.choice(sunset_tones) for _ in range(k)]
    elif style=="cyberpunk":
        cyber_colors = [
            (1.0,0.0,0.8),(0.0,1.0,1.0),(0.2,0.2,1.0),
            (1.0,0.8,0.1),(0.1,0.0,0.1)
        ]
        colors = [random.choice(cyber_colors) for _ in range(k)]
    else:
        colors = [(random.random(), random.random(), random.random()) for _ in range(k)]
    return colors

# --- Shape Generators ---
def blob(center=(0.5,0.5), r=0.2, points=1000, wobble=0.15):
    angles = np.linspace(0,2*math.pi,points)
    radii = r*(1+wobble*(np.random.rand(points)-0.5))
    x = center[0] + radii*np.cos(angles)
    y = center[1] + radii*np.sin(angles)
    return x, y

def shape(center=(0.5,0.5), r=0.2, points=1000, wobble=0.15, shape_type="blob"):
    if shape_type=="circle":
        angles = np.linspace(0,2*np.pi,points)
        x = center[0] + r*np.cos(angles)
        y = center[1] + r*np.sin(angles)
        return x, y
    elif shape_type=="polygon":
        global n_sides
        n_sides = n_sides
        angles = np.linspace(0,2*np.pi,n_sides,endpoint=False)
        x = center[0] + r*np.cos(angles)
        y = center[1] + r*np.sin(angles)
        return np.append(x,x[0]), np.append(y,y[0])
    else:
        return blob(center,r,points,wobble)

# --- Rotate coordinates for 3D effect ---
def rotate_coords(x, y, cx, cy, angle):
    x_rot = (x-cx)*np.cos(angle) - (y-cy)*np.sin(angle) + cx
    y_rot = (x-cx)*np.sin(angle) + (y-cy)*np.cos(angle) + cy
    return x_rot, y_rot

# --- 3D Poster Generator ---
def generate_3d_poster(
    style="pastel", shape_type="blob", n_layers=30, wobble=0.03,
    background="#FFFFFF", title_color="#000000", seed=None,
    shadow_offset=0.02, brightness_strength=0.3,
    alpha_min=0.6, alpha_max=0.9, light_angle=45,
    rotation_range=0.3
):
    random.seed(seed)
    np.random.seed(seed)
    plt.close("all")
    fig = plt.figure(figsize=(7,10), facecolor=background)
    ax = plt.gca()
    ax.axis("off")
    ax.set_facecolor(background)

    palette = random_palette(style, 20)
    dx = shadow_offset * math.cos(math.radians(light_angle))
    dy = -shadow_offset * math.sin(math.radians(light_angle))

    
    for i in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.01,0.25)
        
        # Shadow
        x_s, y_s = shape(center=(cx+dx, cy+dy), r=rr, wobble=wobble, shape_type=shape_type)
        angle = random.uniform(-rotation_range, rotation_range)
        x_s, y_s = rotate_coords(x_s, y_s, cx+dx, cy+dy, angle)
        plt.fill(x_s, y_s, color=(0,0,0), alpha=0.45, edgecolor=(0,0,0,0))

        # Actual shape
        x, y = shape(center=(cx,cy), r=rr, wobble=wobble, shape_type=shape_type)
        x, y = rotate_coords(x, y, cx, cy, angle)
        base_color = np.array(random.choice(palette))
        brightness_factor = 0.7 + brightness_strength*(i/n_layers)
        color = np.clip(base_color*brightness_factor,0,1)
        alpha = random.uniform(alpha_min, alpha_max)
        plt.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))

    # Adjust text color if contrast is too low
    bg_rgb = tuple(int(background.lstrip("#")[i:i+2],16)/255 for i in (0,2,4))
    text_rgb = tuple(int(title_color.lstrip("#")[i:i+2],16)/255 for i in (0,2,4))
    if abs(luminance(bg_rgb)-luminance(text_rgb))<0.5:
        title_color="#FFFFFF" if luminance(bg_rgb)<0.5 else "#000000"

    # Text
    plt.text(0.01,0.95,"3D like Generative Poster",fontsize=26,weight="bold",
             color=title_color,transform=ax.transAxes,alpha=1.0)
    plt.text(0.01,0.91,"Week 4 • Arts & Big Data",fontsize=14,
             color=title_color,transform=ax.transAxes,alpha=1.0)
    plt.text(0.01,0.88,f"Style: {style.title()} / Shape: {shape_type.title()}",fontsize=13,
             color=title_color,transform=ax.transAxes,alpha=1.0)

    plt.xlim(0,1)
    plt.ylim(0,1)
    return fig

# === Streamlit UI ===
st.title("🎨 Generative 3D Poster")

style = st.sidebar.selectbox("Style", ['pastel','neon','monochrome','earth','ocean','sunset','cyberpunk'])
shape_type = st.sidebar.selectbox("Shape Type", ['blob','circle','polygon'])
n_sides = st.sidebar.slider("Polygon Sides", 3, 10, 6, 1)
n_layers = st.sidebar.slider("Layers", 5, 60, 30)
wobble = st.sidebar.slider("Blob Wobble", 0.0, 1.0, 0.4, 0.05)
background = st.sidebar.color_picker("Background", "#FFFFFF")
title_color = st.sidebar.color_picker("adjust Text Color if contrast is too low", "#000000")
seed = st.sidebar.slider("Seed", value=0, step=1)
# seed = st.sidebar.number_input("Seed", value=0, step=1)
shadow_offset = st.sidebar.slider("Shadow Offset", 0.0, 0.1, 0.02, 0.005)
brightness_strength = st.sidebar.slider("Brightness Strength", 0.0, 0.9, 0.3, 0.05)
alpha_min = st.sidebar.slider("Alpha Min", 0.1, 1.0, 0.6, 0.05)
alpha_max = st.sidebar.slider("Alpha Max", 0.1, 1.0, 0.9, 0.05)
light_angle = st.sidebar.slider("Light Angle", 0, 360, 45, 5)
rotation_range = st.sidebar.slider("Rotation Range", 0.0, 1.0, 0.3, 0.05)

fig = generate_3d_poster(
    style=style, shape_type=shape_type, n_layers=n_layers, wobble=wobble,
    background=background, title_color=title_color, seed=seed,
    shadow_offset=shadow_offset, brightness_strength=brightness_strength,
    alpha_min=alpha_min, alpha_max=alpha_max, light_angle=light_angle,
    rotation_range=rotation_range
)

st.pyplot(fig)

# Download
buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", facecolor=background)
buf.seek(0)
st.download_button("💾 Download Poster", data=buf, file_name=f"poster_seed{seed}.png", mime="image/png")
