from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from abc import abstractmethod
from .descriptors.protocol import DescriptorProtocol
from .descriptors.color import ColorAttribute
from .context import clear
from .context import get_sceneobject_cls

import compas.colors  # noqa: F401
import compas.datastructures  # noqa: F401
import compas.geometry  # noqa: F401

from compas.datastructures import TreeNode
from compas.colors import Color
from compas.geometry import Transformation
from functools import reduce
from operator import mul


class SceneObject(TreeNode):
    """Base class for all scene objects.

    Parameters
    ----------
    item : Any
        The item which should be visualized using the created SceneObject.
    name : str, optional
        The name of the scene object. Note that is is not the same as the name of underlying data item, since different scene objects can refer to the same data item.
    color : :class:`compas.colors.Color`, optional
        The color of the object.
    opacity : float, optional
        The opacity of the object.
    show : bool, optional
        Flag for showing or hiding the object. Default is ``True``.
    frame : :class:`compas.geometry.Frame`, optional
        The local frame of the scene object, in relation to its parent frame.
    transformation : :class:`compas.geometry.Transformation`, optional
        The local transformation of the scene object in relation to its frame.
    context : str, optional
        The context in which the scene object is created.
    **kwargs : dict
        Additional keyword arguments to create the scene object for the item.

    Attributes
    ----------
    item : :class:`compas.data.Data`
        The item which should be visualized using the created SceneObject.
    name : str
        The name of the scene object. Note that is is not the same as the name of underlying data item, since different scene objects can refer to the same data item.
    node : :class:`compas.scene.SceneObjectNode`
        The node in the scene tree which represents the scene object.
    guids : list[object]
        The GUIDs of the items drawn in the visualization context.
    frame : :class:`compas.geometry.Frame`
        The local frame of the scene object, in relation to its parent frame.
    transformation : :class:`compas.geometry.Transformation`
        The local transformation of the scene object in relation to its frame.
    worldtransformation : :class:`compas.geometry.Transformation`
        The transformation of the scene object in world coordinates.
    color : :class:`compas.colors.Color`
        The color of the object.
    contrastcolor : :class:`compas.colors.Color`, readon-only
        The contrastcolor wrt to the color.
        This is a 50% darket or lighter version of the color, depending on whether the color is light or dark.
    opacity : float
        The opacity of the object.
    show : bool
        Flag for showing or hiding the object. Default is ``True``.
    settings : dict
        The settings including necessary attributes for reconstructing the scene object besides the Data item.
    context : str
        The context in which the scene object is created.

    """

    # add this to support the descriptor protocol vor Python versions below 3.6
    __metaclass__ = DescriptorProtocol

    color = ColorAttribute()

    def __new__(cls, item, **kwargs):
        sceneobject_cls = get_sceneobject_cls(item, **kwargs)
        return super(SceneObject, cls).__new__(sceneobject_cls)

    def __init__(
        self, item, name=None, color=None, opacity=1.0, show=True, frame=None, transformation=None, context=None, **kwargs
    ):  # type: (compas.geometry.Geometry | compas.datastructures.Datastructure, str | None, compas.colors.Color | None, float, bool, compas.geometry.Frame | None, compas.geometry.Transformation | None, str | None, dict) -> None
        name = name or item.name
        super(SceneObject, self).__init__(name=name, **kwargs)
        # the scene object needs to store the context
        # because it has no access to the tree and/or the scene before it is added
        # which means that adding child objects will be added in context "None"
        self.context = context
        self._item = item
        self._guids = None
        self._node = None
        self._frame = frame
        self._transformation = transformation
        self._contrastcolor = None
        self.color = color or self.color
        self.opacity = opacity
        self.show = show

    @property
    def __data__(self):
        # type: () -> dict
        return {
            "item": str(self.item.guid),
            "settings": self.settings,
            "children": [child.__data__ for child in self.children],
        }

    @classmethod
    def __from_data__(cls, data):
        # type: (dict) -> None
        raise TypeError("Serialisation outside Scene not allowed.")

    def __repr__(self):
        # type: () -> str
        return "<{}: {}>".format(self.__class__.__name__, self.name)

    @property
    def item(self):
        # type: () -> compas.geometry.Geometry | compas.datastructures.Datastructure
        return self._item

    @property
    def guids(self):
        # type: () -> list[str]
        return self._guids or []

    @property
    def frame(self):
        # type: () -> compas.geometry.Frame | None
        return self._frame

    @frame.setter
    def frame(self, frame):
        # type: (compas.geometry.Frame) -> None
        self._frame = frame

    @property
    def transformation(self):
        # type: () -> compas.geometry.Transformation | None
        return self._transformation

    @transformation.setter
    def transformation(self, transformation):
        # type: (compas.geometry.Transformation) -> None
        self._transformation = transformation

    @property
    def worldtransformation(self):
        # type: () -> compas.geometry.Transformation
        frame_stack = []
        parent = self.parent
        while parent and not parent.is_root:
            if parent.frame:
                frame_stack.append(parent.frame)
            parent = parent.parent
        matrices = [Transformation.from_frame(f) for f in frame_stack]
        if matrices:
            worldtransformation = reduce(mul, matrices[::-1])
        else:
            worldtransformation = Transformation()

        if self.transformation:
            worldtransformation *= self.transformation

        return worldtransformation

    @property
    def contrastcolor(self):
        # type: () -> compas.colors.Color
        if not self._contrastcolor:
            if self.color.is_light:
                self._contrastcolor = self.color.darkened(50)
            else:
                self._contrastcolor = self.color.lightened(50)
        return self._contrastcolor

    @contrastcolor.setter
    def contrastcolor(self, color):
        # type: (compas.colors.Color) -> None
        self._contrastcolor = Color.coerce(color)

    @property
    def settings(self):
        # type: () -> dict
        # The settings are all the nessessary attributes to reconstruct the scene object besides the Data item.
        settings = {
            "name": self.name,
            "color": self.color,
            "opacity": self.opacity,
            "show": self.show,
        }

        if self.frame:
            settings["frame"] = self.frame
        if self.transformation:
            settings["transformation"] = self.transformation

        return settings

    def add(self, item, **kwargs):
        """Add a child item to the scene object.

        Parameters
        ----------
        item : :class:`compas.data.Data`
            The item to add.
        **kwargs : dict
            Additional keyword arguments to create the scene object for the item.

        Returns
        -------
        :class:`compas.scene.SceneObject`
            The scene object associated with the added item.

        Raises
        ------
        ValueError
            If the scene object does not have an associated scene node.
        """
        if isinstance(item, SceneObject):
            sceneobject = item
        else:
            if "context" in kwargs:
                if kwargs["context"] != self.context:
                    raise Exception(
                        "Child context should be the same as parent context: {} != {}".format(
                            kwargs["context"], self.context
                        )
                    )
                del kwargs["context"]  # otherwist the SceneObject receives "context" twice, which results in an error
            sceneobject = SceneObject(item, context=self.context, **kwargs)  # type: ignore

        super(SceneObject, self).add(sceneobject)
        return sceneobject

    @abstractmethod
    def draw(self):
        """The main drawing method."""
        raise NotImplementedError

    def clear(self):
        """The main clearing method."""
        clear(guids=self.guids)
        self._guids = None
