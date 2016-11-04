import re

from create_service import main


def test_main(cloud_config, capsys):
    main(cloud_config.storage_bucket, __file__)
    out, err = capsys.readouterr()

    assert not re.search(r'Downloaded file [!]=', out)
    assert re.search(r'Uploading.*Fetching.*Done', out, re.DOTALL)
