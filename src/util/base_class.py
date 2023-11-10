from abc import ABC, abstractmethod


class JSONSerializableData(ABC):
    """Represents JSON serializable data."""

    @abstractmethod
    def to_json_serializable(self):
        ...


class Singleton(object):
    """Represents a singleton class."""

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            print("\nNew instance created for ", cls)
            cls._instance = super(Singleton, cls).__new__(cls)

        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        return cls()
