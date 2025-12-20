from src.domains.nasa_firms import RawFireData, get_fires_in_iran


class LikelyFireAgent:
    def __init__(self):
        pass

    def fetch_likely_fires(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        frp: float = 10,
        bright_ti4: float = 330,
    ) -> list[RawFireData]:
        """Fetch likely fire events in Iran based on criteria.

        Args:
            start_date (str | None): Start date in 'YYYY-MM-DD' format.
            end_date (str | None): End date in 'YYYY-MM-DD' format.
            frp (float): Minimum Fire Radiative Power.
            bright_ti4 (float): Minimum Brightness Temperature.
        Returns:
            list[RawFireData]: List of fire events.
        """
        return get_fires_in_iran(
            start_date=start_date, end_date=end_date, frp=frp, bright_ti4=bright_ti4
        )
