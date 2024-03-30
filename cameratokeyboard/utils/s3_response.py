from datetime import datetime
from xml.dom.minidom import parseString

from cameratokeyboard.types import S3ContentsItem


class S3Response:
    """
    Parses the XML response of S3 api calls.
    """

    def __init__(self, response: str) -> None:
        self._document = parseString(response)

    def get_objects(self):
        """
        Returns the list of objects
        """
        objects = []

        for content in self._contents():
            try:
                key = content.getElementsByTagName("Key")[0].firstChild.nodeValue
                last_modified = content.getElementsByTagName("LastModified")[
                    0
                ].firstChild.nodeValue
                last_modified = datetime.strptime(
                    last_modified, "%Y-%m-%dT%H:%M:%S.%fZ"
                )

                objects.append(S3ContentsItem(key=key, last_modified=last_modified))
            except IndexError:
                continue

        return objects

    def _contents(self):
        return self._document.getElementsByTagName("Contents")
