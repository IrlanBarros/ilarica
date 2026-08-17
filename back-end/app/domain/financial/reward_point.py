"""Financial and remuneration context: reward point entity/value object."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.exceptions import InsufficientRewardPointsError, InvalidRewardAmountError


@dataclass
class RewardPoint:
    """Entity representing accumulated points a user can convert."""

    user_id: str
    points: int = 0

    def accumulate(self, amount: int) -> int:
        """Accumulate stored points."""
        if amount <= 0:
            raise InvalidRewardAmountError("Reward points to accumulate must be greater than zero.")

        self.points += amount
        return self.points

    def convertToCash(self) -> float:
        """Convert all currently available points into cash value."""
        if self.points <= 0:
            raise InsufficientRewardPointsError("No reward points are available to convert to cash.")

        cash_value = self.points * 0.10
        self.points = 0
        return cash_value

    def convertToMeal(self) -> int:
        """Convert points into a number of meal vouchers."""
        if self.points < 50:
            raise InsufficientRewardPointsError("At least 50 reward points are required to convert to a meal.")

        meal_count = self.points // 50
        self.points = self.points % 50
        return meal_count
