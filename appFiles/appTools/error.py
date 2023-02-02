class AppError(Exception):
    def __init__(self, err_mas: str):
        super().__init__()
        self.info = err_mas

    def __str__(self):
        return self.info
