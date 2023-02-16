ORDER_ID_COL = 'order_id'
USER_ID_COL = 'user_id'
ORDER_NUMBER_COL = 'order_number'
ORDER_DOW_COL = 'order_dow'
ORDER_HOD_COL = 'order_hour_of_day'
DAY_SINCE_PRIOR_ORDER_COL = 'days_since_prior_order'
PRODUCT_ID_COL = 'product_id'
ADD_TO_CART_ORDER_COL = 'add_to_cart_order'
REORDERED_COL = 'reordered'
AISLE_ID_COL = 'aisle_id'
DEPARTMENT_ID_COL = 'department_id'


TRANSACTIONS_DTYPES = {
    ORDER_ID_COL: 'int32',
    USER_ID_COL: 'int32',
    ORDER_NUMBER_COL: 'int8',
    ORDER_DOW_COL: 'int8',
    ORDER_HOD_COL: 'int8',
    DAY_SINCE_PRIOR_ORDER_COL: 'float16',
    PRODUCT_ID_COL: 'int32',
    ADD_TO_CART_ORDER_COL: 'int16',
    REORDERED_COL: 'int8',
}

PRODUCTS_DTYPES = {
    PRODUCT_ID_COL: 'int32',
    AISLE_ID_COL: 'int16',
    DEPARTMENT_ID_COL: 'int8',
}
