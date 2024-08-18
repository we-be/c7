from abc import ABC, abstractmethod


class Bot(ABC):
    
    @abstractmethod
    def scan():
        pass
