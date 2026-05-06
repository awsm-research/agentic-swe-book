# tests/test_tax.py
import unittest
from src.tax import calculate_deduction


class TestCalculateDeduction(unittest.TestCase):

    def test_no_supplements_above_mid_income(self) -> None:
        # Arrange
        income = 50_000.0
        age = 40
        has_spouse = False
        disabled = False

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result, 0.0)
        self.assertIsInstance(result, float)

    def test_full_low_income_supplement(self) -> None:
        # Arrange
        income = 15_000.0
        age = 40
        has_spouse = False
        disabled = False

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertEqual(result, 700.0)

    def test_senior_supplement(self) -> None:
        # Arrange
        income = 50_000.0
        age = 70
        has_spouse = False
        disabled = False

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertEqual(result, 400.0)
        self.assertGreater(result, 0)

    def test_spouse_offset(self) -> None:
        # Arrange
        income = 50_000.0
        age = 40
        has_spouse = True
        disabled = False

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertEqual(result, 200.0)

    def test_disability_supplement(self) -> None:
        # Arrange
        income = 50_000.0
        age = 40
        has_spouse = False
        disabled = True

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertEqual(result, 600.0)

    def test_all_supplements_combined(self) -> None:
        # Arrange — taxpayer qualifies for every supplement
        income = 10_000.0   # below LOW_INCOME_THRESHOLD → +$700
        age = 70            # above SENIOR_AGE           → +$400
        has_spouse = True   #                              +$200
        disabled = True     #                              +$600

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert — expected total: 700 + 400 + 200 + 600 = 1900
        self.assertAlmostEqual(result, 1_900.0, places=2)
        self.assertGreaterEqual(result, 1_000.0)

    def test_negative_income_raises_value_error(self) -> None:
        # Arrange
        income = -500.0
        age = 40
        has_spouse = False
        disabled = False

        # Act & Assert — exception is the expected output
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            calculate_deduction(income, age, has_spouse, disabled)

    def test_mid_income_partial_supplement(self) -> None:
        # Arrange — income sits between the two thresholds
        income = 25_000.0   # 18,200 < 25,000 ≤ 37,000 → +$300
        age = 40
        has_spouse = False
        disabled = False

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertEqual(result, 300.0)
        self.assertLess(result, 700.0)      # partial, not full low-income supplement
