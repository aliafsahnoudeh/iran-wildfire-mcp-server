from src.domains.nasa_firms import RawFireData, get_fires
from src.domains.nasa_firms.types import BoundingBox


class LikelyFireAgent:
    def __init__(self):
        pass

    def fetch_likely_fires(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        frp: float = 10,
        bright_ti4: float = 330,
        in_iran: bool = False,
        bounding_box: BoundingBox | None = None,
    ) -> list[RawFireData]:
        """Fetch likely fire events based on criteria.

        Args:
            start_date (str | None): Start date in 'YYYY-MM-DD' format.
            end_date (str | None): End date in 'YYYY-MM-DD' format.
            frp (float): Minimum Fire Radiative Power.
            bright_ti4 (float): Minimum Brightness Temperature.
        Returns:
            list[RawFireData]: List of fire events.
        """
        return get_fires(
            start_date=start_date,
            end_date=end_date,
            frp=frp,
            bright_ti4=bright_ti4,
            in_iran=in_iran,
            bounding_box=bounding_box,
        )
