import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
OUTPUT_DIR = Path("D:/HowTo/backend/sample_data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1280
HEIGHT = 720
FPS = 15

def get_font(size=18, bold=False):
    try:
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except Exception:
        return ImageFont.load_default()

def draw_cursor(draw, x, y):
    # Draw a clean arrow cursor
    points = [
        (x, y),
        (x, y + 20),
        (x + 5, y + 16),
        (x + 12, y + 24),
        (x + 16, y + 20),
        (x + 9, y + 14),
        (x + 16, y + 14)
    ]
    draw.polygon(points, fill="#000000", outline="#ffffff")

def draw_base_dashboard(draw, active_filter=None, drawer_open=False):
    # Background
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill="#f8fafc")
    
    # Top Navbar
    draw.rectangle([0, 0, WIDTH, 64], fill="#1e293b")
    font_bold = get_font(20, bold=True)
    font_nav = get_font(14)
    draw.text((32, 20), "ACME STORE ADMIN", fill="#38bdf8", font=font_bold)
    draw.text((260, 24), "Dashboard", fill="#94a3b8", font=font_nav)
    draw.text((360, 24), "Orders (Active)", fill="#ffffff", font=font_nav)
    draw.text((490, 24), "Customers", fill="#94a3b8", font=font_nav)
    draw.text((600, 24), "Settings", fill="#94a3b8", font=font_nav)

    # Sub-header / Actions
    draw.rectangle([0, 64, WIDTH, 128], fill="#ffffff", outline="#e2e8f0")
    font_h1 = get_font(22, bold=True)
    draw.text((32, 82), "Orders Management", fill="#0f172a", font=font_h1)

    # Filter by Date Button
    btn_color = "#3b82f6" if active_filter else "#ffffff"
    text_color = "#ffffff" if active_filter else "#334155"
    border_color = "#3b82f6" if active_filter else "#cbd5e1"
    draw.rectangle([280, 80, 430, 116], fill=btn_color, outline=border_color, width=1)
    filter_label = f"Filter: {active_filter}" if active_filter else "Filter by Date ▾"
    draw.text((292, 89), filter_label, fill=text_color, font=get_font(13, bold=True))

    # Drawer button (silent action trigger)
    draw.rectangle([450, 80, 580, 116], fill="#f1f5f9", outline="#cbd5e1", width=1)
    draw.text((462, 89), "Filter Drawer ⊞", fill="#334155", font=get_font(13))

    # Export Button
    draw.rectangle([WIDTH - 180, 80, WIDTH - 32, 116], fill="#2563eb")
    draw.text((WIDTH - 150, 89), "Export Orders ⤓", fill="#ffffff", font=get_font(14, bold=True))

    # Orders Table
    table_x, table_y = 32, 148
    draw.rectangle([table_x, table_y, WIDTH - (340 if drawer_open else 32), 580], fill="#ffffff", outline="#e2e8f0")
    
    # Table Header
    draw.rectangle([table_x, table_y, WIDTH - (340 if drawer_open else 32), table_y + 40], fill="#f1f5f9")
    headers = ["ORDER ID", "CUSTOMER", "STATUS", "DATE", "TOTAL", "ITEMS"]
    offsets = [20, 140, 320, 460, 600, 720]
    font_th = get_font(12, bold=True)
    for off, h in zip(offsets, headers):
        if table_x + off < WIDTH - (360 if drawer_open else 50):
            draw.text((table_x + off, table_y + 12), h, fill="#64748b", font=font_th)

    # Sample rows
    orders = [
        ("#ORD-1049", "Alice Johnson", "DELIVERED", "2026-09-14", "$124.50", "3"),
        ("#ORD-1048", "Bob Smith", "PROCESSING", "2026-09-14", "$48.00", "1"),
        ("#ORD-1047", "Charlie Brown", "DELIVERED", "2026-09-13", "$312.80", "5"),
        ("#ORD-1046", "Diana Prince", "DELIVERED", "2026-09-12", "$89.90", "2"),
        ("#ORD-1045", "Evan Wright", "CANCELLED", "2026-09-11", "$15.00", "1"),
        ("#ORD-1044", "Fiona Gallagher", "DELIVERED", "2026-09-10", "$210.00", "4"),
    ]
    font_td = get_font(13)
    for idx, ord_data in enumerate(orders):
        row_y = table_y + 40 + (idx * 44)
        draw.line([(table_x, row_y), (WIDTH - (340 if drawer_open else 32), row_y)], fill="#f1f5f9", width=1)
        for off, val in zip(offsets, ord_data):
            if table_x + off < WIDTH - (360 if drawer_open else 50):
                c = "#16a34a" if val == "DELIVERED" else ("#ea580c" if val == "PROCESSING" else "#334155")
                draw.text((table_x + off, row_y + 12), val, fill=c, font=font_td)

    # Filter Drawer if open
    if drawer_open:
        drawer_x = WIDTH - 310
        draw.rectangle([drawer_x, 64, WIDTH, HEIGHT], fill="#ffffff", outline="#94a3b8")
        draw.rectangle([drawer_x, 64, WIDTH, 120], fill="#f8fafc", outline="#e2e8f0")
        draw.text((drawer_x + 20, 82), "Advanced Filters", fill="#0f172a", font=get_font(16, bold=True))
        draw.text((drawer_x + 20, 140), "Export Format:", fill="#334155", font=get_font(14, bold=True))

def render_video(frames_generator, output_file, total_frames):
    print(f"Generating {output_file.name} ({total_frames} frames)...")
    cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "ultrafast",
        str(output_file)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for img in frames_generator():
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"Done: {output_file.name}")

def generate_normal_demo():
    output_path = OUTPUT_DIR / "test_normal.mp4"
    duration_sec = 16
    total_frames = duration_sec * FPS

    def frames():
        for f in range(total_frames):
            sec = f / FPS
            img = Image.new("RGB", (WIDTH, HEIGHT), color="#f8fafc")
            draw = ImageDraw.Draw(img)

            # State logic
            active_filter = "Past 30 Days" if sec >= 6.0 else None
            draw_base_dashboard(draw, active_filter=active_filter)

            cursor_x, cursor_y = 100, 300
            # Phase 1: 0s - 3s: Cursor moves to Filter by Date button
            if sec < 3.0:
                p = sec / 3.0
                cursor_x = int(100 + p * (350 - 100))
                cursor_y = int(300 + p * (98 - 300))
            # Phase 2: 3s - 6s: Dropdown open, cursor clicks Past 30 Days
            elif sec < 6.0:
                # Draw Dropdown
                draw.rectangle([280, 120, 460, 240], fill="#ffffff", outline="#94a3b8", width=2)
                draw.rectangle([280, 155, 460, 190], fill="#eff6ff" if sec >= 4.5 else "#ffffff")
                draw.text((295, 130), "Today", fill="#334155", font=get_font(13))
                draw.text((295, 165), "✓ Past 30 Days", fill="#1d4ed8" if sec >= 4.5 else "#334155", font=get_font(13, bold=True))
                draw.text((295, 200), "All Time", fill="#334155", font=get_font(13))
                p = (sec - 3.0) / 3.0
                cursor_x = int(350 + p * (360 - 350))
                cursor_y = int(98 + p * (172 - 98))
            # Phase 3: 6s - 10s: Cursor moves to Export button
            elif sec < 10.0:
                p = (sec - 6.0) / 4.0
                cursor_x = int(360 + p * (WIDTH - 100 - 360))
                cursor_y = int(172 + p * (98 - 172))
            # Phase 4: 10s - 14s: Export modal open, CSV selected
            elif sec < 14.0:
                # Draw Modal
                draw.rectangle([0, 0, WIDTH, HEIGHT], fill="#00000033")
                draw.rectangle([WIDTH//2 - 200, HEIGHT//2 - 130, WIDTH//2 + 200, HEIGHT//2 + 130], fill="#ffffff", outline="#64748b", width=2)
                draw.text((WIDTH//2 - 170, HEIGHT//2 - 100), "Export Filtered Orders", fill="#0f172a", font=get_font(18, bold=True))
                draw.text((WIDTH//2 - 170, HEIGHT//2 - 60), "Choose format:", fill="#475569", font=get_font(14))
                # Radios
                draw.ellipse([WIDTH//2 - 170, HEIGHT//2 - 25, WIDTH//2 - 154, HEIGHT//2 - 9], fill="#2563eb", outline="#2563eb")
                draw.ellipse([WIDTH//2 - 165, HEIGHT//2 - 20, WIDTH//2 - 159, HEIGHT//2 - 14], fill="#ffffff")
                draw.text((WIDTH//2 - 140, HEIGHT//2 - 25), "CSV (Spreadsheet)", fill="#0f172a", font=get_font(14, bold=True))
                # Button
                draw.rectangle([WIDTH//2 + 50, HEIGHT//2 + 70, WIDTH//2 + 170, HEIGHT//2 + 105], fill="#2563eb")
                draw.text((WIDTH//2 + 65, HEIGHT//2 + 78), "Download", fill="#ffffff", font=get_font(14, bold=True))
                p = (sec - 10.0) / 4.0
                cursor_x = int(WIDTH - 100 + p * (WIDTH//2 + 110 - (WIDTH - 100)))
                cursor_y = int(98 + p * (HEIGHT//2 + 88 - 98))
            # Phase 5: 14s - 16s: Success state with download banner
            else:
                cursor_x = WIDTH//2 + 110
                cursor_y = HEIGHT//2 + 88
                # Download shelf
                draw.rectangle([0, HEIGHT - 54, WIDTH, HEIGHT], fill="#1e293b")
                draw.rectangle([40, HEIGHT - 44, 340, HEIGHT - 10], fill="#334155", outline="#475569")
                draw.text((55, HEIGHT - 36), "📄 orders_export_2026.csv (14.2 KB) ✓", fill="#4ade80", font=get_font(13, bold=True))

            draw_cursor(draw, cursor_x, cursor_y)
            yield img

    render_video(frames, output_path, total_frames)

def generate_corrected_demo():
    output_path = OUTPUT_DIR / "test_corrected.mp4"
    duration_sec = 18
    total_frames = duration_sec * FPS

    def frames():
        for f in range(total_frames):
            sec = f / FPS
            img = Image.new("RGB", (WIDTH, HEIGHT), color="#f8fafc")
            draw = ImageDraw.Draw(img)

            drawer_open = sec >= 4.0
            draw_base_dashboard(draw, active_filter=None, drawer_open=drawer_open)

            cursor_x, cursor_y = 100, 300
            # Phase 1: 0s - 4s: SILENT ACTION: Mouse moves to Filter Drawer and opens it
            if sec < 4.0:
                p = sec / 4.0
                cursor_x = int(100 + p * (510 - 100))
                cursor_y = int(300 + p * (98 - 300))
            # Phase 2: 4s - 8s: In Drawer: Mistakenly clicks JSON radio
            elif sec < 8.0:
                drawer_x = WIDTH - 310
                # JSON Radio (mistakenly selected)
                is_json = sec >= 6.5
                draw.ellipse([drawer_x + 24, 180, drawer_x + 40, 196], fill="#2563eb" if is_json else "#ffffff", outline="#2563eb")
                draw.text((drawer_x + 50, 180), "JSON format", fill="#0f172a", font=get_font(13))
                # CSV Radio
                draw.ellipse([drawer_x + 24, 220, drawer_x + 40, 236], fill="#ffffff", outline="#94a3b8")
                draw.text((drawer_x + 50, 220), "CSV format", fill="#0f172a", font=get_font(13))
                p = (sec - 4.0) / 4.0
                cursor_x = int(510 + p * (drawer_x + 32 - 510))
                cursor_y = int(98 + p * (188 - 98))
            # Phase 3: 8s - 12s: CORRECTION: notices mistake, moves cursor to CSV and clicks CSV!
            elif sec < 12.0:
                drawer_x = WIDTH - 310
                is_csv = sec >= 10.0
                # JSON Radio (unselected)
                draw.ellipse([drawer_x + 24, 180, drawer_x + 40, 196], fill="#ffffff", outline="#94a3b8")
                draw.text((drawer_x + 50, 180), "JSON format", fill="#64748b", font=get_font(13))
                # CSV Radio (selected)
                draw.ellipse([drawer_x + 24, 220, drawer_x + 40, 236], fill="#2563eb" if is_csv else "#ffffff", outline="#2563eb")
                draw.text((drawer_x + 50, 220), "CSV format ✓", fill="#2563eb" if is_csv else "#0f172a", font=get_font(13, bold=is_csv))
                p = (sec - 8.0) / 4.0
                cursor_x = int(drawer_x + 32 + p * 0)
                cursor_y = int(188 + p * (228 - 188))
            # Phase 4: 12s - 15s: Clicks Export Now button in drawer
            elif sec < 15.0:
                drawer_x = WIDTH - 310
                draw.ellipse([drawer_x + 24, 180, drawer_x + 40, 196], fill="#ffffff", outline="#94a3b8")
                draw.text((drawer_x + 50, 180), "JSON format", fill="#64748b", font=get_font(13))
                draw.ellipse([drawer_x + 24, 220, drawer_x + 40, 236], fill="#2563eb", outline="#2563eb")
                draw.text((drawer_x + 50, 220), "CSV format ✓", fill="#2563eb", font=get_font(13, bold=True))
                # Export Button
                draw.rectangle([drawer_x + 24, 280, drawer_x + 260, 320], fill="#2563eb")
                draw.text((drawer_x + 80, 292), "Export Now ⤓", fill="#ffffff", font=get_font(14, bold=True))
                p = (sec - 12.0) / 3.0
                cursor_x = int(drawer_x + 32 + p * (drawer_x + 140 - (drawer_x + 32)))
                cursor_y = int(228 + p * (300 - 228))
            # Phase 5: 15s - 18s: Success state with download
            else:
                cursor_x = WIDTH - 170
                cursor_y = 300
                draw.rectangle([0, HEIGHT - 54, WIDTH, HEIGHT], fill="#1e293b")
                draw.rectangle([40, HEIGHT - 44, 360, HEIGHT - 10], fill="#334155", outline="#475569")
                draw.text((55, HEIGHT - 36), "📄 orders_q1_2026.csv (28.4 KB) ✓", fill="#4ade80", font=get_font(13, bold=True))

            draw_cursor(draw, cursor_x, cursor_y)
            yield img

    render_video(frames, output_path, total_frames)

def generate_incomplete_demo():
    output_path = OUTPUT_DIR / "test_incomplete.mp4"
    duration_sec = 8
    total_frames = duration_sec * FPS

    def frames():
        for f in range(total_frames):
            sec = f / FPS
            img = Image.new("RGB", (WIDTH, HEIGHT), color="#f8fafc")
            draw = ImageDraw.Draw(img)

            # 0s - 3s: Normal dashboard view
            if sec < 3.5:
                draw_base_dashboard(draw)
                cursor_x = int(100 + (sec / 3.5) * 150)
                cursor_y = 250
                draw_cursor(draw, cursor_x, cursor_y)
            # 3.5s - 8s: ABRUPT JUMP CUT! Directly to black screen with indefinite spinner, then cut off
            else:
                draw.rectangle([0, 0, WIDTH, HEIGHT], fill="#0f172a")
                draw.text((WIDTH//2 - 180, HEIGHT//2 - 40), "Generating Export...", fill="#f8fafc", font=get_font(20, bold=True))
                draw.text((WIDTH//2 - 260, HEIGHT//2 + 10), "[Video abruptly cuts off before configuration or download]", fill="#ef4444", font=get_font(14))

            yield img

    render_video(frames, output_path, total_frames)

if __name__ == "__main__":
    generate_normal_demo()
    generate_corrected_demo()
    generate_incomplete_demo()
    print("All 3 sample demonstration videos generated successfully!")
