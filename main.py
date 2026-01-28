from core.requirements_updater import check_and_update


def main():
    try:
        check_and_update()
    except Exception:
        pass

    from gui.app_qt import main as gui_main

    gui_main()


if __name__ == "__main__":
    main()
