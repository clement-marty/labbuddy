import cv2
import random
import imutils
import pandas as pd
import tkinter as tk
from tkinter import filedialog

from . import funcs
from . import enums
from . import frames



class ObjectDetection(frames.SubMenuOption):

    supported_filetypes = [('Video files', '*.mp4 *.avi'), ]

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, langage_pack: enums.LanguagePackEnum, header_title: tk.Frame, header_subtitle: tk.Frame) -> None:
        super().__init__(parent, color_palette, langage_pack, header_title, header_subtitle)
        self.color_palette = color_palette
        self.display_name = self.lpack.od.DISPLAY_NAME
        
        self.video_path: str = None
        self.video_fps: float = None
        self.video_frames: list[cv2.typing.MatLike] = None

    def load(self) -> None:
        self.tkraise()

        self.header_title.config(text=self.lpack.od.TITLE)
        self.header_subtitle.config(text='')

        self.file_input_frame = frames.FileInputFrame(
            self,
            self.color_palette,
            title=self.lpack.od.file_input_frame.SELECT_FILE,
            text=self.lpack.od.file_input_frame.SUPPORTED_FORMATS,
            button_text=self.lpack.od.file_input_frame.BUTTON_TEXT,
            filetypes=self.supported_filetypes
        )
        self.header_title.config(text=' - '.join([self.lpack.od.TITLE, self.lpack.od.file_input_frame.TITLE]))
        self.file_input_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.file_input_frame.bind('<<FileSelected>>', self._on_file_selected)

    def _on_file_selected(self, event: tk.Event) -> None:
        self.video_path = self.file_input_frame.filepath

        # Load the video
        self.video_load_progress_frame = frames.DeterminateProgressbarFrame(self, self.color_palette)
        self.video_load_progress_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.file_input_frame.destroy()

        self._load_video(self.video_path)

        # Ask the user to select a scale
        self.scale_selector_frame = ScaleSelectorFrame(self, self.color_palette, self.lpack, self.video_frames)
        self.scale_selector_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.scale_selector_frame.bind('<<ScaleSelected>>', self._on_scale_selected)
        self.header_title.config(text=' - '.join([self.lpack.od.TITLE, self.lpack.od.scale_selector_frame.TITLE]))
        self.scale_selector_frame.update_canvas()

        self.header_subtitle.config(text=self._format_path_for_display(self.video_path))
        self.video_load_progress_frame.destroy()

    def _on_scale_selected(self, event: tk.Event) -> None:
        self.scale_point_1 = self.scale_selector_frame.first_point
        self.scale_point_2 = self.scale_selector_frame.second_point
        self.scale_distance = self.scale_selector_frame.distance
        self.scale_distance_unit_power = self.scale_selector_frame.distance_unit_power
        self.scale_distance_unit = self.scale_selector_frame.distance_unit_str

        # Ask the user to select an origin
        self.origin_selector_frame = OriginSelectorFrame(self, self.color_palette, self.lpack, self.video_frames)
        self.header_title.config(text=' - '.join([self.lpack.od.TITLE, self.lpack.od.origin_selector_frame.TITLE]))
        self.origin_selector_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.origin_selector_frame.bind('<<OriginSelected>>', self._on_origin_selected)
        self.origin_selector_frame.update_canvas()

        self.scale_selector_frame.destroy()

    def _on_origin_selected(self, event: tk.Event) -> None:
        self.object_as_origin_frame, self.custom_origin_point = None, None
        if self.origin_selector_frame.object_as_origin_frame is not None:
            self.object_as_origin_frame = self.origin_selector_frame.object_as_origin_frame
        else:
            self.custom_origin_point = self.origin_selector_frame.custom_origin_point

        # Ask the user to select a color range
        self.color_bounds_selector_frame = ColorBoundsSelectorFrame(self, self.color_palette, self.lpack, self.video_frames)
        self.header_title.config(text=' - '.join([self.lpack.od.TITLE, self.lpack.od.color_bounds_selector_frame.TITLE]))
        self.color_bounds_selector_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.color_bounds_selector_frame.bind('<<ColorBoundsSelected>>', self._on_color_bounds_selected)
        self.color_bounds_selector_frame.update_images()

        self.origin_selector_frame.destroy()

    def _on_color_bounds_selected(self, event: tk.Event) -> None:
        lower_color_bound = (
            self.color_bounds_selector_frame.lower_h_slider.get(),
            self.color_bounds_selector_frame.lower_s_slider.get(),
            self.color_bounds_selector_frame.lower_v_slider.get()
        )
        upper_color_bound = (
            self.color_bounds_selector_frame.upper_h_slider.get(),
            self.color_bounds_selector_frame.upper_s_slider.get(),
            self.color_bounds_selector_frame.upper_v_slider.get()
        )

        # Compute the object's positions
        self.video_mask_progress_frame = frames.DeterminateProgressbarFrame(self, self.color_palette)
        self.video_mask_progress_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.color_bounds_selector_frame.destroy()

        self.object_circles, self.object_centroids = self._compute_object_positions(
            video_frames=self.video_frames, 
            lower_bound=lower_color_bound,
            upper_bound=upper_color_bound,
            progressbar=self.video_mask_progress_frame
        )

        self.object_real_positions = self._image_to_real_positions(
            image_positions=self.object_centroids,
            scale_point_1=self.scale_point_1,
            scale_point_2=self.scale_point_2,
            scale_distance=self.scale_distance,
            origin_point=self._get_origin_point(),
            progressbar=self.video_mask_progress_frame
        )

        # Show the save options
        self.save_frame = SaveFrame(self, self.color_palette, self.lpack, self.object_real_positions, self.scale_distance_unit.get(), 1/self.video_fps)
        self.header_title.config(text=' - '.join([self.lpack.od.TITLE, self.lpack.od.save_frame.TITLE]))
        self.save_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.video_mask_progress_frame.destroy()

    def _load_video(self, video_path: str) -> None:
        '''Load a video from the given path.

        :param str video_path: Path to the video file.
        :return np.array[cv2.typing.MatLike]: Array of video frames.
        '''
        self.video_load_progress_frame.tkraise()

        video_capture = cv2.VideoCapture(video_path)
        self.video_fps = video_capture.get(cv2.CAP_PROP_FPS)
        frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_frames = []
        while video_capture.isOpened():
            ret, frame = video_capture.read()
            if not ret:
                break
            self.video_frames.append(frame)
            text = self.lpack.od.LOADING_FRAMES + f' {len(self.video_frames)}/{frame_count}'
            self.video_load_progress_frame.set_progress(progress=len(self.video_frames), maximum=frame_count, text=text)
        video_capture.release()

    def _format_path_for_display(self, path: str, max_length: int = 80) -> str:
        '''Format the file path for display.

        :param str path: Path to the file.
        :param int max_length: Maximum length of the displayed path.
        :return str: Formatted path.
        '''
        l = path.split('/')
        res = ''
        
        if len(path) <= max_length:
            res = path
        else:
            i = len(l) - 1
            while i >= 0 and len(res) + len(l[i]) <= max_length:
                res = l[i] + '/' + res
                i -= 1
            res = '.../' + res[:-1]
        return res

    def _compute_object_positions(self, video_frames: list[cv2.typing.MatLike], lower_bound: tuple[int], upper_bound: tuple[int], object_radius_threshold: int = 2, progressbar: frames.DeterminateProgressbarFrame = None) -> tuple[list[tuple[int]]]:
        '''Apply a color mask to the video frames and returns the obtained circles and centroids positions
        
        :param list[cv2.typing.MatLike] video_frames: List of video frames.
        :param tuple[int] lower_bound: Lower HSV bound of the color range.
        :param tuple[int] upper_bound: Upper HSV bound of the color range.
        :param int object_radius_threshold: The threshold radius below which a detected circle is not taken into account, defaults to 2
        :param frames.DeterminateProgressbarFrame progressbar: The progressbar to be updated along the process, defaults to None
        :return tuple[list[tuple[int]]]: A tuple containing two elements,
            - A list[tuple[int, int, int]] of the detected circles, in format (x, y, radius) or None
            - A list[tuple[int, int]] of the detected centroids, in format (x, y) or None
        '''
        self.video_mask_progress_frame.tkraise()

        object_circles = [] # List of circles representing detected objects, in format (x, y, radius)
        object_centroids = [] # List of centroids of the detected objects, in format (x, y)
        frame_count = len(video_frames)
        for i, frame in enumerate(video_frames):
            # resize, blur and convert the image to HSV
            hsv = cv2.cvtColor(
                cv2.GaussianBlur(imutils.resize(frame, width=600), (11, 11), 0), 
                cv2.COLOR_BGR2HSV
            )
            # Apply a color mask and remove any small blobs left in the mask
            mask = cv2.dilate(
                cv2.erode(
                    cv2.inRange(hsv, lower_bound, upper_bound),
                    None, iterations=2
                ),
                None, iterations=2
            )
            # Find the contours of the object
            contours = imutils.grab_contours(cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE))

            if len(contours) > 0:

                # Find the largest contour in the mask, then compute the minimum enclosing circle and the centroid
                c = max(contours, key=cv2.contourArea)
                (x, y), radius = cv2.minEnclosingCircle(c)
                m = cv2.moments(c)
                center = (
                    int(m['m10'] / m['m00']), int(m['m01'] / m['m00'])
                )

                # Only proceed if the radius is above the threshold
                if radius >= object_radius_threshold:
                    object_circles.append((int(x), int(y), int(radius)))
                    object_centroids.append(center)
                else:
                    object_circles.append(None)
                    object_centroids.append(None)
            else:
                object_circles.append(None)
                object_centroids.append(None)

            if progressbar is not None:
                progressbar.set_progress(
                    progress=i+1,
                    maximum=frame_count,
                    text=self.lpack.od.PROCESSING_FRAMES + f' {i}/{frame_count}',
                    image=self._draw_object_position(frame, object_circles[i], object_centroids[i])
                )
        
        return object_circles, object_centroids

    def _image_to_real_positions(self, image_positions: list[tuple[int, int]], scale_point_1: tuple[int, int], scale_point_2: tuple[int, int], scale_distance: float, origin_point: tuple[int, int], progressbar: frames.DeterminateProgressbarFrame = None) -> list[tuple[float, float]]:
        '''Convert pixel coordinates from an image to real coordinates using a scale and an origin

        :param list[tuple[int, int]] image_positions: The list of pixel coordinates to be converted, in format (x, y)
        :param tuple[int, int] scale_point_1: The first point defining the scale
        :param tuple[int, int] scale_point_2: The second point defining the scale
        :param float scale_distance: The real distance between the two points defining the scale
        :param tuple[int, int] origin_point: The pixel coordinates of the origin
        :param frames.DeterminateProgressbarFrame progressbar: The progressbar to be updated along the process, defaults to None
        :return list[tuple[int, int]]: The list of real coordinates
        '''

        # Compute a conversion factor between image and real distances
        x1, y1, x2, y2 = *scale_point_1, *scale_point_2
        scale_image_distance = ( (x1 - x2)**2 + (y1 - y2)**2 ) **.5
        cfactor = scale_distance / scale_image_distance

        # Convert each coordinates on the image to real positions
        real_positions = []
        ox, oy = origin_point
        points_nb = len(image_positions)
        for i, p in enumerate(image_positions):
            if p is not None:
                x, y = p
                real_positions.append((
                    cfactor * (x - ox),
                    cfactor * (y - oy)
                ))
            else:
                real_positions.append(None)
            if progressbar is not None:
                progressbar.set_progress(
                    progress=i+1,
                    maximum=points_nb,
                    text=self.lpack.od.CONVERTING_COORDINATES + f' {i}/{points_nb}'
                )

        return real_positions

    def _draw_object_position(self, image: cv2.typing.MatLike, circle: tuple[int], centroid: tuple[int]) -> cv2.typing.MatLike:
        '''Return an image with the object's representative circle and centroid drawn on it.

        :param cv2.typing.MatLike image: Image to draw on.
        :param tuple[int] circle: Circle representing the object, in format (x, y, radius).
        :param tuple[int] centroid: Centroid of the object, in format (x, y).
        :return cv2.typing.MatLike: Image with the object position drawn.
        '''
        im_copy = image.copy()
        if circle and centroid:
            x, y, radius = circle
            cv2.circle(im_copy, (x, y), radius, (0, 255, 0), 2)
            cv2.circle(im_copy, centroid, 5, (0, 0, 255), -1)
        return im_copy

    def _get_origin_point(self) -> tuple[int, int]:
        origin_point = (0, 0)
        if self.object_as_origin_frame is None:
            origin_point = self.custom_origin_point
        if self.object_as_origin_frame is not None:
            step = -1 if self.object_as_origin_frame == len(self.video_frames)-1 else 1
            i = self.object_as_origin_frame
            found_point = False
            while i >= 0 and i <= len(self.video_frames) and not found_point:
                if self.object_centroids[i] is not None:
                    origin_point = self.object_centroids[i]
                    found_point = True
                i += step
        return origin_point



class ColorBoundsSelectorFrame(frames.CustomFrame):

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, language_pack: enums.LanguagePackEnum, video_frames: list[cv2.typing.MatLike]) -> None:
        super().__init__(parent, color_palette)
        self.lpack = language_pack

        self.settings_bar = tk.Frame(self, bg=self.color_palette.POPUP)
        self.settings_bar.place(relx=0, rely=.8, relwidth=1, relheight=.2)

        # IMAGES
        self.video_frames = video_frames
        self.current_image = 0

        # SLIDERS
        slider_params = {
            'master': self.settings_bar,
            'from_': 0,
            'to': 255,
            'orient': tk.HORIZONTAL,
            'bg': self.color_palette.POPUP,
            'bd': 0,
            'cursor': 'hand2',
            'activebackground': self.color_palette.HEADER,
            'highlightthickness': 0,
            'troughcolor': self.color_palette.HEADER,
            'command': self._on_slider_update
        }
        label_params = {
            'master': self.settings_bar,
            'bg': self.color_palette.POPUP,
            'font': ('', 10),
            'anchor': 'w',
        }
        for i in range(6):
            name = ''
            text = ''
            relx_label = .05
            relx_slider = .125
            rely = 0

            if i < 3: name = 'lower'; text = self.lpack.od.color_bounds_selector_frame.LOWER_BOUND
            else: name = 'upper'; text = self.lpack.od.color_bounds_selector_frame.UPPER_BOUND

            ch = ''
            if i % 3 == 0: name += '_h'; ch = 'H'
            elif i % 3 == 1: name += '_s'; ch = 'S'
            else: name += '_v'; ch = 'V'
            text = text.replace('{{?}}', ch)

            slider = tk.Scale(**slider_params)
            label = tk.Label(text=text, **label_params)

            setattr(self, f'{name}_slider', slider)
            setattr(self, f'{name}_label', label)

            if i % 3 == 1: rely = .30
            elif i % 3 == 2: rely = .60

            if i > 2:
                relx_label = .375
                relx_slider = .45
                slider.set(255)

            slider.place(relx=relx_slider, rely=rely, relwidth=.2, relheight=.3)
            label.place(relx=relx_label, rely=rely+.1, relwidth=.075, relheight=.2)

        # BUTTONS
        button_params = {
            'master': self.settings_bar,
            'font': ('', 10),
            'bg': self.color_palette.POPUP,
            'cursor': 'hand2',
            'activebackground': self.color_palette.HEADER,
            'borderwidth': 1,
        }
        next_text = self.lpack.od.color_bounds_selector_frame.NEXT
        change_image_text = self.lpack.od.color_bounds_selector_frame.CHANGE_IMAGE
        self.next_button = tk.Button(text=next_text, **button_params, command=lambda: self.event_generate('<<ColorBoundsSelected>>'))
        self.next_button.place(relx=.7, rely=.1, relwidth=.25, relheight=.35)
        self.change_image_button = tk.Button(text=change_image_text, **button_params, command=self._on_change_image_button_click)
        self.change_image_button.place(relx=.7, rely=.55, relwidth=.25, relheight=.35)
        
    def update_images(self) -> None:
        self.update()

        lower_h = self.lower_h_slider.get()
        lower_s = self.lower_s_slider.get()
        lower_v = self.lower_v_slider.get()
        upper_h = self.upper_h_slider.get()
        upper_s = self.upper_s_slider.get()
        upper_v = self.upper_v_slider.get()

        lower_bound = (lower_h, lower_s, lower_v)
        upper_bound = (upper_h, upper_s, upper_v)

        relx1, relx2, rely = .05, .525, .05
        relwidth, relheight = .425, .7
        mask = self._get_color_mask(self.video_frames[self.current_image], lower_bound, upper_bound)
        self.original_image = funcs.get_image_widget_from_cv2(self, self.video_frames[self.current_image], self.color_palette.BACKGROUND, relwidth, relheight)
        self.masked_image = funcs.get_image_widget_from_cv2(self, mask, self.color_palette.BACKGROUND, relwidth, relheight)
        self.original_image.place(relx=relx1, rely=rely, relwidth=relwidth, relheight=relheight)
        self.masked_image.place(relx=relx2, rely=rely, relwidth=relwidth, relheight=relheight)

    def _on_slider_update(self, event: tk.Event) -> None:
        self.update_images()

    def _on_change_image_button_click(self) -> None:
        self.current_image = random.randint(0, len(self.video_frames) - 1)
        self.update_images()

    def _get_color_mask(self, image: cv2.typing.MatLike, lower_bound: tuple[int], upper_bound: tuple[int]) -> cv2.typing.MatLike:
        '''Returns a mask of the image based on the given color bounds.

        :param cv2.typing.MatLike image: Image to apply the mask to.
        :param tuple[int] lower_bound: Lower HSV bound of the color range.
        :param tuple[int] upper_bound: Upper HSV bound of the color range.
        :return cv2.typing.MatLike: Masked image.
        '''
        # Convert the image to HSV color space
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  

        # Create a mask based on the color bounds
        mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

        # # Apply the mask to the image
        # masked_image = cv2.bitwise_and(image, image, mask=mask)

        # # Convert the masked image to PIL format
        # masked_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2RGB)

        return mask



class ScaleSelectorFrame(frames.CustomFrame):

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, language_pack: enums.LanguagePackEnum, video_frames: list[cv2.typing.MatLike]) -> None:
        super().__init__(parent, color_palette)
        self.lpack = language_pack

        self.video_frames = video_frames
        self.first_point: tuple[int, int] = None
        self.second_point: tuple[int, int] = None
        self.distance: float = None
        self.distance_unit_power: int = 0
        self.distance_unit_str = tk.StringVar()

        self.selected_point = 1
        self.current_image = 0
        self.canvas = frames.PanZoomCanvas(self, self.color_palette, self.video_frames[self.current_image])
        self.canvas.place(relx=.05, rely=.05, relwidth=.9, relheight=.7)

        self.settings_bar = tk.Frame(self, bg=self.color_palette.POPUP)
        self.settings_bar.place(relx=0, rely=.8, relwidth=1, relheight=.2)

        button_params = {
            'master': self.settings_bar,
            'font': ('', 10),
            'bg': self.color_palette.POPUP,
            'cursor': 'hand2',
            'activebackground': self.color_palette.HEADER,
            'borderwidth': 1,
        }
        # point selection buttons
        first_point_text = self.lpack.od.scale_selector_frame.SELECT_FIRST_POINT
        second_point_text = self.lpack.od.scale_selector_frame.SELECT_SECOND_POINT
        self.select_1st_point_btn = tk.Button(text=first_point_text, **button_params, command=self._on_point_1_selection)
        self.select_2nd_point_btn = tk.Button(text=second_point_text, **button_params, command=self._on_point_2_selection)
        self.select_1st_point_btn.place(relx=.050, rely=.10, relwidth=.25, relheight=.35)
        self.select_2nd_point_btn.place(relx=.325, rely=.10, relwidth=.25, relheight=.35)
        # other buttons
        next_text = self.lpack.od.scale_selector_frame.NEXT
        change_image_text = self.lpack.od.scale_selector_frame.CHANGE_IMAGE
        self.next_button = tk.Button(text=next_text, **button_params, command=self._on_next_button_click)
        self.change_image_button = tk.Button(text=change_image_text, **button_params, command=self._on_change_image_button_click)
        self.next_button.place(relx=.7, rely=.1, relwidth=.25, relheight=.35)
        self.change_image_button.place(relx=.7, rely=.55, relwidth=.25, relheight=.35)

        # distance input
        distance_text = self.lpack.od.scale_selector_frame.ENTER_DISTANCE
        self.distance_input_label = tk.Label(self.settings_bar, text=distance_text, bg=self.color_palette.POPUP, font=('', 10), anchor='w', justify='left', wraplength=200)
        self.distance_input = tk.Entry(self.settings_bar, validate='all', vcmd=(self.register(self._validate_distance_input), '%P'))
        self.distance_input.config(font=('', 10), bg=self.color_palette.POPUP, bd=0, cursor='hand2')
        
        self.distance_input_label.place(relx=.05, rely=.55, relwidth=.25, relheight=.35)
        self.distance_input.place(relx=.325, rely=.55, relwidth=.15, relheight=.35)

        # distance unit selector
        self.distance_unit_selector = tk.OptionMenu(self.settings_bar, self.distance_unit_str, 'm', 'mm', 'cm', 'km', command=self._on_distance_unit_change)
        self.distance_unit_selector.config(bg=self.color_palette.POPUP, font=('', 10), bd=0, cursor='hand2', activebackground=self.color_palette.HEADER)
        self.distance_unit_selector.place(relx=.475, rely=.55, relwidth=.1, relheight=.35)
        self.distance_unit_str.set('m')

        self.canvas.bind('<<PixelClicked>>', self._on_pixel_clicked)
        self.update_selector_buttons()

    def update_canvas(self) -> None:
        self.canvas.change_image(self.video_frames[self.current_image])

    def _on_point_1_selection(self) -> None:
        self.selected_point = 1
        self.update_selector_buttons()

    def _on_point_2_selection(self) -> None:
        self.selected_point = 2
        self.update_selector_buttons()

    def update_selector_buttons(self) -> None:
        self.select_1st_point_btn.config(relief=tk.RAISED, bg=self.color_palette.POPUP)
        self.select_2nd_point_btn.config(relief=tk.RAISED, bg=self.color_palette.POPUP)
        if self.selected_point == 1:
            self.select_1st_point_btn.config(relief=tk.SUNKEN, bg=self.color_palette.HEADER)
        elif self.selected_point == 2:
            self.select_2nd_point_btn.config(relief=tk.SUNKEN, bg=self.color_palette.HEADER)
        self.update()

    def _validate_distance_input(self, input_str: str) -> bool:
        '''Validate the distance input.

        :param str input_str: Input string.
        :return bool: True if the input is valid, False otherwise.
        '''
        try:
            self.distance = float(input_str)
            valid = True
            self.distance_input.config(bg=self.color_palette.POPUP)
        except ValueError:
            valid = False
        if input_str == '':
            self.distance = None
            valid = True
        return valid

    def _on_distance_unit_change(self, unit_str: str) -> None:
        if   unit_str == 'm' : self.distance_unit_power =  0
        elif unit_str == 'km': self.distance_unit_power =  3
        elif unit_str == 'cm': self.distance_unit_power = -2
        elif unit_str == 'mm': self.distance_unit_power = -3

    def _on_change_image_button_click(self) -> None:
        self.current_image = random.randint(0, len(self.video_frames) - 1)
        self.update_canvas()

    def _on_pixel_clicked(self, event: tk.Event) -> None:
        if self.selected_point == 1:
            self.first_point = (event.x, event.y)
            self.selected_point = 2
        elif self.selected_point == 2:
            self.second_point = (event.x, event.y)
            self.selected_point = 0
        
        self.update_selector_buttons()
        self.canvas.mark_image_points(self.first_point, self.second_point)

    def _on_next_button_click(self) -> None:
        valid_inputs = True
        if self.first_point is None:
            self.select_1st_point_btn.config(bg=self.color_palette.WARNING)
            valid_inputs = False
        if self.second_point is None:
            self.select_2nd_point_btn.config(bg=self.color_palette.WARNING)
            valid_inputs = False
        if self.distance is None:
            self.distance_input.config(bg=self.color_palette.WARNING)
            valid_inputs = False
        if valid_inputs: self.event_generate('<<ScaleSelected>>')



class OriginSelectorFrame(frames.CustomFrame):

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, language_pack: enums.LanguagePackEnum, video_frames: list[cv2.typing.MatLike]) -> None:
        super().__init__(parent, color_palette)
        self.lpack = language_pack

        self.video_frames = video_frames
        self.current_image = 0
        self.canvas = frames.PanZoomCanvas(self, self.color_palette, self.video_frames[self.current_image])
        self.canvas.place(relx=.05, rely=.05, relwidth=.9, relheight=.7)

        self.object_as_origin_frame: int = None
        self.custom_origin: bool = False
        self.custom_origin_point: tuple[int, int] = None

        self.settings_bar = tk.Frame(self, bg=self.color_palette.POPUP)
        self.settings_bar.place(relx=0, rely=.8, relwidth=1, relheight=.2)

        button_params = {
            'master': self.settings_bar,
            'font': ('', 10),
            'bg': self.color_palette.POPUP,
            'cursor': 'hand2',
            'activebackground': self.color_palette.HEADER,
            'borderwidth': 1,
        }
        
        custom_origin_text = self.lpack.od.origin_selector_frame.SELECT_CUSTOM_ORIGIN
        first_object_text = self.lpack.od.origin_selector_frame.FIRST_OBJECT_AS_ORIGIN
        last_object_text = self.lpack.od.origin_selector_frame.LAST_OBJECT_AS_ORIGIN
        self.custom_origin_btn = tk.Button(text=custom_origin_text, **button_params, command=self._on_custom_origin_selection)
        self.first_object_as_origin_btn = tk.Button(text=first_object_text, **button_params, command=self._on_first_object_as_origin_selection)
        self.last_object_as_origin_btn = tk.Button(text=last_object_text, **button_params, command=self._on_last_object_as_origin_selection)
        self.custom_origin_btn.place(relx=.05, rely=.10, relwidth=.525, relheight=.35)
        self.first_object_as_origin_btn.place(relx=.05, rely=.55, relwidth=.25, relheight=.35)
        self.last_object_as_origin_btn.place(relx=.325, rely=.55, relwidth=.25, relheight=.35)

        next_text = self.lpack.od.origin_selector_frame.NEXT
        change_image_text = self.lpack.od.origin_selector_frame.CHANGE_IMAGE
        self.next_button = tk.Button(text=next_text, **button_params, command=self._on_next_button_click)
        self.change_image_button = tk.Button(text=change_image_text, **button_params, command=self._on_change_image_button_click)
        self.next_button.place(relx=.7, rely=.1, relwidth=.25, relheight=.35)
        self.change_image_button.place(relx=.7, rely=.55, relwidth=.25, relheight=.35)

        self.canvas.bind('<<PixelClicked>>', self._on_pixel_clicked)
        self.update_buttons()

    def update_canvas(self) -> None:
        self.canvas.change_image(self.video_frames[self.current_image])

    def update_buttons(self) -> None:
        self.custom_origin_btn.config(relief=tk.RAISED, bg=self.color_palette.POPUP)
        self.first_object_as_origin_btn.config(relief=tk.RAISED, bg=self.color_palette.POPUP)
        self.last_object_as_origin_btn.config(relief=tk.RAISED, bg=self.color_palette.POPUP)
        if self.custom_origin:
            self.custom_origin_btn.config(relief=tk.SUNKEN, bg=self.color_palette.HEADER)
        elif self.object_as_origin_frame == 0:
            self.first_object_as_origin_btn.config(relief=tk.SUNKEN, bg=self.color_palette.HEADER)
        elif self.object_as_origin_frame == len(self.video_frames) - 1:
            self.last_object_as_origin_btn.config(relief=tk.SUNKEN, bg=self.color_palette.HEADER)
        self.update()

    def _on_custom_origin_selection(self) -> None:
        self.object_as_origin_frame = None
        self.custom_origin = True
        self.custom_origin_point = None
        self.update_buttons()

    def _on_first_object_as_origin_selection(self) -> None:
        self.object_as_origin_frame = 0
        self.custom_origin = False
        self.custom_origin_point = None
        self.canvas.mark_image_points()
        self.update_buttons()

    def _on_last_object_as_origin_selection(self) -> None:
        self.object_as_origin_frame = len(self.video_frames) - 1
        self.custom_origin = False
        self.custom_origin_point = None
        self.canvas.mark_image_points()
        self.update_buttons()

    def _on_next_button_click(self) -> None:
        if self.custom_origin and not self.custom_origin_point:
            self.custom_origin_btn.config(bg=self.color_palette.WARNING)
        elif not self.custom_origin and self.object_as_origin_frame is None:
            self.custom_origin_btn.config(bg=self.color_palette.WARNING)
            self.last_object_as_origin_btn.config(bg=self.color_palette.WARNING)
            self.first_object_as_origin_btn.config(bg=self.color_palette.WARNING)
        else:
            self.event_generate('<<OriginSelected>>')

    def _on_change_image_button_click(self) -> None:
        self.current_image = random.randint(0, len(self.video_frames) - 1)
        self.update_canvas()

    def _on_pixel_clicked(self, event: tk.Event) -> None:
        if self.custom_origin:
            self.custom_origin_point = (event.x, event.y)
        self.canvas.mark_image_points(self.custom_origin_point)



class SaveFrame(frames.CustomFrame):

    available_file_extensions = ['.csv', '.ods', '.xlsx']
    available_time_units = ['s', 'ms']

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, language_pack: enums.LanguagePackEnum, object_positions: list[tuple[int, int]], unit: str, time_interval: float) -> None:
        super().__init__(parent, color_palette)
        self.lpack = language_pack

        self.object_positions = object_positions
        self.positions_unit = unit
        self.positions_time_interval = time_interval

        self.file_extension = tk.StringVar(value=self.available_file_extensions[0])
        self.x_column_name = tk.StringVar(value='X')
        self.y_column_name = tk.StringVar(value='Y')
        self.include_unit = tk.BooleanVar(value=True)
        self.time_unit = tk.StringVar(value=self.available_time_units[0])
        self.round_values = tk.BooleanVar(value=False)
        self.decimal_places: int = 2
        self.invert_y_axis = tk.BooleanVar(value=False)

        self.options_frame = tk.Frame(self, bg=self.color_palette.POPUP)
        self.options_frame.place(relx=.2, rely=.1, relwidth=.6, relheight=.8)


        button_params = {
            'master': self.options_frame,
            'font': ('', 10),
            'bg': self.color_palette.POPUP,
            'cursor': 'hand2',
            'activebackground': self.color_palette.HEADER,
            'borderwidth': 1,
        }
        label_params = {
            'master': self.options_frame,
            'bg': self.color_palette.POPUP,
            'font': ('', 10),
            'anchor': 'w',
            'justify': 'left'
        }
        option_menu_params = {
            'bg': self.color_palette.POPUP,
            'font': ('', 10),
            'bd': 0,
            'cursor': 'hand2',
            'activebackground': self.color_palette.HEADER
        }
        entry_params = {
            'master': self.options_frame,
            'font': ('', 10), 
            'bg': self.color_palette.BACKGROUND,
            'bd': 0,
            'cursor': 'hand2'
        }
        checkbox_params = {
            'master': self.options_frame,
            'bg': self.color_palette.POPUP,
            'cursor': 'hand2',
            'activebackground': self.color_palette.HEADER,
            'borderwidth': 0
        }
        title_label_params = label_params.copy()
        title_label_params['font'] = ('', 20, 'bold')

        save_options_text = self.lpack.od.save_frame.SAVE_OPTIONS
        tk.Label(text=save_options_text, **title_label_params).place(relx=.05, rely=0, relwidth=.9, relheight=.1)

        file_format_text = self.lpack.od.save_frame.FILE_FORMAT
        tk.Label(text=file_format_text, **label_params).place(relx=.1, rely=.1, relwidth=.35, relheight=.05)
        self.file_format_selector = tk.OptionMenu(self.options_frame, self.file_extension, *self.available_file_extensions)
        self.file_format_selector.config(**option_menu_params)
        self.file_format_selector.place(relx=.55, rely=.1, relwidth=.35, relheight=.05)

        x_column_text = self.lpack.od.save_frame.X_COLUMN_NAME
        tk.Label(text=x_column_text, **label_params).place(relx=.1, rely=.2, relwidth=.35, relheight=.05)
        self.x_column_name_entry = tk.Entry(**entry_params, textvariable=self.x_column_name)
        self.x_column_name_entry.place(relx=.55, rely=.2, relwidth=.35, relheight=.05)

        y_column_text = self.lpack.od.save_frame.Y_COLUMN_NAME
        tk.Label(text=y_column_text, **label_params).place(relx=.1, rely=.25, relwidth=.35, relheight=.05)
        self.y_column_name_entry = tk.Entry(**entry_params, textvariable=self.y_column_name)
        self.y_column_name_entry.place(relx=.55, rely=.25, relwidth=.35, relheight=.05)

        include_units_text = self.lpack.od.save_frame.INCLUDE_UNITS
        tk.Label(text=include_units_text, **label_params).place(relx=.15, rely=.3, relwidth=.35, relheight=.05)
        self.include_units_checkbox = tk.Checkbutton(**checkbox_params, variable=self.include_unit)
        self.include_units_checkbox.place(relx=.55, rely=.3, relwidth=.05, relheight=.05)

        time_unit_text = self.lpack.od.save_frame.TIME_UNIT
        tk.Label(text=time_unit_text, **label_params).place(relx=.1, rely=.4, relwidth=.35, relheight=.05)
        self.time_unit_selector = tk.OptionMenu(self.options_frame, self.time_unit, *self.available_time_units)
        self.time_unit_selector.config(**option_menu_params)
        self.time_unit_selector.place(relx=.55, rely=.4, relwidth=.35, relheight=.05)

        round_values_text = self.lpack.od.save_frame.ROUND_VALUES
        tk.Label(text=round_values_text, **label_params).place(relx=.1, rely=.45, relwidth=.35, relheight=.05)
        self.round_values_checkbox = tk.Checkbutton(**checkbox_params, variable=self.round_values, command=self._on_round_values_checkbox_clicked)
        self.decimal_places_entry = tk.Entry(**entry_params, validate='all', vcmd=(self.register(self._validate_decimal_places_input), '%P'))
        self.decimal_places_entry.config(bg=self.color_palette.POPUP)
        self.round_values_checkbox.place(relx=.55, rely=.45, relwidth=.05, relheight=.05)
        self.decimal_places_entry.place(relx=.6, rely=.45, relwidth=.25, relheight=.05)
        tk.Label(text='dp', **label_params).place(relx=.85, rely=.45, relwidth=.05, relheight=.05)

        invert_y_axis_text = self.lpack.od.save_frame.INVERT_Y_AXIS
        tk.Label(text=invert_y_axis_text, **label_params).place(relx=.1, rely=.5, relwidth=.35, relheight=.05)
        self.invert_y_axis_checkbox = tk.Checkbutton(**checkbox_params, variable=self.invert_y_axis)
        self.invert_y_axis_checkbox.place(relx=.55, rely=.5, relwidth=.05, relheight=.05)

        save_text = self.lpack.od.save_frame.SAVE
        self.save_btn = tk.Button(text=save_text, **button_params, command=self._on_save_btn_click)
        self.save_btn.place(relx=.35, rely=.9, relwidth=.3, relheight=.05)

    def _on_round_values_checkbox_clicked(self) -> None:
        if not self.round_values.get():
            self.decimal_places_entry.config(bg=self.color_palette.POPUP)
            self.decimal_places_entry.delete(0, tk.END)
        else:
            self.decimal_places_entry.config(bg=self.color_palette.BACKGROUND)
            self.decimal_places_entry.delete(0, tk.END)
            self.decimal_places_entry.insert(0, str(self.decimal_places))

    def _validate_decimal_places_input(self, input_str: str) -> bool:
        try:
            assert self.round_values.get() is True
            decimal_places = int(input_str)
            assert decimal_places > 0
            self.decimal_places = decimal_places
            valid = True
        except ValueError: valid = False
        except AssertionError: valid = False
        if input_str == '':
            self.decimal_places = 2
            valid = True
        return valid

    def _on_save_btn_click(self) -> None:
        filetype = self.file_extension.get()
        filepath = filedialog.asksaveasfilename(defaultextension=filetype)

        time_col_name = self.lpack.od.save_frame.TIME_COLUMN_NAME + f' ({self.time_unit.get()})'
        time_power_factor = 3 if self.time_unit.get() == 'ms' else 1
        x_col_name = self.x_column_name.get().replace(',', ' ')
        y_col_name = self.y_column_name.get().replace(',', ' ')
        if self.include_unit.get():
            x_col_name += f' ({self.positions_unit})'
            y_col_name += f' ({self.positions_unit})'

        time_values, x_values, y_values = [], [], []
        for i, p in enumerate(self.object_positions):
            if p is not None:
                time_values.append(i * self.positions_time_interval * 10**time_power_factor)
                x_values.append(p[0])
                y_values.append(p[1])

        if self.round_values.get() is True:
            for i in range(len(time_values)):
                time_values[i] = round(time_values[i], self.decimal_places)
                x_values[i] = round(x_values[i], self.decimal_places)
                y_values[i] = round(y_values[i], self.decimal_places)

        # Condition is inverted because coordinates are by default from top to bottom
        # ( y values are already inverted by default )
        if self.invert_y_axis.get() is False:
            for i in range(len(time_values)):
                y_values[i] *= -1

        data = pd.DataFrame({
            time_col_name: time_values,
            x_col_name: x_values,
            y_col_name: y_values
        })

        if filetype == '.csv':
            data.to_csv(filepath, index=False)

        elif filetype == '.xlsx':
            data.to_excel(filepath, index=False, engine='openpyxl')
        
        elif filetype == '.ods':
            with pd.ExcelWriter(filepath, engine='odf') as writer:
                data.to_excel(writer, index=False)
