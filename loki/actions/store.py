from director import Action
from director.decorators import general_help

from loki import SetupTasks


class Store(Action):
    """
    loki server action.
    """

    description_txt = "Manages Database Store"

    @general_help("Setup the Database Schema.", examples=['loki store setup'])
    def setup(self):
        """
        Setup the Database Schema.
        """
        SetupTasks.createSchema()

    @general_help("Setup the Database Schema.", examples=['loki store update'])
    def update(self):
        """
        Update the Database Schema.
        """
        SetupTasks.updateSchema()
