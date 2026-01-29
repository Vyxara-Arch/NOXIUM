import os

from core.requirements_updater import check_and_update


def main():
    if os.getenv("NOXIUM_AUTO_UPDATE_DEPS") == "1":
        try:
            check_and_update()
        except Exception:
            pass

    from gui.app_qt import main as gui_main

    gui_main()


if __name__ == "__main__":
    main()
