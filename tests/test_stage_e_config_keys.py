"""data.config.require_databento_key selects the Databento key by account (Stage E.11, V19).

acct-1 reads DATABENTO_API_KEY1 and acct-2 reads DATABENTO_API_KEY2; the default is
ACTIVE_ACCOUNT. Every test uses obviously fake values and a .env file under tmp_path, deletes the
real variable names from the environment first, and never reads the repo's .env or prints a key.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from data import config
from data.config import (
    ACCOUNT_1_ID,
    ACCOUNT_2_ID,
    ACCOUNTS,
    DATABENTO_KEY_ENV_BY_ACCOUNT,
    MissingSecretError,
    require_databento_key,
)

KEY1 = "DATABENTO_API_KEY1"
KEY2 = "DATABENTO_API_KEY2"
LEGACY = "DATABENTO_API_KEY"
FAKE_1 = "fake-key-1-not-real"
FAKE_2 = "fake-key-2-not-real"
FAKE_FILE_1 = "fake-file-key-1-not-real"
FAKE_FILE_2 = "fake-file-key-2-not-real"
FAKE_LEGACY = "fake-legacy-key-not-real"


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """No real key variable from the developer's shell reaches a test."""
    for name in (KEY1, KEY2, LEGACY):
        monkeypatch.delenv(name, raising=False)


def _env_file(tmp_path: Path, lines: list[str] | None = None) -> Path:
    path = tmp_path / ".env"
    if lines is not None:
        path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    return path


def _missing_message(env_file: Path, account: str | None) -> str:
    with pytest.raises(MissingSecretError) as info:
        require_databento_key(env_file=env_file, account=account)
    return str(info.value)


# ------------------------------------------------------------------ the mapping ----

def test_each_account_maps_to_its_numbered_variable() -> None:
    # Arrange / Act
    mapping = dict(DATABENTO_KEY_ENV_BY_ACCOUNT)

    # Assert
    assert mapping == {ACCOUNT_1_ID: KEY1, ACCOUNT_2_ID: KEY2}


def test_every_registered_account_has_a_key_variable() -> None:
    # Arrange / Act / Assert
    assert set(DATABENTO_KEY_ENV_BY_ACCOUNT) == set(ACCOUNTS)


def test_the_mapping_is_read_only() -> None:
    # Arrange / Act / Assert
    with pytest.raises(TypeError):
        DATABENTO_KEY_ENV_BY_ACCOUNT[ACCOUNT_1_ID] = LEGACY  # type: ignore[index]


# ------------------------------------------------------------- selection by account ----

def test_acct_1_reads_key1_from_the_environment(tmp_path: Path,
                                                monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv(KEY1, FAKE_1)
    monkeypatch.setenv(KEY2, FAKE_2)

    # Act
    key = require_databento_key(env_file=_env_file(tmp_path), account=ACCOUNT_1_ID)

    # Assert
    assert key == FAKE_1


def test_acct_2_reads_key2_from_the_environment(tmp_path: Path,
                                                monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv(KEY1, FAKE_1)
    monkeypatch.setenv(KEY2, FAKE_2)

    # Act
    key = require_databento_key(env_file=_env_file(tmp_path), account=ACCOUNT_2_ID)

    # Assert
    assert key == FAKE_2


def test_acct_1_and_acct_2_read_their_own_lines_of_the_env_file(tmp_path: Path) -> None:
    # Arrange
    env_file = _env_file(tmp_path, [f"{KEY1}={FAKE_FILE_1}", f"{KEY2}={FAKE_FILE_2}"])

    # Act
    key_1 = require_databento_key(env_file=env_file, account=ACCOUNT_1_ID)
    key_2 = require_databento_key(env_file=env_file, account=ACCOUNT_2_ID)

    # Assert
    assert (key_1, key_2) == (FAKE_FILE_1, FAKE_FILE_2)


def test_default_account_is_the_active_account(tmp_path: Path,
                                               monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv(KEY1, FAKE_1)
    monkeypatch.setenv(KEY2, FAKE_2)
    expected = {ACCOUNT_1_ID: FAKE_1, ACCOUNT_2_ID: FAKE_2}[config.ACTIVE_ACCOUNT]

    # Act
    implicit = require_databento_key(env_file=_env_file(tmp_path))
    explicit_none = require_databento_key(env_file=_env_file(tmp_path), account=None)

    # Assert
    assert implicit == explicit_none == expected


def test_default_follows_active_account_when_it_is_repointed(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv(KEY1, FAKE_1)
    monkeypatch.setenv(KEY2, FAKE_2)

    # Act
    monkeypatch.setattr(config, "ACTIVE_ACCOUNT", ACCOUNT_1_ID)
    on_acct_1 = require_databento_key(env_file=_env_file(tmp_path))
    monkeypatch.setattr(config, "ACTIVE_ACCOUNT", ACCOUNT_2_ID)
    on_acct_2 = require_databento_key(env_file=_env_file(tmp_path))

    # Assert
    assert (on_acct_1, on_acct_2) == (FAKE_1, FAKE_2)


# ------------------------------------------------------- environment versus .env file ----

def test_environment_variable_wins_over_the_env_file(tmp_path: Path,
                                                     monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    env_file = _env_file(tmp_path, [f"{KEY2}={FAKE_FILE_2}"])
    monkeypatch.setenv(KEY2, FAKE_2)

    # Act
    key = require_databento_key(env_file=env_file, account=ACCOUNT_2_ID)

    # Assert
    assert key == FAKE_2


def test_env_file_is_read_when_the_variable_is_absent_from_the_environment(
        tmp_path: Path) -> None:
    # Arrange
    env_file = _env_file(tmp_path, ["# comment line", f'{KEY1}="{FAKE_FILE_1}"'])

    # Act
    key = require_databento_key(env_file=env_file, account=ACCOUNT_1_ID)

    # Assert
    assert key == FAKE_FILE_1


@pytest.mark.parametrize("blank", ["", "   ", "\t"])
def test_blank_environment_variable_does_not_shadow_the_env_file(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, blank: str) -> None:
    # Arrange
    env_file = _env_file(tmp_path, [f"{KEY2}={FAKE_FILE_2}"])
    monkeypatch.setenv(KEY2, blank)

    # Act
    key = require_databento_key(env_file=env_file, account=ACCOUNT_2_ID)

    # Assert
    assert key == FAKE_FILE_2


def test_env_file_is_not_opened_when_the_environment_holds_the_key(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    def _must_not_read(path: Path) -> dict[str, str]:
        raise AssertionError("the .env file was read although the environment held the key")

    monkeypatch.setattr(config, "_read_env_file", _must_not_read)
    monkeypatch.setenv(KEY1, FAKE_1)

    # Act
    key = require_databento_key(env_file=_env_file(tmp_path), account=ACCOUNT_1_ID)

    # Assert
    assert key == FAKE_1


# ------------------------------------------------------------------- refusals ----

def test_missing_variable_raises_naming_the_variable_and_the_account(tmp_path: Path) -> None:
    # Arrange
    env_file = _env_file(tmp_path, [f"{KEY1}={FAKE_FILE_1}"])

    # Act
    message = _missing_message(env_file, ACCOUNT_2_ID)

    # Assert
    assert KEY2 in message
    assert ACCOUNT_2_ID in message


def test_missing_env_file_and_environment_raises(tmp_path: Path) -> None:
    # Arrange
    env_file = _env_file(tmp_path)  # never written: the file does not exist

    # Act
    message = _missing_message(env_file, ACCOUNT_1_ID)

    # Assert
    assert not env_file.exists()
    assert KEY1 in message


@pytest.mark.parametrize("line", [f"{KEY1}=", f"{KEY1}=   ", f'{KEY1}=""', f'{KEY1}="   "',
                                  f"{KEY1}=''"])
def test_empty_or_whitespace_only_value_in_the_env_file_raises(tmp_path: Path, line: str) -> None:
    # Arrange
    env_file = _env_file(tmp_path, [line])

    # Act
    message = _missing_message(env_file, ACCOUNT_1_ID)

    # Assert
    assert KEY1 in message


@pytest.mark.parametrize("blank", ["", "   ", "\t \t"])
def test_empty_or_whitespace_only_environment_value_raises_without_a_file_fallback(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, blank: str) -> None:
    # Arrange
    monkeypatch.setenv(KEY2, blank)

    # Act
    message = _missing_message(_env_file(tmp_path), ACCOUNT_2_ID)

    # Assert
    assert KEY2 in message


@pytest.mark.parametrize("account", ["acct-3", "", "ACCT-1", "acct_1"])
def test_unknown_account_raises_naming_the_account(tmp_path: Path,
                                                   monkeypatch: pytest.MonkeyPatch,
                                                   account: str) -> None:
    # Arrange
    monkeypatch.setenv(KEY1, FAKE_1)
    monkeypatch.setenv(KEY2, FAKE_2)

    # Act
    message = _missing_message(_env_file(tmp_path), account)

    # Assert
    assert repr(account) in message
    assert FAKE_1 not in message and FAKE_2 not in message


def test_legacy_single_variable_alone_is_not_accepted(tmp_path: Path,
                                                      monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv(LEGACY, FAKE_LEGACY)
    env_file = _env_file(tmp_path, [f"{LEGACY}={FAKE_LEGACY}"])

    # Act
    messages = [_missing_message(env_file, account)
                for account in (None, ACCOUNT_1_ID, ACCOUNT_2_ID)]

    # Assert
    for message in messages:
        assert FAKE_LEGACY not in message
    assert KEY1 in messages[1] and KEY2 in messages[2]


def test_one_accounts_key_never_stands_in_for_the_other(tmp_path: Path,
                                                        monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv(KEY1, FAKE_1)
    env_file = _env_file(tmp_path, [f"{KEY1}={FAKE_FILE_1}"])

    # Act
    message = _missing_message(env_file, ACCOUNT_2_ID)

    # Assert
    assert KEY2 in message


def test_refusal_messages_never_contain_a_key_value_and_nothing_is_printed(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    # Arrange
    monkeypatch.setenv(KEY1, FAKE_1)
    monkeypatch.setenv(LEGACY, FAKE_LEGACY)
    env_file = _env_file(tmp_path, [f"{KEY1}={FAKE_FILE_1}", f"{KEY2}=   ",
                                    f"{LEGACY}={FAKE_LEGACY}"])

    # Act
    messages = [_missing_message(env_file, ACCOUNT_2_ID),
                _missing_message(env_file, "acct-9")]
    captured = capsys.readouterr()

    # Assert
    for message in messages:
        for value in (FAKE_1, FAKE_FILE_1, FAKE_LEGACY):
            assert value not in message
    assert captured.out == "" and captured.err == ""


# ------------------------------------------------------------ backward compatibility ----

def test_signature_still_binds_with_no_arguments_for_key_loader_callers() -> None:
    # Arrange
    signature = inspect.signature(require_databento_key)

    # Act
    bound = signature.bind()
    bound.apply_defaults()

    # Assert
    assert list(signature.parameters) == ["env_file", "account"]
    assert bound.arguments == {"env_file": config.ENV_FILE, "account": None}


def test_zero_argument_call_returns_the_active_accounts_environment_key(
        monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange: the repo's .env must never be opened, so any file read fails the test
    def _must_not_read(path: Path) -> dict[str, str]:
        raise AssertionError("the repo .env was read")

    monkeypatch.setattr(config, "_read_env_file", _must_not_read)
    monkeypatch.setattr(config, "ACTIVE_ACCOUNT", ACCOUNT_2_ID)
    monkeypatch.setenv(KEY2, FAKE_2)

    # Act
    key = require_databento_key()

    # Assert
    assert key == FAKE_2


def test_missing_secret_error_is_still_a_runtime_error() -> None:
    # Arrange / Act / Assert
    assert issubclass(MissingSecretError, RuntimeError)
