import re
import pandas as pd
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.collections as collections
import matplotlib.backends.backend_tkagg as tkagg

from . import funcs
from . import enums
from . import frames



class MinMaxSlopes(frames.SubMenuOption):

    display_name = 'Min-Max Slopes'
    title = 'Min-Max Slopes'
    file_input_title = 'Select a file'
    data_selection_title = 'Select the data series'
    plot_title = 'Results'
    supported_filetypes = [
        ('Spreadsheet files', '*.csv *.ods *.xlsx'),
    ]

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, header_title: tk.Frame, header_subtitle: tk.Frame) -> None:
        super().__init__(parent, color_palette, header_title, header_subtitle)
        self.color_palette = color_palette

        self.filepath: str = None
        self.filetype: str = None
        self.data: pd.DataFrame = None
        self.excel_file: pd.ExcelFile = None
        self.x_values: list[float]
        self.y_values: list[float]

    def load(self) -> None:
        self.tkraise()

        self.header_title.config(text=self.title)
        self.header_subtitle.config(text=self.subtitle)

        self.file_input_frame = frames.FileInputFrame(
            self,
            self.color_palette,
            title='Select a spreadsheet file',
            text='Supported formats are CSV, ODS and XLSX',
            filetypes=self.supported_filetypes
        )

        self.header_title.config(text=' - '.join([self.title, self.file_input_title]))
        self.file_input_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.file_input_frame.bind('<<FileSelected>>', self._on_file_selected)

    def _on_file_selected(self, event: tk.Event) -> None:
        self._load_spreadsheet(self.file_input_frame.filepath)
        self.data_selection_frame = DataSelectionFrame(
            self, 
            self.color_palette,
            **{'data': self.data} if self.data is not None else {'excel_file': self.excel_file}
        )
        self.header_title.config(text=' - '.join([self.title, self.data_selection_title]))
        self.data_selection_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.data_selection_frame.bind('<<DataSelected>>', self._on_data_selected)
        self.file_input_frame.destroy()

    def _on_data_selected(self, event: tk.Event) -> None:
        self.x_column_name, self.y_column_name = self.data_selection_frame.x_column_name.get(), self.data_selection_frame.y_column_name.get()
        self.x_values = self.data_selection_frame.df[self.x_column_name].tolist()
        self.y_values = self.data_selection_frame.df[self.y_column_name].tolist()
        self.dx_values, self.dy_values = [], []

        dx_type, dy_type = self.data_selection_frame.x_uncertainties_type.get(), self.data_selection_frame.y_uncertainties_type.get()
        type_relative, type_constant, type_column = self.data_selection_frame.uncertainties_type_selector_options

        # Get the uncertainty values on X
        if dx_type == type_constant: self.dx_values = [self.data_selection_frame.x_uncertainties] * len(self.x_values)
        elif dx_type == type_relative: self.dx_values = [self.data_selection_frame.x_uncertainties * val for val in self.x_values]
        elif dx_type == type_column: self.dx_values = self.data_selection_frame.df[self.data_selection_frame.x_uncertainties_column.get()].tolist()
        # Get the uncertainty values on Y
        if dy_type == type_constant: self.dy_values = [self.data_selection_frame.y_uncertainties] * len(self.y_values)
        elif dy_type == type_relative: self.dy_values = [self.data_selection_frame.y_uncertainties * val for val in self.y_values]
        elif dy_type == type_column: self.dy_values = self.data_selection_frame.df[self.data_selection_frame.y_uncertainties_column.get()].tolist()

        self.plot_frame = PlotFrame(self, self.color_palette, self.x_values, self.y_values, self.x_column_name, self.y_column_name, self.dx_values, self.dy_values)
        self.header_title.config(text=' - '.join([self.title, self.plot_title]))
        self.plot_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.data_selection_frame.destroy()
  
    def _load_spreadsheet(self, filepath: str) -> None:
        self.filepath = filepath
        self.filetype = self.filepath.split('.')[-1]

        if self.filetype == 'csv':
            self.data = pd.read_csv(filepath)
        if self.filetype == 'ods':
            self.excel_file = pd.ExcelFile(filepath, engine='odf')
        if self.filetype == 'xlsx':
            self.excel_file = pd.ExcelFile(filepath, engine='openpyxl')



class DataSelectionFrame(frames.CustomFrame):

    def __init__(self, parent: tk.Frame, color_palette: enums.configparser, data: pd.DataFrame = None, excel_file: pd.ExcelFile = None) -> None:
        super().__init__(parent, color_palette)
        self.data = data
        self.excel_file = excel_file

        self.df = data if data is not None else None
        self.uncertainties_type_selector_options = ['Relative', 'Constant', 'Select a column']

        self.sheet_name = tk.StringVar(value=None)
        self.x_column_name = tk.StringVar(value=None)
        self.y_column_name = tk.StringVar(value=None)
        self.x_uncertainties_type = tk.StringVar(value=self.uncertainties_type_selector_options[0])
        self.y_uncertainties_type = tk.StringVar(value=self.uncertainties_type_selector_options[0])
        self.x_uncertainties: float = 0
        self.y_uncertainties: float = 0
        self.x_uncertainties_column = tk.StringVar(value='')
        self.y_uncertainties_column = tk.StringVar(value='')

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

        tk.Label(text='Select your data', **title_label_params).place(relx=.05, rely=0, relwidth=.9, relheight=.1)

        if self.excel_file is not None:
            tk.Label(text='Select the sheet:', **label_params).place(relx=.1, rely=.1, relwidth=.35, relheight=.1)
            self.sheet_name.set(self.excel_file.sheet_names[0]) # Set the default selector value as the first sheet
            self.sheet_selector = tk.OptionMenu(self.options_frame, self.sheet_name, *self.excel_file.sheet_names, command=self._update_selector_options)
            self.sheet_selector.config(**option_menu_params)
            self.sheet_selector.place(relx=.55, rely=.1, relwidth=.35, relheight=.05)
            self.df = self.excel_file.parse(self.sheet_name.get())

        tk.Label(text='X values column:', **label_params).place(relx=.1, rely=.2, relwidth=.35, relheight=.05)
        self.x_column_selector = tk.OptionMenu(self.options_frame, self.x_column_name, '', '')
        self.x_column_selector.config(**option_menu_params)
        self.x_column_selector.place(relx=.55, rely=.2, relwidth=.35, relheight=.05)

        tk.Label(text='Y values column:', **label_params).place(relx=.1, rely=.25, relwidth=.35, relheight=.05)
        self.y_column_selector = tk.OptionMenu(self.options_frame, self.y_column_name, '', '')
        self.y_column_selector.config(**option_menu_params)
        self.y_column_selector.place(relx=.55, rely=.25, relwidth=.35, relheight=.05)
        
        tk.Label(text='Uncertainties on X values:', **label_params).place(relx=.1, rely=.35, relwidth=.35, relheight=.05)
        self.x_uncertainties_type_selector = tk.OptionMenu(self.options_frame, self.x_uncertainties_type, *self.uncertainties_type_selector_options, command=self._update_x_uncertainties_options)
        self.x_uncertainties_type_selector.config(**option_menu_params)
        self.x_uncertainties_type_selector.place(relx=.55, rely=.35, relwidth=.35, relheight=.05)

        tk.Label(text='Value:', **label_params).place(relx=.15, rely=.4, relwidth=.3, relheight=.05)
        self.x_uncertainties_entry = tk.Entry(**entry_params, validate='all', vcmd=(self.register(self._validate_x_uncertainties_input), '%P'))
        self.x_uncertainties_entry.place(relx=.55, rely=.4, relwidth=.35, relheight=.05)

        tk.Label(text='Column:', **label_params).place(relx=.15, rely=.45, relwidth=.35, relheight=.05)
        self.x_uncertainties_column_selector = tk.OptionMenu(self.options_frame, self.x_uncertainties_column, '', '')
        self.x_uncertainties_column_selector.config(**option_menu_params)
        self.x_uncertainties_column_selector.place(relx=.55, rely=.45, relwidth=.35, relheight=.05)

        tk.Label(text='Uncertainties on Y values:', **label_params).place(relx=.1, rely=.5, relwidth=.35, relheight=.05)
        self.y_uncertainties_type_selector = tk.OptionMenu(self.options_frame, self.y_uncertainties_type, *self.uncertainties_type_selector_options, command=self._update_y_uncertainties_options)
        self.y_uncertainties_type_selector.config(**option_menu_params)
        self.y_uncertainties_type_selector.place(relx=.55, rely=.5, relwidth=.35, relheight=.05)

        tk.Label(text='Value:', **label_params).place(relx=.15, rely=.55, relwidth=.3, relheight=.05)
        self.y_uncertainties_entry = tk.Entry(**entry_params, validate='all', vcmd=(self.register(self._validate_y_uncertainties_input), '%P'))
        self.y_uncertainties_entry.place(relx=.55, rely=.55, relwidth=.35, relheight=.05)

        tk.Label(text='Column:', **label_params).place(relx=.15, rely=.6, relwidth=.35, relheight=.05)
        self.y_uncertainties_column_selector = tk.OptionMenu(self.options_frame, self.y_uncertainties_column, '', '')
        self.y_uncertainties_column_selector.config(**option_menu_params)
        self.y_uncertainties_column_selector.place(relx=.55, rely=.6, relwidth=.35, relheight=.05)

        self.next_btn = tk.Button(text='Next', **button_params, command=self._on_next_btn_clicked)
        self.next_btn.place(relx=.35, rely=.9, relwidth=.3, relheight=.05)


        self._update_selector_options()
        self._update_x_uncertainties_options()
        self._update_y_uncertainties_options()

    def _update_selector_options(self, event: tk.Event = None) -> None:
        if self.excel_file is not None:
            self.df = self.excel_file.parse(self.sheet_name.get())
        column_names = self.df.columns.values.tolist()
        c1, c2, c3, c4 = '', '', '', ''
        if len(column_names) >= 2:
            c1, c2 = column_names[0], column_names[1]
            c3, c4 = column_names[2%len(column_names)], column_names[3%len(column_names)]
        else:
            self.sheet_selector.config(bg=self.color_palette.WARNING)
        
        if not (self.x_column_name.get() in column_names and self.y_column_name.get() in column_names):
            self.x_column_name.set(c1)
            self.y_column_name.set(c2)
        
        # Remove previous options
        self.x_column_selector['menu'].delete(0, tk.END)
        self.y_column_selector['menu'].delete(0, tk.END)
        update_dx_selector, update_dy_selector = False, False
        if self.x_uncertainties_type.get() == self.uncertainties_type_selector_options[-1] and self.x_uncertainties_column.get() == '':
            self.x_uncertainties_column_selector['menu'].delete(0, tk.END)
            self.x_uncertainties_column.set(c3)
            update_dx_selector = True
        if self.y_uncertainties_type.get() == self.uncertainties_type_selector_options[-1] and self.y_uncertainties_column.get() == '':
            self.y_uncertainties_column_selector['menu'].delete(0, tk.END)
            self.y_uncertainties_column.set(c4)
            update_dy_selector = True
        # Add the new options to each OptionMenu
        for col in column_names:
            self.x_column_selector['menu'].add_command(label=col, command=tk._setit(self.x_column_name, col))
            self.y_column_selector['menu'].add_command(label=col, command=tk._setit(self.y_column_name, col))
            if update_dx_selector:
                self.x_uncertainties_column_selector['menu'].add_command(label=col, command=tk._setit(self.x_uncertainties_column, col))
            if update_dy_selector:
                self.y_uncertainties_column_selector['menu'].add_command(label=col, command=tk._setit(self.y_uncertainties_column, col))

    def _update_x_uncertainties_options(self, uncertainty_type: str = None) -> None:
        if uncertainty_type is None: uncertainty_type = self.x_uncertainties_type.get()
        return self._update_uncertainties_options(uncertainty_type, self.x_uncertainties_entry, self.x_uncertainties_column_selector, self.x_uncertainties_column)
    
    def _update_y_uncertainties_options(self, uncertainty_type: str = None) -> None:
        if uncertainty_type is None: uncertainty_type = self.y_uncertainties_type.get()
        return self._update_uncertainties_options(uncertainty_type, self.y_uncertainties_entry, self.y_uncertainties_column_selector, self.y_uncertainties_column)

    def _update_uncertainties_options(self, uncertainty_type: str, entry: tk.Entry, selector: tk.OptionMenu, selector_variable: tk.StringVar) -> None:
        if uncertainty_type == self.uncertainties_type_selector_options[-1]:
            entry.delete(0, tk.END)
            entry.config(bg=self.color_palette.HEADER)
            selector.config(bg=self.color_palette.POPUP)
            self._update_selector_options()
        else:
            selector_variable.set('')
            selector['menu'].delete(0, tk.END)
            selector.config(bg=self.color_palette.HEADER)
            entry.config(bg=self.color_palette.POPUP)

    def _validate_x_uncertainties_input(self, input_str: str) -> bool:
        return self._validate_uncertainties_input(input_str, x_values=True)
    
    def _validate_y_uncertainties_input(self, input_str: str) -> bool:
        return self._validate_uncertainties_input(input_str, x_values=False)

    def _validate_uncertainties_input(self, input_str: str, x_values: bool) -> bool:
        uncertainties_type = self.x_uncertainties_type.get() if x_values else self.y_uncertainties_type
        try:
            assert uncertainties_type != self.uncertainties_type_selector_options[-1]
            uncertainty = float(input_str)
            assert uncertainty > 0
            if x_values: self.x_uncertainties = uncertainty
            else: self.y_uncertainties = uncertainty
            valid = True
        except ValueError: valid = False
        except AssertionError: valid = False
        # if input_str in ['', '.', '0', '0.']:
            
        if re.compile(r'\A[0]*\.?[0]*\Z').match(input_str):
            if x_values: self.x_uncertainties = 0
            else: self.y_uncertainties = 0
            valid = True
        return valid

    def _on_next_btn_clicked(self) -> None:
        if len(self.df.columns.values.tolist()) < 2: pass
        else:
            self.event_generate('<<DataSelected>>')



class PlotFrame(frames.CustomFrame):

    def __init__(self, parent: tk.Frame, color_palette: enums.ColorPaletteEnum, x_values: list[float], y_values: list[float], x_name: str, y_name: str, dx_values: list[float], dy_values: list[float]) -> None:
        super().__init__(parent, color_palette)

        self.x_values, self.y_values = x_values, y_values
        self.x_name, self.y_name = x_name, y_name
        self.dx_values, self.dy_values = dx_values, dy_values

        self.min_slope: float = None
        self.max_slope: float = None
        self.min_y_intercept: float = None
        self.max_y_intercept: float = None

        self.btns_frame = tk.Frame(self, bg=self.color_palette.POPUP)
        self.btns_frame.place(relx=0, rely=.8, relwidth=1, relheight=.2)

        self._add_graph_canvas()

        self.slope_min_frame = tk.Frame(self.btns_frame)
        self.slope_max_frame = tk.Frame(self.btns_frame)
        self.slope_result_frame = tk.Frame(self.btns_frame)
        self._display_slope_equation(self.slope_min_frame, self.min_slope, self.min_y_intercept, 'Minimum Slope:')
        self._display_slope_equation(self.slope_max_frame, self.max_slope, self.max_y_intercept, 'Maximum Slope:')
        self._display_slope_result(self.slope_result_frame, self.avg_slope, self.slope_uncertainty, 'Value of the slope (y=mx+c):')
        self.slope_min_frame.place(relx=.0, rely=0, relwidth=.5, relheight=.5)
        self.slope_max_frame.place(relx=.5, rely=0, relwidth=.5, relheight=.5)
        self.slope_result_frame.place(relx=.5, rely=.5, relwidth=.5, relheight=.5)

    def _add_graph_canvas(self) -> None:
        fig, ax = plt.subplots(1, 1)
        fig.patch.set_facecolor(self.color_palette.BACKGROUND)
        ax.plot(self.x_values, self.y_values, 'k+')
        self._add_uncertainty_boxes(ax)
        self._get_slopes()
        self._add_line(ax, self.min_slope, self.min_y_intercept)
        self._add_line(ax, self.max_slope, self.max_y_intercept)
        
        canvas = tkagg.FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        toolbar = tkagg.NavigationToolbar2Tk(canvas, window=self.btns_frame)
        toolbar.config(bg=self.color_palette.POPUP)
        toolbar.update()
        canvas.get_tk_widget().place(relx=0, rely=0, relwidth=1, relheight=.8)
        toolbar.place(relx=.05, rely=.6, relwidth=.4, relheight=.3)

    def _add_uncertainty_boxes(self, axis: plt.Axes) -> None:
        facecolor = '#dddddd'
        edgecolor = '#333333'
        boxes = [
            patches.Rectangle((x - dx, y - dy), width=2*dx, height=2*dy)
            for x, y, dx, dy in zip(self.x_values, self.y_values, self.dx_values, self.dy_values)
        ]
        axis.add_collection(collections.PatchCollection(boxes, facecolor=facecolor, edgecolor=edgecolor))

    def _add_line(self, axis: plt.Axes, slope: float, y_intercept: float) -> None:
        x1, x2 = self.x_values[0] - self.dx_values[0], self.x_values[-1] + self.dx_values[-1]
        y1, y2 = slope * x1 + y_intercept, slope * x2 + y_intercept
        axis.plot([x1, x2], [y1, y2])

    def _get_slopes(self) -> None:
        # Compute the positions of all points at the corner of every uncertainty box
        points = []
        for i in range(len(self.x_values)):
            xi, yi = self.x_values[i], self.y_values[i]
            dxi, dyi = self.dx_values[i], self.dy_values[i]
            points.extend([
                (xi - dxi, yi - dyi), # bottom-left point
                (xi - dxi, yi + dyi), # top-left point
                (xi + dxi, yi - dyi), # bottom-right point
                (xi + dxi, yi + dyi)  # top-right point
            ])

        slope_min, slope_max = float('inf'), -float('inf')
        y_intercept_min, y_intercept_max = 0, 0
        # Check every slope between every possible pair of points computed above
        for i in range(len(points)):
            for j in range(i+1, len(points)):
                x1, y1, x2, y2 = *points[i], *points[j]

                # Skip points having the same x position to avoid ZeroDivisionError and infinite slopes
                if x1 == x2: continue

                # Compute the slope (m) and y-intercept (c) of the line between the two points
                m = (y2 - y1) / (x2 - x1)
                c = y1 - m * x1 # We use y=mx+c
                
                # Check if the line goes through every uncertainty box
                if (m < slope_min or m > slope_max) and self._is_slope_valid(m, c):
                    if m < slope_min: slope_min, y_intercept_min = m, c
                    if m > slope_max: slope_max, y_intercept_max = m, c

        if slope_min != float('inf') and slope_max != -float('inf'):
            self.min_slope, self.max_slope = slope_min, slope_max
            self.min_y_intercept, self.max_y_intercept = y_intercept_min, y_intercept_max

            self.avg_slope = (self.max_slope + self.min_slope) / 2
            self.slope_uncertainty = (self.max_slope - self.min_slope) / 2

    def _is_slope_valid(self, slope: float, y_intercept: float) -> bool:
        '''Checks if the provided line crosses all uncertainty boxes of all points

        :param float slope: The slope of the line
        :param float y_intercept: The y-intercept of the line
        :return bool: True if the line crosses all uncertainty boxes, False otherwise
        '''
        valid = True
        i = 0
        while valid and i < len(self.x_values):

            if  not funcs.collision_line_rectangle(
                m= slope, 
                c= y_intercept,
                x= self.x_values[i] - self.dx_values[i],
                y= self.y_values[i] - self.dx_values[i],
                w= 2 * self.dx_values[i],
                h= 2 * self.dy_values[i]
            ):
                valid = False
            i += 1
        return valid

    def _display_slope_equation(self, parent: tk.Frame, slope: float, y_intercept: float, text: str) -> None:
        frame = tk.Frame(parent, bg=self.color_palette.POPUP)
        label_params = {
            'master': frame,
            'bg': self.color_palette.POPUP,
            'font': ('', 10, 'bold'),
            'anchor': 'c',
            'justify': 'center'
        }
        tk.Label(text=text, **label_params).pack(expand=True)
        frame.place(relx=0, rely=0, relwidth=1, relheight=.25)
        funcs.equation_widget(parent, [f'm={slope}', f'c={y_intercept}'], bg=self.color_palette.POPUP).place(relx=0, rely=.25, relwidth=1, relheight=.75)

    def _display_slope_result(self, parent: tk.Frame, slope: float, slope_uncertainty: float, text: str) -> None:
        frame = tk.Frame(parent, bg=self.color_palette.POPUP)
        label_params = {
            'master': frame,
            'bg': self.color_palette.POPUP,
            'font': ('', 10, 'bold'),
            'anchor': 'c',
            'justify': 'center'
        }
        tk.Label(text=text, **label_params).pack(expand=True)
        frame.place(relx=0, rely=0, relwidth=1, relheight=.25)
        funcs.equation_widget(parent, [f'm={slope}', f'\\Delta m={slope_uncertainty}'], bg=self.color_palette.POPUP).place(relx=0, rely=.25, relwidth=1, relheight=.75)
