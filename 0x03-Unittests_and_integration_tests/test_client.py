#!/usr/bin/env python3
"""
Unit tests for client.GithubOrgClient.org
"""

import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    def test_org(self, org_name: str) -> None:
        """get_json is called once with the right URL; .org returns its payload"""
        expected = {"login": org_name}
        url = f"https://api.github.com/orgs/{org_name}"

        # Patch where it's used: client.get_json
        with patch("client.get_json", return_value=expected) as mock_get_json:
            client = GithubOrgClient(org_name)
            self.assertEqual(client.org, expected)
            mock_get_json.assert_called_once_with(url)


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient"""

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the correct repos_url"""

        expected_url = "https://api.github.com/orgs/google/repos"

        # Patching *the property* GithubOrgClient.org
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock,
            return_value={"repos_url": expected_url}
        ):
            client = GithubOrgClient("google")
            result = client._public_repos_url  # Access property

            self.assertEqual(result, expected_url)


if __name__ == "__main__":
    unittest.main()
