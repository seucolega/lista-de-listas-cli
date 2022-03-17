import main
from click.testing import CliRunner


def test_hello_world():
    runner = CliRunner()
    result = runner.invoke(main.hello_command, ['people'])

    assert result.exit_code == 0
    assert result.output == 'Hello people!\n'
