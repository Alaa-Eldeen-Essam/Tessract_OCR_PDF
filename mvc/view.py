class ConsoleView:
    def info(self, message: str) -> None:
        print(message)

    def success(self, message: str) -> None:
        print(message)

    def error(self, message: str) -> None:
        print(f"Error: {message}")