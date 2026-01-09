from mvc.controller import OcrController


def main() -> None:
    controller = OcrController()
    raise SystemExit(controller.run())


if __name__ == "__main__":
    main()