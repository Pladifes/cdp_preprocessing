from abc import ABC, abstractmethod


class GetGivenYear(ABC):
    """
    This is an abstract class that serves as a template for every years
    """

    @abstractmethod
    def get_useful_sheets(self):
        pass

    @abstractmethod
    def get_scopes_3(self):
        pass

    @abstractmethod
    def get_year_dataset(self):
        pass
