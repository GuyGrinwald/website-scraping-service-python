class Node(dict):
    def __init__(self, url: str) -> None:
        super().__init__()
        self.__dict__ = self
        self.url = url
        self.urls = []

    def __hash__(self):
        return hash((self.url, self.urls))

    def __eq__(self, other):
        return (self.url, self.urls) == (other.url, other.urls)


