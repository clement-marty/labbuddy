import os
import webbrowser
import configparser
import tkinter as tk
from tkinter import ttk

from . import funcs
from .frames import StartFrame
from .object_detection import ObjectDetection
from .minmax_slopes import MinMaxSlopes


class Application(tk.Tk):

    def __init__(self, config: configparser.ConfigParser) -> None:
        tk.Tk.__init__(self)

        self.protocol('WM_DELETE_WINDOW', self.close_app)

        title = config.get('application', 'title')
        github_link = config.get('application', 'github_link')
        banner_filepath = os.path.join(os.getcwd(), config.get('application.assets', 'banner'))
        self.color_palette = {
            'background': config.get('application.color_palette', 'background'),
            'sidebar': config.get('application.color_palette', 'sidebar'),
            'header': config.get('application.color_palette', 'header'),
            'popup': config.get('application.color_palette', 'popup'),
            'warning': config.get('application.color_palette', 'warning')
        }

        self.title(title)
        self.geometry('1200x800')
        self.resizable(False, False)
        self.config(bg=self.color_palette['background'])

        self.load_styles()

        # Header
        self.header = tk.Frame(self, bg=self.color_palette['header'])
        self.header.place(relx=.2, rely=0, relwidth=.8, relheight=.1)
        self.header_title = tk.Label(
            self.header,
            text='',
            bg=self.color_palette['header'],
            font=('', 20, 'bold'),
            fg='#ffffff'
        )
        self.header_subtitle = tk.Label(
            self.header,
            text='',
            bg=self.color_palette['header'],
            font=('', 15),
            fg='#ffffff'
        )
        self.header_title.place(relx=.05, rely=.3, anchor='w')
        self.header_subtitle.place(relx=.05, rely=.7, anchor='w')

        # Sidebar
        self.sidebar = tk.Frame(self, bg=self.color_palette['sidebar'])
        self.sidebar.place(relx=0, rely=0, relwidth=.2, relheight=1)

        # Logo
        self.logo_frame = tk.Frame(self.sidebar, bg=self.color_palette['sidebar'])
        self.logo_frame.place(relx=0, rely=0, relwidth=1, relheight=.1)
        self.logo_frame.update()
        logo = funcs.get_image_widget_from_filepath(
            parent=self.logo_frame,
            filepath=banner_filepath,
            bg=self.color_palette['sidebar']
        )
        logo.place(relx=0, rely=0, relwidth=1, relheight=1)

        # MAIN FRAME
        self.main_frame = tk.Frame(self, bg='#ff0000')
        self.main_frame.place(relx=.2, rely=.1, relwidth=.8, relheight=.9)

        # SUBMENUES
        self.submenues_frame = tk.Frame(self.sidebar, bg=self.color_palette['sidebar'])
        self.submenues_frame.place(relx=0, rely=.15, relwidth=1, relheight=.85)
        self.submenues = (
            SidebarSubMenu(
                self.submenues_frame,
                self.main_frame,
                'Video Analysis',
                [ObjectDetection],
                self.color_palette,
                self.header_title,
                self.header_subtitle
            ),
            SidebarSubMenu(
                self.submenues_frame,
                self.main_frame,
                'Uncertainty Tools',
                [MinMaxSlopes],
                self.color_palette,
                self.header_title,
                self.header_subtitle
            )
        )
        # Place the submenus in the sidebar
        y = 0
        for submenu in self.submenues:
            height = 50 * ( len(submenu.options) + 1 )
            submenu.place(x=0, y=y, relwidth=1, height=height)
            y += height

        
        # START FRAME
        self.start_frame = StartFrame(self.main_frame, self.color_palette)
        self.start_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def load_styles(self):
        ttk.Style().configure('TProgressbar', background=self.color_palette['header'], bordercolor=self.color_palette['background'])

    def close_app(self):
        self.quit()
        self.destroy()



class SidebarSubMenu(tk.Frame):

    def __init__(self, parent: tk.Frame, main_frame: tk.Frame, heading: str, option_classes: list, color_palette: dict, header_title, header_subtitle) -> None:
        tk.Frame.__init__(self, parent)

        self.color_palette = color_palette
        self.header_title = header_title
        self.header_subtitle = header_subtitle

        self.config(bg=self.color_palette['sidebar'])
        self.sub_menu_heading_label = tk.Label(
            self,
            text=heading,
            bg=self.color_palette['sidebar'],
            font=('', 12, 'bold'),
            fg='#ffffff'
        )
        self.sub_menu_heading_label.place(x=30, y=10, anchor='w')

        sub_menu_sep = ttk.Separator(self, orient='horizontal')
        sub_menu_sep.place(x=30, y=30, relwidth=.8, anchor='w')

        self.options = []
        for option_class in option_classes:
            option = option_class(main_frame, self.color_palette, self.header_title, self.header_subtitle)
            option.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.options.append(option)


        for i in range(len(self.options)):
            option = self.options[i]

            button = tk.Button(
                self,
                text=option.display_name,
                bg=self.color_palette['sidebar'],
                font=('', 10),
                bd=0,
                cursor='hand2',
                activebackground='#ffffff',
                fg='#ffffff',
                width=20,
                borderwidth=1,
                command=option.load
            )
            button.place(x=30, y=60 + 30*i, anchor='w')
