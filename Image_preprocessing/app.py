import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2 as cv
import os
import uuid
from utils import *


class ImagePreprocessing:
    """
    A simple GUI tool for image preprocessing:
    - Load images from a folder
    - Display images on canvas
    - Draw bounding boxes
    - Crop and save selected regions
    - Navigate through images
    """

    def __init__(self, root, state):
        """
        Initialize the application.

        Args:
            root (tk.Tk): Main Tkinter window
            state (dict): Shared state for drawing bounding box
        """
        self.root = root
        self.state = state

        self.root.title("Image Preprocessing")
        self.root.geometry("1000x700")

        self.folder_path = None
        self.image_paths = []
        self.current_index = 0
        self.current_frame = None

        self._init_layout()

    # =========================
    # UI LAYOUT
    # =========================
    def _init_layout(self):
        """Initialize full UI layout."""
        self._init_header()
        self._init_center()
        self._init_footer()

    def _init_header(self):
        """Create header section."""
        header = tk.Frame(self.root, bg="#f5f5f5", height=50)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Image Preprocessing",
            font=("Times New Roman", 16, "bold"),
            bg="#f5f5f5"
        ).pack(pady=10)

    def _init_center(self):
        """Create main area (canvas + control panel)."""
        center = tk.Frame(self.root)
        center.pack(fill="both", expand=True)

        # Canvas
        self.canvas = tk.Canvas(center, bg="black", highlightthickness=0)
        self.canvas.pack(side="left", padx=5, pady=20)

        self.canvas_img = self.canvas.create_image(0, 0, anchor="nw")

        # Control panel
        panel = tk.Frame(center, width=300, bg="#eeeeee")
        panel.pack(side="right", fill="y")
        panel.pack_propagate(False)

        self._create_button(panel, "Choose Folder", self.choose_folder, 20)
        self._create_button(panel, "Draw BBox",
                            lambda: toggle_draw(self.canvas, self.state, self.root), 10)
        self._create_button(panel, "Capture", self.capture, 10)
        self._create_button(panel, "Next", self.next, 10)

    def _init_footer(self):
        """Create footer section."""
        footer = tk.Frame(self.root, bg="#f5f5f5", height=30)
        footer.pack(fill="x")

        tk.Label(footer, text="", bg="#f5f5f5").pack(pady=5)

    def _create_button(self, parent, text, command, pady):
        """Helper to create consistent buttons."""
        tk.Button(
            parent,
            text=text,
            command=command,
            font=("Times New Roman", 12),
            width=15
        ).pack(pady=pady)

    # =========================
    # EVENT HANDLERS
    # =========================
    def choose_folder(self):
        """
        Open folder dialog and load images.
        Display the first image if available.
        """
        self.folder_path = filedialog.askdirectory()
        if not self.folder_path:
            return

        print("Chosen folder:", self.folder_path)

        exts = (".jpg", ".jpeg", ".png", ".bmp")
        self.image_paths = [
            os.path.join(self.folder_path, f)
            for f in os.listdir(self.folder_path)
            if f.lower().endswith(exts)
        ]

        if not self.image_paths:
            messagebox.showerror("Error", "Folder does not contain images!")
            return

        self.current_index = 0
        self.show_image(self.image_paths[self.current_index])

    def show_image(self, path):
        """
        Display an image on the canvas.

        Args:
            path (str): Path to image file
        """
        img = cv.imread(path)
        self.current_frame = img.copy()

        h, w = img.shape[:2]
        self.canvas.config(width=w, height=h)

        img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        self.tk_img = ImageTk.PhotoImage(img_pil)
        self.canvas.itemconfig(self.canvas_img, image=self.tk_img)
        self.canvas.coords(self.canvas_img, 0, 0)

        # Ensure bounding box stays on top
        if self.state.get("rect_id"):
            self.canvas.tag_raise(self.state["rect_id"])

    def capture(self):
        """
        Crop the selected bounding box area and save it as a new image.
        """
        if not self.folder_path:
            messagebox.showerror("Error", "Please select a folder first!")
            return

        if not self.state.get("points"):
            messagebox.showerror("Error", "Please draw a bounding box first!")
            return

        x1, y1, x2, y2 = self.state["points"]
        img_cropped = crop_image(self.current_frame, x1, y1, x2, y2)

        base = os.path.basename(self.image_paths[self.current_index])
        name, ext = os.path.splitext(base)

        img_name = f"cropped_{name}_{uuid.uuid4().hex[:8]}{ext}"
        img_path = os.path.join(self.folder_path, img_name)

        cv.imwrite(img_path, img_cropped)

        print("Saved:", img_path)

    def next(self):
        """
        Move to the next image in the folder.
        """
        if self.current_index + 1 >= len(self.image_paths):
            messagebox.showinfo("Info", "No more images!")
            return

        self.current_index += 1
        self.show_image(self.image_paths[self.current_index])


# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = ImagePreprocessing(root, state)
    root.mainloop()