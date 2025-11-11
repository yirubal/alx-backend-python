#!/usr/bin/env python3
"""
Tests for access_nested_map function
"""

import unittest
from parameterized import parameterized
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for access_nested_map"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns correct value"""
        self.assertEqual(access_nested_map(nested_map, path), expected)
        
class TestAccessNestedMap(unittest.TestCase):
    """Tests for access_nested_map"""

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        """Test that KeyError is raised for invalid paths"""
        with self.assertRaises(KeyError) as error:
            access_nested_map(nested_map, path)

        # Confirm that the message matches the missing key
        self.assertEqual(str(error.exception), f"'{path[-1]}'")
