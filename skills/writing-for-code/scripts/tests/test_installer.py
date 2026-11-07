"""Test the Bash installer with temporary source and home directories."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


INSTALLER = Path(__file__).resolve().parents[4] / "install.sh"
BEGIN = "<!-- writing-for-code:begin -->"
END = "<!-- writing-for-code:end -->"


class InstallerTests(unittest.TestCase):
    """Keep installer writes inside a temporary HOME for each test."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.home = self.base / "test home"
        self.home.mkdir()
        self.repo = self.base / "source with spaces"
        self.repo.mkdir()
        self.installer = self.repo / "install.sh"
        shutil.copyfile(INSTALLER, self.installer)
        self.source = self.repo / "skills" / "writing-for-code"
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text("Skill instructions.\n")
        self.target = self.home / ".claude" / "skills" / "writing-for-code"
        self.instructions = self.home / ".claude" / "CLAUDE.md"

    def run_installer(self, *args, expected=0):
        result = subprocess.run(
            ["bash", str(self.installer), *args],
            cwd=self.base,
            env={**os.environ, "HOME": str(self.home)},
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def write_instructions(self, text):
        self.instructions.parent.mkdir(parents=True, exist_ok=True)
        self.instructions.write_text(text)

    def test_success_repeat_and_default_opt_out(self):
        self.run_installer()
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(self.target.readlink(), self.source)
        self.run_installer()
        self.assertFalse(self.instructions.exists())

    def test_only_skills_with_skill_file_are_linked(self):
        other = self.repo / "skills" / "other skill"
        other.mkdir()
        (other / "SKILL.md").write_text("Other instructions.\n")
        (self.repo / "skills" / "not-a-skill").mkdir()
        self.run_installer()
        self.assertEqual((self.target.parent / "other skill").readlink(), other)
        self.assertFalse((self.target.parent / "not-a-skill").exists())

    def test_dry_run_creates_nothing(self):
        self.run_installer("--dry-run", "--claude-md")
        self.assertEqual(list(self.home.iterdir()), [])

    def test_dry_run_force_preserves_files(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text("Keep the file.\n")
        self.write_instructions("Keep the instructions.\n")
        self.run_installer("--dry-run", "--force", "--claude-md")
        self.assertEqual(self.target.read_text(), "Keep the file.\n")
        self.assertEqual(self.instructions.read_text(), "Keep the instructions.\n")

    def test_file_collision_does_not_register_instructions(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text("Keep the file.\n")
        self.run_installer("--claude-md", expected=1)
        self.assertEqual(self.target.read_text(), "Keep the file.\n")
        self.assertFalse(self.instructions.exists())

    def test_force_replaces_file(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text("Old file.\n")
        self.run_installer("--force", "--claude-md")
        self.assertEqual(self.target.readlink(), self.source)
        self.assertIn(BEGIN, self.instructions.read_text())

    def test_symlink_collisions_and_force(self):
        for broken in (False, True):
            with self.subTest(broken=broken):
                old = self.base / ("missing" if broken else "old skill")
                if not broken:
                    old.mkdir()
                self.target.parent.mkdir(parents=True, exist_ok=True)
                self.target.symlink_to(old)
                self.run_installer("--claude-md", expected=1)
                self.assertEqual(self.target.readlink(), old)
                self.assertFalse(self.instructions.exists())
                self.run_installer("--force")
                self.assertEqual(self.target.readlink(), self.source)
                self.target.unlink()

    def test_real_directory_survives_force(self):
        self.target.mkdir(parents=True)
        sentinel = self.target / "keep.txt"
        sentinel.write_text("Keep this content.\n")
        self.run_installer("--force", "--claude-md", expected=1)
        self.assertEqual(sentinel.read_text(), "Keep this content.\n")
        self.assertFalse(self.instructions.exists())

    def test_registration_preserves_unrelated_instructions_and_repeats(self):
        original = "# Local instructions\n\nKeep these instructions.\n"
        self.write_instructions(original)
        self.run_installer("--claude-md")
        first = self.instructions.read_text()
        self.assertTrue(first.startswith(original))
        self.assertEqual(first.count(BEGIN), 1)
        self.assertEqual(first.count(END), 1)
        self.run_installer("--claude-md")
        self.assertEqual(self.instructions.read_text(), first)

    def test_replace_only_managed_block(self):
        before = "# Local instructions\n\n"
        after = "\nKeep this final line without a newline."
        self.write_instructions(f"{before}{BEGIN}\nOld instructions.\n{END}\n{after}")
        self.run_installer("--claude-md")
        result = self.instructions.read_text()
        self.assertTrue(result.startswith(before + BEGIN + "\n"))
        self.assertTrue(result.endswith(END + "\n" + after))
        self.assertNotIn("Old instructions.", result)

    def test_append_after_unterminated_line(self):
        self.write_instructions("Keep this line.")
        self.run_installer("--claude-md")
        self.assertTrue(self.instructions.read_text().startswith("Keep this line.\n\n" + BEGIN))

    def test_invalid_markers_do_not_change_files(self):
        cases = [
            BEGIN + "\nPartial block.\n",
            END + "\n",
            f"{END}\n{BEGIN}\n",
            f"{BEGIN}\n{BEGIN}\n{END}\n",
            f"{BEGIN}\n{END}\n{BEGIN}\n{END}\n",
            "<!-- writing-for-code:begin --> trailing text\n",
            "<!-- writing-for-code: begin -->\n",
            "<!-- writing-for-code begin -->\n",
            "<!-- writing-for-code:unknown -->\n",
            "writing-for-code:begin -->\n",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.write_instructions(text)
                self.run_installer("--claude-md", expected=1)
                self.assertEqual(self.instructions.read_text(), text)
                self.assertFalse(self.target.exists())
                self.assertFalse(self.target.is_symlink())
                self.run_installer("--dry-run", "--claude-md", expected=1)

    def test_link_failure_does_not_register_instructions(self):
        self.write_instructions("Keep these instructions.\n")
        (self.home / ".claude" / "skills").write_text("Not a directory.\n")
        self.run_installer("--claude-md", expected=1)
        self.assertEqual(self.instructions.read_text(), "Keep these instructions.\n")

    def test_preflight_checks_all_skills_before_registration(self):
        blocked = self.repo / "skills" / "z-blocked"
        blocked.mkdir()
        (blocked / "SKILL.md").write_text("Blocked instructions.\n")
        self.target.parent.mkdir(parents=True)
        (self.target.parent / "z-blocked").write_text("Keep this file.\n")
        self.run_installer("--claude-md", expected=1)
        self.assertFalse(self.target.exists())
        self.assertFalse(self.instructions.exists())

    def test_instruction_symlink_is_not_replaced(self):
        original = self.base / "shared instructions"
        original.write_text("Keep these instructions.\n")
        self.instructions.parent.mkdir()
        self.instructions.symlink_to(original)
        self.run_installer("--force", "--claude-md", expected=1)
        self.assertEqual(self.instructions.readlink(), original)
        self.assertEqual(original.read_text(), "Keep these instructions.\n")
        self.assertFalse(self.target.exists())

    def test_missing_skills_fail_without_registration(self):
        (self.source / "SKILL.md").unlink()
        self.run_installer("--claude-md", expected=1)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_registration_requires_writing_skill(self):
        self.source.rename(self.source.with_name("other-skill"))
        self.run_installer("--claude-md", expected=1)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_help_and_usage_status(self):
        for flag in ("--help", "-h"):
            self.assertIn("Usage:", self.run_installer(flag).stdout)
        for flag in ("--unknown", "positional", "--force=true"):
            self.assertIn("Usage:", self.run_installer(flag, expected=2).stderr)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
