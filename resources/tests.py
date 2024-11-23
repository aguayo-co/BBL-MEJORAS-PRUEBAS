"""Define tests for Resources app."""
from time import sleep

from django.core.cache import cache
from django.test import TestCase

from .helpers import ParallelCallsNotAllowed, unparallel


class UnparallelTestCase(TestCase):
    """Test functionality of unparallel decorator."""

    def test_unparallel_sets_flag(self):
        """Test that the decorator sets a flag to control parallel execution."""
        cache_key = ".".join(
            [
                "unparallel:",
                self.__class__.test_unparallel_sets_flag.__module__,
                self.__class__.test_unparallel_sets_flag.__qualname__,
                "<locals>.check_flag",
            ]
        )

        @unparallel
        def check_flag():
            self.assertTrue(cache.get(cache_key))

        check_flag()

    def test_unparallel_raises_on_flag(self):
        """Test that the decorator raises exception when the flag is set."""
        cache_key = ".".join(
            [
                "unparallel:",
                self.__class__.test_unparallel_raises_on_flag.__module__,
                self.__class__.test_unparallel_raises_on_flag.__qualname__,
                "<locals>.raise_exception",
            ]
        )
        cache.set(cache_key, True)

        @unparallel
        def raise_exception():
            pass

        self.assertRaises(ParallelCallsNotAllowed, raise_exception)

    def test_unparallel_clears_flag(self):
        """Test that the decorator removes the flag when done."""
        cache_key = ".".join(
            [
                "unparallel:",
                self.__class__.test_unparallel_clears_flag.__module__,
                self.__class__.test_unparallel_clears_flag.__qualname__,
                "<locals>.unparalleled",
            ]
        )

        @unparallel
        def unparalleled():
            self.assertTrue(cache.get(cache_key))

        unparalleled()

        self.assertIsNone(cache.get(cache_key))

    def test_unparallel_timout(self):
        """Test that the default timeout is used."""
        cache_key = ".".join(
            [
                "unparallel:",
                self.__class__.test_unparallel_timout.__module__,
                self.__class__.test_unparallel_timout.__qualname__,
                "<locals>.wait_for_timeout",
            ]
        )

        @unparallel(timeout=1)
        def wait_for_timeout():
            self.assertTrue(cache.get(cache_key))
            sleep(1)
            self.assertIsNone(cache.get(cache_key))

        wait_for_timeout()

    def test_returned_value(self):
        """Test that the return value form the decorated function is returned."""
        return_value = "return value"

        @unparallel(timeout=1)
        def has_a_return():
            return return_value

        self.assertEqual(has_a_return(), return_value)
