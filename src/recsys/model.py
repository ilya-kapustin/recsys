import pickle

from recsys.features import Features
from recsys.constants import PRODUCT_ID_COL, USER_ID_COL

import pandas as pd
import catboost as cb


def train(transactions: pd.DataFrame, products: pd.DataFrame, dump_path: str = 'dump_path.pickle', **kwargs):
    """Обучение модели рекомендательной системы
    :param transactions: Днные о транзакциях
    :param products: Данные о характеристиках товаров
    :param dump_path: Имя файло для сохранения обученной модели
    :return: Обученна модель
    """
    features = Features(transactions=transactions, products=products)
    model = cb.CatBoostRegressor(
        n_estimators=kwargs.get('n_estimators', 300),
        max_depth=kwargs.get('max_depth', 2),
        thread_count=kwargs.get('thread_count', 4),
        **kwargs
    )
    model.fit(features.get_features(), features.target)
    model_and_features = {
        'model': model,
        'features': features
    }
    with open(dump_path, 'wb') as file:
        pickle.dump(
            model_and_features,
            file
        )
    return model_and_features


def predict(user_id: int, k: int = 10, model_and_features=None, dump_path: str = 'dump_path.pickle'):
    """Предсказание k наиболее релевантных товаров для пользователья user_id
    :param user_id: Идентификатор пользователя
    :param k: Колчиество релевантных товаров
    :param model_and_features: Обученная модель
    :param dump_path: Имя файло c обученной моделью
    :return: k наиболее релевантных товаров
    """
    if model_and_features is None:
        with open(dump_path, 'rb') as file:
            model_and_features = pickle.load(file)
    user_product_features = model_and_features['features'].user_product_features[
        model_and_features['features'].user_product_features[USER_ID_COL].eq(user_id)
    ]
    X = (
            pd.merge(
                pd.merge(
                    user_product_features,
                    model_and_features['features'].user_features,
                    on=USER_ID_COL,
                    how='left'
                ),
                model_and_features['features'].product_features,
                on=PRODUCT_ID_COL,
                how='left'
            )
                .set_index([USER_ID_COL, PRODUCT_ID_COL])
        )
    prediction = pd.Series(model_and_features['model'].predict(X), index=X.index, name='prediction')
    prediction = list(prediction.sort_values(ascending=False).head(k).reset_index()['product_id'])
    if len(prediction) < k:
        list(prediction) + list(model_and_features['features'].product_orders_number[:k-len(prediction)])
    return prediction
