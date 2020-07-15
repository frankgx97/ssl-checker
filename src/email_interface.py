from abc import ABC, abstractmethod

class EmailServiceInterface(ABC):
    def __init__(self):
        super().__init__()
   
    @abstractmethod
    def set_message(self):
        raise NotImplementedError()
        pass

    @abstractmethod
    def authenticate(self):
        raise NotImplementedError()
        pass
    
    @abstractmethod
    def init(self):
        raise NotImplementedError()
        pass

    @abstractmethod
    def send(self):
        raise NotImplementedError()
        pass