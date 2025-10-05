from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree, Header, Footer, Static
from textual.containers import Container, Horizontal
from textual import events
import os

class FileInfo(Static):
    """Widget to display information about selected file"""
    
    def __init__(self):
        super().__init__()
        self.selected_path = None

    def update_info(self, path: str) -> None:
        """Update the file information display"""
        if path and os.path.exists(path):
            stats = os.stat(path)
            info = f"""Selected: {os.path.basename(path)}
Type: {'Directory' if os.path.isdir(path) else 'File'}
Size: {stats.st_size:,} bytes
Path: {path}"""
            self.update(info)
        else:
            self.update("No file selected")

class FileExplorerApp(App):
    """A simple terminal file explorer"""
    
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
        # Get the tree widget and set focus
        tree = self.query_one(DirectoryTree)
        tree.focus()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Event handler called when user selects a file."""
        info_widget = self.query_one(FileInfo)
        info_widget.update_info(event.path)

if __name__ == "__main__":
    app = FileExplorerApp()
    app.run()
