from retro_gaming.app import run


if __name__ == "__main__":
    try:
        run()
    except ValueError as error:
        raise SystemExit(str(error)) from None
