"""Provenance helpers for canonical raw datasets."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

from .contracts import RawDatasetManifest, SourceDatasetDescriptor


def sha256_for_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def build_raw_dataset_manifest(
    descriptor: SourceDatasetDescriptor,
    repo_root: Path,
    import_date: str | None = None,
) -> RawDatasetManifest:
    dataset_path = descriptor.absolute_path(repo_root)
    resolved_import_date = import_date or date.today().isoformat()
    return RawDatasetManifest(
        dataset_name=descriptor.name,
        canonical_path=descriptor.relative_path,
        original_filename=descriptor.original_filename,
        source_category=descriptor.source_category,
        file_format=descriptor.file_format,
        encoding=descriptor.encoding,
        size_bytes=dataset_path.stat().st_size,
        sha256=sha256_for_file(dataset_path),
        import_date=resolved_import_date,
        steward=descriptor.steward,
        immutable=descriptor.immutable,
        description=descriptor.description,
        known_limitations=descriptor.known_limitations,
    )
