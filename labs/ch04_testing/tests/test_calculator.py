import unittest
from src.calculator import add, divide


class TestAdd(unittest.TestCase):
    def test_add_returns_correct_sum(self):
        # Arrange — set up inputs
        a = 3
        b = 5

        # Act — call the unit under test
        result = add(a, b)

        # Assert — compare actual output to expected output
        self.assertEqual(result, 8)


class TestDivide(unittest.TestCase):
    def test_divide_raises_on_zero(self):
        # Arrange
        a = 10
        b = 0

        # Act + Assert — the exception is the expected output
        with self.assertRaises(ValueError):
            divide(a, b)

    def test_divide_raises_correct_message(self):
        with self.assertRaisesRegex(ValueError, "Cannot divide by zero"):
            divide(10, 0)

    def test_divide_normal(self):
        self.assertEqual(divide(10, 2), 5.0)   # exercises the normal branch

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            divide(10, 0)                       # exercises the guard branch
