import pytest
from unittest.mock import patch, MagicMock
from ra_aid.tools.shell import run_shell_command
from ra_aid.tools.memory import _global_memory

@pytest.fixture
def mock_console():
    with patch('ra_aid.tools.shell.console') as mock:
        yield mock

@pytest.fixture
def mock_confirm():
    with patch('ra_aid.tools.shell.Confirm') as mock:
        yield mock

@pytest.fixture
def mock_run_interactive():
    with patch('ra_aid.tools.shell.run_interactive_command') as mock:
        mock.return_value = (b"test output", 0)
        yield mock

def test_shell_command_cowboy_mode(mock_console, mock_confirm, mock_run_interactive):
    """Test shell command execution in cowboy mode (no approval)"""
    _global_memory['config'] = {'cowboy_mode': True}
    
    result = run_shell_command("echo test")
    
    assert result['success'] is True
    assert result['return_code'] == 0
    assert "test output" in result['output']
    mock_confirm.ask.assert_not_called()

def test_shell_command_interactive_approved(mock_console, mock_confirm, mock_run_interactive):
    """Test shell command execution with interactive approval"""
    _global_memory['config'] = {'cowboy_mode': False}
    mock_confirm.ask.return_value = True
    
    result = run_shell_command("echo test")
    
    assert result['success'] is True
    assert result['return_code'] == 0
    assert "test output" in result['output']
    mock_confirm.ask.assert_called_once()

def test_shell_command_interactive_rejected(mock_console, mock_confirm, mock_run_interactive):
    """Test shell command rejection in interactive mode"""
    _global_memory['config'] = {'cowboy_mode': False}
    mock_confirm.ask.return_value = False
    
    result = run_shell_command("echo test")
    
    assert result['success'] is False
    assert result['return_code'] == 1
    assert "cancelled by user" in result['output']
    mock_confirm.ask.assert_called_once()
    mock_run_interactive.assert_not_called()

def test_shell_command_execution_error(mock_console, mock_confirm, mock_run_interactive):
    """Test handling of shell command execution errors"""
    _global_memory['config'] = {'cowboy_mode': True}
    mock_run_interactive.side_effect = Exception("Command failed")
    
    result = run_shell_command("invalid command")
    
    assert result['success'] is False
    assert result['return_code'] == 1
    assert "Command failed" in result['output']