import unittest

from arithmetic import total


class ArithmeticTests(unittest.TestCase):
    def test_nonempty_result_is_numeric(self):
        self.assertIsInstance(total([1, 2]), int)
