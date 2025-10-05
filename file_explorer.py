from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree, Header, Footer, Static
from textual.containers import Container, Horizontal
from textual import events
import os
import shutil

class FileInfo(Static):
    """Widget to display information about selected file"""
    
    def __init__(self):
        super().__init__()
        self.selected_path = None

    def update_info(self, path: str) -> None:
        """Update the file information display"""
        self.selected_path = path
        if path and os.path.exists(path):
            stats = os.stat(path)
            name = os.path.basename(path) or path
            info = f"""Selected: {name}
Type: {'Directory' if os.path.isdir(path) else 'File'}
Size: {stats.st_size:,} bytes
Path: {path}

Operations:
- F5: Copy
- F6: Move
- F7: Create Directory
- F8: Delete
- F9: Create File"""
            self.update(info)
        else:
            self.update("No file selected")

    def clear_selection(self) -> None:
        """Clear the current selection"""
        self.selected_path = None
        self.update("No file selected")


class FileExplorerApp(App):
    """A terminal file explorer with file operations"""
    
    CSS = """
    DirectoryTree {
        width: 60%;
        border: solid green;
    }
    
    FileInfo {
        width: 40%;
        height: 100%;
        border: solid blue;
        background: $surface;
        padding: 1 2;
    }
    
    Container {
        height: 100%;
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container():
            with Horizontal():
                yield DirectoryTree(".", id="tree")
                yield FileInfo()
        yield Footer()

    def on_mount(self) -> None:
        """Event handler called when app is loaded."""
        self.title = "Terminal File Explorer"
        tree = self.query_one(DirectoryTree)
        tree.focus()

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Event handler called when a directory is selected."""
        info_widget = self.query_one(FileInfo)
        info_widget.update_info(event.path)

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Event handler called when user selects a file."""
        info_widget = self.query_one(FileInfo)
        info_widget.update_info(event.path)

    def handle_file_operation(self, operation: str) -> None:
        """Handle file operations"""
        info_widget = self.query_one(FileInfo)
        if not info_widget.selected_path:
            self.notify("No file selected!")
            return

        try:
            if operation == "delete":
                if os.path.isdir(info_widget.selected_path):
                    shutil.rmtree(info_widget.selected_path)
                else:
                    os.remove(info_widget.selected_path)
                self.notify("Item deleted successfully!")
            elif operation in ["copy", "move"]:
                new_path = f"{info_widget.selected_path}_{'copy' if operation == 'copy' else 'moved'}"
                if operation == "copy":
                    if os.path.isdir(info_widget.selected_path):
                        shutil.copytree(info_widget.selected_path, new_path)
                    else:
                        shutil.copy2(info_widget.selected_path, new_path)
                else:  # move
                    shutil.move(info_widget.selected_path, new_path)

                if operation == "copy":
                    self.notify(f"Item copied successfully!")
                else:
                    self.notify(f"Item moved successfully!")

            # Refresh the directory tree
            tree = self.query_one(DirectoryTree)
            tree.reload()
            info_widget.clear_selection()
        except Exception as e:
            self.notify(f"Error: {str(e)}", severity="error")
            info_widget.clear_selection()

    def on_key(self, event: events.Key) -> None:
        """Handle key events for file operations"""
        if event.key == "f5":
            self.handle_file_operation("copy")
        elif event.key == "f6":
            self.handle_file_operation("move")
        elif event.key == "f7":
            # Create directory
            try:
                new_dir = os.path.join(os.getcwd(), "new_directory")
                os.makedirs(new_dir)
                self.notify("Directory created!")
                self.query_one(DirectoryTree).reload()
            except Exception as e:
                self.notify(f"Error: {str(e)}", severity="error")
        elif event.key == "f8":
            self.handle_file_operation("delete")
        elif event.key == "f9":
            # Create file
            try:
                new_file = os.path.join(os.getcwd(), "new_file.txt")
                with open(new_file, 'w') as f:
                    f.write("")
                self.notify("File created!")
                self.query_one(DirectoryTree).reload()
            except Exception as e:
                self.notify(f"Error: {str(e)}", severity="error")

if __name__ == "__main__":
    app = FileExplorerApp()
    app.run()
