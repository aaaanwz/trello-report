import unittest
import trello
import os

class Test(unittest.TestCase):
    def test(self):
        report = trello.create_report(os.getenv("TRELLO_API_KEY"), os.getenv(
            "TRELLO_API_TOKEN"), os.getenv("TRELLO_BOARD_ID"), os.getenv('REPORT_TITLE'))
        print(report)
        return

if __name__ == "__main__":
    unittest.main()
