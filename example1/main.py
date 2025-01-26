import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import mss
import mss.tools
from datetime import datetime
import os
import logging
from .ui import ScreenshotUI

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ScreenshotManager:
    def __init__(self):
        self.screenshot = None
        self.original_screenshot = None
        self.cropped_image = None
    
    def capture_screen(self):
        """Capture the screen and return the image"""
        logging.info("Starting screenshot capture")
        try:
            with mss.mss() as sct:
                # Capture entire screen
                monitor = sct.monitors[0]
                logging.debug(f"Monitor info: {monitor}")
                screenshot = sct.grab(monitor)
                logging.info(f"Screenshot captured: {screenshot.width}x{screenshot.height}")
                
                # Save screenshot to temporary file
                temp_filename = "temp_screenshot.png"
                logging.debug(f"Saving screenshot to: {temp_filename}")
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=temp_filename)
                
                # Load and return image
                self.original_screenshot = Image.open(temp_filename)
                os.remove(temp_filename)
                return self.original_screenshot
                
        except Exception as e:
            logging.error(f"Screenshot capture failed: {e}", exc_info=True)
            return None
    
    def crop_image(self, image, box):
        """Crop image with given box coordinates"""
        try:
            self.cropped_image = image.crop(box)
            return self.cropped_image
        except Exception as e:
            logging.error(f"Error cropping image: {e}", exc_info=True)
            return None
    
    def save_screenshot(self, image, directory="screenshots"):
        """Save the image to a file"""
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{directory}/screenshot_{timestamp}.png"
            image.save(filename)
            logging.info(f"Screenshot saved: {filename}")
            return True
        except Exception as e:
            logging.error(f"Error saving screenshot: {e}", exc_info=True)
            return False

def main():
    # Initialize X threads for Linux
    try:
        if os.name != 'nt':  # Not Windows
            tk.Tk.tk.call('package', 'require', 'Tk')
            tk.Tk.tk.call('tk', 'useinputmethods', '1')
    except Exception as e:
        logging.warning(f"Failed to initialize X threads: {e}")

    root = tk.Tk()
    app = ScreenshotUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 