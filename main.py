import os
import configparser

from app import Application


if __name__ == '__main__':  
    config = configparser.ConfigParser()
    config.read(os.path.join(os.getcwd(), 'config.ini'))

    app = Application(config)
    app.mainloop()
