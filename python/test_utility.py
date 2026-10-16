import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import utility


class ResponseWithoutContentLength(io.BytesIO):
  def getheader(self, name):
    return None


class DownloadFileTest(unittest.TestCase):
  def test_download_without_content_length(self):
    response = ResponseWithoutContentLength(b"downloaded data")

    with tempfile.TemporaryDirectory() as folder:
      output = io.StringIO()
      with patch("utility.urllib.request.urlopen", return_value=response):
        with redirect_stdout(output):
          utility.download_file("data/", "sample.zip", folder=folder)

      with open(os.path.join(folder, "data", "sample.zip"), "rb") as downloaded:
        self.assertEqual(downloaded.read(), b"downloaded data")
      self.assertIn("Downloaded 15 bytes", output.getvalue())


if __name__ == "__main__":
  unittest.main()
