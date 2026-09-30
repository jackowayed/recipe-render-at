import tempfile
import unittest
from pathlib import Path

from fetch_airtable import content_hash, meaningful_record


class ContentHashTest(unittest.TestCase):
    fields = {
        'Countdown': {'name': 'Countdown', 'type': 'formula'},
        'Photo': {'name': 'Photo', 'type': 'multipleAttachments'},
        'Name': {'name': 'Name', 'type': 'singleLineText'},
    }

    def test_ignores_formula_values_and_attachment_urls(self):
        first = {'id': 'rec1', 'fields': {
            'Name': 'Soup',
            'Countdown': '2 days',
            'Photo': [{'id': 'att1', 'filename': 'soup.jpg', 'size': 10,
                       'type': 'image/jpeg', 'url': 'https://old.example'}],
        }}
        second = {'id': 'rec1', 'fields': {
            **first['fields'],
            'Countdown': '1 day',
            'Photo': [{**first['fields']['Photo'][0], 'url': 'https://new.example'}],
        }}

        self.assertEqual(
            meaningful_record(first, self.fields),
            meaningful_record(second, self.fields),
        )

    def test_hash_changes_with_meaningful_data_or_template(self):
        record = {'id': 'rec1', 'fields': {'Name': 'Soup'}}
        table = {'name': 'Recipes', 'fields': list(self.fields.values())}
        with tempfile.TemporaryDirectory() as directory:
            template = Path(directory) / 'template.html'
            template.write_text('one')
            original = content_hash([record], table, template)
            changed_data = content_hash(
                [{'id': 'rec1', 'fields': {'Name': 'Stew'}}], table, template
            )
            template.write_text('two')
            changed_template = content_hash([record], table, template)

        self.assertNotEqual(original, changed_data)
        self.assertNotEqual(original, changed_template)


if __name__ == '__main__':
    unittest.main()
