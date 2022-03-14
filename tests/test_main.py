from click.testing import CliRunner

from main import hello, lst


def test_hello_world():
    runner = CliRunner()
    result = runner.invoke(hello, ['Peter'])

    assert result.exit_code == 0
    assert result.output == 'Hello Peter!\n'


