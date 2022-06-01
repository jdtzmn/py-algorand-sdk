from collections import OrderedDict
from typing import List, Tuple

from algosdk import error


class BoxReference:
    """
    Represents a box reference with a foreign app index and the box name.

    Args:
        app_index (int): index of the application in the foreign app array
        name (bytes): name of the box in bytes
    """

    def __init__(self, app_index: int, name: bytes):
        self.app_index = app_index
        self.name = name

    @staticmethod
    def translate_box_reference(
        ref: Tuple[int, bytes],
        foreign_apps: List[int],
        this_app_id: int,
    ) -> "BoxReference":
        # Try coercing reference id and name.
        from algosdk.future.transaction import ApplicationCallTxn

        ref_id, ref_name = int(ref[0]), ApplicationCallTxn.as_bytes(ref[1])
        index = 0
        try:
            # Foreign apps start from index 1; index 0 is its own app ID.
            index = foreign_apps.index(ref_id) + 1
        except ValueError:
            # Check if the app referenced is itself after checking the
            # foreign apps array (in case its own app id is in its own
            # foreign apps array).
            if ref_id == 0 or ref_id == this_app_id:
                pass
            else:
                raise error.InvalidForeignAppIdError(
                    f"Box ref with appId {ref_id} not in foreign-apps"
                )
        return BoxReference(index, ref_name)

    @staticmethod
    def translate_box_references(
        references: List[Tuple[int, bytes]],
        foreign_apps: List[int],
        this_app_id: int,
    ) -> List["BoxReference"]:
        """
        Translates a list of tuples with app IDs and names into an array of
        BoxReferences with foreign indices.
        """
        if not references:
            return []

        return [
            BoxReference.translate_box_reference(
                ref, foreign_apps, this_app_id
            )
            for ref in references
        ]

    def dictify(self):
        d = dict()
        if self.app_index:
            d["i"] = self.app_index
        if self.name:
            d["n"] = self.name
        od = OrderedDict(sorted(d.items()))
        return od

    @staticmethod
    def undictify(d):
        args = {
            "app_index": d["i"] if "i" in d else None,
            "name": d["n"] if "n" in d else None,
        }
        return args

    def __eq__(self, other):
        if not isinstance(other, BoxReference):
            return False
        return self.app_index == other.app_index and self.name == other.name
