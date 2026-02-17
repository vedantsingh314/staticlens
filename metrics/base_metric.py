from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseMetric(ABC):
    

    @abstractmethod
    def analyze(self, tree: Any, file_path: str,lang:str) -> Dict:
       
        pass
