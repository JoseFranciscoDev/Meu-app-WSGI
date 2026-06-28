from typing import Callable


class Router:
    def __init__(self):
        self.routes: dict[tuple, Callable] = {}

    def get(self, path: str):
        def wrapper(func: Callable) -> Callable:
            self.routes[("GET", path)] = func
            return func

        return wrapper

    def post(self, path: str):
        def wrapper(func: Callable) -> Callable:
            self.routes[("POST", path)] = func
            return func

        return wrapper
