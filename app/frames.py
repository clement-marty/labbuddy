import os
import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from . import funcs
from . import enums


class CustomFrame(tk.Frame):

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum) -> None:
        tk.Frame.__init__(self, parent)
        self.color_palette = color_palette   
        self.config(bg=self.color_palette.BACKGROUND)



class SubMenuOption(tk.Frame):

    # Attributes to be set in the subclass
    display_name = None
    title = None
    subtitle = None

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, header_title: tk.Frame, header_subtitle: tk.Frame) -> None:
        tk.Frame.__init__(self, parent)
        self.color_palette = color_palette
        self.config(bg=self.color_palette.BACKGROUND)

        self.header_title = header_title
        self.header_subtitle = header_subtitle

    def load(self) -> None:
        '''The method called right after creating the object.
        This method must be impremented in all subclasses.
        '''
        raise NotImplementedError('This method must be implemented in the subclass.')  


# ------------------------

class StartFrame(CustomFrame):

    TITLE = 'Welcome!'
    TEXT = 'All tools can be seen in the sidebar.\nSelect a tool to get started.'

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, banner_filepath: str) -> None:
        super().__init__(parent, color_palette)

        self.banner_filepath = banner_filepath
        self.popup_frame = tk.Frame(self, bg=self.color_palette.POPUP)
        self.popup_frame.place(relx=.25, rely=.2, relwidth=.5, relheight=.4)

        label1 = tk.Label(self.popup_frame, text=self.TITLE, font=("Arial", 20, 'bold'), bg=self.color_palette.POPUP, anchor='w')
        label2 = tk.Label(self.popup_frame, text=self.TEXT, font=("Arial", 12), bg=self.color_palette.POPUP, anchor='w', justify='left')
        label1.place(relx=.1, rely=.5, relwidth=.8, relheight=.2)
        label2.place(relx=.1, rely=.7, relwidth=.8, relheight=.2)

    def _add_banner(self, parent: tk.Frame, banner_filepath: str) -> None:
        banner = funcs.get_image_widget_from_filepath(parent, banner_filepath, bg=self.color_palette.POPUP, relwidth=1, relheight=.5)
        banner.place(relx=0, rely=0, relwidth=1, relheight=.5)

    def load(self) -> None:
        self.update()
        self._add_banner(self.popup_frame, self.banner_filepath)



class FileInputFrame(CustomFrame):

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, title: str, text: str, filetypes: list[tuple[str, str]]) -> None:
        super().__init__(parent, color_palette)

        popup_frame = tk.Frame(self, bg=self.color_palette.POPUP)
        popup_frame.place(relx=.25, rely=.2, relwidth=.5, relheight=.3)

        self.label1 = tk.Label(popup_frame, text=title, font=("Arial", 20, 'bold'), bg=self.color_palette.POPUP, anchor='w')
        self.label2 = tk.Label(popup_frame, text=text, font=("Arial", 12), bg=self.color_palette.POPUP, anchor='w')
        self.label1.place(relx=.1, rely=.1, relwidth=.8, relheight=.2)
        self.label2.place(relx=.1, rely=.3, relwidth=.8, relheight=.2)

        button = tk.Button(
            popup_frame,
            text='Select File',
            font=("Arial", 15, "bold"),
            bd=0,
            bg=self.color_palette.POPUP,
            cursor='hand2',
            activebackground=self.color_palette.HEADER,
            borderwidth=1,
            command=self._upload_btn_command
        )
        button.place(relx=.3, rely=.65, relwidth=.4, relheight=.2)

        self.filetypes = filetypes
        self.filepath = None

    def _upload_btn_command(self) -> None:
        filepath = filedialog.askopenfilename(filetypes=self.filetypes)
        if filepath:
            self.filepath = filepath
            self.event_generate('<<FileSelected>>')



class DeterminateProgressbarFrame(CustomFrame):

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum) -> None:
        super().__init__(parent, color_palette)

        self.label = tk.Label(self, text='', font=('Arial', 12), bg=self.color_palette.BACKGROUND, anchor='w')
        self.progress_bar = ttk.Progressbar(self, mode='determinate')
        self.label.place(relx=.25, rely=.75, relwidth=.5, relheight=.05)
        self.progress_bar.place(relx=.25, rely=.8, relwidth=.5, relheight=.05)
        self.image_widget: tk.Label = None
                                
    def set_progress(self, progress: int, maximum: int, text: str, image: cv2.typing.MatLike = None) -> None:
        self.update()
        if image is not None:
            self.image_widget = funcs.get_image_widget_from_cv2(self, image, bg=self.color_palette.BACKGROUND, relwidth=.9, relheight=.6, return_as_label=True)
            self.image_widget.place(relx=.05, rely=.05, relwidth=.9, relheight=.6)
        elif self.image_widget is not None:
            self.image_widget.config(state='disabled')
            self.image_widget = None
        self.label.config(text=text)
        self.progress_bar.config(maximum=maximum, value=progress)
        self.progress_bar.update()



class PanZoomCanvas(CustomFrame):
    
    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, image: cv2.typing.MatLike) -> None:
        super().__init__(parent, color_palette)
        
        self.cv2_image = image
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1
        self.canvas = tk.Canvas(self, bg=self.color_palette.BACKGROUND)
        self.marked_points = []

        self.canvas.bind('<Button-1>', self._on_mouse_left_click)
        self.canvas.bind("<Button-3>", self._on_mouse_right_click)
        self.canvas.bind("<B3-Motion>", self._on_mouse_right_drag)
        
        # Binding the mouse wheel event is done differently depending on the OS
        if os.name == 'nt':  # for Windows
            self.canvas.bind("<MouseWheel>", self._on_mouse_scroll_windows)
        elif os.name == 'posix': # for Linux and Mac
            self.canvas.bind('<Button-4>', self._on_mouse_scroll_up)
            self.canvas.bind('<Button-5>', self._on_mouse_scroll_down)

        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _on_mouse_right_click(self, event: tk.Event) -> None:
        self._old_event = event

    def _on_mouse_right_drag(self, event: tk.Event) -> None:
        self.offset_x += event.x - self._old_event.x
        self.offset_y += event.y - self._old_event.y
        self._old_event = event
        self._check_offset_bounds()
        self.update_canvas()

    def _on_mouse_scroll(self, up: bool) -> None:
        '''
        An OS dependant implementation of the mouse scroll event
        is required since the event.delta is not available on linux and macOS.
        For Windows, the event.delta is a positive value when scrolling up and negative when scrolling down.
        For event handlers, see the methods _on_mouse_scroll_windows, _on_mouse_scroll_up and _on_mouse_scroll_down.
        '''
        old_zoom = self.zoom
        if not up and self.zoom != 1:
            self.zoom -= 1
        elif up and self.zoom != 10:
            self.zoom += 1

        self.offset_x = (self.offset_x * self.zoom) // old_zoom
        self.offset_y = (self.offset_y * self.zoom) // old_zoom
        self._check_offset_bounds()
        self.update_canvas()

    def _on_mouse_scroll_up(self, event: tk.Event) -> None:
        self._on_mouse_scroll(True)

    def _on_mouse_scroll_down(self, event: tk.Event) -> None:
        self._on_mouse_scroll(False)

    def _on_mouse_scroll_windows(self, event: tk.Event) -> None:
        self._on_mouse_scroll(event.delta > 0)

    def _check_offset_bounds(self) -> None:
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        # Bounds
        lower_x = -cw//2 - self.cv2_image.shape[1] * self.zoom // 2
        upper_x =  cw//2 + self.cv2_image.shape[1] * self.zoom // 2
        lower_y = -ch//2 - self.cv2_image.shape[0] * self.zoom // 2
        upper_y =  ch//2 + self.cv2_image.shape[0] * self.zoom // 2

        self.offset_x = max(lower_x, min(self.offset_x, upper_x))
        self.offset_y = max(lower_y, min(self.offset_y, upper_y))

    def update_canvas(self) -> None:
        self.update()
        image = funcs.get_image_widget_from_cv2(self, self.cv2_image, bg=self.color_palette.BACKGROUND, relheight=self.zoom, relwidth=self.zoom, return_as_label=True)
        canvas_w, canvas_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.canvas.delete('all')
        self.canvas.create_image(canvas_w//2 + self.offset_x, canvas_h//2 + self.offset_y, anchor='center', image=image.image)

        # Draw each point
        for point in self.marked_points:
            x, y = point
            # Get the width and height of the canvas and the image
            img_w, img_h = self.cv2_image.shape[1], self.cv2_image.shape[0]
            # Get the original's image scaling factor (as computed in funcs.get_image_widget)
            scale_w = canvas_w * self.zoom / img_w
            scale_h = canvas_h * self.zoom / img_h
            scaling_factor = min(scale_w, scale_h)

            # Convert the coordinates to the canvas coordinates
            canvas_x = (x - img_w//2) * scaling_factor + canvas_w//2 + self.offset_x
            canvas_y = (y - img_h//2) * scaling_factor + canvas_h//2 + self.offset_y

            # Draw a circle at the point
            rel_radius = .02
            radius = rel_radius * min(self.canvas.winfo_width(), self.canvas.winfo_height())
            self.canvas.create_oval(canvas_x-radius, canvas_y-radius, canvas_x+radius, canvas_y+radius, outline='red')
            self.canvas.create_line(canvas_x-radius, canvas_y, canvas_x+radius, canvas_y, fill='red')
            self.canvas.create_line(canvas_x, canvas_y-radius, canvas_x, canvas_y+radius, fill='red')

        # Draw lines between the points if there are at least 2
        if len(self.marked_points) > 1:
            for i in range(len(self.marked_points) - 1):
                x1, y1 = self.marked_points[i]
                x2, y2 = self.marked_points[i + 1]
                canvas_x1 = (x1 - img_w//2) * scaling_factor + canvas_w//2 + self.offset_x
                canvas_y1 = (y1 - img_h//2) * scaling_factor + canvas_h//2 + self.offset_y
                canvas_x2 = (x2 - img_w//2) * scaling_factor + canvas_w//2 + self.offset_x
                canvas_y2 = (y2 - img_h//2) * scaling_factor + canvas_h//2 + self.offset_y
                self.canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, fill='red')
    
    def change_image(self, image: cv2.typing.MatLike) -> None:
        self.cv2_image = image
        self.update_canvas()

    def _on_mouse_left_click(self, event: tk.Event) -> None:
        # Get the coordinates of the mouse click
        x, y = event.x, event.y
        # Get the width and height of the canvas and the image
        canvas_w, canvas_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        img_w, img_h = self.cv2_image.shape[1], self.cv2_image.shape[0]

        # Get the original's image scaling factor (as computed in funcs.get_image_widget)
        scale_w = canvas_w * self.zoom / img_w
        scale_h = canvas_h * self.zoom / img_h
        scaling_factor = min(scale_w, scale_h)

        # Convert the coordinates to the image coordinates
        img_x = ( x - canvas_w//2 - self.offset_x ) // scaling_factor + img_w//2
        img_y = ( y - canvas_h//2 - self.offset_y ) // scaling_factor + img_h//2

        # Check if the coordinates are within the bounds of the image
        if 0 <= img_x < img_w and 0 <= img_y < img_h:
            self.event_generate('<<PixelClicked>>', x=img_x, y=img_y)

    def mark_image_points(self, *points: list[tuple[int, int]]) -> None:
        self.marked_points = []
        for point in points:
            if point is not None:
                self.marked_points.append(point)
        self.update_canvas()



class ComingSoonFrame(CustomFrame):

    TITLE = 'Coming soon!'
    TEXT = 'This feature is still in development\nand will be available in a future update.'

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum) -> None:
        super().__init__(parent, color_palette)

        self.popup_frame = tk.Frame(self, bg=self.color_palette.POPUP)
        self.popup_frame.place(relx=.25, rely=.3, relwidth=.5, relheight=.2)

        label1 = tk.Label(self.popup_frame, text=self.TITLE, font=("Arial", 20, 'bold'), bg=self.color_palette.POPUP, anchor='w')
        label2 = tk.Label(self.popup_frame, text=self.TEXT, font=("Arial", 12), bg=self.color_palette.POPUP, anchor='w', justify='left')
        label1.place(relx=.1, rely=.2, relwidth=.8, relheight=.2)
        label2.place(relx=.1, rely=.4, relwidth=.8, relheight=.5)



class CreditsFrame(CustomFrame):

    TITLE = 'About LabBuddy'
    TEXT_1 = '''LabBuddy v1.1.1
Physics Lab Assistant Tool

DEVELOPED BY
Clément MARTY
GitHub: @clement-marty

BUILT WITH Python 3.12

THIRD-PARTY LIBRARIES
This software uses the following\nopen-source libraries:
• OpenCV (opencv-python 4.11.0.86)
• Matplotlib (3.10.3)
• NumPy (2.3.0)
• Pandas (2.3.0)
• Pillow (11.2.1)
• And other supporting libraries\n(see requirements.txt)
'''
    TEXT_2 = '''LICENSE
This project is licensed\nunder the MIT License.

Copyright © 2025 Clément MARTY

CONTRIBUTING
Contributions are welcome! Please\nvisit our GitHub repository to:
• Report issues or bugs
• Suggest new features
• Submit pull requests
• Join discussions

SUPPORT
Need help? Open an issue on GitHub\nor contact @clement-marty

Thank you for using LabBuddy!
'''

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, app_version: str) -> None:
        super().__init__(parent, color_palette)

        self.popup_frame = tk.Frame(self, bg=self.color_palette.POPUP)
        self.popup_frame.place(relx=.1, rely=.1, relwidth=.8, relheight=.75)

        label1 = tk.Label(self.popup_frame, text=self.TITLE, font=("Arial", 20, 'bold'), bg=self.color_palette.POPUP, anchor='c')
        label2 = tk.Label(self.popup_frame, text=self.TEXT_1, font=("Arial", 12), bg=self.color_palette.POPUP, anchor='w', justify='left')
        label3 = tk.Label(self.popup_frame, text=self.TEXT_2, font=("Arial", 12), bg=self.color_palette.POPUP, anchor='w', justify='left')
        label1.place(relx=.1, rely=.05, relwidth=.8, relheight=.05)
        label2.place(relx=.05, rely=.1, relwidth=.425, relheight=.9)
        label3.place(relx=.55, rely=.1, relwidth=.425, relheight=.9)
