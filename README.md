# recsys

## Рекомендательная система для интернет магазина Instacart

**Установка пакета recsys**

```bash
cd recsys
pip install -e .
```


**Обучение и использование модели рекомендательной системы**
```python
import pandas as pd
from recsys import predict, train

products = pd.read_csv('products.csv.zip')
transactions = pd.read_csv('transactions.csv.zip')

model = train(transactions, products)

predict(user_id=1, k=10, model)
```
