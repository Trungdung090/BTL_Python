import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import sys
from pathlib import Path

class FolderManagerGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.current_folder = ""
        self.create_widgets()
        self.setup_styles()

    def setup_window(self):
        """Thiết lập cửa sổ chính"""
        self.root.title("📁 Trình Quản Lý Thư Mục")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)

        # Cấu hình grid weight để responsive
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Màu nền hiện đại
        self.root.configure(bg='#f0f0f0')

    def setup_styles(self):
        style = ttk.Style()
        # Style cho buttons
        style.configure("Modern.TButton",
                        font=('Segoe UI', 10, 'bold'),
                        padding=(15, 8))
        # Style cho frame
        style.configure("Card.TFrame",
                        relief="solid",
                        borderwidth=1,
                        background='white')
        # Style cho treeview
        style.configure("Modern.Treeview",
                        font=('Segoe UI', 9),
                        rowheight=25)
        style.configure("Modern.Treeview.Heading",
                        font=('Segoe UI', 10, 'bold'))

    def create_widgets(self):
        """Tạo các widget giao diện"""
        # Header Frame
        header_frame = ttk.Frame(self.root, style="Card.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(header_frame,
                                text="📁 TRÌNH QUẢN LÝ THƯ MỤC",
                                font=('Segoe UI', 16, 'bold'),
                                foreground='#2c3e50')
        title_label.grid(row=0, column=0, columnspan=3, pady=15)

        # Button chọn thư mục
        self.select_btn = ttk.Button(header_frame,
                                     text="📂 Chọn Thư Mục",
                                     command=self.select_folder,
                                     style="Modern.TButton")
        self.select_btn.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Label hiển thị đường dẫn
        self.path_label = ttk.Label(header_frame,
                                    text="Chưa chọn thư mục...",
                                    font=('Segoe UI', 9),
                                    foreground='#7f8c8d')
        self.path_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Button refresh
        self.refresh_btn = ttk.Button(header_frame,
                                      text="🔄 Làm Mới",
                                      command=self.refresh_files,
                                      style="Modern.TButton",
                                      state="disabled")
        self.refresh_btn.grid(row=1, column=2, padx=10, pady=10, sticky="e")

        # Main content frame
        main_frame = ttk.Frame(self.root, style="Card.TFrame")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Treeview với scrollbar
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Treeview
        columns = ("name", "type", "size", "modified")
        self.tree = ttk.Treeview(tree_frame,
                                 columns=columns,
                                 show="tree headings",
                                 style="Modern.Treeview")

        # Cấu hình columns
        self.tree.heading("#0", text="📄 Tên File", anchor="w")
        self.tree.heading("name", text="Tên Đầy Đủ", anchor="w")
        self.tree.heading("type", text="Loại", anchor="center")
        self.tree.heading("size", text="Kích Thước", anchor="center")
        self.tree.heading("modified", text="Ngày Sửa Đổi", anchor="center")

        # Cấu hình width columns
        self.tree.column("#0", width=200, minwidth=150)
        self.tree.column("name", width=250, minwidth=200)
        self.tree.column("type", width=80, minwidth=60)
        self.tree.column("size", width=100, minwidth=80)
        self.tree.column("modified", width=150, minwidth=120)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout cho tree và scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Bind events
        self.tree.bind("<Double-1>", self.open_file)
        self.tree.bind("<Return>", self.open_file)

        # Footer frame
        footer_frame = ttk.Frame(self.root)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        footer_frame.grid_columnconfigure(0, weight=1)

        # Buttons frame
        buttons_frame = ttk.Frame(footer_frame)
        buttons_frame.grid(row=0, column=0, sticky="e")

        # Button mở file
        self.open_btn = ttk.Button(buttons_frame,
                                   text="📖 Mở File",
                                   command=self.open_selected_file,
                                   style="Modern.TButton",
                                   state="disabled")
        self.open_btn.grid(row=0, column=0, padx=5)

        # Button xóa danh sách
        self.clear_btn = ttk.Button(buttons_frame,
                                    text="🗑️ Xóa Danh Sách",
                                    command=self.clear_list,
                                    style="Modern.TButton")
        self.clear_btn.grid(row=0, column=1, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        status_bar = ttk.Label(footer_frame,
                               textvariable=self.status_var,
                               font=('Segoe UI', 8),
                               foreground='#7f8c8d')
        status_bar.grid(row=1, column=0, sticky="w", pady=(5, 0))

    def select_folder(self):
        """Chọn thư mục và hiển thị files"""
        try:
            folder_path = filedialog.askdirectory(
                title="Chọn thư mục cần quản lý",
                initialdir=os.path.expanduser("~")
            )
            if folder_path:
                self.current_folder = folder_path
                self.path_label.config(text=f"📁 {folder_path}")
                self.show_files()
                self.refresh_btn.config(state="normal")
                self.status_var.set(f"Đã chọn thư mục: {os.path.basename(folder_path)}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể chọn thư mục:\n{str(e)}")
            self.status_var.set("Lỗi khi chọn thư mục")

    def show_files(self):
        """Scan thư mục và hiển thị files trong Treeview"""
        if not self.current_folder:
            return
        try:
            # Xóa dữ liệu cũ
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Kiểm tra đường dẫn tồn tại
            if not os.path.exists(self.current_folder):
                raise FileNotFoundError(f"Không tìm thấy đường dẫn: {self.current_folder}")

            files = []
            supported_types = {'.txt', '.py', '.jpg', '.jpeg', '.png', '.gif', '.bmp',
                               '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                               '.mp3', '.mp4', '.avi', '.mov', '.zip', '.rar', '.exe'}

            # Scan files
            for filename in os.listdir(self.current_folder):
                filepath = os.path.join(self.current_folder, filename)
                if os.path.isfile(filepath):
                    file_ext = Path(filename).suffix.lower()
                    # Lấy thông tin file
                    try:
                        stat_info = os.stat(filepath)
                        file_size = self.format_file_size(stat_info.st_size)
                        modified_time = self.format_date(stat_info.st_mtime)

                        # Icon theo loại file
                        icon = self.get_file_icon(file_ext)

                        files.append({
                            'name': filename,
                            'path': filepath,
                            'ext': file_ext,
                            'size': file_size,
                            'modified': modified_time,
                            'icon': icon
                        })
                    except OSError:
                        continue
            # Sắp xếp files theo tên
            files.sort(key=lambda x: x['name'].lower())

            # Nhóm theo loại file
            file_groups = {}
            for file_info in files:
                ext = file_info['ext'] or 'Không có phần mở rộng'
                if ext not in file_groups:
                    file_groups[ext] = []
                file_groups[ext].append(file_info)

            # Thêm vào treeview theo nhóm
            total_files = 0
            for ext, group_files in sorted(file_groups.items()):
                # Tạo node nhóm
                group_icon = "📁" if ext == 'Không có phần mở rộng' else self.get_file_icon(ext)
                group_name = f"{group_icon} {ext.upper()} Files ({len(group_files)})"

                group_node = self.tree.insert("", "end",
                                              text=group_name,
                                              values=("", "Thư mục", f"{len(group_files)} files", ""),
                                              tags=("group",))
                # Thêm files vào nhóm
                for file_info in group_files:
                    self.tree.insert(group_node, "end",
                                     text=f"{file_info['icon']} {file_info['name']}",
                                     values=(file_info['name'],
                                             file_info['ext'] or 'N/A',
                                             file_info['size'],
                                             file_info['modified']),
                                     tags=("file",))
                    total_files += 1

                # Mở rộng nhóm
                self.tree.item(group_node, open=True)

            # Cấu hình tags
            self.tree.tag_configure("group", background="#e8f4f8", font=('Segoe UI', 9, 'bold'))
            self.tree.tag_configure("file", background="white")

            self.status_var.set(f"Đã tải {total_files} files từ {len(file_groups)} loại khác nhau")
            self.open_btn.config(state="normal" if total_files > 0 else "disabled")
        except FileNotFoundError as e:
            messagebox.showerror("Lỗi đường dẫn", str(e))
            self.status_var.set("Không tìm thấy đường dẫn")
        except PermissionError:
            messagebox.showerror("Lỗi quyền truy cập",
                                 "Không có quyền truy cập vào thư mục này!")
            self.status_var.set("Lỗi quyền truy cập")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra:\n{str(e)}")
            self.status_var.set("Có lỗi xảy ra")

    def get_file_icon(self, ext):
        """Trả về icon phù hợp cho loại file"""
        icons = {
            '.txt': '📄', '.py': '🐍', '.jpg': '🖼️', '.jpeg': '🖼️',
            '.png': '🖼️', '.gif': '🖼️', '.bmp': '🖼️',
            '.pdf': '📕', '.doc': '📘', '.docx': '📘',
            '.xls': '📊', '.xlsx': '📊', '.ppt': '📋', '.pptx': '📋',
            '.mp3': '🎵', '.mp4': '🎬', '.avi': '🎬', '.mov': '🎬',
            '.zip': '📦', '.rar': '📦', '.exe': '⚙️'
        }
        return icons.get(ext.lower(), '📄')

    def format_file_size(self, size_bytes):
        """Định dạng kích thước file"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

    def format_date(self, timestamp):
        """Định dạng ngày giờ"""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%d/%m/%Y %H:%M")

    def open_file(self, event=None):
        """Mở file khi double-click"""
        selection = self.tree.selection()
        if not selection:
            return
        item = selection[0]
        tags = self.tree.item(item, "tags")

        # Chỉ mở file, không mở group
        if "file" in tags:
            self.open_selected_file()

    def open_selected_file(self):
        """Mở file được chọn bằng chương trình mặc định"""
        try:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn một file để mở!")
                return
            item = selection[0]
            tags = self.tree.item(item, "tags")
            if "file" not in tags:
                messagebox.showinfo("Thông báo", "Vui lòng chọn một file, không phải thư mục!")
                return

            # Lấy tên file từ values
            file_name = self.tree.item(item, "values")[0]
            if not file_name:
                return
            file_path = os.path.join(self.current_folder, file_name)
            if not os.path.exists(file_path):
                messagebox.showerror("Lỗi", f"File không tồn tại:\n{file_path}")
                return

            # Mở file bằng chương trình mặc định
            if sys.platform.startswith('win'):
                os.startfile(file_path)
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
            self.status_var.set(f"Đã mở file: {file_name}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở file:\n{str(e)}")
            self.status_var.set("Lỗi khi mở file")

    def refresh_files(self):
        if self.current_folder:
            self.show_files()
            self.status_var.set("Đã làm mới danh sách files")

    def clear_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.current_folder = ""
        self.path_label.config(text="Chưa chọn thư mục...")
        self.refresh_btn.config(state="disabled")
        self.open_btn.config(state="disabled")
        self.status_var.set("Đã xóa danh sách")

def main():
    root = tk.Tk()
    app = FolderManagerGUI(root)

    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    root.mainloop()

if __name__ == "__main__":
    main()