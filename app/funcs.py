import cv2
import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
from PIL import Image, ImageTk



def get_image_widget(parent: tk.Frame, image: Image.Image, bg: str, relwidth: float =1, relheight: float =1) -> tk.Frame:
    '''Returns a widget containing the image specified, with it being resized to fit the parent widget
    
    :param tk.Frame parent: The image's parent widget
    :param str filepath: The image object
    :param str bg: The widget's background color
    :param float relwidth: The width of the widget relative to the parent's width, defaults to 1
    :param float relheight: The height of the widget relative to the parent's height, defaults to 1
    :return tk.Frame: The created widget
    '''
    scale_w = parent.winfo_width() * relwidth / image.width
    scale_h = parent.winfo_height() * relheight / image.height

    scaling_factor = min(scale_w, scale_h)
    im = image.resize((int(image.width * scaling_factor), int(image.height * scaling_factor)), resample=Image.Resampling.NEAREST)

    frame = tk.Frame(parent, bg=bg, width=relwidth*parent.winfo_width(), height=relheight*parent.winfo_height())

    imtk = ImageTk.PhotoImage(im)
    widget = tk.Label(frame, image=imtk, bg=bg)
    widget.image = imtk
    widget.pack(expand=True)

    return frame

def get_image_widget_from_filepath(parent: tk.Frame, filepath: str, bg: str, relwidth: float =1, relheight: float =1) -> tk.Label:
    '''Returns a widget containing the image file specified, with it being resized to fit the parent widget
    
    :param tk.Frame parent: The image's parent widget
    :param str filepath: The path of the image file
    :param str bg: The widget's background color
    :param float relwidth: The width of the widget relative to the parent's width, defaults to 1
    :param float relheight: The height of the widget relative to the parent's height, defaults to 1
    :return tk.Label: The created widget
    '''
    image = Image.open(filepath)
    return get_image_widget(parent, image, bg, relwidth, relheight)

def get_image_widget_from_cv2(parent: tk.Frame, image: cv2.typing.MatLike, bg: str, relwidth: float =1, relheight: float =1) -> tk.Label:
    '''Returns a widget containing the opencv image specified, with it being resized to fit the parent widget
    
    :param tk.Frame parent: The image's parent widget
    :param str filepath: The image as an opencv object in BGR format
    :param str bg: The widget's background color
    :param float relwidth: The width of the widget relative to the parent's width, defaults to 1
    :param float relheight: The height of the widget relative to the parent's height, defaults to 1
    :return tk.Label: The created widget
    '''
    im = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    return get_image_widget(parent, im, bg, relwidth, relheight)

def collision_line_rectangle(m: float, c: float, x: float, y: float, w: float, h: float) -> bool:
    '''Checks if a line (y=mx+c) collides with a rectangle

    :param float m: The slope of the line
    :param float c: The y-intercept of the line
    :param float x: The x coordinate of the top left corner of the rectangle
    :param float y: The y coordinate of the top left corner of the rectangle
    :param float w: The width of the rectangle
    :param float h: The height of the rectangle
    :return bool: True if the line collides with the rectangle, False otherwise
    '''
    # For each corner (x, y) of the rectangle, we compute mx + c - y
    # If the computed values of opposed corners have opposite signs, then the line crosses the rectangle
    f = lambda x, y: m*x + c - y
    top_left = f(x, y)
    top_right = f(x + w, y)
    bottom_left = f(x, y + h)
    bottom_right = f(x + w, y + h)
    return (top_left == 0 or top_right == 0 or bottom_left == 0 or bottom_right == 0
        or top_left//abs(top_left) != bottom_right//abs(bottom_right) 
        or top_right//abs(top_right) != bottom_left/abs(bottom_left)
    )

def equation_widget(parent: tk.Frame, exps: list[str], bg: str = None) -> tk.Widget:
    '''Returns a tkinter widget containing the LaTeX given as parameter
    
    :param tk.Frame parent: The widget's parent
    :param list[str] exps: The list of LaTeX expressions to be rendered in the widget
    :param str bg: The background color of the widget
    :return tk.Widget: The widget on which the LaTeX expressions were rendered
    '''
    matplotlib.use('TkAgg')
    fig, ax = plt.subplots(1,1)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    
    if bg is not None:
        fig.patch.set_facecolor(bg)

    canvas = tkagg.FigureCanvasTkAgg(fig, parent)
    n = len(exps)
    for i in range(n):
        ax.text(.05, .2 + .4*i, r'$\mathit{ ? }$'.replace('?', exps[n-1-i]))
    canvas.draw()

    return canvas.get_tk_widget()
