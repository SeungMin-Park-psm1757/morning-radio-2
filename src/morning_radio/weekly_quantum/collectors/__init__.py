from .base import Collector, CollectorResult, SourceConfig
from .fqcf import FQCFCollector
from .physorg import PhysOrgCollector
from .qcr import QCRCollector
from .quantumfrontiers import QuantumFrontiersCollector
from .quantumzeitgeist import QuantumZeitgeistCollector
from .tqi import TQICollector

__all__ = [
    "Collector",
    "CollectorResult",
    "SourceConfig",
    "FQCFCollector",
    "TQICollector",
    "PhysOrgCollector",
    "QuantumZeitgeistCollector",
    "QCRCollector",
    "QuantumFrontiersCollector",
]
