from abc import ABC, abstractmethod

class BaseCollector(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def collect_data(self, target):
        """Collects data about the target."""
        pass

    @abstractmethod
    def process_data(self, raw_data):
        """Processes the collected raw data into a structured format."""
        pass

    @abstractmethod
    def get_results(self):
        """Returns the processed data."""
        pass

