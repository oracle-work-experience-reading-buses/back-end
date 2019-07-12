# Import dependencies
import pandas as pd
import numpy as np

# Load the dataset in a dataframe object and include only four features as mentioned
url = "./../data-science/route_17_data_1-7-July.csv"
df = pd.read_csv(url)
# include = ['Age', 'Sex', 'Embarked', 'Survived'] # Only four features
# df_ = df[include]

# Data Preprocessing
# categoricals = []
# for col, col_type in df_.dtypes.iteritems():
#      if col_type == 'O':
#           categoricals.append(col)
#      else:
#           df_[col].fillna(0, inplace=True)

# df_ohe = pd.get_dummies(df_, columns=categoricals, dummy_na=True)

# Linear Regression classifier
from sklearn.linear_model import LinearRegression
X = df[['prev_stop_delay', 'avg_time_from_prev']].fillna(0)
y = df.punctuality
lr = LinearRegression()
lr.fit(X, y)

# Save your model
from sklearn.externals import joblib
joblib.dump(lr, 'model.pkl')
print("Model dumped!")

# Load the model that you just saved
lr = joblib.load('model.pkl')

# Saving the data columns from training
model_columns = list(X.columns)
joblib.dump(model_columns, 'model_columns.pkl')
print("Models columns dumped!")