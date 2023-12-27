from enum import StrEnum, auto


class Environment(StrEnum):
    LOCAL = auto()
    STAGING = auto()
    TESTING = auto()
    PRODUCTION = auto()

    @property
    def is_debug(self):
        return self in (self.LOCAL, self.STAGING, self.TESTING)

    @property
    def is_testing(self):
        return self == self.TESTING

    @property
    def is_deployed(self) -> bool:
        return self in (self.STAGING, self.PRODUCTION)
