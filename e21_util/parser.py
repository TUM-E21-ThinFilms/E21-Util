
class TemperaturePressureLogParser(object):
    def __init__(self, dataobject):
        self.data = dataobject

    def get_data(self):

        parsed = []

        for line in self.data:
            item = self.parse_line(line)
            if item is not None:
                parsed.append(item)

        return parsed

    def parse_line(self, line):
        if line.startswith('Starting measurement'):
            return None

        if line.startswith('Stopping'):
            return None

        if line.startswith('Time;'):
            return None

        if line == "":
            return None

        splitted = line.split(";")

        if not len(splitted) >= 6:
            return None

        # if any element is empty, throw away all..
        if not all(map(bool, ar)):
            return None

        return splitted