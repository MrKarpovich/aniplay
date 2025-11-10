# -*- coding: utf-8 -*-

"""
Скрипт для автоматического создания плейлиста playlist.m3u
из видеофайлов в выбранной папке и запуска его в VLC.
"""

import re
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Optional, Union

# Поддерживаемые расширения видео
VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".webm", ".mov", ".flv", ".wmv"}


def natural_sort_key(s: Union[str, Path]) -> List[Union[str, int]]:
    """
    Возвращает ключ сортировки, учитывающий числа.

    Пример:
        "серия 2" будет идти перед "серия 10".
    """
    text = str(s)
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", text)
    ]


def find_vlc_path() -> Optional[Path]:
    """
    Ищет исполняемый файл VLC в стандартных местах установки Windows.

    Returns:
        Optional[Path]: путь к VLC, если найден.
    """
    candidates = [
        Path(r"C:\Program Files\VideoLAN\VLC\vlc.exe"),
        Path(r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def create_playlist(folder_path: Path) -> Optional[Path]:
    """
    Создаёт файл playlist.m3u в указанной папке.

    Args:
        folder_path (Path): путь к папке с видеофайлами.

    Returns:
        Optional[Path]: путь к созданному плейлисту или None, если ошибка.
    """
    video_files = [
        f
        for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    ]

    if not video_files:
        messagebox.showwarning(
            "⚠️ Нет видео",
            "В выбранной папке не найдено ни одного видеофайла.",
        )
        return None

    video_files.sort(key=natural_sort_key)
    playlist_path = folder_path / "playlist.m3u"

    try:
        with open(playlist_path, "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")
            for vf in video_files:
                file.write(f"#EXTINF: -1, {vf.name}\n{vf.name}\n")
        return playlist_path
    except OSError as exc:
        messagebox.showerror(
            "❌ Ошибка",
            f"Не удалось создать плейлист: \n{exc}",
        )
        return None


def launch_with_vlc(playlist_path: Path) -> bool:
    """
    Запускает VLC с указанным плейлистом, если VLC найден.

    Args:
        playlist_path (Path): путь к .m3u файлу.

    Returns:
        bool: True, если запуск успешен.
    """
    vlc_path = find_vlc_path()
    if vlc_path is None:
        return False

    try:
        subprocess.Popen(
            [str(vlc_path), str(playlist_path)],
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def main() -> None:
    """Основная функция выбора папки, создания и запуска плейлиста."""
    root = tk.Tk()
    root.withdraw()

    folder = filedialog.askdirectory(
        initialdir=r"E:\Видео\anime",
        title="📁 Выберите папку с аниме (там должны быть серии)",
    )
    if not folder:
        return

    folder_path = Path(folder)
    playlist_path = create_playlist(folder_path)
    if playlist_path is None:
        return

    series_count = sum(
        1
        for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    )

    launch = messagebox.askyesno(
        "🎬 Плейлист готов!",
        f"Создан playlist.m3u\nВсего серий: {series_count}\n\n"
        "Запустить в VLC сейчас?",
    )

    if launch:
        success = launch_with_vlc(playlist_path)
        if not success:
            messagebox.showwarning(
                "⚠️ VLC не найден",
                "VLC не установлен или не обнаружен.\n\n"
                "Откройте playlist.m3u вручную:\n"
                "→ ПКМ по файлу → Открыть с помощью → VLC",
            )
    else:
        messagebox.showinfo(
            "ℹ️ Готово",
            "Файл playlist.m3u сохранён в папке с аниме.\n\n"
            "Чтобы открыть:\n"
            "• ПКМ по playlist.m3u → Открыть с помощью → VLC\n"
            "• Или назначьте VLC плеером по умолчанию для .m3u",
        )


if __name__ == "__main__":
    main()
