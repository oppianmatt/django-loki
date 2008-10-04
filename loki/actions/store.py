from director import Action
from loki import SetupTasks


class Store(Action):
    """
    loki server action.
    """

    description_txt = "Manages Database Store"

    def setup(self):
        """
        Setup the Database Schema.

        == help ==
        \nOptions:
        \tNone

        Example:
        \tloki store setup
        == end help ==
        """

        SetupTasks.createSchema()

    def update(self):
        """
        Update the Database Schema.

        == help ==
        \nOptions:
        \tNone

        Example:
        \tloki store update
        == end help ==
        """

        SetupTasks.updateSchema()
