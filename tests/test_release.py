"""Protect reviewed content and avoid publishing review controls or internal data."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build', ROOT / 'scripts/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class ReleaseContentTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'site/content.json').read_text())

    def test_release_retains_reviewed_sections_and_original_assets(self):
        release, assets = build.render(self.data, review=False)
        review, review_assets = build.render(self.data, review=True)
        for section in ['HERO_VISUAL', 'WORKS_SECTION', 'PARTNER_SECTION',
                        'PRACTICE_SECTION', 'PROCESS_SECTION', 'FAQ_SECTION']:
            self.assertTrue(release[section], section)
            self.assertEqual(release[section], review[section], section)
        self.assertEqual(assets, review_assets)
        self.assertEqual(len(assets), 11)
        self.assertTrue(all(path.startswith(('assets/cases/', 'assets/brand/')) for path in assets))
        self.assertEqual(release['ABOUT_SECTION'], '')
        self.assertEqual(release['REVIEW_BAR'], '')
        self.assertNotIn('紹介文案', release['PARTNER_SECTION'])
        self.assertEqual(release['ROBOTS'], 'index,follow')

    def test_instagram_profile_confirmation_is_distinct_from_dm_verification(self):
        self.data['contact']['linkVerified'] = False
        self.assertNotIn('ユーザー指定のInstagramプロフィールURLを確認する', build.release_issues(self.data))
        self.data['contact']['profileUrlConfirmed'] = False
        self.assertIn('ユーザー指定のInstagramプロフィールURLを確認する', build.release_issues(self.data))


if __name__ == '__main__':
    unittest.main()
