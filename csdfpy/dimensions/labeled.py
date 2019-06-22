# -*- coding: utf-8 -*-
"""The Dimension SubTypes class."""
from __future__ import division
from __future__ import print_function

from copy import deepcopy

import numpy as np

from csdfpy.utils import _type_message


__author__ = "Deepansh J. Srivastava"
__email__ = "srivastava.89@osu.edu"


class LabeledDimension:
    """Declare a LabeledDimension class."""

    __slots__ = ("_count", "_labels", "_label", "_description", "_application")

    _type = "labeled"

    def __init__(
        self, labels, label="", description="", application={}, **kwargs
    ):
        r"""Instantiate a LabeledDimension class instance."""
        self._description = description
        self._application = application
        self._label = label
        self.labels = labels

    # ----------------------------------------------------------------------- #
    #                          LabeledDimension Methods                       #
    # ----------------------------------------------------------------------- #
    # label
    @property
    def label(self):
        r"""Label associated with the dimension."""
        return deepcopy(self._label)

    @label.setter
    def label(self, label=""):
        if not isinstance(label, str):
            raise TypeError(_type_message(str, type(label)))
        self._label = label

    # description
    @property
    def description(self):
        r"""Return the description of the object."""
        return deepcopy(self._description)

    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            raise ValueError("A string value is required.")
        self._description = value

    # is_quantitative
    def _is_quantitative(self):
        r"""Return `True`, if the dimension is quantitative, otherwise `False`.
        :returns: A Boolean.
        """
        return False

    def _get_python_dictionary(self):
        dictionary = {}
        dictionary["type"] = self._type
        if self._description.strip() != "":
            dictionary["description"] = self._description.strip()
        dictionary["labels"] = self._labels.tolist()
        return dictionary

    # ----------------------------------------------------------------------- #
    #                        LabeledDimension Attributes                      #
    # ----------------------------------------------------------------------- #

    # labels
    @property
    def labels(self):
        r"""Return a list of labels along the dimension."""
        return deepcopy(self._labels)

    @labels.setter
    def labels(self, labels):
        self._labels = np.asarray(labels)
        self._count = len(labels)

    # application
    @property
    def application(self):
        r"""Return a list of values along the dimension."""
        return deepcopy(self._application)

    @application.setter
    def application(self, value):
        self._application = value
