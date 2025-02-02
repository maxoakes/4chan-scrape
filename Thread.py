class Thread:
    id: int
    title: str
    desc: str
    responses: int
    images: int

    def __init__(self, id, title, desc, responses, images):
        self.id = id
        self.title = title
        self.desc = desc
        self.responses = responses
        self.images = images

    def __str__(self):
        return f"{self.id}, (R:{self.responses}/I:{self.images})\t **{self.title}** {self.desc[:64]}"