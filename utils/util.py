from apps.dashboard.models import CourtType

from decimal import Decimal


def get_freeze_weights_by_court_type(court_type: CourtType) -> Decimal:
    mapping = {
        CourtType.FULL: Decimal('1'),
        CourtType.HALF: Decimal('0.5'),
        CourtType.QUARTER: Decimal('0.25')
    }
    return mapping[court_type]
