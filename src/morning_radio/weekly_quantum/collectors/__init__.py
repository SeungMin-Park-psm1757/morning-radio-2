from .base import Collector, CollectorResult, SourceConfig
from .physorg import PhysOrgCollector
from .qcr import QCRCollector
from .quantumfrontiers import QuantumFrontiersCollector
from .quantumzeitgeist import QuantumZeitgeistCollector
from .tqi import TQICollector

__all__ = [
    "Collector",
    "CollectorResult",
    "SourceConfig",
    "TQICollector",
    "PhysOrgCollector",
    "QuantumZeitgeistCollector",
    "QCRCollector",
    "QuantumFrontiersCollector",
]
