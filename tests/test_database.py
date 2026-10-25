"""Run with: python -m unittest discover -s tests -v"""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import database
from agent import DatabaseAgent


def mock_response(content="", tool_calls=None):
    return SimpleNamespace(message=SimpleNamespace(
        content=content, tool_calls=tool_calls or []
    ))


def mock_tool(name, **kwargs):
    return SimpleNamespace(function=SimpleNamespace(name=name, arguments=kwargs))


class StubClient:
    def __init__(self, calls):
        self.calls = list(calls)
        self.sent = []

    def chat(self, **kwargs):
        self.sent.append(kwargs)
        return self.calls.pop(0)


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.original = database.DATABASE_FILE
        database.DATABASE_FILE = Path(self.folder.name) / "inventory.db"
        database.initialize_database()

    def tearDown(self):
        database.DATABASE_FILE = self.original
        self.folder.cleanup()

    def test_low_stock(self):
        result = database.list_low_stock()
        self.assertEqual(result["count"], 4)
        self.assertIn("USB Drive", [p["Name"] for p in result["products"]])

    def test_find_product(self):
        result = database.find_product("USB")
        self.assertEqual(result["products"][0]["Name"], "USB Drive")
        self.assertEqual(database.find_product("%")['count'], 0)

    def test_category(self):
        result = database.list_category("stationery")
        self.assertEqual(result["count"], 3)

    def test_inventory_value(self):
        self.assertEqual(database.inventory_value()["total_value_rm"], 2481.50)

    def test_read_only_database(self):
        with self.assertRaises(Exception):
            database.select_rows("DELETE FROM Products")
        self.assertEqual(len(database.select_rows("SELECT * FROM Products")), 8)

    def test_agent_tool_call(self):
        fake = StubClient([
            mock_response(tool_calls=[mock_tool("list_low_stock")]),
            mock_response(content="Four items need restocking."),
        ])
        answer = DatabaseAgent(client=fake).ask("Which items need restocking?")
        self.assertIn("Four items", answer)
        self.assertEqual(len(fake.sent), 2)
        tool_result = json.loads(fake.sent[-1]["messages"][-1]["content"])
        self.assertEqual(tool_result["count"], 4)

    def test_agent_refuses_unknown_function(self):
        fake = StubClient([
            mock_response(tool_calls=[mock_tool("delete_everything")]),
            mock_response(content="That operation is not available."),
        ])
        self.assertIn("not available", DatabaseAgent(client=fake).ask("Delete all"))
        data = json.loads(fake.sent[-1]["messages"][-1]["content"])
        self.assertIn("error", data)
        self.assertEqual(len(database.select_rows("SELECT * FROM Products")), 8)

    def test_unsupported_request(self):
        fake = StubClient([mock_response(content="I changed the price")])
        text = DatabaseAgent(client=fake).ask("Change prices")
        self.assertIn("No supported database tool", text)


if __name__ == "__main__":
    unittest.main()
