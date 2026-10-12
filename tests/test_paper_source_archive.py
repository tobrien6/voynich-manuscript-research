import hashlib
import io
import tarfile
import unittest

from scripts.verify_paper_source_archive import verify_archive


def fixture(names=("article.tex", "figure.pdf"), symlink=False):
    payloads = [b"invented typesetting source", b"%PDF-invented fixture"]
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for index, (name, payload) in enumerate(zip(names, payloads, strict=True)):
            info = tarfile.TarInfo(name)
            if symlink and index == 0:
                info.type = tarfile.SYMTYPE
                info.linkname = names[1]
                archive.addfile(info)
            else:
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
    data = buffer.getvalue()
    record = {
        "record_version": 1, "archive_bytes": len(data),
        "archive_sha256": hashlib.sha256(data).hexdigest(),
        "members": [{"name": name, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                     "role": "article_tex" if index == 0 else "figure_pdf"}
                    for index, (name, payload) in enumerate(zip(names, payloads, strict=True))],
        "pdf_attachment_observations": {"embedded_files_by_member": {names[1]: 0}},
    }
    return data, record


class PaperSourceArchiveTests(unittest.TestCase):
    def test_every_member_and_optional_attachment_count_is_verified(self):
        data, record = fixture()
        observed = []
        def checker(payload):
            observed.append(payload)
            return 0
        result = verify_archive(data, record, checker)
        self.assertEqual(result["verified_regular_members"], 2)
        self.assertEqual(result["pdf_attachment_counts_checked"], {"figure.pdf": 0})
        self.assertEqual(observed, [b"%PDF-invented fixture"])
        self.assertEqual(verify_archive(data, record)["pdf_attachment_counts_checked"], {})

    def test_outer_byte_drift_is_rejected_before_tar_reading(self):
        data, record = fixture()
        with self.assertRaisesRegex(ValueError, "archive differs"):
            verify_archive(data + b"drift", record)

    def test_member_order_length_and_digest_mismatches_fail(self):
        for mutation in ("order", "length", "digest"):
            data, record = fixture()
            if mutation == "order":
                record["members"].reverse()
            elif mutation == "length":
                record["members"][0]["bytes"] = 1
            else:
                record["members"][0]["sha256"] = "0" * 64
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                verify_archive(data, record)

    def test_duplicate_unsafe_and_nonregular_names_are_rejected(self):
        for names, link in ((("article.tex", "article.tex"), False),
                            (("../article.tex", "figure.pdf"), False),
                            (("/article.tex", "figure.pdf"), False),
                            (("article.tex", "figure.pdf"), True)):
            data, record = fixture(names, symlink=link)
            with self.subTest(names=names, link=link), self.assertRaises(ValueError):
                verify_archive(data, record)

    def test_unexpected_pdf_attachments_fail_when_the_check_is_requested(self):
        data, record = fixture()
        with self.assertRaisesRegex(ValueError, "attachment count differs"):
            verify_archive(data, record, lambda payload: 1)


if __name__ == "__main__":
    unittest.main()
