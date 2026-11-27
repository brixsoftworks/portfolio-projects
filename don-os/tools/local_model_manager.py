"""Hardware-aware local model discovery and Ollama/Hugging Face downloads."""

import json
import os
import platform
import posixpath
import re
import shutil
import subprocess
import tarfile
import tempfile
import threading
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from tools.model_registry import (
    DEFAULT_OLLAMA_URL,
    ModelRegistryError,
    add_model,
    list_models,
    set_active_model,
)


OLLAMA_API_URL = "http://127.0.0.1:11434"
MODEL_CATALOG = (
    {
        "id": "qwen3-0.6b",
        "name": "Qwen 3 · Small",
        "description": "Quick responses and lighter tasks. A good fit for modest computers.",
        "model": "hf.co/unsloth/Qwen3-0.6B-GGUF:Q4_K_M",
        "repository": "unsloth/Qwen3-0.6B-GGUF",
        "parameters": "0.6B",
        "download_bytes": 500_000_000,
        "memory_gb": 2.0,
    },
    {
        "id": "qwen3-4b",
        "name": "Qwen 3 · Balanced",
        "description": "A stronger everyday assistant for chat, writing, and reasoning.",
        "model": "hf.co/unsloth/Qwen3-4B-GGUF:Q4_K_M",
        "repository": "unsloth/Qwen3-4B-GGUF",
        "parameters": "4B",
        "download_bytes": 2_700_000_000,
        "memory_gb": 5.0,
    },
    {
        "id": "qwen3-8b",
        "name": "Qwen 3 · Advanced",
        "description": "More capable, but needs more memory and takes longer to download.",
        "model": "hf.co/unsloth/Qwen3-8B-GGUF:Q4_K_M",
        "repository": "unsloth/Qwen3-8B-GGUF",
        "parameters": "8B",
        "download_bytes": 5_300_000_000,
        "memory_gb": 9.0,
    },
)
CATALOG_BY_ID = {model["id"]: model for model in MODEL_CATALOG}
JOB_ID_PATTERN = re.compile(r"^[a-f0-9]{32}$")
_jobs: Dict[str, Dict[str, Any]] = {}
_jobs_lock = threading.Lock()
_managed_ollama_process: Optional[subprocess.Popen] = None
_ollama_runtime_output = deque(maxlen=30)


def _ollama_install_root() -> Path:
    return Path.home() / ".local" / "share" / "don-os" / "ollama"


def _find_ollama_executable() -> Optional[str]:
    executable = shutil.which("ollama")
    if executable:
        return executable
    candidates = (
        Path.home() / ".local" / "bin" / "ollama",
        _ollama_install_root() / "bin" / "ollama",
        Path("/usr/local/bin/ollama"),
        Path("/usr/bin/ollama"),
        Path("/bin/ollama"),
    )
    return next((str(path) for path in candidates if path.is_file() and os.access(path, os.X_OK)), None)


def _job_is_cancelled(job_id: str) -> bool:
    with _jobs_lock:
        job = _jobs.get(job_id)
        return not job or job.get("status") == "cancelled"


def _set_job_stage(job_id: str, status: str, message: str, progress: int) -> None:
    if not _job_is_cancelled(job_id):
        _update_job(
            job_id,
            status=status,
            message=message,
            progress=progress,
            progress_label=f"{progress}%",
        )


def _download_runtime_archive(job_id: str, archive_path: Path, url: str) -> None:
    if _job_is_cancelled(job_id):
        return
    request = Request(url, headers={"User-Agent": "DON-OS local model setup"})
    with urlopen(request, timeout=60) as response:
        with _jobs_lock:
            job = _jobs.get(job_id)
            if not job or job.get("status") == "cancelled":
                return
            job["response"] = response
        try:
            with archive_path.open("wb") as archive:
                try:
                    total = int(response.headers.get("Content-Length", "0") or 0)
                except ValueError:
                    total = 0
                received = 0
                while True:
                    if _job_is_cancelled(job_id):
                        return
                    chunk = response.read(256 * 1024)
                    if not chunk:
                        break
                    archive.write(chunk)
                    received += len(chunk)
                    progress = 2 + int(10 * received / total) if total else 2
                    _set_job_stage(
                        job_id,
                        "installing_runtime",
                        f"Downloading the local model runtime ({received // (1024 * 1024)} MB)…",
                        min(12, progress),
                    )
        finally:
            with _jobs_lock:
                job = _jobs.get(job_id)
                if job and job.get("response") is response:
                    job["response"] = None
    if not _job_is_cancelled(job_id) and archive_path.stat().st_size == 0:
        raise OSError("The runtime download was empty. Check your connection and try again.")


def _extract_ollama_archive(job_id: str, archive_path: Path, destination: Path) -> None:
    process = None
    compressed_stream = None
    if archive_path.suffix == ".tgz":
        compressed_stream = archive_path.open("rb")
        archive_stream = compressed_stream
        archive_mode = "r|gz"
    else:
        zstd = shutil.which("zstd")
        if not zstd:
            raise OSError("This computer needs the zstd archive utility to install the local runtime.")
        process = subprocess.Popen(
            [zstd, "-d", "-c", str(archive_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        with _jobs_lock:
            job = _jobs.get(job_id)
            if job and job.get("status") != "cancelled":
                job["process"] = process
        if not process.stdout:
            _stop_process(process)
            raise OSError("Could not read the local runtime archive.")
        archive_stream = process.stdout
        archive_mode = "r|"

    destination.mkdir(parents=True, exist_ok=True)
    extracted_bytes = 0
    symlinks = []
    try:
        with tarfile.open(fileobj=archive_stream, mode=archive_mode) as archive:
            for member in archive:
                if _job_is_cancelled(job_id):
                    if process:
                        _stop_process(process)
                    return
                relative_path = PurePosixPath(member.name)
                parts = tuple(part for part in relative_path.parts if part not in {"", "."})
                allowed_path = (
                    (parts == ("bin",) and member.isdir())
                    or (parts == ("bin", "ollama") and member.isfile())
                    or (parts in {("lib",), ("lib", "ollama")} and member.isdir())
                    or (
                        len(parts) >= 3
                        and parts[:2] == ("lib", "ollama")
                        and (member.isfile() or member.isdir() or member.issym())
                    )
                )
                if (
                    relative_path.is_absolute()
                    or not parts
                    or ".." in parts
                    or not allowed_path
                ):
                    raise OSError("The local runtime archive contains an unexpected file.")
                if member.islnk() or member.isdev() or not (member.isdir() or member.isfile() or member.issym()):
                    raise OSError("The local runtime archive contains an unsafe file.")
                if member.issym():
                    link_target = member.linkname
                    resolved_target = posixpath.normpath(posixpath.join(posixpath.dirname(member.name), link_target))
                    if (
                        not link_target
                        or PurePosixPath(link_target).is_absolute()
                        or not resolved_target.startswith("lib/ollama/")
                    ):
                        raise OSError("The local runtime archive contains an unsafe symbolic link.")
                    symlinks.append((parts, link_target))
                    continue
                extracted_bytes += member.size
                if extracted_bytes > 12 * 1024 * 1024 * 1024:
                    raise OSError("The local runtime archive is larger than expected.")
                target = destination.joinpath(*parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                source = archive.extractfile(member)
                if source is None:
                    raise OSError("Could not extract the local runtime.")
                with source, target.open("wb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
                target.chmod(0o755 if member.mode & 0o111 else 0o644)
        for parts, link_target in symlinks:
            target = destination.joinpath(*parts)
            parent = target.parent
            while parent != destination:
                if parent.is_symlink():
                    raise OSError("The local runtime archive contains conflicting files.")
                parent = parent.parent
            if target.exists() or target.is_symlink():
                raise OSError("The local runtime archive contains conflicting files.")
            target.symlink_to(link_target)
    except Exception:
        if process:
            _stop_process(process)
        raise
    finally:
        if process and process.stdout:
            process.stdout.close()
        if compressed_stream:
            compressed_stream.close()
    if process:
        return_code = process.wait()
        if return_code:
            raise OSError("Could not unpack the local runtime. Try again and check available disk space.")


def _install_managed_ollama(job_id: str) -> str:
    if platform.system() != "Linux":
        raise OSError("Automatic local runtime setup is currently supported on Linux.")
    architecture = {"x86_64": "amd64", "aarch64": "arm64"}.get(platform.machine().lower())
    if not architecture:
        raise OSError(f"Automatic local runtime setup does not support {platform.machine()}.")

    install_root = _ollama_install_root()
    install_root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".ollama-setup-", dir=install_root.parent) as temporary:
        work_dir = Path(temporary)
        use_zstd = bool(shutil.which("zstd"))
        archive_suffix = ".tar.zst" if use_zstd else ".tgz"
        archive_path = work_dir / f"ollama{archive_suffix}"
        extracted_dir = work_dir / "runtime"
        url = f"https://ollama.com/download/ollama-linux-{architecture}{archive_suffix}"
        _set_job_stage(job_id, "installing_runtime", "Downloading the local model runtime…", 1)
        _download_runtime_archive(job_id, archive_path, url)
        if _job_is_cancelled(job_id):
            return ""
        _set_job_stage(job_id, "installing_runtime", "Unpacking the local model runtime…", 13)
        _extract_ollama_archive(job_id, archive_path, extracted_dir)
        if _job_is_cancelled(job_id):
            return ""
        binary = extracted_dir / "bin" / "ollama"
        if not binary.is_file():
            raise OSError("The runtime archive did not contain the Ollama application.")
        binary.chmod(0o755)
        staged_install = work_dir / "install"
        shutil.copytree(extracted_dir, staged_install, symlinks=True)
        staged_binary = staged_install / "bin" / "ollama"
        if not staged_binary.is_file() or not os.access(staged_binary, os.X_OK):
            raise OSError("The staged local runtime is incomplete.")

        backup_root = install_root.parent / f".ollama-backup-{job_id}"
        if install_root.exists():
            os.replace(install_root, backup_root)
        try:
            os.replace(staged_install, install_root)
        except OSError:
            if backup_root.exists() and not install_root.exists():
                os.replace(backup_root, install_root)
            raise
        if backup_root.exists():
            shutil.rmtree(backup_root)
    installed_binary = install_root / "bin" / "ollama"
    if not installed_binary.is_file() or not os.access(installed_binary, os.X_OK):
        raise OSError("The local runtime could not be installed in your user profile.")
    return str(installed_binary)


def _start_ollama_service(job_id: str, executable: str) -> None:
    global _managed_ollama_process
    if _ollama_is_running():
        return
    _set_job_stage(job_id, "starting_runtime", "Starting the local model service…", 20)
    _ollama_runtime_output.clear()
    environment = os.environ.copy()
    environment["OLLAMA_HOST"] = "127.0.0.1:11434"
    process = subprocess.Popen(
        [executable, "serve"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=environment,
        start_new_session=(os.name == "posix"),
    )
    if process.stdout:
        threading.Thread(
            target=_capture_runtime_output,
            args=(process.stdout,),
            daemon=True,
        ).start()
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job and job.get("status") != "cancelled":
            job["process"] = process
    _managed_ollama_process = process
    for _ in range(60):
        if _job_is_cancelled(job_id):
            _stop_process(process)
            return
        if process.poll() is not None:
            details = " ".join(_ollama_runtime_output)
            raise OSError(
                "The local model service exited during startup."
                + (f" Runtime says: {details[-500:]}" if details else " Try again.")
            )
        if _ollama_is_running():
            with _jobs_lock:
                job = _jobs.get(job_id)
                if job and job.get("process") is process:
                    job["process"] = None
            return
        threading.Event().wait(0.5)
    _stop_process(process)
    details = " ".join(_ollama_runtime_output)
    raise OSError(
        "The local model service did not start."
        + (f" Runtime says: {details[-500:]}" if details else " Check whether port 11434 is available, then try again.")
    )


def _capture_runtime_output(stream) -> None:
    for line in stream:
        text = line.strip()
        if text:
            _ollama_runtime_output.append(text[:240])


def _ensure_ollama_runtime(job_id: str) -> Optional[str]:
    executable = _find_ollama_executable()
    if not executable:
        executable = _install_managed_ollama(job_id)
    if _job_is_cancelled(job_id):
        return None
    _start_ollama_service(job_id, executable)
    if _job_is_cancelled(job_id):
        return None
    return executable


def get_local_model_catalog() -> Dict[str, Any]:
    runtime_installed = _find_ollama_executable() is not None
    setup_overhead_gb = 1 if runtime_installed else 4
    runtime_running, installed_models = _ollama_status_and_models()
    installed = {model["name"] for model in installed_models}
    return {
        "models": [
            {
                "id": model["id"],
                "name": model["name"],
                "description": model["description"],
                "model": model["model"],
                "repository": model["repository"],
                "parameters": model["parameters"],
                "download_gb": round(model["download_bytes"] / 1_000_000_000, 1),
                "required_disk_gb": round(model["download_bytes"] / 1_000_000_000 + setup_overhead_gb, 1),
                "memory_gb": model["memory_gb"],
                "installed": model["model"] in installed,
                "runtime_installed": runtime_installed,
                "runtime_running": runtime_running,
                "huggingface_url": f"https://huggingface.co/{model['repository']}",
            }
            for model in MODEL_CATALOG
        ]
    }


def _system_memory_gb() -> Optional[float]:
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        return round((pages * page_size) / (1024 ** 3), 1)
    except (AttributeError, OSError, ValueError):
        return None


def _ollama_disk_free_gb() -> Optional[float]:
    model_dir = Path(os.environ.get("OLLAMA_MODELS", Path.home() / ".ollama" / "models")).expanduser()
    while not model_dir.exists() and model_dir.parent != model_dir:
        model_dir = model_dir.parent
    try:
        return round(shutil.disk_usage(model_dir).free / (1024 ** 3), 1)
    except OSError:
        return None


def _gpu_details() -> Dict[str, Any]:
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi:
        try:
            result = subprocess.run(
                [nvidia_smi, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=1.5,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                name, _, memory = result.stdout.strip().splitlines()[0].partition(",")
                return {
                    "name": name.strip(),
                    "vram_gb": round(float(memory.strip()) / 1024, 1),
                }
        except (OSError, subprocess.SubprocessError, ValueError):
            pass

    drm = Path("/sys/class/drm")
    if drm.exists():
        for vendor_file in drm.glob("card*/device/vendor"):
            try:
                vendor = vendor_file.read_text(encoding="utf-8").strip().lower()
            except OSError:
                continue
            names = {"0x1002": "AMD graphics", "0x8086": "Intel graphics", "0x10de": "NVIDIA graphics"}
            if vendor in names:
                return {"name": names[vendor], "vram_gb": None}
    return {"name": None, "vram_gb": None}


def _ollama_status_and_models() -> tuple:
    try:
        with urlopen(f"{OLLAMA_API_URL}/api/tags", timeout=1.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError, UnicodeDecodeError):
        return False, []
    models = [
        {"name": str(model.get("name", "")), "size": model.get("size")}
        for model in payload.get("models", [])
        if model.get("name")
    ]
    return True, models


def _installed_ollama_models() -> list:
    return _ollama_status_and_models()[1]


def _recommendation_budget(ram_gb: Optional[float], vram_gb: Optional[float]) -> float:
    if vram_gb:
        return max(ram_gb or 0, vram_gb) - 1.5
    if ram_gb:
        return ram_gb - 3.0
    return 0


def _public_catalog(
    ram_gb: Optional[float],
    vram_gb: Optional[float],
    installed: set,
    disk_free_gb: Optional[float] = None,
) -> list:
    budget = _recommendation_budget(ram_gb, vram_gb)
    eligible = [
        model for model in MODEL_CATALOG
        if model["memory_gb"] <= budget
        and (disk_free_gb is None or disk_free_gb >= model["download_bytes"] / 1_000_000_000 + 1)
    ]
    recommended_id = eligible[-1]["id"] if eligible else MODEL_CATALOG[0]["id"]
    result = []
    for model in MODEL_CATALOG:
        result.append({
            **{key: value for key, value in model.items() if key not in {"download_bytes", "memory_gb"}},
            "download_gb": round(model["download_bytes"] / 1_000_000_000, 1),
            "required_disk_gb": round(model["download_bytes"] / 1_000_000_000 + 1, 1),
            "memory_gb": model["memory_gb"],
            "recommended": model["id"] == recommended_id,
            "fits_hardware": model["memory_gb"] <= budget,
            "fits_disk": disk_free_gb is None or disk_free_gb >= model["download_bytes"] / 1_000_000_000 + 1,
            "installed": model["model"] in installed,
            "huggingface_url": f"https://huggingface.co/{model['repository']}",
        })
    return result


def scan_local_model_hardware() -> Dict[str, Any]:
    with ThreadPoolExecutor(max_workers=2) as executor:
        gpu_future = executor.submit(_gpu_details)
        ollama_future = executor.submit(_ollama_status_and_models)
        ram_gb = _system_memory_gb()
        disk_free_gb = _ollama_disk_free_gb()
        gpu = gpu_future.result()
        ollama_running, installed_models = ollama_future.result()
    ollama_path = _find_ollama_executable()
    installed = {model["name"] for model in installed_models}
    try:
        cpu_cores = os.cpu_count()
    except OSError:
        cpu_cores = None
    return {
        "ram_gb": ram_gb,
        "disk_free_gb": disk_free_gb,
        "cpu_cores": cpu_cores,
        "gpu_name": gpu["name"],
        "vram_gb": gpu["vram_gb"],
        "ollama_installed": bool(ollama_path),
        "ollama_running": ollama_running,
        "installed_models": installed_models,
        "catalog": _public_catalog(ram_gb, gpu["vram_gb"], installed, disk_free_gb),
    }


def _ollama_is_running() -> bool:
    return _ollama_status_and_models()[0]


def _connect_downloaded_model(catalog_id: str) -> Dict[str, Any]:
    entry = CATALOG_BY_ID[catalog_id]
    configured = list_models()["models"]
    existing = next((model for model in configured if model.get("model") == entry["model"]), None)
    if existing:
        set_active_model(existing["id"])
        return existing
    display_name = _unique_local_model_name(entry["name"], configured)
    model = add_model(
        display_name,
        "ollama",
        entry["model"],
        DEFAULT_OLLAMA_URL,
    )
    set_active_model(model["id"])
    return model


def _unique_local_model_name(name: str, configured: list) -> str:
    used = {model["name"].casefold() for model in configured}
    candidate = name
    suffix = 2
    while candidate.casefold() in used:
        candidate = f"{name} ({suffix})"
        suffix += 1
    return candidate


def connect_installed_local_model(catalog_id: str) -> Dict[str, Any]:
    if catalog_id not in CATALOG_BY_ID:
        raise ModelRegistryError("Choose a model from the available list.")
    installed = {item["name"] for item in _installed_ollama_models()}
    if CATALOG_BY_ID[catalog_id]["model"] not in installed:
        raise ModelRegistryError("This model is not downloaded yet.")
    return _connect_downloaded_model(catalog_id)


def connect_existing_local_model(model_name: str) -> Dict[str, Any]:
    model_name = model_name.strip()
    installed = {item["name"] for item in _installed_ollama_models()}
    if model_name not in installed:
        raise ModelRegistryError("Choose a model that is installed in Ollama.")
    configured = list_models()["models"]
    existing = next((model for model in configured if model.get("model") == model_name), None)
    if existing:
        set_active_model(existing["id"])
        return existing
    model = add_model(
        _unique_local_model_name(model_name, configured),
        "ollama",
        model_name,
        DEFAULT_OLLAMA_URL,
    )
    set_active_model(model["id"])
    return model


def _pull_model_from_ollama(job_id: str, model_name: str) -> None:
    request = Request(
        f"{OLLAMA_API_URL}/api/pull",
        data=json.dumps({"model": model_name, "stream": True}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        response = urlopen(request, timeout=300)
    except HTTPError as error:
        details = error.read(2048).decode("utf-8", errors="replace")
        try:
            details = json.loads(details).get("error") or details
        except json.JSONDecodeError:
            pass
        raise OSError(f"Ollama could not start the model download: {details[:300]}") from error

    succeeded = False
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job or job.get("status") == "cancelled":
            response.close()
            return
        job["response"] = response
        job["status"] = "downloading"
    try:
        for raw_line in response:
            if _job_is_cancelled(job_id):
                return
            if not raw_line.strip():
                continue
            try:
                event = json.loads(raw_line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise OSError("Ollama returned an unreadable model-download update.") from error
            if event.get("error"):
                raise OSError(f"Ollama could not download this model: {str(event['error'])[:300]}")
            status = str(event.get("status") or "Downloading model layers…")
            updates: Dict[str, Any] = {"message": status[:160]}
            total = event.get("total")
            completed = event.get("completed")
            if isinstance(total, int) and total > 0 and isinstance(completed, int):
                file_progress = max(0, min(100, int(completed * 100 / total)))
                updates["progress"] = max(22, min(99, 22 + int(file_progress * 0.77)))
                updates["progress_label"] = f"{file_progress}% of current file"
                updates["message"] = f"{status[:110]} · {file_progress}% of current file"
            _update_job(job_id, **updates)
            if status.casefold() == "success":
                succeeded = True
        if not _job_is_cancelled(job_id) and not succeeded:
            raise OSError("Ollama closed the download before the model was ready. Try again.")
    finally:
        with _jobs_lock:
            job = _jobs.get(job_id)
            if job and job.get("response") is response:
                job["response"] = None
        response.close()


def _download_worker(job_id: str, catalog_id: str) -> None:
    entry = CATALOG_BY_ID[catalog_id]
    try:
        executable = _ensure_ollama_runtime(job_id)
        if _job_is_cancelled(job_id):
            return
        if not executable:
            raise OSError("The local model runtime could not be started.")
        _set_job_stage(job_id, "downloading", "Downloading model from Hugging Face…", 22)
        _pull_model_from_ollama(job_id, entry["model"])
        if _job_is_cancelled(job_id):
            return
        connected_model = _connect_downloaded_model(catalog_id)
        _update_job(
            job_id,
            status="completed",
            progress=100,
            message="Ready to use",
            connected_model=connected_model,
        )
    except (OSError, URLError, ModelRegistryError, tarfile.TarError) as error:
        if _job_is_cancelled(job_id):
            return
        _update_job(
            job_id,
            status="failed",
            message="Could not finish setting up the local model.",
            error=str(error),
        )


def _update_job(job_id: str, **changes: Any) -> None:
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].update(changes)


def _stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    try:
        process.terminate()
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def start_local_model_download(catalog_id: str) -> Dict[str, Any]:
    if catalog_id not in CATALOG_BY_ID:
        raise ModelRegistryError("Choose a model from the available list.")
    installed = {item["name"] for item in _installed_ollama_models()}
    if CATALOG_BY_ID[catalog_id]["model"] in installed:
        model = _connect_downloaded_model(catalog_id)
        return {"status": "completed", "progress": 100, "message": "Ready to use", "connected_model": model}

    disk_free_gb = _ollama_disk_free_gb()
    runtime_needed = _find_ollama_executable() is None
    required_disk_gb = (
        CATALOG_BY_ID[catalog_id]["download_bytes"] / 1_000_000_000
        + (4 if runtime_needed else 1)
    )
    if disk_free_gb is not None and disk_free_gb < required_disk_gb:
        raise ModelRegistryError(
            f"Free up at least {required_disk_gb:.1f} GB on this computer for the runtime and model, then try again."
        )
    with _jobs_lock:
        if any(job["status"] in {"queued", "installing_runtime", "starting_runtime", "downloading"} for job in _jobs.values()):
            raise ModelRegistryError("A model download is already in progress.")
        job_id = uuid.uuid4().hex
        _jobs[job_id] = {
            "id": job_id,
            "catalog_id": catalog_id,
            "status": "queued",
            "progress": 0,
            "progress_label": "0%",
            "message": "Preparing the local runtime and model…",
            "error": None,
            "connected_model": None,
            "process": None,
        }
    threading.Thread(target=_download_worker, args=(job_id, catalog_id), daemon=True).start()
    return {"job_id": job_id, "status": "queued"}


def get_local_model_download(job_id: str) -> Dict[str, Any]:
    if not JOB_ID_PATTERN.fullmatch(job_id):
        raise ModelRegistryError("Invalid download identifier.")
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            raise ModelRegistryError("This download is no longer available.")
        return {key: value for key, value in job.items() if key not in {"process", "response"}}


def cancel_local_model_download(job_id: str) -> Dict[str, Any]:
    if not JOB_ID_PATTERN.fullmatch(job_id):
        raise ModelRegistryError("Invalid download identifier.")
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            raise ModelRegistryError("This download is no longer available.")
        if job["status"] not in {"queued", "installing_runtime", "starting_runtime", "downloading"}:
            return {key: value for key, value in job.items() if key not in {"process", "response"}}
        job["status"] = "cancelled"
        job["message"] = "Download stopped"
        process = job.get("process")
        response = job.get("response")
        result = {key: value for key, value in job.items() if key not in {"process", "response"}}
    if response:
        response.close()
    if process and process.poll() is None:
        _stop_process(process)
    return result
