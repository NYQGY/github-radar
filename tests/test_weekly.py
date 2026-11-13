import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from collect import parse_trending


class TrendingTests(unittest.TestCase):
    def test_ranks_weekly_stars_and_caps_at_ten(self):
        articles = [f'<article class="Box-row"><h2><a href="/owner/repo{i}">repo</a></h2><span>{i:,} stars this week</span></article>' for i in range(12)]
        articles.append('<article class="Box-row"><h2><a href="/ignored/repo">repo</a></h2>no weekly count</article>')
        self.assertEqual(parse_trending(''.join(articles)), [(f'owner/repo{i}', i) for i in range(11, 1, -1)])

    def test_fails_when_page_structure_changes(self):
        with self.assertRaises(ValueError):
            parse_trending('<article class="Box-row">missing weekly count</article>')
