# -*- coding: utf-8 -*-
import json

import numpy as np
import pytest
from astropy import units as u

import csdmpy as cp
from csdmpy.units import ScalarQuantity


# linear dimension
def test_linear_new():
    data = cp.new()
    dim = {
        "type": "linear",
        "increment": "10 m/s",
        "count": 10,
        "coordinates_offset": "5 m/s",
    }
    data.add_dimension(dim)

    assert data.dimensions[0].type == "linear"

    error = "can't set attribute"
    with pytest.raises(AttributeError, match=".*{0}.*".format(error)):
        data.dimensions[0].type = "monotonic"

    assert str(data.dimensions[0].increment) == "10.0 m / s"
    data.dimensions[0].increment = ScalarQuantity("20.0 m / s")
    assert str(data.dimensions[0].increment) == "20.0 m / s"
    data.dimensions[0].increment = 20.0 * u.Unit("m / s")
    assert str(data.dimensions[0].increment) == "20.0 m / s"

    error = "Expecting an instance of type"
    with pytest.raises(TypeError, match=".*{0}.*".format(error)):
        data.dimensions[0].increment = 10

    data.dimensions[0].increment = "20/2 m / s"
    assert str(data.dimensions[0].increment) == "10.0 m / s"

    assert data.dimensions[0].count == 10

    assert data.dimensions[0].application == {}
    data.dimensions[0].application = {"my_application": {}}
    assert data.dimensions[0].application == {"my_application": {}}
    error = "Expecting an instance of type"
    with pytest.raises(TypeError, match=".*{0}.*".format(error)):
        data.dimensions[0].application = "my_application"

    assert str(data.dimensions[0].coordinates_offset) == "5.0 m / s"

    error = "Expecting an instance of type"
    with pytest.raises(TypeError, match=".*{0}.*".format(error)):
        data.dimensions[0].coordinates_offset = 50

    data.dimensions[0].coordinates_offset = ScalarQuantity("5.0 m / s")
    assert str(data.dimensions[0].coordinates_offset) == "5.0 m / s"

    assert str(data.dimensions[0].origin_offset) == "0.0 m / s"
    assert data.dimensions[0].quantity_name == "speed"
    assert str(data.dimensions[0].period) == "inf m / s"
    assert data.dimensions[0].complex_fft is False
    assert np.all(data.dimensions[0].coordinates.value == np.arange(10) * 10.0 + 5.0)

    data.dimensions[0].count = 12
    assert data.dimensions[0].count == 12
    assert np.all(data.dimensions[0].coordinates.value == np.arange(12) * 10.0 + 5.0)
    assert np.all(
        data.dimensions[0].absolute_coordinates.value == np.arange(12) * 10.0 + 5.0
    )

    data.dimensions[0].origin_offset = "1 km/s"
    assert str(data.dimensions[0].origin_offset) == "1.0 km / s"
    assert np.all(data.dimensions[0].coordinates.value == np.arange(12) * 10.0 + 5.0)

    test_with = np.arange(12) * 10.0 + 5.0 + 1000.0
    assert np.all(data.dimensions[0].absolute_coordinates.value == test_with)

    data.dimensions[0].increment = "20 m/s"
    assert str(data.dimensions[0].increment) == "20.0 m / s"
    assert np.all(data.dimensions[0].coordinates.value == np.arange(12) * 20.0 + 5.0)

    test_with = np.arange(12) * 20.0 + 5.0 + 1000.0
    assert np.all(data.dimensions[0].absolute_coordinates.value == test_with)

    data.dimensions[0].complex_fft = True
    assert data.dimensions[0].complex_fft is True
    assert np.all(
        data.dimensions[0].coordinates.value == (np.arange(12) - 6) * 20.0 + 5.0
    )

    test_with = (np.arange(12) - 6) * 20.0 + 5.0 + 1000.0
    assert np.all(data.dimensions[0].absolute_coordinates.value == test_with)

    error = "The attribute cannot be modifed for Dimension objects with"
    with pytest.raises(AttributeError, match=".*{0}.*".format(error)):
        data.dimensions[0].coordinates = [1, 3]

    data.dimensions[0].reciprocal.description = "blah blah"

    dict1 = {
        "csdm": {
            "version": "1.0",
            "dimensions": [
                {
                    "type": "linear",
                    "count": 12,
                    "increment": "20.0 m * s^-1",
                    "coordinates_offset": "5.0 m * s^-1",
                    "origin_offset": "1.0 km * s^-1",
                    "quantity_name": "speed",
                    "application": {"my_application": {}},
                    "complex_fft": True,
                    "reciprocal": {"description": "blah blah"},
                }
            ],
            "dependent_variables": [],
        }
    }
    assert data.data_structure == json.dumps(
        dict1, ensure_ascii=False, sort_keys=False, indent=2
    )
    assert data.dimensions[0].to_dict() == dict1["csdm"]["dimensions"][0]

    # check equality
    dim1 = data.dimensions[0].copy()
    assert data.dimensions[0] == dim1

    dim1.coordinates_offset = "0 m * s^-1"
    assert data.dimensions[0] != dim1

    assert dim1 != 21


# monotonic dimension
def test_monotonic_new():
    data = cp.new()
    dim = {
        "type": "monotonic",
        "description": "Far far away.",
        "coordinates": ["1 m", "100 m", "1 km", "1 Gm", "0.25 lyr"],
    }
    data.add_dimension(dim)

    # description
    assert data.dimensions[0].description == "Far far away."
    data.dimensions[0].description = "A galaxy far far away."
    assert data.dimensions[0].description == "A galaxy far far away."

    error = "Expecting an instance of type"
    with pytest.raises(TypeError, match=".*{0}.*".format(error)):
        data.dimensions[0].description = 12

    # dimension type
    assert data.dimensions[0].type == "monotonic"

    # values
    assert data.dimensions[0].subtype._values == [
        "1 m",
        "100 m",
        "1 km",
        "1 Gm",
        "0.25 lyr",
    ]

    # increment
    error = "'MonotonicDimension' object has no attribute 'increment'"
    with pytest.raises(AttributeError, match=".*{0}.*".format(error)):
        data.dimensions[0].increment

    # label
    assert data.dimensions[0].label == ""
    data.dimensions[0].label = "some string"
    assert data.dimensions[0].label == "some string"

    error = "Expecting an instance of type"
    with pytest.raises(TypeError, match=".*{0}.*".format(error)):
        data.dimensions[0].label = {}

    # count
    assert data.dimensions[0].count == 5
    error = "Cannot set the count,"
    with pytest.raises(ValueError, match=".*{0}.*".format(error)):
        data.dimensions[0].count = 12

    error = "Expecting an instance of type"
    with pytest.raises(TypeError, match=".*{0}.*".format(error)):
        data.dimensions[0].count = "12"

    # coordinates_offset
    error = "`MonotonicDimension` has no attribute `coordinates_offset`."
    with pytest.raises(AttributeError, match=".*{0}.*".format(error)):
        data.dimensions[0].coordinates_offset

    error = "can't set attribute"
    with pytest.raises(AttributeError, match=".*{0}.*".format(error)):
        data.dimensions[0].coordinates_offset = "1"

    # origin offset
    assert str(data.dimensions[0].origin_offset) == "0.0 m"

    data.dimensions[0].origin_offset = ScalarQuantity("3.1415 m")
    assert str(data.dimensions[0].origin_offset) == "3.1415 m"

    data.dimensions[0].origin_offset = "1 lyr"
    assert str(data.dimensions[0].origin_offset) == "1.0 lyr"

    error = "Expecting an instance of type"
    with pytest.raises(TypeError, match=".*{0}.*".format(error)):
        data.dimensions[0].origin_offset = {"12 m"}

    # quantity_name
    assert data.dimensions[0].quantity_name == "length"

    error = "This attribute is not yet implemented"
    with pytest.raises(NotImplementedError, match=".*{0}.*".format(error)):
        data.dimensions[0].quantity_name = "area/length"

    # period
    assert str(data.dimensions[0].period) == "inf m"
    data.dimensions[0].period = "Infinity m"
    assert str(data.dimensions[0].period) == "inf m"
    data.dimensions[0].period = "20 m^2/m"
    assert str(data.dimensions[0].period) == "20.0 m"
    data.dimensions[0].period = "(1/0) m^5/m^4"
    assert str(data.dimensions[0].period) == "inf m"
    data.dimensions[0].period = 1 * u.Unit("m^5/m^4")
    assert str(data.dimensions[0].period) == "1.0 m"

    error = "Expecting an instance of type `str` for period, got `int`."
    with pytest.raises(TypeError, match=".*{0}.*".format(error)):
        data.dimensions[0].period = 1

    # fft output order
    error = "'MonotonicDimension' object has no attribute 'complex_fft'"
    with pytest.raises(AttributeError, match=".*{0}.*".format(error)):
        data.dimensions[0].complex_fft

    # coordinates
    assert np.allclose(
        data.dimensions[0].coordinates.value,
        np.asarray(
            [1.00000000e00, 1.00000000e02, 1.00000000e03, 1.00000000e09, 2.36518262e15]
        ),
    )

    # coordinates
    assert np.allclose(
        data.dimensions[0].absolute_coordinates.value,
        np.asarray(
            [9.46073047e15, 9.46073047e15, 9.46073047e15, 9.46073147e15, 1.18259131e16]
        ),
    )

    data.dimensions[0].application = {"go": "in"}

    dict1 = {
        "csdm": {
            "version": "1.0",
            "dimensions": [
                {
                    "type": "monotonic",
                    "description": "A galaxy far far away.",
                    "coordinates": ["1 m", "100 m", "1 km", "1 Gm", "0.25 lyr"],
                    "origin_offset": "1.0 lyr",
                    "quantity_name": "length",
                    "period": "1.0 m",
                    "label": "some string",
                    "application": {"go": "in"},
                    "reciprocal": {"quantity_name": "wavenumber"},
                }
            ],
            "dependent_variables": [],
        }
    }
    assert data.data_structure == json.dumps(
        dict1, ensure_ascii=False, sort_keys=False, indent=2
    )
    assert data.dimensions[0].to_dict() == dict1["csdm"]["dimensions"][0]

    error = r"The unit 's' \(time\) is inconsistent with the unit 'm' \(length\)"
    with pytest.raises(Exception, match=".*{0}.*".format(error)):
        data.dimensions[0].coordinates = ["1s", "2s"]

    data.dimensions[0].coordinates = ["1m", "2m"]
    assert np.allclose(data.dimensions[0].coordinates.value, np.asarray([1, 2]))

    # check equality
    dim1 = data.dimensions[0].copy()
    assert data.dimensions[0] == dim1

    dim1.origin_offset = "1 m"
    assert data.dimensions[0] != dim1

    dim2 = dim1.copy()
    dim2.origin_offset = "100 cm"
    assert dim1 == dim2

    assert dim1 != 21


# labeled dimension
def test_labeled_new():
    data = cp.new()
    dim = {
        "type": "labeled",
        "description": "Far far away.",
        "labels": ["m", "s", "t", "a"],
    }
    data.add_dimension(dim)

    # description
    assert data.dimensions[0].description == "Far far away."
    data.dimensions[0].description = "A galaxy far far away."
    assert data.dimensions[0].description == "A galaxy far far away."

    error = "Expecting an instance of type"
    with pytest.raises(TypeError, match=".*{0}.*".format(error)):
        data.dimensions[0].description = 12

    assert data.dimensions[0].labels[0] == "m"
    assert data.dimensions[0].coordinates[-1] == "a"

    error = "A list of labels is required"
    with pytest.raises(ValueError, match=".*{0}.*".format(error)):
        data.dimensions[0].labels = 12

    error = "A list of string labels are required"
    with pytest.raises(ValueError, match=".*{0}.*".format(error)):
        data.dimensions[0].labels = ["12", "1", 4]

    data.dimensions[0].label = "labeled dimension"
    assert data.dimensions[0].label == "labeled dimension"

    data.dimensions[0].application = {"this is it": "period"}
    assert data.dimensions[0].application == {"this is it": "period"}

    data.dimensions[0].coordinates = ["a", "b", "c"]
    assert data.dimensions[0].coordinates[-1] == "c"

    dict1 = {
        "csdm": {
            "version": "1.0",
            "dimensions": [
                {
                    "type": "labeled",
                    "description": "A galaxy far far away.",
                    "labels": ["a", "b", "c"],
                    "label": "labeled dimension",
                    "application": {"this is it": "period"},
                }
            ],
            "dependent_variables": [],
        }
    }
    assert data.data_structure == json.dumps(
        dict1, ensure_ascii=False, sort_keys=False, indent=2
    )
    assert data.dimensions[0].to_dict() == dict1["csdm"]["dimensions"][0]

    # check equality
    dim1 = data.dimensions[0].copy()
    assert data.dimensions[0] == dim1

    dim1.labels[1] = "Skywalker"
    assert data.dimensions[0] != dim1

    assert dim1 != 21
