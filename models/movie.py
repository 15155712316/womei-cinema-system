class Movie:
    def __init__(self, movie_id: str, name: str, duration: int):
        self.movie_id = movie_id
        self.name = name
        self.duration = duration  # 单位：分钟 