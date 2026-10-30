"""Verify preview isolation and the publication-specific SEO output."""
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build', ROOT / 'scripts/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class SeoPublicationTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'site/content.json').read_text())

    def test_missing_url_blocks_release_without_invented_canonical(self):
        self.data['publication']['siteUrl'] = None
        self.assertIn('正式な公開URLを設定する', build.release_issues(self.data))
        head = build.seo_head(self.data, review=False)
        self.assertNotIn('rel="canonical"', head)
        self.assertNotIn('property="og:url"', head)

    def test_preview_does_not_claim_production_url(self):
        self.data['publication']['siteUrl'] = 'https://example.test/libright/'
        head = build.seo_head(self.data, review=True)
        self.assertNotIn('https://example.test', head)

    def test_metadata_and_sitemap_share_exact_subdirectory_url(self):
        self.data['publication']['siteUrl'] = 'https://example.test/libright'
        head = build.seo_head(self.data, review=False)
        self.assertIn('rel="canonical" href="https://example.test/libright/"', head)
        structured = json.loads(re.search(r'application/ld\+json">(.*?)</script>', head)[1])
        self.assertEqual(structured['@type'], 'Organization')
        self.assertEqual(structured['url'], 'https://example.test/libright/')
        self.assertEqual(structured['logo'], 'https://example.test/libright/assets/brand/libright/logos/svg/horizontal-jp-color.svg')
        for key in ('address', 'telephone', 'priceRange', 'aggregateRating'):
            self.assertNotIn(key, structured)
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            build.write_indexing_files(out, self.data)
            loc = ET.parse(out / 'sitemap.xml').find('.//{*}loc').text
            self.assertEqual(loc, structured['url'])
            self.assertIn('Sitemap: https://example.test/libright/sitemap.xml', (out / 'robots.txt').read_text())

    def test_json_ld_preserves_text_without_breaking_script(self):
        self.data['seo']['description'] = '補修 </script> の説明'
        head = build.seo_head(self.data, review=True)
        payload = re.search(r'application/ld\+json">(.*?)</script>', head)[1]
        self.assertNotIn('</script>', payload)
        self.assertEqual(json.loads(payload)['description'], self.data['seo']['description'])

    def test_photo_dimensions_are_read_without_altering_originals(self):
        for case in self.data['cases']['items']:
            for side in ('before', 'after'):
                path = ROOT / 'site' / case[side]
                self.assertIsNotNone(build.raster_dimensions(path))
        build.verify_photos(self.data)


if __name__ == '__main__':
    unittest.main()
