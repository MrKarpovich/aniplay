import re
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox


# Поддерживаемые расширения видео
VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.webm', '.mov', '.flv', '.wmv'}


def natural_sort_key(s):
    """Сортирует строки с учётом чисел: [2] перед [10]"""
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r'(\d+)', str(s))
    ]


def find_vlc_path():
    """Ищет vlc.exe в стандартных местах установки на Windows"""
    candidates = [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
    ]
    for path in candidates:
        if Path(path).exists():
            return Path(path)
    return None


def create_playlist(folder_path: Path) -> Path | None:
    """Создаёт playlist.m3u в указанной папке"""
    # Собираем видеофайлы
    video_files = [
        f for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    ]

    if not video_files:
        messagebox.showwarning("⚠️ Нет видео", "В выбранной папке не найдено ни одного видеофайла.")
        return None

    # Сортируем естественным образом
    video_files.sort(key=natural_sort_key)

    # Пишем .m3u
    playlist_path = folder_path / "playlist.m3u"
    try:
        with open(playlist_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for vf in video_files:
                f.write(f"#EXTINF:-1, {vf.name}\n")
                f.write(f"{vf.name}\n")
        return playlist_path
    except OSError as e:
        messagebox.showerror("❌ Ошибка", f"Не удалось создать плейлист:\n{e}")
        return None


def launch_with_vlc(playlist_path: Path) -> bool:
    """Запускает плейлист в VLC, если он найден"""
    vlc_path = find_vlc_path()
    if not vlc_path:
        return False
    try:
        # Запускаем VLC в фоне — скрипт завершится сразу
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


def main():
    # Скрываем основное окно Tkinter
    root = tk.Tk()
    root.withdraw()

    # Открываем проводник для выбора папки
    folder = filedialog.askdirectory(
        initialdir=r"E:\Видео\anime",
        title="📁 Выберите папку с аниме (там должны быть серии)",
    )

    if not folder:
        return  # Пользователь отменил выбор

    folder_path = Path(folder)
    playlist_path = create_playlist(folder_path)
    if not playlist_path:
        return

    # Считаем количество серий
    series_count = len([
        f for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    ])

    # Спрашиваем, запускать ли
    launch = messagebox.askyesno(
        "🎬 Плейлист готов!",
        f"Создан playlist.m3u\nВсего серий: {series_count}\n\nЗапустить в VLC сейчас?",
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
