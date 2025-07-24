import json
import configparser


class ColorPaletteEnum:

    BACKGROUND: str
    SIDEBAR: str
    HEADER: str
    POPUP: str
    WARNING: str

    def __init__(self, config: configparser.ConfigParser) -> None:
        self.BACKGROUND = config.get('application.color_palette', 'background')
        self.SIDEBAR = config.get('application.color_palette', 'sidebar')
        self.HEADER = config.get('application.color_palette', 'header')
        self.POPUP = config.get('application.color_palette', 'popup')
        self.WARNING = config.get('application.color_palette', 'warning')



class IconsEnum:

    INFORMATION: str
    ALERT: str
    QUIT: str
    SETTINGS: str
    GITHUB: str

    def __init__(self, config: configparser.ConfigParser) -> None:
        self.INFORMATION = config.get('application.icons', 'information')
        self.ALERT = config.get('application.icons', 'alert')
        self.QUIT = config.get('application.icons', 'quit')
        self.SETTINGS = config.get('application.icons', 'settings')
        self.GITHUB = config.get('application.icons', 'github')



class LanguagePackEnum:

    LANGUAGE: str
    APP_VERSION: str # Replace {{?}} with app version
    class submenus_names:
        VIDEO_ANALYSIS: str
        UNCERTAINTY_TOOLS: str
    class object_detection:
        DISPLAY_NAME: str
        TITLE: str
        LOADING_FRAMES: str
        PROCESSING_FRAMES: str
        CONVERTING_COORDINATES: str
        class file_input_frame:
            TITLE: str
            SELECT_FILE: str
            SUPPORTED_FORMATS: str
            BUTTON_TEXT: str
        class scale_selector_frame:
            TITLE: str
            SELECT_FIRST_POINT: str
            SELECT_SECOND_POINT: str
            ENTER_DISTANCE: str
            NEXT: str
            CHANGE_IMAGE: str
        class origin_selector_frame:
            TITLE: str
            SELECT_CUSTOM_ORIGIN: str
            FIRST_OBJECT_AS_ORIGIN: str
            LAST_OBJECT_AS_ORIGIN: str
            NEXT: str
            CHANGE_IMAGE: str
        class color_bounds_selector_frame:
            TITLE: str
            UPPER_BOUND: str # Replace {{?}} with parameter (H|S|V)
            LOWER_BOUND: str # Replace {{?}} with parameter (H|S|V)
            NEXT: str
            CHANGE_IMAGE: str
        class save_frame:
            TITLE: str
            SAVE_OPTIONS: str
            FILE_FORMAT: str
            X_COLUMN_NAME: str
            Y_COLUMN_NAME: str
            INCLUDE_UNITS: str
            TIME_UNIT: str
            ROUND_VALUES: str
            INVERT_Y_AXIS: str
            SAVE: str
            TIME_COLUMN_NAME: str
    class minmax_slopes:
        DISPLAY_NAME: str
        TITLE: str
        class file_input_frame:
            TITLE: str
            SELECT_FILE: str
            SUPPORTED_FORMATS: str
            BUTTON_TEXT: str
        class data_selection_frame:
            TITLE: str
            RELATIVE_TYPE: str
            CONSTANT_TYPE: str
            SELECT_COLUMN_TYPE: str
            SELECT_DATA: str
            SELECT_SHEET: str
            X_COLUMN: str
            Y_COLUMN: str
            X_UNCERTAINTIES: str
            Y_UNCERTAINTIES: str
            UNCERTAINTY_VALUE: str
            UNCERTAINTY_COLUMN: str
            NEXT: str
        class plot_frame:
            TITLE: str
            MINIMUM_SLOPE: str
            MAXIMUM_SLOPE: str
            SLOPE_VALUE: str
    class start_frame:
        WELCOME: str
        TEXT: str
    class coming_soon_frame:
        TITLE: str
        TEXT: str
    class credits_frame:
        TITLE: str
        LEFT_COLUMN_TEXT_LINES: list[str] # Line 0 -> replace {{?}} with app version
        RIGHT_COLUMN_TEXT_LINES: list[str]

    def __init__(self, filepath: str) -> None:

        class Obj:
            def __init__(self, d: dict) -> None: self.__dict__ = d

        def dict_to_obj(a: any) -> any:
            if isinstance(a, dict):
                d = {}
                for k, v in a.items():
                    v_obj = dict_to_obj(v)
                    d[k if isinstance(v_obj, Obj) else k.upper()] = v_obj
                return Obj(d)
            else: return a

        with open(filepath, 'r') as f:
            d = json.load(f)
        self.__dict__ = dict_to_obj(d).__dict__

    # Aliases
    @property
    def od(self) -> object_detection: return self.object_detection
    @property
    def mms(self) -> minmax_slopes: return self.minmax_slopes
