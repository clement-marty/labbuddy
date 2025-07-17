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