class Node:
    def __init__(self, url: str) -> None:
        self.url = url
        self.children = []

    def __hash__(self):
        return hash((self.url, self.children))

    def __eq__(self, other):
        return (self.url, self.children) == (other.url, other.children)
