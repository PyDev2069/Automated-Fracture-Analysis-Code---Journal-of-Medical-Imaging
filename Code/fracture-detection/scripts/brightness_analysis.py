import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance
import numpy as np




def adjust_brightness(img: Image.Image, percent: float) -> Image.Image:

    factor = 1 + (percent / 100.0)
    return ImageEnhance.Brightness(img).enhance(factor)


def plot_intensity_graph(ax: plt.Axes, orig: Image.Image, modified: Image.Image) -> None:
    o = np.array(orig.convert("L")).flatten()
    m = np.array(modified.convert("L")).flatten()
    ax.plot(o, label="Original", linewidth=1)
    ax.plot(m, label="Adjusted", linewidth=1)
    ax.tick_params(labelsize=6)
    ax.legend(fontsize=6)



paths = ["test.jpg", "test2.jpg", "test3.jpg", "test4.jpg"]
images = [Image.open(p).convert("RGB") for p in paths]
brightness_levels = [-15, -10, -5, 5, 10, 15]
fig1 = plt.figure(figsize=(32, 20))
rows = len(images)
cols = len(brightness_levels) + 1   
index = 1
for img in images:
    for b in [None] + brightness_levels:  
        ax = fig1.add_subplot(rows, cols, index)
        show_img = img.resize((600, 600)) if b is None else adjust_brightness(img, b).resize((600, 600))
        ax.imshow(show_img)
        ax.set_title("Original" if b is None else f"{b:+d}%", fontsize=8)
        ax.axis("off")
        index += 1

plt.subplots_adjust(wspace=0.15, hspace=0.25)
plt.suptitle("Figure 1 – X-ray Brightness Variants", fontsize=16, y=1.01)
plt.savefig("static/outputs/figure1_image_grid.png", dpi=150, bbox_inches="tight")
plt.show()




fig2 = plt.figure(figsize=(32, 28))
rows = len(images)
cols = len(brightness_levels)
index = 1
for img in images:
    for b in brightness_levels:
        ax = fig2.add_subplot(rows, cols, index)
        bright_img = adjust_brightness(img, b)
        plot_intensity_graph(ax, img, bright_img)
        ax.set_title(f"Δ{b:+d}%", fontsize=7)
        index += 1

plt.subplots_adjust(wspace=0.25, hspace=0.55)
plt.suptitle("Figure 2 – Pixel Intensity Distribution Shift", fontsize=16, y=1.01)
plt.savefig("static/outputs/figure2_intensity_curves.png", dpi=150, bbox_inches="tight")
plt.show()
