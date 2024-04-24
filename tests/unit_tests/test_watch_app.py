import pytest
from unittest.mock import MagicMock, mock_open, patch
from watch_app import WatchApp, Watch

@pytest.fixture
def app(monkeypatch):
    # Mock filesystem operations to prevent any real file operations
    monkeypatch.setattr('os.makedirs', MagicMock())
    monkeypatch.setattr('os.path.exists', MagicMock(return_value=True))
    monkeypatch.setattr('os.listdir', MagicMock(return_value=[]))  # Assuming no files initially
    monkeypatch.setattr('os.path.getsize', MagicMock(return_value=1))  # Assume file exists with size

    # Mock 'open' to simulate file read/write operations
    with patch('builtins.open', mock_open(read_data='[]')) as mock_file:
        app_instance = WatchApp(
            watch_dir='tests/data/watches',
            watch_file='tests/data/watchlist.txt',
            form_dir='tests/data/forms',
            choosen_dir='tests/data/choosen'
        )
        # Prevent any actual file writing or reading
        app_instance.load_week_watches = MagicMock()
        app_instance.load_watches = MagicMock()
        return app_instance

def test_watch_initialization():
    """ Test if the Watch object initializes correctly. """
    watch = Watch("TestWatch", "tests/data/Watch.png")
    assert watch.name == "TestWatch"
    assert watch.image_path == "tests/data/Watch.png"

def test_watchapp_initialization(app):
    """ Test if the WatchApp initializes with correct properties. """
    assert app.watch_dir == 'tests/data/watches'
    assert app.watch_file == 'tests/data/watchlist.txt'
    assert app.form_dir == 'tests/data/forms'
    assert app.choosen_dir == 'tests/data/choosen'

def test_add_watch_directly(app):
    """ Test adding a watch directly to the app without user interaction. """
    watch = Watch("TestWatch", "tests/data/Watch.png")
    app.watches.append(watch.__dict__)
    assert len(app.watches) == 1
    assert app.watches[0]['name'] == "TestWatch"
    assert app.watches[0]['image_path'] == "tests/data/Watch.png"

def test_remove_watch_directly(app):
    """ Test removing a watch directly from the app. """
    watch = Watch("TestWatch", "tests/data/Watch.png")
    app.watches.append(watch.__dict__)
    app.watches = [w for w in app.watches if w['name'] != "TestWatch"]
    assert len(app.watches) == 0

def test_modify_watch_directly(app):
    """ Test modifying a watch directly in the app. """
    watch = Watch("TestWatch", "tests/data/Watch.png")
    app.watches.append(watch.__dict__)
    # Assume we modify the first watch in the list
    app.watches[0]['name'] = "ModifiedWatch"
    app.watches[0]['image_path'] = "tests/data/ModifiedWatch.png"
    assert app.watches[0]['name'] == "ModifiedWatch"
    assert app.watches[0]['image_path'] == "tests/data/ModifiedWatch.png"
