from watch_app import WatchApp
from watch_gui import WatchAppGUI

def main():
    app = WatchApp()
    gui = WatchAppGUI(app)
    gui.run()

if __name__ == '__main__':
    main()
