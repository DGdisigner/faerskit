from abc import ABC, abstractmethod

from typing import List


class DbFaers(ABC):
    @abstractmethod
    def session(self):
        pass

    @abstractmethod
    def batch_insert_faers_data(self, year, quarter, model, list_data: List[dict]):
        pass

    @abstractmethod
    def batch_insert_data(self, model, list_data: List[dict]):
        pass


class DbDict(ABC):
    @abstractmethod
    def session(self):
        pass

    @abstractmethod
    def insert_meddra_row(self, data):
        pass

    @abstractmethod
    def batch_insert_data(self, model, list_data: List[dict]):
        pass
