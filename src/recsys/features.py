from functools import lru_cache

from recsys.constants import (
    AISLE_ID_COL,
    DEPARTMENT_ID_COL,
    DAY_SINCE_PRIOR_ORDER_COL,
    ORDER_DOW_COL,
    ORDER_HOD_COL,
    ORDER_ID_COL,
    ORDER_NUMBER_COL,
    PRODUCT_ID_COL,
    REORDERED_COL,
    TRANSACTIONS_DTYPES,
    USER_ID_COL
)
from recsys.utils import mean_hod, mean_dow

import numpy as np
import pandas as pd


class Features:
    """
    Генерация признаков
    """

    def __init__(self, transactions, products):
        self.transactions = transactions
        self.products = products

    @property
    @lru_cache
    def user_max_orders(self):
        return self.__get_user_max_orders()

    @property
    @lru_cache
    def target(self):
        return self.__get_target()

    @property
    @lru_cache
    def user_product_features(self):
        return self.__get_user_product_features()

    @property
    @lru_cache
    def product_orders_number(self):
        return self.__get_product_orders_number()

    @property
    @lru_cache
    def user_features(self):
        return self.__get_user_features()

    @property
    @lru_cache
    def product_features(self):
        return self.__get_product_features()

    def get_features(self):

        return (
            pd.merge(
                pd.merge(
                    self.user_product_features,
                    self.user_features,
                    on=USER_ID_COL
                ),
                self.product_features,
                on=PRODUCT_ID_COL
            )
            .set_index([USER_ID_COL, PRODUCT_ID_COL])
            .reindex(self.target.index)
        )

    def __get_user_max_orders(self):
        return (
            self.transactions
            .groupby(by=USER_ID_COL)
            [ORDER_NUMBER_COL]
            .max()
            .astype(TRANSACTIONS_DTYPES[ORDER_NUMBER_COL])
        )

    def __get_product_orders_number(self):
        return (
            self.target
            .reset_index()
            .groupby(PRODUCT_ID_COL)
            ['total_reordered'].sum()
            .sort_values(ascending=False)
            .index
        )

    def __get_target(self):
        target = (
            self.transactions
            .groupby([USER_ID_COL, PRODUCT_ID_COL])
            [REORDERED_COL].sum()
            .reset_index()
            .rename(columns={REORDERED_COL: 'total_reordered'})
            .astype({
                USER_ID_COL: TRANSACTIONS_DTYPES[USER_ID_COL],
                PRODUCT_ID_COL: TRANSACTIONS_DTYPES[PRODUCT_ID_COL]
            })
        )

        target['total_reordered'] = target['total_reordered'] / target[USER_ID_COL].map(self.user_max_orders)
        target = target.set_index([USER_ID_COL, PRODUCT_ID_COL]).squeeze()

        return target

    def __get_user_product_features(self):
        user_product = (
            self.transactions
            .groupby([USER_ID_COL, PRODUCT_ID_COL])
            [ORDER_NUMBER_COL].max()
            .rename('up_order_num')
            .reset_index()
            .astype({
                USER_ID_COL: TRANSACTIONS_DTYPES[USER_ID_COL],
                PRODUCT_ID_COL: TRANSACTIONS_DTYPES[PRODUCT_ID_COL],
                'up_order_num': np.int8,
            })
        )

        user_product_days_since_prior_order_max = (
            self.transactions
            .groupby([USER_ID_COL, PRODUCT_ID_COL])
            [DAY_SINCE_PRIOR_ORDER_COL]
            .max()
            .reset_index()
            .rename(columns={DAY_SINCE_PRIOR_ORDER_COL: 'user_product_days_since_prior_order_max'})
        )

        user_product_max_orders = (
            self.transactions
            .groupby([USER_ID_COL, PRODUCT_ID_COL])
            [ORDER_ID_COL]
            .size()
            .reset_index()
            .rename(columns={ORDER_ID_COL: 'user_item_order_number'})
        )

        user_product = pd.merge(
            user_product,
            user_product_days_since_prior_order_max,
            on=[USER_ID_COL, PRODUCT_ID_COL]
        )
        user_product = pd.merge(
            user_product,
            user_product_max_orders,
            on=[USER_ID_COL, PRODUCT_ID_COL]
        )

        return user_product

    def __get_product_features(self):
        prod_reorder_mean = (
            self.transactions
            .groupby(by=PRODUCT_ID_COL)
             [REORDERED_COL].mean()
            .to_frame('prod_reorder_mean')
            .reset_index()
        )

        products_dt_features = (
            self.transactions
            .groupby(PRODUCT_ID_COL).agg({
                ORDER_DOW_COL: mean_dow,
                ORDER_HOD_COL: mean_hod,
                DAY_SINCE_PRIOR_ORDER_COL: np.mean
            })
            .rename(
                columns={
                    ORDER_DOW_COL: 'mean_order_dow',
                    ORDER_HOD_COL: 'mean_order_hour_of_day',
                    DAY_SINCE_PRIOR_ORDER_COL: 'mean_days_since_prior_order'
                }
            )
            .reset_index()
            .astype({
                'mean_order_dow': np.float32,
                'mean_order_hour_of_day': np.float32,
                'mean_days_since_prior_order': np.float32
            })
        )

        products_features = pd.merge(
            products_dt_features,
            prod_reorder_mean,
            on=PRODUCT_ID_COL
        )

        products_features = pd.merge(
            products_features,
            self.products.set_index(PRODUCT_ID_COL)[[AISLE_ID_COL, DEPARTMENT_ID_COL]],
            on=PRODUCT_ID_COL
        )

        return products_features

    def __get_user_features(self):
        return (
            self.transactions
            .groupby(by=USER_ID_COL)
            [ORDER_NUMBER_COL].max()
            .to_frame('max_orders')
            .reset_index()
            .astype({
                USER_ID_COL: TRANSACTIONS_DTYPES[USER_ID_COL],
                'max_orders': np.int8
            })
        )
