import datetime

class Post():
    image_url: str | None
    post_id: int
    post_timestamp: datetime
    post_content: str

    def __init__(self, url: str | None, id: int, timestamp: int, content: str):
        self.image_url = f'https:{url}' if url else ''
        self.post_id = id
        self.post_timestamp = datetime.datetime.fromtimestamp(timestamp)
        self.post_content = content

    def __str__(self):
        return f"{self.post_timestamp.strftime('%d/%m/%y(%a)%H:%M:%S')} No. {self.post_id}: '{self.post_content[:64]}' ~{self.image_url}"