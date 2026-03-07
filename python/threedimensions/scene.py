class Scene:
    def __init__(self):
        self.objects = []

    def add(self, mesh):
        self.objects.append(mesh)

    def clear(self):
        self.objects.clear()

    def object_count(self):
        return len(self.objects)
