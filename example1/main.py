import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import mss
import mss.tools
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot OCR")
        logging.info("Initializing ScreenshotApp")
        self.root.geometry("800x600")
        
        # Center the window and bring to front
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        self.root.geometry(f"800x600+{x}+{y}")
        
        # Ensure window is on top initially
        self.root.lift()  # Bring window to front
        self.root.attributes('-topmost', True)  # Keep on top
        self.root.after_idle(self.root.attributes, '-topmost', False)  # Disable topmost after showing
        self.root.focus_force()  # Force focus
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Screenshot button
        self.screenshot_btn = ttk.Button(self.main_frame, text="Take Screenshot", command=self.take_screenshot)
        self.screenshot_btn.grid(row=0, column=0, pady=10)
        
        # Preview canvas
        self.canvas = tk.Canvas(self.main_frame, bg='white', width=700, height=400)
        self.canvas.grid(row=1, column=0, pady=10)
        
        # Crop button (initially disabled)
        self.crop_btn = ttk.Button(self.main_frame, text="Crop Screenshot", command=self.start_crop, state='disabled')
        self.crop_btn.grid(row=2, column=0, pady=10)
        
        # Save button (initially disabled)
        self.save_btn = ttk.Button(self.main_frame, text="Save Screenshot", command=self.save_screenshot, state='disabled')
        self.save_btn.grid(row=3, column=0, pady=10)
        
        # Make window resizable
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        # Screenshot related variables
        self.screenshot = None
        self.photo_image = None
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_rect = None
        self.cropped_image = None
        self.original_screenshot = None
        
    def take_screenshot(self):
        # Disable buttons during capture
        self.screenshot_btn.config(state='disabled')
        self.crop_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        
        # Start countdown
        self.countdown(1)
    
    def countdown(self, count):
        if count > 0:
            self.screenshot_btn.config(text=f"Taking screenshot in {count}...")
            self.root.after(1000, lambda: self.countdown(count - 1))
        else:
            self.screenshot_btn.config(text="Capturing...")
            self.root.after(100, self._capture_screenshot)
        
    def _capture_screenshot(self):
        logging.info("Starting screenshot capture")
        try:
            with mss.mss() as sct:
                # Capture entire screen
                monitor = sct.monitors[0]  # Get the primary monitor
                logging.debug(f"Monitor info: {monitor}")
                screenshot = sct.grab(monitor)
                logging.info(f"Screenshot captured: {screenshot.width}x{screenshot.height}")
                
                # Save screenshot directly to file
                temp_filename = "temp_screenshot.png"
                logging.debug(f"Saving screenshot to: {temp_filename}")
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=temp_filename)
                
                # Load and process image
                try:
                    # Load directly with Tkinter
                    self.photo_image = tk.PhotoImage(file=temp_filename)
                    logging.info(f"Image loaded with Tkinter: {self.photo_image.width()}x{self.photo_image.height()}")
                    
                    # Store original for later use
                    self.original_screenshot = Image.open(temp_filename)
                    
                    # Calculate preview size
                    aspect_ratio = self.photo_image.width() / self.photo_image.height()
                    preview_width = 700
                    preview_height = int(preview_width / aspect_ratio)
                    
                    if preview_height > 400:
                        preview_height = 400
                        preview_width = int(preview_height * aspect_ratio)
                    
                    logging.debug(f"Preview size calculated: {preview_width}x{preview_height}")
                    
                    # Subsample the image for preview (Tkinter's way of resizing)
                    scale_x = self.photo_image.width() / preview_width
                    scale_y = self.photo_image.height() / preview_height
                    self.photo_image = self.photo_image.subsample(int(scale_x), int(scale_y))
                    
                    # Store preview size for cropping
                    self.screenshot = Image.open(temp_filename).resize((preview_width, preview_height))
                    
                    # Clear and update canvas
                    self.canvas.delete("all")
                    x = (700 - preview_width) // 2
                    y = (400 - preview_height) // 2
                    self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo_image)
                    logging.info("Preview displayed successfully")
                    
                except Exception as e:
                    logging.error(f"Error processing image: {e}", exc_info=True)
                    raise
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                        logging.debug("Temporary file removed")
                
                # Reset UI state
                self.screenshot_btn.config(text="Take Screenshot", state='normal')
                self.crop_btn.config(state='normal')
                self.save_btn.config(state='normal')
                logging.info("Screenshot capture completed")
                
        except Exception as e:
            logging.error(f"Screenshot capture failed: {e}", exc_info=True)
            self.screenshot_btn.config(text="Take Screenshot", state='normal')
        
    def start_crop(self):
        self.canvas.bind("<ButtonPress-1>", self.crop_start)
        self.canvas.bind("<B1-Motion>", self.crop_drag)
        self.canvas.bind("<ButtonRelease-1>", self.crop_end)
        
    def crop_start(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        
    def crop_drag(self, event):
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self.crop_rect = self.canvas.create_rectangle(
            self.crop_start_x, self.crop_start_y,
            event.x, event.y,
            outline='red'
        )
        
    def crop_end(self, event):
        if not self.screenshot:
            return
            
        # Get coordinates
        x1 = min(self.crop_start_x, event.x)
        y1 = min(self.crop_start_y, event.y)
        x2 = max(self.crop_start_x, event.x)
        y2 = max(self.crop_start_y, event.y)
        
        # Crop the image
        self.cropped_image = self.screenshot.crop((x1, y1, x2, y2))
        
        # Update preview
        self.photo_image = ImageTk.PhotoImage(self.cropped_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        
        # Unbind crop events
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        
    def save_screenshot(self):
        if not self.screenshot and not self.cropped_image:
            return
            
        # Create screenshots directory if it doesn't exist
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
            
        # Save the image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_to_save = self.cropped_image if self.cropped_image else self.screenshot
        image_to_save.save(f"screenshots/screenshot_{timestamp}.png")

def main():
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 