"""Chia ảnh theo nội dung để ảnh trùng không lọt qua nhiều tập."""
import hashlib
import random
import shutil
import unicodedata
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, UnidentifiedImageError

from src.model.predict import CLASS_NAMES

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
SOURCE_FOLDER_MAP = {
    "leafblast": "dao_on",
    "bacterialleafblight": "bac_la",
    "brownspot": "dom_nau",
    "healthy": "la_khoe",
}


def _normalize_folder(name: str) -> str:
    """Chuẩn hóa tên thư mục nguồn, bỏ dấu cách và dấu câu."""
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return "".join(character.lower() for character in normalized if character.isalnum())


def extract_mendeley_subset(
    archive_path: str | Path, thu_muc_ra: str | Path = "data/raw/mendeley_n8jpkpfz5p_v1"
) -> dict[str, int]:
    """Giải nén riêng bốn lớp của archive Mendeley theo tên thư mục lớp."""
    archive = Path(archive_path)
    output = Path(thu_muc_ra)
    if not archive.is_file():
        raise FileNotFoundError(f"Không tìm thấy archive dữ liệu: {archive}")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Thư mục đầu ra không rỗng: {output}")

    counts = {name: 0 for name in SOURCE_FOLDER_MAP.values()}
    with ZipFile(archive) as zipped:
        for member in zipped.infolist():
            if member.is_dir():
                continue
            parts = member.filename.replace("\\", "/").split("/")
            if Path(parts[-1]).suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            label = next(
                (SOURCE_FOLDER_MAP[_normalize_folder(part)]
                 for part in reversed(parts[:-1])
                 if _normalize_folder(part) in SOURCE_FOLDER_MAP),
                None,
            )
            if label is None:
                continue
            destination_dir = output / label
            destination_dir.mkdir(parents=True, exist_ok=True)
            destination = destination_dir / Path(parts[-1]).name
            if destination.exists():
                destination = destination_dir / f"{counts[label]:06d}_{destination.name}"
            with zipped.open(member) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)
            counts[label] += 1
    return counts


def _records(source: Path, excluded_hashes: set[str] | None = None) -> dict[str, dict[str, Path]]:
    """Đọc ảnh theo thư mục lớp, gom bản sao byte giống hệt theo SHA-256."""
    records: dict[str, dict[str, Path]] = {name: {} for name in CLASS_NAMES}
    labels_by_digest: dict[str, str] = {}
    for class_name in CLASS_NAMES:
        class_dir = source / class_name
        if not class_dir.is_dir():
            raise ValueError(f"Thiếu thư mục lớp: {class_dir}")
        for path in sorted(class_dir.iterdir()):
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS or not path.is_file():
                continue
            try:
                with Image.open(path) as image:
                    image.verify()
            except (UnidentifiedImageError, OSError) as exc:
                raise ValueError(f"Ảnh hỏng: {path}") from exc
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if excluded_hashes and digest in excluded_hashes:
                continue
            if digest in labels_by_digest and labels_by_digest[digest] != class_name:
                raise ValueError(
                    f"Ảnh trùng nội dung nhưng gán hai nhãn: {labels_by_digest[digest]} và {class_name}."
                )
            labels_by_digest[digest] = class_name
            records[class_name].setdefault(digest, path)
    for label, group in records.items():
        if len(group) < 3:
            raise ValueError(f"Lớp {label} cần ít nhất ba ảnh khác nhau để chia tập.")
    return records


def prepare_data(
    thu_muc: str | Path,
    thu_muc_ra: str | Path = "artifacts/data",
    seed: int = 1314,
    exclude_paths: list[str | Path] | None = None,
) -> dict[str, int]:
    """Tạo cấu trúc train/validation/test theo tỷ lệ 60/20/20.

    Dữ liệu đầu vào phải được sắp trong thư mục con mang mã lớp chuẩn. Ảnh
    không bị sửa; ảnh có cùng checksum luôn nằm trong một phân vùng.
    """
    source = Path(thu_muc)
    output = Path(thu_muc_ra)
    excluded_hashes = set()
    for excluded_path in exclude_paths or []:
        path = Path(excluded_path)
        if not path.is_file():
            raise FileNotFoundError(f"Không tìm thấy ảnh cần giữ ngoài tập: {path}")
        excluded_hashes.add(hashlib.sha256(path.read_bytes()).hexdigest())
    records = _records(source, excluded_hashes)
    if output.resolve() == source.resolve() or source.resolve() in output.resolve().parents:
        raise ValueError("Thư mục đầu ra không được nằm trong thư mục ảnh nguồn.")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Thư mục đầu ra không rỗng: {output}")

    rng = random.Random(seed)
    counts = {"train": 0, "validation": 0, "test": 0}
    for class_name, images in records.items():
        grouped_paths = list(images.values())
        rng.shuffle(grouped_paths)
        train_end = min(len(grouped_paths) - 2, max(1, round(len(grouped_paths) * 0.6)))
        validation_end = min(
            len(grouped_paths) - 1,
            max(train_end + 1, round(len(grouped_paths) * 0.8)),
        )
        partitions = {
            "train": grouped_paths[:train_end],
            "validation": grouped_paths[train_end:validation_end],
            "test": grouped_paths[validation_end:],
        }
        for partition, paths in partitions.items():
            target = output / partition / class_name
            target.mkdir(parents=True, exist_ok=True)
            for index, path in enumerate(paths):
                shutil.copy2(path, target / f"{index:05d}_{path.name}")
                counts[partition] += 1
    return counts
