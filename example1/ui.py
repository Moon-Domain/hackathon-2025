import tkinter as tk
from tkinter import ttk
import logging
import os
from .screenshot_manager import ScreenshotManager
from .chat_manager import ChatManager

class ScreenshotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot OCR")
        logging.info("Initializing ScreenshotUI")
        
        # Initialize managers
        self.screenshot_manager = ScreenshotManager()
        self.chat_manager = ChatManager()
        
        # UI state variables
        self.photo_image = None
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_rect = None
        self.current_image = None
        
        self._setup_window()
        self._create_widgets()
        
        # Only show API key dialog if not properly initialized
        if not self.chat_manager.is_initialized():
            logging.warning("Chat manager not initialized from environment, requesting API key")
            self._request_api_key()
        else:
            logging.info("Chat manager successfully initialized from environment")
        
    def _setup_window(self):
        """Setup window properties"""
        self.root.geometry("1000x600")  # Wider window to accommodate both panels
        
        # Center the window and bring to front
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 1000) // 2
        y = (screen_height - 600) // 2
        self.root.geometry(f"1000x600+{x}+{y}")
        
        # Ensure window is on top initially
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.focus_force()
        
        # Make window resizable
        self.root.columnconfigure(0, weight=2)  # Screenshot side gets more space
        self.root.columnconfigure(1, weight=1)  # Chat side gets less space
        self.root.rowconfigure(0, weight=1)
    
    def _request_api_key(self):
        """Request Anthropic API key from user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("API Key Required")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, 
                 text="Please enter your Anthropic API key\n(or add it to .env file as ANTHROPIC_API_KEY=your_key)",
                 justify=tk.CENTER).pack(pady=10)
        
        api_key = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=api_key, width=40, show="*")
        entry.pack(pady=10)
        
        def submit():
            if api_key.get().strip():
                self.chat_manager.initialize(api_key.get().strip())
                dialog.destroy()
        
        ttk.Button(dialog, text="Submit", command=submit).pack(pady=10)
    
    def _create_widgets(self):
        """Create and setup all UI widgets"""
        # Left frame for screenshot
        self.left_frame = ttk.Frame(self.root, padding="20")
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.left_frame.columnconfigure(0, weight=1)
        
        # Right frame for chat
        self.right_frame = ttk.Frame(self.root, padding="20")
        self.right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(1, weight=1)  # Make chat area expandable
        
        # Screenshot section
        self.screenshot_btn = ttk.Button(self.left_frame, text="Take Screenshot", command=self.take_screenshot)
        self.screenshot_btn.grid(row=0, column=0, pady=10)
        
        # Preview canvas
        self.canvas = tk.Canvas(self.left_frame, bg='white', width=500, height=400)
        self.canvas.grid(row=1, column=0, pady=10)
        
        # Crop button
        self.crop_btn = ttk.Button(self.left_frame, text="Crop Screenshot", command=self.start_crop, state='disabled')
        self.crop_btn.grid(row=2, column=0, pady=10)
        
        # Save button
        self.save_btn = ttk.Button(self.left_frame, text="Save Screenshot", command=self.save_screenshot, state='disabled')
        self.save_btn.grid(row=3, column=0, pady=10)
        
        # Chat section
        chat_label = ttk.Label(self.right_frame, text="Chat")
        chat_label.grid(row=0, column=0, pady=5)
        
        # Chat display area with scrollbar
        chat_frame = ttk.Frame(self.right_frame)
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        self.chat_text = tk.Text(chat_frame, width=30, height=20, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=scrollbar.set)
        
        self.chat_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Analyze button
        self.analyze_btn = ttk.Button(self.right_frame, text="Analyze with Claude", 
                                    command=self.analyze_screenshot, state='disabled')
        self.analyze_btn.grid(row=2, column=0, pady=10)
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Update preview dimensions
        self.PREVIEW_WIDTH = 500
        self.PREVIEW_HEIGHT = 400
    
    def take_screenshot(self):
        """Handle screenshot capture process"""
        self.screenshot_btn.config(state='disabled')
        self.crop_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        self.countdown(1)
    
    def countdown(self, count):
        """Countdown before taking screenshot"""
        if count > 0:
            self.screenshot_btn.config(text=f"Taking screenshot in {count}...")
            self.root.after(1000, lambda: self.countdown(count - 1))
        else:
            self.screenshot_btn.config(text="Capturing...")
            self.root.after(100, self._capture_and_preview)
    
    def _capture_and_preview(self):
        """Capture screenshot and show preview"""
        image = self.screenshot_manager.capture_screen()
        if image:
            self.current_image = image
            self._update_preview(image)
            self.screenshot_btn.config(text="Take Screenshot", state='normal')
            self.crop_btn.config(state='normal')
            self.save_btn.config(state='normal')
    
    def _update_preview(self, image):
        """Update canvas with preview of the image"""
        try:
            # Calculate preview size
            aspect_ratio = image.width / image.height
            preview_width = self.PREVIEW_WIDTH
            preview_height = int(preview_width / aspect_ratio)
            
            if preview_height > self.PREVIEW_HEIGHT:
                preview_height = self.PREVIEW_HEIGHT
                preview_width = int(preview_height * aspect_ratio)
            
            # Store preview dimensions for coordinate mapping
            self.preview_width = preview_width
            self.preview_height = preview_height
            self.preview_scale_x = image.width / preview_width
            self.preview_scale_y = image.height / preview_height
            
            # Create preview image
            preview = image.resize((preview_width, preview_height))
            
            # Save temporary file for preview
            temp_preview = "temp_preview.png"
            preview.save(temp_preview)
            
            # Load with Tkinter
            self.photo_image = tk.PhotoImage(file=temp_preview)
            os.remove(temp_preview)
            
            # Clear and update canvas
            self.canvas.delete("all")
            x = (self.PREVIEW_WIDTH - preview_width) // 2
            y = (self.PREVIEW_HEIGHT - preview_height) // 2
            self.preview_x = x
            self.preview_y = y
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo_image)
            
            # Enable analyze button when we have an image
            self.analyze_btn.config(state='normal')
            
        except Exception as e:
            logging.error(f"Error updating preview: {e}", exc_info=True)
    
    def start_crop(self):
        """Start crop mode"""
        self.canvas.bind("<ButtonPress-1>", self.crop_start)
        self.canvas.bind("<B1-Motion>", self.crop_drag)
        self.canvas.bind("<ButtonRelease-1>", self.crop_end)
    
    def crop_start(self, event):
        """Handle start of crop selection"""
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
    
    def crop_drag(self, event):
        """Handle crop selection dragging"""
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self.crop_rect = self.canvas.create_rectangle(
            self.crop_start_x, self.crop_start_y,
            event.x, event.y,
            outline='red'
        )
    
    def crop_end(self, event):
        """Handle end of crop selection"""
        if not self.current_image:
            return
        
        # Get coordinates relative to preview image
        x1 = min(self.crop_start_x, event.x) - self.preview_x
        y1 = min(self.crop_start_y, event.y) - self.preview_y
        x2 = max(self.crop_start_x, event.x) - self.preview_x
        y2 = max(self.crop_start_y, event.y) - self.preview_y
        
        # Ensure coordinates are within preview bounds
        x1 = max(0, min(x1, self.preview_width))
        y1 = max(0, min(y1, self.preview_height))
        x2 = max(0, min(x2, self.preview_width))
        y2 = max(0, min(y2, self.preview_height))
        
        # Convert preview coordinates to original image coordinates
        orig_x1 = int(x1 * self.preview_scale_x)
        orig_y1 = int(y1 * self.preview_scale_y)
        orig_x2 = int(x2 * self.preview_scale_x)
        orig_y2 = int(y2 * self.preview_scale_y)
        
        logging.debug(f"Cropping original image at coordinates: ({orig_x1}, {orig_y1}, {orig_x2}, {orig_y2})")
        
        # Crop the original image
        cropped = self.screenshot_manager.crop_image(self.current_image, (orig_x1, orig_y1, orig_x2, orig_y2))
        if cropped:
            self.current_image = cropped
            self._update_preview(cropped)
        
        # Unbind crop events
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
    
    def save_screenshot(self):
        """Save the current screenshot"""
        if self.current_image:
            self.screenshot_manager.save_screenshot(self.current_image)
    
    def analyze_screenshot(self):
        """Send screenshot to Claude for analysis"""
        if not self.current_image:
            return
            
        self.analyze_btn.config(state='disabled', text="Analyzing...")
        self.chat_text.insert(tk.END, "\n\nAnalyzing screenshot...\n")
        self.chat_text.see(tk.END)
        
        # Run analysis in a separate thread to keep UI responsive
        def run_analysis():
            response = self.chat_manager.analyze_image(self.current_image)
            
            # Update UI in main thread
            self.root.after(0, lambda: self._update_chat(response))
        
        import threading
        threading.Thread(target=run_analysis, daemon=True).start()
    
    def _update_chat(self, message):
        """Update chat with new message"""
        self.chat_text.insert(tk.END, f"\nClaude: {message}\n")
        self.chat_text.see(tk.END)
        self.analyze_btn.config(state='normal', text="Analyze with Claude") 