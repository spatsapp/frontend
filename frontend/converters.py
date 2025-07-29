from enum import Enum

from starlette.convertors import Convertor

class Symbolic(str, Enum):
    asset = "asset"
    combo = "combo"

class SymbolicConverter(Convertor):
    regex = f"({'|'.join([v.value for v in Symbolic])})"

    def convert(self, value: str) -> Symbolic:
        return Symbolic[value]

    def to_string(self, value: Symbolic) -> str:
        return str(value)



class Material(str, Enum):
    thing = "thing"
    group = "group"

class MaterialConverter(Convertor):
    regex = f"({'|'.join([v.value for v in Material])})"

    def convert(self, value: str) -> Material:
        return Material[value]

    def to_string(self, value: Material) -> str:
        return str(value)


class SuidConverter(Convertor):
    regex = "[a-z]{7}"

    def convert(self, value: str) -> str:
        return value

    def to_string(self, value: str) -> str:
        return value

