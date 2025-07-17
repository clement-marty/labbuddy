import os
import webbrowser
import configparser
import tkinter as tk
from tkinter import ttk

from . import funcs
from . import enums
from .frames import StartFrame, ComingSoonFrame, CreditsFrame
from .object_detection import ObjectDetection
from .minmax_slopes import MinMaxSlopes


class Application(tk.Tk):

    def __init__(self, config: configparser.ConfigParser) -> None:
        tk.Tk.__init__(self)

        self.protocol('WM_DELETE_WINDOW', self.close_app)

        title = config.get('application', 'title')
        self.version = config.get('application', 'version')
        github_link = config.get('application', 'github_link')
        banner_filepath = os.path.join(os.getcwd(), config.get('application.assets', 'banner'))
        banner_inverted_filepath = os.path.join(os.getcwd(), config.get('application.assets', 'banner_inverted'))
        self.color_palette = enums.ColorPaletteEnum(config)
        self.icons = enums.IconsEnum(config)

        self.title(title)
        self.geometry('1200x800')
        self.resizable(False, False)
        self.config(bg=self.color_palette.BACKGROUND)

        self.load_styles()

        # Header
        self.header = tk.Frame(self, bg=self.color_palette.HEADER)
        self.header.place(relx=.2, rely=0, relwidth=.8, relheight=.1)
        self.header_title = tk.Label(
            self.header,
            text='',
            bg=self.color_palette.HEADER,
            font=('', 20, 'bold'),
            fg='#ffffff'
        )
        self.header_subtitle = tk.Label(
            self.header,
            text='',
            bg=self.color_palette.HEADER,
            font=('', 15),
            fg='#ffffff'
        )
        self.header_title.place(relx=.05, rely=.3, anchor='w')
        self.header_subtitle.place(relx=.05, rely=.7, anchor='w')

        # Sidebar
        self.sidebar = tk.Frame(self, bg=self.color_palette.SIDEBAR)
        self.sidebar.place(relx=0, rely=0, relwidth=.2, relheight=1)

        # Logo
        self.logo_frame = tk.Frame(self.sidebar, bg=self.color_palette.SIDEBAR)
        self.logo_frame.place(relx=0, rely=0, relwidth=1, relheight=.1)
        self.logo_frame.update()
        logo = funcs.get_image_widget_from_filepath(
            parent=self.logo_frame,
            filepath=banner_filepath,
            bg=self.color_palette.SIDEBAR
        )
        logo.place(relx=0, rely=0, relwidth=1, relheight=1)

        # MAIN FRAME
        self.main_frame = tk.Frame(self, bg=self.color_palette.BACKGROUND)
        self.main_frame.place(relx=.2, rely=.1, relwidth=.8, relheight=.9)

        # SUBMENUES
        self.submenues_frame = tk.Frame(self.sidebar, bg=self.color_palette.SIDEBAR)
        self.submenues_frame.place(relx=0, rely=.15, relwidth=1, relheight=.85)
        self.submenues_frame.update()
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
        rely = 0
        for submenu in self.submenues:
            relheight = .1 + .05 * len(submenu.options)
            submenu.place(relx=0, rely=rely, relwidth=1, relheight=relheight)
            rely += relheight

        # Add the buttons at the bottom of the sidebar
        btn_params = {
            'bg': self.color_palette.SIDEBAR,
            'bd': 0,
            'highlightthickness': 0,
            'relief': 'flat',
            'cursor': 'hand2',
            'activebackground': self.color_palette.BACKGROUND,
            'borderwidth': 1
        }
        funcs.add_icon_button( # Settings
            parent=self.submenues_frame,
            svg_file=self.icons.SETTINGS,
            color=self.color_palette.BACKGROUND,
            hovered_color=self.color_palette.SIDEBAR,
            relx=.125, rely=.9, relwidth=.15, relheight=.05,
            command=self.show_coming_soon_frame, **btn_params
        )
        funcs.add_icon_button( # Credits
            parent=self.submenues_frame,
            svg_file=self.icons.INFORMATION,
            color=self.color_palette.BACKGROUND,
            hovered_color=self.color_palette.SIDEBAR,
            relx=.325, rely=.9, relwidth=.15, relheight=.05,
            command=self.show_credits_frame, **btn_params
        )
        funcs.add_icon_button( # Github repository
            parent=self.submenues_frame,
            svg_file=self.icons.GITHUB,
            color=self.color_palette.BACKGROUND,
            hovered_color=self.color_palette.SIDEBAR,
            relx=.525, rely=.9, relwidth=.15, relheight=.05,
            command=lambda: webbrowser.open(github_link), **btn_params
        )
        funcs.add_icon_button( # Quit
            parent=self.submenues_frame, 
            svg_file=self.icons.QUIT, 
            color=self.color_palette.BACKGROUND,
            hovered_color=self.color_palette.WARNING, 
            relx=.7, rely=.9, relwidth=.15, relheight=.05, 
            command=self.close_app, **btn_params
        )
        version_label = tk.Label(
            self.submenues_frame,
            text=f'version {self.version}',
            bg=self.color_palette.SIDEBAR,
            font=('', 10, 'italic'),
            fg='#ffffff',
            anchor='c',
        )
        version_label.place(relx=.1, rely=.95, relwidth=.8, relheight=.05)
        
        
        # START FRAME
        self.start_frame = StartFrame(self.main_frame, self.color_palette, banner_inverted_filepath)
        self.start_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.start_frame.load()

    def load_styles(self):
        ttk.Style().configure('TProgressbar', background=self.color_palette.HEADER, bordercolor=self.color_palette.BACKGROUND)

    def show_coming_soon_frame(self):
        self.header_title.config(text='')
        self.header_subtitle.config(text='')
        frame = ComingSoonFrame(self.main_frame, self.color_palette)
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        frame.tkraise()

    def show_credits_frame(self):
        self.header_title.config(text='')
        self.header_subtitle.config(text='')
        frame = CreditsFrame(self.main_frame, self.color_palette, self.version)
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        frame.tkraise()
    
    def close_app(self):
        self.quit()
        self.destroy()



class SidebarSubMenu(tk.Frame):

    def __init__(self, parent: tk.Frame, main_frame: tk.Frame, heading: str, option_classes: list, color_palette: enums.ColorPaletteEnum, header_title, header_subtitle) -> None:
        tk.Frame.__init__(self, parent)

        self.color_palette = color_palette
        self.header_title = header_title
        self.header_subtitle = header_subtitle

        self.config(bg=self.color_palette.SIDEBAR)
        self.sub_menu_heading_label = tk.Label(
            self,
            text=heading,
            bg=self.color_palette.SIDEBAR,
            font=('', 12, 'bold'),
            fg='#ffffff'
        )

        rely_unit = 1 / (len(option_classes) + 2)

        self.sub_menu_heading_label.place(relx=.1, rely=rely_unit*.5, relwidth=.8, relheight=rely_unit)

        sub_menu_sep = ttk.Separator(self, orient='horizontal')
        sub_menu_sep.place(relx=.1, rely=rely_unit*1.5, relwidth=.8)

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
                bg=self.color_palette.SIDEBAR,
                font=('', 10),
                bd=0,
                cursor='hand2',
                activebackground='#ffffff',
                fg='#ffffff',
                width=20,
                borderwidth=1,
                command=option.load
            )
            button.place(relx=.1, rely=rely_unit * (i+2), relwidth=.8, relheight=rely_unit)
