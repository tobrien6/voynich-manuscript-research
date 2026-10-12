from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.audit_reddy_history import HISTORY, audit, load, source_inventory, verify_tree


def native_git_tree(raw):
    return subprocess.check_output(['git', 'hash-object', '-t', 'tree', '--stdin'], input=raw).decode().strip()


def example_tree():
    blob = '1' * 40
    child_raw = b'100644 item\0' + bytes.fromhex(blob)
    child = native_git_tree(child_raw)
    # Git orders the file data.txt before the directory data/.
    root_raw = b'100644 data.txt\0' + bytes.fromhex(blob) + b'40000 data\0' + bytes.fromhex(child)
    return {'sha': native_git_tree(root_raw), 'truncated': False, 'tree': [
        {'path': 'data/item', 'mode': '100644', 'type': 'blob', 'sha': blob, 'size': 3},
        {'path': 'data', 'mode': '040000', 'type': 'tree', 'sha': child},
        {'path': 'data.txt', 'mode': '100644', 'type': 'blob', 'sha': blob, 'size': 3},
    ]}


class ReddyHistoryTests(unittest.TestCase):
    def test_recursive_reconstruction_matches_native_git_with_directory_order(self):
        tree = example_tree()
        self.assertEqual([entry['path'] for entry in verify_tree(tree)], ['data.txt', 'data/item'])
        tree['tree'].reverse()
        self.assertEqual(len(verify_tree(tree)), 2)

    def test_truncated_missing_duplicate_and_changed_entries_are_rejected(self):
        original = example_tree()
        variants = []
        truncated = deepcopy(original)
        truncated['truncated'] = True
        variants.append(truncated)
        missing = deepcopy(original)
        missing['tree'].pop(0)
        variants.append(missing)
        duplicate = deepcopy(original)
        duplicate['tree'].append(deepcopy(duplicate['tree'][0]))
        variants.append(duplicate)
        changed = deepcopy(original)
        changed['tree'][0]['sha'] = '2' * 40
        variants.append(changed)
        for tree in variants:
            with self.subTest(tree=tree), self.assertRaises(ValueError):
                verify_tree(tree)

    def test_source_inventory_parses_without_executing_author_code(self):
        raw = b'''raise RuntimeError("never execute")
import codecs
class Example:
    def method(self, filename):
        return "data/voy.b.paged.wds"
def standalone(value):
    return value
'''
        result = source_inventory(raw)
        self.assertEqual([item['name'] for item in result['definitions']], ['Example.method', 'standalone'])
        self.assertEqual(result['imports'], ['codecs'])
        self.assertEqual(result['literal_native_paths'], ['data/voy.b.paged.wds'])

    def test_incomplete_commit_capture_and_non_strict_json_are_rejected(self):
        for raw in [b'{"a":1,"a":2}', b'{"a":NaN}']:
            with self.assertRaises(ValueError):
                load(raw)
        with tempfile.TemporaryDirectory() as temporary:
            reference = Path(temporary)
            (reference / 'commits.json').write_text(json.dumps([[{'sha': identity} for identity, _ in HISTORY[:-1]]]))
            (reference / 'branches.json').write_text(json.dumps([[{'name': 'master', 'commit': {'sha': HISTORY[0][0]}}]]))
            (reference / 'tags.json').write_text('[[]]')
            with self.assertRaisesRegex(ValueError, 'six-commit chain'):
                audit(reference)


if __name__ == '__main__':
    unittest.main()
