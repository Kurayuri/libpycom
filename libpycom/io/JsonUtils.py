import orjson

class JsonUtils:
    @staticmethod
    def loadJsonLines(f):
        if hasattr(f, "read") and callable(f.read):
            lines = f.readlines()
        else:
            with open(f, "r") as readable:
                lines = readable.readlines()
        return [orjson.loads(line) for line in lines]