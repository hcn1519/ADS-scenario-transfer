from abc import ABC, abstractmethod
from typing import TypeVar, Dict

Product = TypeVar('Product')


class Builder(ABC):
    """
    Interface for defining Builder for generating OpenSCENARIO Message.

    Properties:
        properties (Dict[Any]): Dict of properties to build the object.
    """

    properties: Dict

    @abstractmethod
    def get_result(self) -> Product:
        pass