from math import degrees
from cmath import rect, phase
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


def mean_angle(deg: 'ArrayLike') -> float:
    """Рассчет среднего угла
    :param deg: массив углов
    :return: средний угол
    """
    np_rect = np.vectorize(lambda x: rect(1, x))
    return degrees(
        phase(
            np.nanmean(np_rect(np.radians(deg)))
        )
    )


def mean_hod(hours: 'ArrayLike') -> float:
    """Рассчет среднего часа
    :param hours: массив часов
    :return: средний час
    """
    hours2degrees = hours / 24 * 360
    mean_hour = mean_angle(hours2degrees)*24/360
    if mean_hour < 0:
        mean_hour = mean_hour + 24
    if mean_hour == 24:
        return 0.0
    return mean_hour


def mean_dow(dow: 'ArrayLike') -> float:
    """Рассчет среднего дня недели
    :param dow: массив дней недели
    :return: средний день недели
    """
    dow2degrees = dow / 7 * 360
    mean_dow = mean_angle(dow2degrees)*7/360
    if mean_dow < 0:
        mean_dow = mean_dow + 7
    if mean_dow == 7:
        return 0.0
    return mean_dow
