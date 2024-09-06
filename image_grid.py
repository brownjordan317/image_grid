import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageTk
import os
import re

# Function to resize images
def resize_images(image_files, resize_dimensions, image_folder, resolution_scale):
    resized_images = []
    resize_dimensions = (resize_dimensions[0] * resolution_scale, resize_dimensions[1] * resolution_scale)
    for img_file in image_files:
        img_path = os.path.join(image_folder, img_file)
        img = Image.open(img_path)
        resized_image = img.resize(resize_dimensions)
        resized_images.append(resized_image)
    return resized_images

# Function to extract numerical part from filename
def extract_number(filename):
    match = re.search(r'(\d+)', filename)
    num = int(match.group(0)) if match else float('inf')
    return (num, filename)

def create_grid(resized_images, resize_dimensions, resolution_scale, grid_dims, x_spacing, y_spacing, background_color, y_texts, x_texts, font_path, font_size, font_color):
    resize_dimensions = (resize_dimensions[0] * resolution_scale, resize_dimensions[1] * resolution_scale)
    font_size = font_size * resolution_scale

    # Parse the background color
    if background_color.startswith('#') and len(background_color) == 7:
        background_color = tuple(int(background_color[i:i+2], 16) for i in (1, 3, 5)) + (255,)
    else:
        background_color = ImageColor.getcolor(background_color, "RGBA")

    # Parse the font color
    if font_color.startswith('#') and len(font_color) == 7:
        font_color = tuple(int(font_color[i:i+2], 16) for i in (1, 3, 5)) + (255,)
    else:
        font_color = ImageColor.getcolor(font_color, "RGBA")

    # Load the font
    if font_size != 0:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.truetype("times.ttf", font_size)

    # Calculate the text height and max text width
    text_height = font.getbbox("A")[3] if font_size != 0 else 0
    max_text_width = max([font.getbbox(text)[2] for text in x_texts]) if font_size != 0 else 0

    # Calculate the size of the new image including the border spacing and text space
    if len(x_texts[0]) > 0:
        total_width = (resize_dimensions[0] + x_spacing) * grid_dims[0] + (max_text_width * 2) + x_spacing
    else:
        total_width = (resize_dimensions[0] + x_spacing) * grid_dims[0] + x_spacing
    total_height = (resize_dimensions[1] + y_spacing) * grid_dims[1] + (text_height * 4) + y_spacing

    # Create a new blank image with size large enough to hold the grid with border
    new_image = Image.new('RGBA', (total_width, total_height), background_color)
    draw = ImageDraw.Draw(new_image)

    # Paste each image into the new image with the specified spacing and add text
    for index, img in enumerate(resized_images):
        col = index % grid_dims[0]
        row = index // grid_dims[0]
        if len(x_texts[0]) > 0:
            x = col * (resize_dimensions[0] + x_spacing) + (max_text_width * 2) 
        else:
            x = x_spacing + col * (resize_dimensions[0] + x_spacing) + (max_text_width * 2) 
        y = y_spacing + row * (resize_dimensions[1] + y_spacing) + (text_height * 2)
        new_image.paste(img, (x, y))
        
        if row == 0 and font_size != 0:
            # Draw the text centered below the image
            text = y_texts[col] if col < len(y_texts) else ""
            text_bbox = font.getbbox(text)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = x + (resize_dimensions[0] - text_width) // 2
            text_y = y - int(text_height * 1.5)
            draw.text((text_x, text_y), text, font=font, fill=font_color)
        
        if col == 0 and font_size != 0:
            # Draw the text on the left side of the image
            text = x_texts[row] if row < len(x_texts) else ""
            text_bbox = font.getbbox(text)
            text_height_actual = text_bbox[3] - text_bbox[1]
            text_x = x - int(max_text_width * 1.5)
            text_y = y + (resize_dimensions[1] - text_height_actual) // 2
            draw.text((text_x, text_y), text, font=font, fill=font_color)

    return new_image

class ImageGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Grid Creator")

        # Initialize parameters
        self.image_folder = tk.StringVar(value='your/images/folder')
        self.resize_width = tk.IntVar(value=128)
        self.resize_height = tk.IntVar(value=64)
        self.resolution_scale = tk.IntVar(value=1)
        self.grid_columns = tk.IntVar(value=6)
        self.grid_rows = tk.IntVar(value=6)
        self.x_spacing = tk.IntVar(value=15)
        self.y_spacing = tk.IntVar(value=0)
        self.background_color = tk.StringVar(value='white')
        self.y_texts = tk.StringVar(value="RGB,IR,RGB Pred,RGBT Pred,IR Pred,Ground Truth")
        self.x_texts = tk.StringVar(value="FR-T, FR-T, FR-T, FR-T, FR-T, FR-T")
        self.font_path = tk.StringVar(value='times.ttf')
        self.font_size = tk.IntVar(value=8)
        self.font_color = tk.StringVar(value='black')  # New parameter

        # Create UI elements
        self.create_widgets()

        # Bind changes to auto-update preview
        self.bind_changes()

    def create_widgets(self):
        # Create frames for better organization
        input_frame = tk.LabelFrame(self.root, text="Input Parameters", padx=10, pady=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
        
        preview_frame = tk.LabelFrame(self.root, text="Image Preview", padx=10, pady=10)
        preview_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")

        # Input fields
        self.create_label_button(input_frame, "Image Folder:", self.image_folder, self.select_image_folder)
        self.create_label_button(input_frame, "Font Path:", self.font_path, self.select_font_path)
        self.create_label_entry(input_frame, "Resize Width:", self.resize_width)
        self.create_label_entry(input_frame, "Resize Height:", self.resize_height)
        self.create_label_entry(input_frame, "Resolution Scale:", self.resolution_scale)
        self.create_label_entry(input_frame, "Grid Columns:", self.grid_columns)
        self.create_label_entry(input_frame, "Grid Rows:", self.grid_rows)
        self.create_label_entry(input_frame, "X Spacing:", self.x_spacing)
        self.create_label_entry(input_frame, "Y Spacing:", self.y_spacing)
        self.create_label_entry(input_frame, "Background Color:", self.background_color)
        self.create_label_entry(input_frame, "Column Texts (comma-separated):", self.y_texts)
        self.create_label_entry(input_frame, "Row Texts (comma-separated):", self.x_texts)
        self.create_label_entry(input_frame, "Font Size:", self.font_size)
        self.create_label_entry(input_frame, "Font Color:", self.font_color)  # New field

        # Preview canvas
        self.canvas = tk.Canvas(preview_frame, width=1000, height=800, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Save button
        self.save_button = tk.Button(preview_frame, text="Save Image", command=self.save_image)
        self.save_button.pack(pady=5)

    def create_label_entry(self, parent, text, variable):
        tk.Label(parent, text=text).grid(sticky='e', padx=5, pady=5)
        tk.Entry(parent, textvariable=variable).grid(sticky='w', padx=5, pady=5)

    def create_label_button(self, parent, text, variable, command):
        tk.Label(parent, text=text).grid(sticky='e', padx=5, pady=5)
        tk.Entry(parent, textvariable=variable, state='readonly').grid(sticky='w', padx=5, pady=5)
        tk.Button(parent, text="Browse", command=command).grid(sticky='e', padx=5, pady=5)

    def bind_changes(self):
        # Bind all variables to the auto-update function
        def on_change(*args):
            self.preview_image()
        self.image_folder.trace_add("write", on_change)
        self.resize_width.trace_add("write", on_change)
        self.resize_height.trace_add("write", on_change)
        self.resolution_scale.trace_add("write", on_change)
        self.grid_columns.trace_add("write", on_change)
        self.grid_rows.trace_add("write", on_change)
        self.x_spacing.trace_add("write", on_change)
        self.y_spacing.trace_add("write", on_change)
        self.background_color.trace_add("write", on_change)
        self.y_texts.trace_add("write", on_change)
        self.x_texts.trace_add("write", on_change)
        self.font_path.trace_add("write", on_change)
        self.font_size.trace_add("write", on_change)
        self.font_color.trace_add("write", on_change)  # New binding

    def preview_image(self):
        image_files = [f for f in os.listdir(self.image_folder.get()) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif'))]
        image_files.sort(key=lambda x: (extract_number(x), x))

        resize_dimensions = (self.resize_width.get(), self.resize_height.get())
        grid_dims = (self.grid_columns.get(), self.grid_rows.get())
        y_texts = self.y_texts.get().split(',')
        x_texts = self.x_texts.get().split(',')
        
        resized_images = resize_images(image_files, resize_dimensions, self.image_folder.get(), self.resolution_scale.get())
        new_image = create_grid(resized_images, resize_dimensions, self.resolution_scale.get(), grid_dims, self.x_spacing.get(), self.y_spacing.get(), self.background_color.get(), y_texts, x_texts, self.font_path.get(), self.font_size.get(), self.font_color.get())
        
        self.display_image(new_image)

    def display_image(self, image):
        # Resize image to fit canvas
        img_width, img_height = image.size
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        scale = min(canvas_width / img_width, canvas_height / img_height)
        new_size = (int(img_width * scale), int(img_height * scale))
        resized_image = image.resize(new_size)
        
        self.photo_image = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.photo_image, anchor=tk.CENTER)

    def select_image_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.image_folder.get())
        if folder_selected:
            self.image_folder.set(folder_selected)
            self.preview_image()

    def select_font_path(self):
        file_selected = filedialog.askopenfilename(filetypes=[("Font files", "*.ttf"), ("All files", "*.*")], initialdir=self.font_path.get())
        if file_selected:
            self.font_path.set(file_selected)
            self.preview_image()

    def save_image(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if output_path:
            resized_images = self.get_resized_images()
            new_image = create_grid(resized_images, self.get_resize_dimensions(), self.resolution_scale.get(), self.get_grid_dims(), self.x_spacing.get(), self.y_spacing.get(), self.background_color.get(), self.y_texts.get().split(','), self.x_texts.get().split(','), self.font_path.get(), self.font_size.get(), self.font_color.get())
            new_image.save(output_path)
            messagebox.showinfo("Image Saved", f"Image saved to {output_path}")

    def get_resized_images(self):
        image_files = [f for f in os.listdir(self.image_folder.get()) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif'))]
        image_files.sort(key=lambda x: (extract_number(x), x))
        return resize_images(image_files, self.get_resize_dimensions(), self.image_folder.get(), self.resolution_scale.get())

    def get_resize_dimensions(self):
        return (self.resize_width.get(), self.resize_height.get())

    def get_grid_dims(self):
        return (self.grid_columns.get(), self.grid_rows.get())

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageGridApp(root)
    root.mainloop()
