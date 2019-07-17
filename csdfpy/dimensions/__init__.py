# -*- coding: utf-8 -*-
"""The base ControlledVariable object: attributes and methods."""
import json
import warnings

from csdfpy.dimensions.labeled import LabeledDimension
from csdfpy.dimensions.linear import LinearDimension
from csdfpy.dimensions.monotonic import MonotonicDimension
from csdfpy.utils import _axis_label
from csdfpy.utils import _get_dictionary
from csdfpy.utils import attribute_error
from csdfpy.utils import validate

__author__ = "Deepansh J. Srivastava"
__email__ = "srivastava.89@osu.edu"
__all__ = ["Dimension"]


functional_dimension = ["linear"]


class Dimension:
    r"""
    Create an instance of the Dimension class.

    An instance of this class describes a dimension of a multi-dimensional system.
    In version 1.0, there are three subtypes of the Dimension class:

        - LinearDimension,
        - MonotonicDimension, and
        - LabeledDimension.

    **LinearDimension subtype**

    As given from the name, the coordinates along this dimension follow a linear
    relationship with respect to the indices along the dimension.
    Let :math:`\Delta x_k` be the `increment`, :math:`N_k \ge 1`, the number of points
    (`counts`), :math:`b_k`, the `coordinates offset`, and :math:`o_k`, the `origin offset`
    along the :math:`k^{th}` dimension, then the corresponding coordinates along the
    dimension, :math:`\mathbf{X}_k`, are given as

    .. math ::
        \mathbf{X}_k = \Delta x_k \mathbf{J}_k - b_k \mathbf{1},

    and the absolute coordinates as,

    .. math::
        \mathbf{X}_k^\mathrm{abs} = \mathbf{X}_k + o_k \mathbf{1}.

    Here, :math:`\mathbf{1}` is an array of ones. The parameter, :math:`\mathbf{J}_k`,
    is an array of indexes along the :math:`k^\mathrm{th}` dimension and is given by

    .. math::
        \mathbf{J}_k = [0, 1, 2, 3, ..., N_k-1]

    when the value of the `fft_output_order` attribute is false, otherwise,

    .. math::
        \mathbf{J}_k = \left[0, 1, ... \frac{N_k}{2}-1, \pm\frac{N_k}{2},
                                -\frac{N_k}{2}+1, ..., -1 \right]

    when :math:`N_k` is even, and

    .. math::
        \mathbf{J}_k = \left[0, 1, ... \frac{T_k}{2}, -\frac{T_k}{2}, ..., -1 \right]

    when :math:`N_k` is odd where :math:`T_k=N_k-1`.

    **MonotonicDimension subtype**

    A monotonic dimension is where the coordinates along the dimension are explicitly
    defined and, unlike the linear dimension, may not be derivable from the dimension
    indices. Let :math:`\mathbf{A}_k` be an ordered set of strictly ascending or descending
    quantities and :math:`o_k` be the origin offset along the :math:`k^{th}`
    dimension, then the coordinates and the absolute coordinates along a monotonic
    dimension are given as,

    .. math ::
        \begin{align}
        \mathbf{X}_k &= \mathbf{A}_k\\
        \mathbf{X}_k^\mathrm{abs} &= \mathbf{X}_k + o_k \mathbf{1},
        \end{align}

    **LabeledDimension subtype**

    A labeled dimension is a non-quantitative dimension composed of character string
    labels. Consider, :math:`\mathbf{A}_k` as an ordered array of lables, then the
    coordinates along a labeled dimension are given as

    .. math ::
        \mathbf{X}_k = \mathbf{A}_k.

    **Creating an instance of a dimension object.**

    There are two ways of creating a new instance of a Dimension class.

    `From a python dictionary containing valid keywords.`

    .. doctest::

        >>> from csdfpy import Dimension
        >>> dimension_dictionary = {
        ...     'type': 'linear',
        ...     'description': 'test',
        ...     'increment': '5 G',
        ...     'count': 10,
        ...     'coordinates_offset': '10 mT',
        ...     'origin_offset': '10 T'
        ... }
        >>> x = Dimension(dimension_dictionary)

    Here, ``dimension_dictionary`` is the python dictionary.

    `From valid keyword arguments.`

    .. doctest::

        >>> x = Dimension(type = 'linear',
        ...               description = 'test',
        ...               increment = '5 G',
        ...               count = 10,
        ...               coordinates_offset = '10 mT',
        ...               origin_offset = '10 T')

    """

    __slots__ = ("subtype",)

    _immutable_objects_ = ()

    def __init__(self, *args, **kwargs):
        """Initialize an instance of Dimension object."""
        default = {
            "type": None,  # valid for all dimension subtypes
            "description": "",  # valid for all dimension subtypes
            "count": None,  # valid for linear dimension subtype
            "increment": None,  # valid for linear dimension subtype
            "labels": None,  # valid for labled dimension subtype
            "coordinates": None,  # valid for monotonic dimension subtype
            "coordinates_offset": None,  # valid for linear dimension subtype
            "origin_offset": None,  # valid for linear dimension subtype
            "fft_output_order": False,  # valid for linear dimension subtype
            "period": None,  # valid for monotonic and linear dimension subtypes
            "quantity_name": None,  # valid for monotonic and linear dimension subtypes
            "label": "",  # valid for all dimension subtypes
            "application": {},  # valid for all dimension subtypes
            "reciprocal": {  # valid for all monotonic and linear subtypes
                "increment": None,  # valid for all monotonic and linear subtypes
                "coordinates_offset": None,  # valid for all monotonic and linear subtypes
                "origin_offset": None,  # valid for all monotonic and linear subtypes
                "period": None,  # valid for all monotonic and linear subtypes
                "quantity_name": None,  # valid for all monotonic and linear subtypes
                "label": "",  # valid for all monotonic and linear subtypes
                "description": "",  # valid for all monotonic and linear subtypes
                "application": {},  # valid for all monotonic and linear subtypes
            },
        }

        default_keys = default.keys()
        input_dict = _get_dictionary(*args, **kwargs)
        input_keys = input_dict.keys()

        if "type" not in input_keys:
            raise ValueError("Missing a required 'type' key from the dimension object.")

        if "reciprocal" in input_keys:
            input_subkeys = input_dict["reciprocal"].keys()
        for key in input_keys:
            if key in default_keys:
                if key == "reciprocal":
                    for subkey in input_subkeys:
                        default[key][subkey] = input_dict[key][subkey]
                else:
                    default[key] = input_dict[key]

        _valid_types = ["monotonic", "linear", "labeled"]

        typ = default["type"]
        message = (
            f"'{typ}' is an invalid value for the dimension type. "
            "The allowed values are 'monotonic', 'linear' and 'labeled'."
        )

        if default["type"] not in _valid_types:
            raise ValueError(message)

        if default["type"] == "labeled" and default["labels"] is None:
            raise KeyError("`labels` key is missing from LabeledDimension.")
        if default["type"] == "labeled":
            self.subtype = LabeledDimension(**default)

        if default["type"] == "monotonic" and default["coordinates"] is None:
            raise KeyError("`coordinates` key is missing from MonotonicDimension.")
        if default["type"] == "monotonic":
            self.subtype = MonotonicDimension(values=default["coordinates"], **default)

        if default["type"] == "linear":
            self.subtype = self.linear(default)

    def linear(self, default):
        """Create and assign a linear dimension."""
        missing_key = ["increment", "count"]

        for item in missing_key:
            if default[item] is None:
                raise KeyError(f"{item} key is missing from the linear dimension.")

        validate(default["count"], "count", int)

        return LinearDimension(**default)

    # ======================================================================= #
    #                          Dimension Attributes                           #
    # ======================================================================= #
    @property
    def absolute_coordinates(self):
        r"""
        Absolute coordinates, :math:`{\bf X}_k^\rm{abs}`, along the dimension.

        This attribute is only *valid* for quantitative dimensions, that is,
        `linear` and `monotonic` dimensions. The absolute coordinates are given as

        .. math::

            \mathbf{X}_k^\mathrm{abs} = \mathbf{X}_k + o_k \mathbf{1}

        where :math:`\mathbf{X}_k` are the coordinates along the dimension and
        :math:`o_k` is the :attr:`~csdfpy.dimensions.Dimension.origin_offset`.
        For example, consider

        .. doctest::

            >>> print(x.origin_offset)
            10.0 T
            >>> print(x.coordinates)
            [100. 105. 110. 115. 120. 125. 130. 135. 140. 145.] G

        then the absolute coordinates are

        .. doctest::

            >>> print(x.absolute_coordinates)
            [100100. 100105. 100110. 100115. 100120. 100125. 100130. 100135.
            100140. 100145.] G

        For `linear` dimensions, the order of the `absolute_coordinates`
        further depend on the value of the
        :attr:`~csdfpy.dimensions.Dimension.fft_output_order` attributes. For
        examples, when the value of the `fft_output_order` attribute is True,
        the absolute coordinates are

        .. doctest::

            >>> x.fft_output_order = True
            >>> print(x.absolute_coordinates)
            [100100. 100105. 100110. 100115. 100120. 100075. 100080. 100085. 100090.
             100095.] G

        .. note::

            This attribute is *invalid* for `labeled` dimensions.

        .. testsetup::

            >>> x.fft_output_order = False

        Return:
            A Quantity array of absolute coordinates for quantitative dimensions, `i.e`
            `linear` and `monotonic`.

        Raise:
            AttributeError: For labeled dimensions.
        """
        if self.subtype != "labeled":
            return (self.coordinates + self.origin_offset).to(self.subtype._unit)
        raise AttributeError(attribute_error(self.subtype, "absolute_coordinates"))

    @property
    def application(self):
        """
        Application metadata dictionary of the dimension object.

        .. doctest::

            >>> print(x.application)
            {}

        The application attribute is where an application can place its own
        metadata as a python dictionary object with application specific
        metadata, using a reverse domain name notation string as the attribute
        key, for example,

        .. doctest::

            >>> x.application = {
            ...     "com.example.myApp" : {
            ...         "myApp_key": "myApp_metadata"
            ...      }
            ... }
            >>> print(x.application)
            {'com.example.myApp': {'myApp_key': 'myApp_metadata'}}

        Return:
            A python dictionary containing dimension application metadata.
        """
        return self.subtype._application

    @application.setter
    def application(self, value):
        self.subtype.application = value

    @property
    def axis_label(self):
        r"""
        Formatted string for displaying the label along the dimension.

        This attribute is not a part of the original core scientific dataset
        model, however, it is a convenient supplementary attribute that provides
        a formated string ready for labeling dimension axes.
        For quantitative dimensions, this attributes returns a string,
        `label / unit`,  if the `label` is a non-empty string, otherwise,
        `quantity_name / unit`. Here
        :attr:`~csdfpy.dimensions.Dimension.quantity_name` and
        :attr:`~csdfpy.dimensions.Dimension.label` are the attributes of the
        :ref:`dim_api` instances, and `unit` is the unit associated with the
        coordinates along the dimension. For examples,

        .. doctest::

            >>> x.label
            'field strength'
            >>> x.axis_label
            'field strength / (G)'

        For labled dimensions, this attribute returns 'label'.

        Returns:
            A formated string of label.

        Raises:
            AttributeError: When assigned a value.
        """
        if hasattr(self.subtype, "quantity_name"):
            if self.label.strip() == "":
                label = self.quantity_name
            else:
                label = self.label
            return _axis_label(label, self.subtype._unit)
        else:
            return self.label

    @property
    def coordinates(self):
        r"""
        Coordinates, :math:`{\bf X}_k`, along the dimension.

        Example:
            >>> print(x.coordinates)
            [100. 105. 110. 115. 120. 125. 130. 135. 140. 145.] G

        For `linear` dimensions, the order of the `coordinates` also depend on the
        value of the :attr:`~csdfpy.dimensions.Dimension.fft_output_order` attributes.
        For examples, when the value of the `fft_output_order` attribute is True,
        the coordinates are

        .. doctest::

            >>> x.fft_output_order = True
            >>> print(x.coordinates)
            [100. 105. 110. 115. 120. 75. 80. 85. 90. 95.] G

        .. testsetup::

            >>> x.fft_output_order = False

        Returns:
            A Quantity array of coordinates for quantitative dimensions, `i.e.` `linear`
            and `monotonic`.

        Returns:
            A Numpy array for labeled dimensions.

        Raises:
            AttributeError: For dimensions with subtype `linear`.
        """
        _n = self.subtype._count
        coordinates = self.subtype._coordinates[:_n]
        if self.type == "monotonic":
            return coordinates
        if self.type == "linear":
            return (coordinates + self.coordinates_offset).to(self.subtype._unit)
        if self.type == "labeled":
            return self.subtype.labels

    @coordinates.setter
    def coordinates(self, value):
        if self.type == "monotonic":
            self.subtype.values = value
        if self.type == "labeled":
            self.subtype.labels = value
        if self.type == "linear":
            raise AttributeError(
                (
                    "The attribute cannot be modifed for dimensions with subtype `linear`. "
                    "Use `count`, `increment` or `coordinates_offset` attributes to update "
                    "the coordinate along a linear dimension."
                )
            )

    @property
    def data_structure(self):
        r"""
        Json serialized string describing the Dimension class instance.

        This supplementary attribute is useful for a quick preview of the dimension
        object. The attribute cannot be modified.

        .. doctest::

            >>> print(x.data_structure)
            {
              "type": "linear",
              "description": "This is a test",
              "count": 10,
              "increment": "5.0 G",
              "coordinates_offset": "10.0 mT",
              "origin_offset": "10.0 T",
              "quantity_name": "magnetic flux density",
              "label": "field strength"
            }

        Returns:
            A json serialized string of the dimension object.
        Raise:
            AttributeError: When modified.
        """
        dictionary = self._get_python_dictionary()
        return json.dumps(dictionary, ensure_ascii=False, sort_keys=False, indent=2)

    @property
    def description(self):
        """
        Brief description of the dimension object.

        The default value is an empty string, ''. The attribute may be
        modified, for example,

        .. doctest::

            >>> print(x.description)
            This is a test

            >>> x.description = 'This is a test dimension.'

        Returns:
            A string of UTF-8 allows characters describing the dimension.

        Raises:
            ValueError: When the assigned value is not a string.
        """
        return self.subtype.description

    @description.setter
    def description(self, value):
        self.subtype.description = value

    @property
    def fft_output_order(self):
        r"""
        Boolean specifying if the coordinates are ordered as fft output order.

        This attribute is only `valid` for the Dimension instances with `linear`
        subtype.
        The value of this attribute is a boolean specifying if the coordinates along
        the dimension are ordered according to the output of a fast Fourier transform
        (FFT) routine. The universal behavior of all FFT routine is to order the
        :math:`N_k` output amplitudes by placing the zero `frequency` at the start of
        the output array, with positive `frequencies` increasing in magnitude placed
        at increasing array offset until reaching :math:`\frac{N_k}{2} -1` if
        :math:`N_k` is even, otherwise :math:`\frac{N_k-1}{2}`, followed by negative
        frequencies decreasing in magnitude until reaching :math:`N_k-1`.
        This is also the ordering needed for the input of the inverse FFT.
        For example, consider the following Dimension object,

        .. doctest::

            >>> test = Dimension(
            ...            type='linear',
            ...	           increment = '1',
            ...            count = 10
            ...        )

            >>> test.fft_output_order
            False
            >>> print(test.coordinates)
            [0. 1. 2. 3. 4. 5. 6. 7. 8. 9.]

            >>> test.fft_output_order = True
            >>> print(test.coordinates)
            [ 0.  1.  2.  3.  4. -5. -4. -3. -2. -1.]

        Returns:
            A Boolean.

        Raises:
            TypeError: When the assigned value is not a boolean.
        """
        return self.subtype.fft_output_order

    @fft_output_order.setter
    def fft_output_order(self, value):
        self.subtype.fft_output_order = value

    @property
    def increment(self):
        r"""
        Increment along a `linear` dimension.

        The attribute is only `valid` for Dimension instances with the subtype
        `linear`. When assigning a value, the dimensionality of the value must
        be consistent with the dimensionality of other members specifying the
        dimension.

        Example:
            >>> print(x.increment)
            5.0 G
            >>> x.increment = "0.1 G"
            >>> print(x.coordinates)
            [100.  100.1 100.2 100.3 100.4 100.5 100.6 100.7 100.8 100.9] G

        Returns:
            A Quantity instance with the increment along the dimension.

        Raises:
            AttributeError: For dimension with subtypes other than `linear`.
            TypeError: When the assigned value is not a string or Quantity object.
        """
        # .. note:: The sampling interval along a grid dimension and the
        #     respective reciprocal grid dimension follow the Nyquist–Shannon
        #     sampling theorem. Therefore, updating the ``increment``
        #     will automatically trigger an update on its reciprocal
        #     counterpart.
        return self.subtype.increment

    @increment.setter
    def increment(self, value):
        self.subtype.increment = value

    @property
    def coordinates_offset(self):
        r"""
        Value at the zeroth index of the dimension.

        When assigning a value, the dimensionality of the value must be consistent with
        the dimensionality of the other members specifying the dimension.

        Example:
            >>> print(x.coordinates_offset)
            10.0 mT
            >>> x.coordinates_offset = "0 T"
            >>> print(x.coordinates)
            [ 0.  5. 10. 15. 20. 25. 30. 35. 40. 45.] G

        The attribute is `invalid` for the labeled dimensions.

        Returns:
            A Quantity instance with the reference offset.

        Raises:
            AttributeError: For the labeled dimensions.
            TypeError: When the assigned value is not a string or Quantity object.
        """
        if self.type == "linear":
            return self.subtype.coordinates_offset
        raise AttributeError(attribute_error(self.subtype, "coordinates_offset"))

    @coordinates_offset.setter
    def coordinates_offset(self, value):
        self.subtype.coordinates_offset = value

    @property
    def label(self):
        r"""
        Label associated with the dimension.

        Example:
            >>> print(x.label)
            field strength
            >>> x.label = 'magnetic field strength'
            >>> print(x.axis_label)
            magnetic field strength / (G)

        Returns:
            A string containing the label.
        Raises:
            TypeError: When the assigned value is not a string.
        """
        return self.subtype.label

    @label.setter
    def label(self, label=""):
        self.subtype.label = label

    @property
    def count(self):
        r"""
        Number of coordinates, :math:`N_k \ge 1`, along the dimension.

        Example:
            >>> print(x.count)
            10
            >>> x.count = 5

        Returns:
            An Integer specifying the number of coordinates along the dimension.

        Raises:
            TypeError: When the assigned value is not an integer.
        """
        return self.subtype._count

    @count.setter
    def count(self, value):
        value = validate(value, "count", int)

        if self.type in functional_dimension:
            self.subtype._count = value
            self.subtype._get_coordinates()
            return

        if value > self.count:
            raise ValueError(
                (
                    f"Cannot set count, {value}, more than the number of "
                    f"coordinates, {self.count}, for monotonic and labeled"
                    " dimensions."
                )
            )

        if value < self.count:
            warnings.warn(
                f"The number of coordinates, {self.count}, are truncated "
                f"to {value}."
            )
            self.subtype._count = value

    @property
    def origin_offset(self):
        r"""
        Origin offset, :math:`o_k`, along the dimension.

        When assigning a value, the dimensionality of the value must be consistent
        with the dimensionality of other members specifying the dimension.

        Example:
            >>> print(x.origin_offset)
            10.0 T
            >>> x.origin_offset = "1e5 G"

        The origin offset only affect the absolute_coordinates along the dimension.
        This attribute is `invalid` for the labeled dimensions.

        Returns:
            A Quantity instance with the origin offset.

        Raises:
            AttributeError: For the labeled dimensions.
            TypeError: When the assigned value is not a string or Quantity object.
        """
        return self.subtype.origin_offset

    @origin_offset.setter
    def origin_offset(self, value):
        self.subtype.origin_offset = value

    @property
    def period(self):
        r"""
        Period of the dimension.

        The default value of the period is infinity, i.e., the dimension is
        non-periodic.

        Example:
            >>> print(x.period)
            inf G
            >>> x.period = '1 T'

        To assign a dimension as non-periodic, one of the following may be
        used,

        .. doctest::

            >>> x.period = '1/0 T'
            >>> x.period = 'infinity µT'
            >>> x.period = '∞ G'

        Return:
            A Quantity instance with the period of the dimension.

        Raise:
            AttributeError: For the `labeled` dimensions.
            TypeError: When the assigned value is not a string or Quantity object.
        """
        return self.subtype.period

    @period.setter
    def period(self, value=None):
        self.subtype.period = value

    @property
    def quantity_name(self):
        r"""
        Quantity name associated with the physical quantities specifying the dimension.

        The attribute is `invalid` for the labeled dimension.

        .. doctest::

            >>> print(x.quantity_name)
            magnetic flux density

        Returns:
            A string with the `quantity name`.

        Raises:
            AttributeError: For `labeled` dimensions.
            NotImplementedError: When assigning a value.
        """
        return self.subtype.quantity_name

    @quantity_name.setter
    def quantity_name(self, value):
        self.subtype.quantity_name = value

    @property
    def type(self):
        r"""
        The dimension subtype.

        There are three *valid* subtypes of Dimension class with the following
        enumeration literals,

        | ``linear``
        | ``monotonic``
        | ``labeled``

        corresponding to the LinearDimension, MonotonicDimension, and
        LabeledDimension, respectively.

        .. doctest::

            >>> print(x.type)
            linear

        Returns:
            A string with a valid dimension subtype.

        Raises:
            AttributeError: When the attribute is modified.
        """
        return self.subtype.__class__._type

    @property
    def labels(self):
        r"""
        Ordered list of labels along the Labeled dimension.

        .. doctest::

            >>> x2 = Dimension(
            ...         type='labeled',
            ...         labels=['Cu', 'Ag', 'Au']
            ...      )
            >>> print(x2.data_structure)
            {
              "type": "labeled",
              "labels": [
                "Cu",
                "Ag",
                "Au"
              ]
            }

        In the above example, ``x2`` is an instance of the :ref:`dim_api` class with
        `labeled` subtype.

        Returns:
             A Numpy array with labels along the dimension.

        Raises:
            AttributeError: For dimensions with subtype other than `labeled`.
        """
        return self.subtype.labels

    @labels.setter
    def labels(self, array):
        self.subtype.labels = array
        self.subtype._get_coordinates(array)

    @property
    def reciprocal(self):
        r"""
        An instance of the ReciprocalVariable class.

        The attributes of ReciprocalVariable class are:
            - coordinates_offset
            - origin_offset
            - period
            - quantity_name
            - label
        where the definition of each attribute is the same as the corresponding
        attribute from the Dimension instance.
        """
        return self.subtype.reciprocal

    # ======================================================================= #
    #                           Dimension Methods                             #
    # ======================================================================= #

    def _get_python_dictionary(self):
        r"""Return the Dimension instance as a python dictionary."""
        return self.subtype._get_python_dictionary()

    def is_quantitative(self):
        r"""Return True if the independent variable is quantitative."""
        return self.subtype._is_quantitative()

    def to(self, unit="", equivalencies=None):
        r"""
        Convert the coordinates along the dimension to unit, `unit`.

        This method is a wrapper of the `to` method from the
        `Quantity <http://docs.astropy.org/en/stable/api/\
        astropy.units.Quantity.html#astropy.units.Quantity.to>`_ class
        and is only `valid` for physical dimensions.

        Example:
            >>> print(x.coordinates)
            [100. 105. 110. 115. 120. 125. 130. 135. 140. 145.] G
            >>> x.to('mT')
            >>> print(x.coordinates)
            [10.  10.5 11.  11.5 12.  12.5 13.  13.5 14.  14.5] mT

        Args:
            `unit` : A string containing a unit with the same dimensionality as the
                     coordinates along the dimension.

        Raises:
            AttributeError: For the labeled dimensions.
        """
        self.subtype._to(unit, equivalencies)
