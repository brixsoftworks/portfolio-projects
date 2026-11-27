import io
import json
import tarfile
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from tools import local_model_manager


class LocalModelManagerTests(unittest.TestCase):
    def setUp(self):
        with local_model_manager._jobs_lock:
            local_model_manager._jobs.clear()

    def tearDown(self):
        with local_model_manager._jobs_lock:
            local_model_manager._jobs.clear()
        local_model_manager._managed_ollama_process = None

    def test_download_catalog_is_available_without_hardware_scan(self):
        catalog = local_model_manager.get_local_model_catalog()["models"]

        self.assertEqual([model["id"] for model in catalog], ["qwen3-0.6b", "qwen3-4b", "qwen3-8b"])
        self.assertTrue(all(model["huggingface_url"].startswith("https://huggingface.co/") for model in catalog))
        self.assertTrue(all(model["download_gb"] > 0 and model["memory_gb"] > 0 for model in catalog))

    def test_catalog_storage_estimate_includes_runtime_when_not_installed(self):
        with (
            patch.object(local_model_manager, "_find_ollama_executable", return_value=None),
            patch.object(local_model_manager, "_ollama_status_and_models", return_value=(False, [])),
        ):
            without_runtime = local_model_manager.get_local_model_catalog()["models"][0]
        with (
            patch.object(local_model_manager, "_find_ollama_executable", return_value="/usr/bin/ollama"),
            patch.object(local_model_manager, "_ollama_status_and_models", return_value=(True, [{"name": local_model_manager.CATALOG_BY_ID["qwen3-0.6b"]["model"]}])),
        ):
            with_runtime = local_model_manager.get_local_model_catalog()["models"][0]

        self.assertEqual(without_runtime["required_disk_gb"], 4.5)
        self.assertEqual(with_runtime["required_disk_gb"], 1.5)
        self.assertFalse(without_runtime["installed"])
        self.assertTrue(with_runtime["installed"])

    def test_catalog_endpoint_does_not_run_hardware_scan(self):
        from fastapi.testclient import TestClient

        import agent_server

        with patch.object(agent_server, "scan_local_model_hardware", side_effect=AssertionError("hardware scan called")):
            response = TestClient(agent_server.app).get("/api/models/local/catalog")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["models"]), 3)

    def test_catalog_marks_best_fit_and_links_to_hugging_face(self):
        catalog = local_model_manager._public_catalog(8, None, set())

        self.assertEqual(
            next(model["id"] for model in catalog if model["recommended"]),
            "qwen3-4b",
        )
        self.assertTrue(next(model for model in catalog if model["id"] == "qwen3-4b")["fits_hardware"])
        self.assertIn(
            "huggingface.co/unsloth/Qwen3-4B-GGUF",
            next(model for model in catalog if model["id"] == "qwen3-4b")["huggingface_url"],
        )

    def test_catalog_accounts_for_free_disk_space(self):
        catalog = local_model_manager._public_catalog(8, None, set(), disk_free_gb=2)

        recommended = next(model for model in catalog if model["recommended"])
        self.assertEqual(recommended["id"], "qwen3-0.6b")
        self.assertTrue(recommended["fits_disk"])
        self.assertFalse(next(model for model in catalog if model["id"] == "qwen3-4b")["fits_disk"])

    def test_scan_reports_computer_and_runtime_details(self):
        with (
            patch.object(local_model_manager, "_system_memory_gb", return_value=16),
            patch.object(local_model_manager, "_gpu_details", return_value={"name": "Example GPU", "vram_gb": 8}),
            patch.object(local_model_manager, "_ollama_status_and_models", return_value=(True, [{"name": "qwen3:4b"}])),
            patch.object(local_model_manager.shutil, "which", return_value="/usr/bin/ollama"),
            patch.object(local_model_manager, "_ollama_disk_free_gb", return_value=20),
        ):
            result = local_model_manager.scan_local_model_hardware()

        self.assertEqual(result["ram_gb"], 16)
        self.assertEqual(result["gpu_name"], "Example GPU")
        self.assertTrue(result["ollama_installed"])
        self.assertTrue(result["ollama_running"])
        self.assertTrue(result["catalog"])

    def test_scan_checks_ollama_once_even_when_no_models_are_installed(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({"models": []}).encode()
        with (
            patch.object(local_model_manager, "_system_memory_gb", return_value=8),
            patch.object(local_model_manager, "_ollama_disk_free_gb", return_value=20),
            patch.object(local_model_manager, "_gpu_details", return_value={"name": None, "vram_gb": None}),
            patch.object(local_model_manager.shutil, "which", return_value="/usr/bin/ollama"),
            patch.object(local_model_manager, "urlopen", return_value=response) as open_url,
        ):
            result = local_model_manager.scan_local_model_hardware()

        self.assertTrue(result["ollama_running"])
        self.assertEqual(result["installed_models"], [])
        open_url.assert_called_once_with(f"{local_model_manager.OLLAMA_API_URL}/api/tags", timeout=1.5)

    def test_scan_runs_gpu_and_ollama_checks_concurrently(self):
        checks_started_together = threading.Barrier(2)

        def gpu_scan():
            checks_started_together.wait(timeout=1)
            return {"name": "Example GPU", "vram_gb": 8}

        def ollama_scan():
            checks_started_together.wait(timeout=1)
            return True, []

        with (
            patch.object(local_model_manager, "_system_memory_gb", return_value=16),
            patch.object(local_model_manager, "_ollama_disk_free_gb", return_value=20),
            patch.object(local_model_manager, "_gpu_details", side_effect=gpu_scan),
            patch.object(local_model_manager, "_ollama_status_and_models", side_effect=ollama_scan),
            patch.object(local_model_manager.shutil, "which", return_value="/usr/bin/ollama"),
        ):
            result = local_model_manager.scan_local_model_hardware()

        self.assertEqual(result["gpu_name"], "Example GPU")
        self.assertTrue(result["ollama_running"])

    def test_unknown_catalog_selection_is_rejected(self):
        with self.assertRaisesRegex(local_model_manager.ModelRegistryError, "available list"):
            local_model_manager.start_local_model_download("untrusted/model")

    def test_download_rejects_model_larger_than_free_storage(self):
        with (
            patch.object(local_model_manager, "_ollama_disk_free_gb", return_value=2),
            self.assertRaisesRegex(local_model_manager.ModelRegistryError, "Free up"),
        ):
            local_model_manager.start_local_model_download("qwen3-4b")

    def test_installed_ollama_model_can_be_connected_and_selected(self):
        model = {"id": "a" * 32, "name": "qwen3.5:4b"}
        with (
            patch.object(local_model_manager, "_installed_ollama_models", return_value=[{"name": "qwen3.5:4b"}]),
            patch.object(local_model_manager, "list_models", return_value={"models": [{"id": "default", "name": "Gemini"}]}),
            patch.object(local_model_manager, "add_model", return_value=model) as add,
            patch.object(local_model_manager, "set_active_model") as set_active,
        ):
            connected = local_model_manager.connect_existing_local_model("qwen3.5:4b")

        self.assertEqual(connected, model)
        add.assert_called_once_with(
            "qwen3.5:4b",
            "ollama",
            "qwen3.5:4b",
            local_model_manager.DEFAULT_OLLAMA_URL,
        )
        set_active.assert_called_once_with(model["id"])

    def test_download_connects_and_selects_model_on_success(self):
        job_id = "d" * 32
        with local_model_manager._jobs_lock:
            local_model_manager._jobs[job_id] = {
                "id": job_id,
                "catalog_id": "qwen3-4b",
                "status": "queued",
                "progress": 0,
            }
        response = MagicMock()
        response.__iter__.return_value = iter([
            b'{"status":"pulling manifest"}\n',
            b'{"status":"pulling layer","total":100,"completed":55}\n',
            b'{"status":"success"}\n',
        ])
        model = {"id": "a" * 32, "name": "Qwen 3 · Balanced"}

        with (
            patch.object(local_model_manager, "_ensure_ollama_runtime", return_value="/usr/bin/ollama") as ensure,
            patch.object(local_model_manager, "urlopen", return_value=response) as open_url,
            patch.object(local_model_manager, "_connect_downloaded_model", return_value=model) as connect,
        ):
            local_model_manager._download_worker(job_id, "qwen3-4b")

        result = local_model_manager.get_local_model_download(job_id)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["progress"], 100)
        self.assertEqual(result["connected_model"], model)
        ensure.assert_called_once_with(job_id)
        request = open_url.call_args.args[0]
        self.assertEqual(request.full_url, f"{local_model_manager.OLLAMA_API_URL}/api/pull")
        self.assertEqual(
            json.loads(request.data),
            {"model": "hf.co/unsloth/Qwen3-4B-GGUF:Q4_K_M", "stream": True},
        )
        connect.assert_called_once_with("qwen3-4b")
        response.close.assert_called_once()

    def test_pull_api_surfaces_runtime_error_and_does_not_connect_model(self):
        job_id = "1" * 32
        with local_model_manager._jobs_lock:
            local_model_manager._jobs[job_id] = {"id": job_id, "status": "queued", "progress": 0}
        response = MagicMock()
        response.__iter__.return_value = iter([b'{"error":"unsupported model reference"}\n'])

        with (
            patch.object(local_model_manager, "_ensure_ollama_runtime", return_value="/usr/bin/ollama"),
            patch.object(local_model_manager, "urlopen", return_value=response),
            patch.object(local_model_manager, "_connect_downloaded_model") as connect,
        ):
            local_model_manager._download_worker(job_id, "qwen3-4b")

        result = local_model_manager.get_local_model_download(job_id)
        self.assertEqual(result["status"], "failed")
        self.assertIn("unsupported model reference", result["error"])
        connect.assert_not_called()

    def test_cancel_closes_in_flight_model_download_response(self):
        job_id = "2" * 32
        with local_model_manager._jobs_lock:
            response = MagicMock()
            local_model_manager._jobs[job_id] = {
                "id": job_id,
                "status": "downloading",
                "progress": 35,
                "response": response,
            }

        result = local_model_manager.cancel_local_model_download(job_id)

        self.assertEqual(result["status"], "cancelled")
        response.close.assert_called_once()

    def test_model_download_can_start_without_an_existing_ollama_service(self):
        with (
            patch.object(local_model_manager, "_ollama_disk_free_gb", return_value=10),
            patch.object(local_model_manager, "_find_ollama_executable", return_value="/usr/bin/ollama"),
            patch.object(local_model_manager, "_installed_ollama_models", return_value=[]),
            patch.object(local_model_manager.threading.Thread, "start"),
        ):
            result = local_model_manager.start_local_model_download("qwen3-0.6b")

        self.assertEqual(result["status"], "queued")
        self.assertTrue(local_model_manager.get_local_model_download(result["job_id"])["message"])

    def test_runtime_install_downloads_official_archive_into_user_managed_directory(self):
        job_id = "e" * 32
        with local_model_manager._jobs_lock:
            local_model_manager._jobs[job_id] = {"id": job_id, "status": "queued", "progress": 0}
        with tempfile.TemporaryDirectory() as temporary:
            install_root = Path(temporary) / "ollama"

            def extract(job_id, _archive_path, destination):
                binary = destination / "bin" / "ollama"
                binary.parent.mkdir(parents=True)
                binary.write_text("#!/bin/sh\n", encoding="utf-8")
                binary.chmod(0o755)

            with (
                patch.object(local_model_manager, "_ollama_install_root", return_value=install_root),
                patch.object(local_model_manager.platform, "system", return_value="Linux"),
                patch.object(local_model_manager.platform, "machine", return_value="x86_64"),
                patch.object(local_model_manager.shutil, "which", return_value=None),
                patch.object(local_model_manager, "_download_runtime_archive") as download,
                patch.object(local_model_manager, "_extract_ollama_archive", side_effect=extract),
            ):
                executable = local_model_manager._install_managed_ollama(job_id)

        self.assertEqual(executable, str(install_root / "bin" / "ollama"))
        download.assert_called_once()
        self.assertEqual(
            download.call_args.args[2],
            "https://ollama.com/download/ollama-linux-amd64.tgz",
        )

    def test_tgz_runtime_archive_extracts_only_expected_runtime_files(self):
        archive_data = io.BytesIO()
        with tarfile.open(fileobj=archive_data, mode="w:gz") as archive:
            entry = tarfile.TarInfo("bin/ollama")
            entry.mode = 0o755
            entry.size = 6
            archive.addfile(entry, io.BytesIO(b"binary"))
        job_id = "b" * 32
        with local_model_manager._jobs_lock:
            local_model_manager._jobs[job_id] = {"id": job_id, "status": "installing_runtime"}

        with tempfile.TemporaryDirectory() as temporary:
            archive_path = Path(temporary) / "ollama.tgz"
            archive_path.write_bytes(archive_data.getvalue())
            destination = Path(temporary) / "runtime"
            local_model_manager._extract_ollama_archive(job_id, archive_path, destination)

            binary = destination / "bin" / "ollama"
            self.assertEqual(binary.read_bytes(), b"binary")
            self.assertTrue(binary.stat().st_mode & 0o111)

    def test_runtime_archive_extraction_rejects_path_traversal(self):
        archive_data = io.BytesIO()
        with tarfile.open(fileobj=archive_data, mode="w") as archive:
            entry = tarfile.TarInfo("../outside")
            entry.size = 1
            archive.addfile(entry, io.BytesIO(b"x"))
        job_id = "f" * 32
        with local_model_manager._jobs_lock:
            local_model_manager._jobs[job_id] = {"id": job_id, "status": "installing_runtime"}
        process = MagicMock()
        process.stdout = io.BytesIO(archive_data.getvalue())
        process.wait.return_value = 0

        with (
            patch.object(local_model_manager.shutil, "which", return_value="/usr/bin/zstd"),
            patch.object(local_model_manager.subprocess, "Popen", return_value=process),
            tempfile.TemporaryDirectory() as temporary,
            self.assertRaisesRegex(OSError, "unexpected file"),
        ):
            local_model_manager._extract_ollama_archive(
                job_id,
                Path(temporary) / "ollama.tar.zst",
                Path(temporary) / "runtime",
            )

    def test_runtime_archive_allows_internal_library_symlinks(self):
        archive_data = io.BytesIO()
        with tarfile.open(fileobj=archive_data, mode="w") as archive:
            library = tarfile.TarInfo("lib/ollama/libsample.so.1")
            library.size = 1
            archive.addfile(library, io.BytesIO(b"x"))
            link = tarfile.TarInfo("lib/ollama/libsample.so")
            link.type = tarfile.SYMTYPE
            link.linkname = "libsample.so.1"
            archive.addfile(link)
        job_id = "c" * 32
        with local_model_manager._jobs_lock:
            local_model_manager._jobs[job_id] = {"id": job_id, "status": "installing_runtime"}
        process = MagicMock()
        process.stdout = io.BytesIO(archive_data.getvalue())
        process.wait.return_value = 0

        with (
            patch.object(local_model_manager.shutil, "which", return_value="/usr/bin/zstd"),
            patch.object(local_model_manager.subprocess, "Popen", return_value=process),
            tempfile.TemporaryDirectory() as temporary,
        ):
            destination = Path(temporary) / "runtime"
            local_model_manager._extract_ollama_archive(
                job_id,
                Path(temporary) / "ollama.tar.zst",
                destination,
            )
            self.assertTrue((destination / "lib" / "ollama" / "libsample.so").is_symlink())

    def test_runtime_startup_launches_loopback_service_and_waits_until_ready(self):
        job_id = "a" * 32
        with local_model_manager._jobs_lock:
            local_model_manager._jobs[job_id] = {"id": job_id, "status": "queued", "progress": 0}
        process = MagicMock()
        process.poll.return_value = None
        with (
            patch.object(local_model_manager, "_find_ollama_executable", return_value="/managed/ollama"),
            patch.object(local_model_manager, "_ollama_is_running", side_effect=[False, True]),
            patch.object(local_model_manager.subprocess, "Popen", return_value=process) as popen,
        ):
            executable = local_model_manager._ensure_ollama_runtime(job_id)

        self.assertEqual(executable, "/managed/ollama")
        self.assertEqual(popen.call_args.args[0], ["/managed/ollama", "serve"])
        self.assertEqual(popen.call_args.kwargs["env"]["OLLAMA_HOST"], "127.0.0.1:11434")


if __name__ == "__main__":
    unittest.main()
