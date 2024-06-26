# -*- coding: utf-8 -*-
"""sales_prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YLy2U1F68hTFanw-KAykarO0PsqQ8JYY

# libraries and initializing spark session
"""

#loading the libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dask.dataframe as dd

import seaborn as sns

#from google.colab import files
#uploaded = files.upload()
from google.colab import drive
drive.mount('/content/drive')

# import findspark
# findspark.init()
# import pyspark
# from pyspark.sql import SparkSession
# spark = SparkSession.builder.appName('sertis')\
# .config('spark-master', 'local')\
# .getOrCreate()
# from pyspark.sql.functions import col, lit


# Install Java
!apt-get install openjdk-8-jdk-headless -qq > /dev/null

# Install PySpark
!pip install pyspark

# Initialize Spark Session
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("sertis") \
    .getOrCreate()

from pyspark.sql.functions import col, lit
from pyspark import SparkContext, SparkConf
from pyspark.ml import Pipeline
from pyspark.ml.linalg import DenseMatrix, Vectors
from pyspark.ml.stat import Correlation
from pyspark.mllib.stat import Statistics
from typing import List, Tuple, Dict
from pyspark.sql import Row, DataFrame
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier, DecisionTreeClassifier
from pyspark.ml.feature import VectorAssembler, StringIndexer, StandardScaler
from pyspark.ml.evaluation import BinaryClassificationEvaluator, RegressionEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml.regression import RandomForestRegressor
from sklearn.metrics import confusion_matrix
from pyspark.sql.functions import when, col
from pyspark.sql.functions import mean
from pyspark.sql.functions import col, round
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.regression import DecisionTreeRegressor

"""# preprocessing"""

#loading the training dataset

file_path = '/content/drive/My Drive/train.csv'
df = spark.read.csv(file_path, header=True, inferSchema=True)
df.printSchema()
df.show(5)


#unused codes:
# df = dd.read_csv(file_path)
#df = ddf.compute()
# print(df.head())
# row_count = len(df)
# print("Total rows:", row_count)

#for first round of data cleaning, i will remove the id column as it does not affectr the target variable at all and is simply an identifier
#i will be removing all rows with negative values in unit_sales due to returning of products
#i will all fill the empty cells in the onpromotion tab
df1 = df.drop('id')
df1 = df1.filter(df['unit_sales'] >= 0)
df1.show(5)


#unused codes:
# df = pd.read_csv(file_path)
# df.drop(columns=['id'], inplace=True)
# df.drop(df.loc[df['unit_sales'] < 0].index, inplace=True)
# df['onpromotion'].fillna('no', inplace=True)

"""from the start, i have been using pandas and kept expereincing lack of ram.
after digging around, i finally realised that this problem requires parallel computing and hence requires me to use libraires like dask or spark. i will be using spark to tackle this problem due to it being more familiar to me.
"""

#loading the other datasets
file_path_2 = '/content/drive/My Drive/holidays_events.csv'
df_he = spark.read.csv(file_path_2, header=True, inferSchema=True)
df_he.printSchema()
df_he.show(5)

file_path_3 = '/content/drive/My Drive/oil.csv'
df_o = spark.read.csv(file_path_3, header=True, inferSchema=True)
df_o.printSchema()
df_o.show(5)

file_path_4 = '/content/drive/My Drive/items.csv'
df_i = spark.read.csv(file_path_4, header=True, inferSchema=True)
df_i.printSchema()
df_i.show(5)

file_path_5 = '/content/drive/My Drive/stores.csv'
df_s = spark.read.csv(file_path_5, header=True, inferSchema=True)
df_s.printSchema()
df_s.show(5)

file_path_6 = '/content/drive/My Drive/transactions.csv'
df_t = spark.read.csv(file_path_6, header=True, inferSchema=True)
df_t.printSchema()
df_t.show(5)


# # unused code:
# file_path_2 = '/content/drive/My Drive/holidays_events.csv'
# df_he = pd.read_csv(file_path_2)
# print(df_he.head())
# #row_count = len(df_he)
# #print("Total rows:", row_count)

# file_path_3 = '/content/drive/My Drive/oil.csv'
# df_o = pd.read_csv(file_path_3)
# print(df_o.head())
# #row_count = len(df_o)
# #print("Total rows:", row_count)

# file_path_4 = '/content/drive/My Drive/items.csv'
# df_i = pd.read_csv(file_path_4)
# print(df_i.head())
# #row_count = len(df_i)
# #print("Total rows:", row_count)

# file_path_5 = '/content/drive/My Drive/stores.csv'
# df_s = pd.read_csv(file_path_5)
# print(df_s.head())
# #row_count = len(df_s)
# #print("Total rows:", row_count)

# file_path_6 = '/content/drive/My Drive/transactions.csv'
# df_t = pd.read_csv(file_path_6)
# print(df_t.head())
# #row_count = len(df_t)
# #print("Total rows:", row_count)

"""Exploring the datasets"""

#converting to pandas dataset
pd_he = df_he.toPandas()
#visualising the data
sns.pairplot(pd_he)
plt.suptitle('days transfered', y=1.02)
plt.show()

#converting to pandas dataset
pd_o = df_o.toPandas()
#visualising the data
sns.pairplot(pd_o)
plt.suptitle('daily oil prices', y=1.02)
plt.show()

#converting to pandas dataset
pd_i = df_i.toPandas()
#visualising the data
sns.pairplot(pd_i)
plt.suptitle('Scatter Matrix', y=1.02)
plt.show()

#converting to pandas dataset
pd_s = df_s.toPandas()
#visualising the data
sns.pairplot(pd_s)
plt.suptitle('Scatter Matrix', y=1.02)
plt.show()

#converting to pandas dataset
pd_t = df_t.toPandas()
#visualising the data
sns.pairplot(pd_t)
plt.suptitle('Scatter Matrix', y=1.02)
plt.show()

#adjusting the holiday events df
#create a new col called hol_true, by removing the transfered and type columns.
#if the transfered value is true, hol_true will return 0
#if the type is transfer or additional, hol_true will return 1
df_he = df_he.withColumn('hol_true',
                        when(df_he['type'] == 'Transfer', 1)
                        .when(df_he['transferred'] == 'TRUE', 0)
                        .otherwise(1))
df_he = df_he.drop('transferred', 'type')
df_he.show(5)


# unused code
# def create_new_column(row):
#     if row['type'] == "Transfer":
#       return 1
#     elif row['transferred'] == 'TRUE':
#       return 0
#     else:
#       return 1

# df_he['hol_true'] = df_he.apply(create_new_column, axis=1)
# df_he.drop(columns=['transferred'], inplace=True)
# df_he.drop(columns=['type'], inplace=True)
# print(df_he.head())

#cleaning the oil dataframe
mean_value = df_o.select(mean('dcoilwtico')).collect()[0][0]
print(mean_value)
df_o = df_o.na.fill({'dcoilwtico': mean_value})
df_o.show(5)


#unused code
# df_o['dcoilwtico'].fillna(df_o['dcoilwtico'].mean(), inplace=True)
# print(df_o.head())

#making sure that a specific store is affected by a holiday
#national is celebrated by all
#region is celebrated by locals in the state
#local oonly celebrated within the city
# part 1
df2 = df1.join(df_s, on='store_nbr', how='inner')
df2.show(5)


# unused code
# mdf_v1 = pd.merge(df, df_s, on='store_nbr', how='inner')
# print(mdf_v1.column)

# part 2
df3 = df2.join(df_he, on='date', how='inner')
df3.show(5)

# part 2
df4 = df3.withColumn('holiday',
                     when((col('hol_true') == 1) & (col('locale') == 'National'), 1)
                     .when((col('hol_true') == 1) & (col('locale') == 'Regional') & (col('locale_name') == col('state')), 1)
                     .when((col('hol_true') == 1) & (col('locale') == 'Local') & (col('locale_name') == col('city')), 1)
                     .otherwise(0))
df4 = df4.drop('hol_true')
df4.show(5)


# unused code
# def create_new_column(row):
#     if row['hol_true'] == 1:
#       if row['locale'] == 'National':
#         return 1
#       elif row['locale'] == 'Regional':
#         if row['locale_name'] == row['state']:
#           return 1
#         else:
#           return 0
#       elif row['locale'] == 'Local':
#         if row['locale_name'] == row['city']:
#           return 1
#         else:
#           return 0
#       else:
#         return 0
#     else:
#       return 0

# mdf_v1['holiday'] = mdf_v1.apply(create_new_column, axis=1)

# #including special events like wage day and earthquake for a few weeks(6 weeks sound like a reasonable value)
# def create_new_column(row):
#   if row['date'] < pd.Timestamp(''):
#     return 1
#   elif row['date'] >= pd.Timestamp(''):
#     return 1
#   else:
#     return 0

#aggregating the dataframes
df5 = df4.join(df_o, on='date', how='inner')
df5.show(5)

df6 = df5.join(df_i, on='item_nbr', how='inner')
df6.show(5)

df7 = df6.join(df_t, on=['date', 'store_nbr'], how='inner')
df7.show(5)


# unused code
# mdf_v2 = pd.merge(mdf_v1, df_o, on='date', how='inner')
# print(mdf_v2.columns)

# mdf_v3 = pd.merge(mdf_v2, df_he, on='date', how='inner')
# print(mdf_v3.columns)

# mdf_v4 = pd.merge(mdf_v3, df_i, on='item_nbr', how='inner')
# print(mdf_v4.columns)

# mdf_v5 = pd.merge(mdf_v4, df_t, on=['date', 'store_nbr'], how='inner')
# print(mdf_v5.column)

# merged_df_v1 = dd.merge(df, ddf_he, on='date', how='inner')
# print(merged_df_v1.columns)
# merged_df_v2 = dd.merge(merged_df_v1, ddf_o, on='date', how='inner')
# print(merged_df_v2.columns)
# merged_df_v3 = dd.merge(merged_df_v2, ddf_i, on='item_nbr', how='inner')
# print(merged_df_v3.columns)
# merged_df_v4 = dd.merge(merged_df_v3, ddf_s, on='store_nbr', how='inner')
# print(merged_df_v4.columns)
# mdf = dd.merge(merged_df_v4, ddf_t, on=['date', 'store_nbr'], how='inner')

#pruning of unrequired columns
#based on personal judgement, i have decided to remove the following columns:
#date, store_nbr, item_nbr as they serve no purpose except as identifiers, and have no toher use sincei am done with aggregation
# i also dropped locale name and locale as it is an identifier to show which country/state celebrates the holday

df_train = df7.drop('date', 'store_nbr','item_nbr','locale_name','locale')
df_train.printSchema()
df_train.show(5)

# to make things easier to work with, i will convert the results of onpromotion to 1 or 0 as it is a boolean
df_train = df_train.withColumn('promotion',
                   when(df['onpromotion'] == True, 1)
                   .otherwise(0))
df_train = df_train.drop('onpromotion')
df_train.printSchema()
df_train.show(5)

"""# further analysis
i will now analyse each individual variable and then determine the corelation
"""

#analysing city
cities = df_train.groupBy('city').count()
cities.show()

"""this graph shows the cities and how many transactions occured within said city. how this may affect unit sales would be difference in lifestyle and preferences of people living in each city, possibly influenced by culture, environment, population age and income group distribution.

i believe city would be a very big factor to predicting unit sales
"""

#analysing state
state = df_train.groupBy('state').count()
state.show()

"""similar explanation to city, i also believe state would play a big role in predicting unit sales"""

#analysing type
storetype = df_train.groupBy('type').count()
storetype.show()

"""this represents the type of store that each transaction occured in. this may possibly influence unit sales due to factors like selection of items and stock. i hypothesise that while it does have an impact on predicting unit sales, i believe that it would not be that significant."""

#analysing cluster
cluster = df_train.groupBy('cluster').count()
cluster.show()

"""i personally have no idea and cannot fully understand what cluster represents due to lack of business and blockchain concept knowledge. however, with my limited understanding, i hypothesise that its degree of impact on predicting unit sales is similar to store type."""

#analysing holiday
holiday = df_train.groupBy('holiday').count()
holiday.show()

"""this represents the number of items being transacted on a holiday. i believe it is an important factor in affecting the unit sales as we tend to go shopping more on holidays, or there may be holiday collection of items and offers that are available only on that holiday"""

#analysing family
family = df_train.groupBy('family').count()
family.show()

"""this represents the categorical family of each item. i believe that it affects unit sales based on culture and consumer behavior. for example, grocery items tend to be purchased more often than deli products"""

#analysing class
itemclass = df_train.groupBy('class').count()
itemclass.show()

"""from my limited understanding of this column, i deduced that it represents the brand of the item. this should be a significant factor as brand affects spending behaviour, such as price of the item or quality/how reknowned an item is."""

#analysing perishable
perishable = df_train.groupBy('perishable').count()
perishable.show()

"""this represents whether an item being transacted is perishable or not. perishable items tend to be bought more often than non perishable items due to reusability and shelf life. i hypthesise that its impact on unit price is not that significant."""

#analysing promotion
promotion = df_train.groupBy('promotion').count()
promotion.show()

"""this represents whether or not an item being transacted is bought on promotion. i hypothesise that its impact is significant as common consumer behaviour would be to purchase more if there is a promotion.

i did not do an analysis on daily oil prices and transactions made in a day as both are conitnuous varaibles. however, here are my deductions:

-daily oil prices should not have that big of an impact on unit sales

-transactions made in a day should have a moderate impact on unit sales.

# data prepping for training and fitting
"""

#indexing categorical volumns

def index_and_drop_columns(df, columns_to_index):
    indexed_df = df
    indexers = []

    for col_name in columns_to_index:
        indexer = StringIndexer(inputCol=col_name, outputCol=f"{col_name}_index")
        indexed_df = indexer.fit(indexed_df).transform(indexed_df)
        indexers.append(indexer)

    columns_to_drop = [col_name for col_name in columns_to_index]
    indexed_df = indexed_df.drop(*columns_to_drop)

    return indexed_df

# apply the function to the train and test dataframes
#cluster is not indexed as it is already in an indexed format
columns_to_index = ['city','state','type','description','family','class']
df_train_indexed = index_and_drop_columns(df_train, columns_to_index)
df_train_indexed.printSchema()
df_train_indexed.show(5)

# #roundinf off unit sales to integers
# df_train_indexed = df_train_indexed.withColumn('unit_sales_int', round(col('unit_sales'), 0))
# df_train_indexed = df_train_indexed.drop('unit_sales')
# df_train_indexed.printSchema()
# df_train_indexed.show(5)

#splitting the data for training and testing
train, test = df_train_indexed.randomSplit([0.8, 0.2], seed=42)

train.printSchema()
train.show(5)
test.printSchema()
test.show(5)

"""i split the dataset on a ratio of 8:2, where 80% of the data will be used for training, and the remaining 20% for testing"""

# #producing correlation heatmap
# plt.figure(figsize=(1,15))
# heatmap = sns.heatmap(train.corr()[['unit_sales']].abs().sort_values(by='unit_sales', ascending=False),
#                       vmin=-1,vmax=1, annot=True, cmap='YlGnBu')

# heatmap.set_title('heatmap of corelatin with unit sales', fontdict={'fontsize':15}, pad=14)

# plt.show()

#producing corelation matrix
# Assemble the features into a single vector column
vector_assembler = VectorAssembler(inputCols=['unit_sales','city_index','state_index','type_index','cluster','description_index','holiday','dcoilwtico','family_index','class_index','perishable','transactions','promotion'], outputCol='features')
df_vector = vector_assembler.transform(train).select('features')

# Calculate the correlation matrix
correlation_matrix = Correlation.corr(df_vector, 'features').head()[0]

# Convert the correlation matrix to a numpy array and print it
correlation_matrix = correlation_matrix.toArray()
print(correlation_matrix)

"""i will not be using z score normalization as i am using tree based regression models"""

# Assemble features into a single vector column
feature_columns = ['city_index', 'state_index', 'type_index', 'cluster',
                   'holiday', 'dcoilwtico', 'family_index', 'perishable',
                   'transactions', 'promotion']
vector_assembler = VectorAssembler(inputCols=feature_columns, outputCol='features')
train_vector = vector_assembler.transform(train).select('features', 'unit_sales')
test_vector = vector_assembler.transform(test).select('features', 'unit_sales')

#unused code
#class_index contains 330 entries which requires at least 330 maxbins. due to technological restrictions of my system, i have decided to exclude class_index
#similarly, description_index contains 80 entires, whcih require at least 80 maxbins.
# feature_columns = ['city_index', 'state_index', 'type_index', 'cluster', 'description_index',
#                    'holiday', 'dcoilwtico', 'family_index', 'class_index', 'perishable',
#                    'transactions', 'promotion']

"""preparing the evaluators. i chose rmse and r2 as my metrics to evaluate performance"""

evaluator_rmse = RegressionEvaluator(labelCol='unit_sales', predictionCol='prediction', metricName='rmse')
evaluator_r2 = RegressionEvaluator(labelCol='unit_sales', predictionCol='prediction', metricName='r2')

"""Due to the presence of a mix of categorical and continuous data in the feature selection, i will be using random forest regression and decision tree regression

# Random Forest
"""

# Initialize the Random Forest Regressor
rf = RandomForestRegressor(featuresCol='features', labelCol='unit_sales', maxBins=33)

# Train the model
rf_model = rf.fit(train_vector)

# Make predictions
predictions_rf = rf_model.transform(test_vector)


# rf = RandomForestClassifier(labelCol='unit_sales_int', featuresCol="features")

# # train the Random Forest model
# rf_model = rf.fit(train_vector)

# # Evaluate the model on the test data
# test_results = rf_model.transform(test)

# Calculate RMSE
rmse_rf = evaluator_rmse.evaluate(predictions_rf)
print("RootMean Squared Error:", rmse_rf)

# Calculate R2
r2_rf = evaluator_r2.evaluate(predictions_rf)
print("R2:", r2_rf)

"""# Decision Tree"""

# Initialize the Decision Tree Regressor
dt = DecisionTreeRegressor(featuresCol='features', labelCol='unit_sales', maxBins=33)

# Train the model
dt_model = dt.fit(train_vector)

# Make predictions on the test data
predictions_dt = dt_model.transform(test_vector)

# Calculate RMSE
rmse_dt = evaluator_rmse.evaluate(predictions_dt)
print("RootMean Squared Error:", rmse_dt)

# Calculate R2
r2_dt = evaluator_r2.evaluate(predictions_dt)
print("R2:", r2_dt)

"""# Afterword
for the random forest method, we have the following results

RootMean Squared Error: 29.237659440452358

R2: 0.031956791080037794

and for decision tree method, we have the following results

RootMean Squared Error: 29.244050805197578

R2: 0.03153351550949024

This shows that for my model, the predictions for both are at least 29 units away from the actual value on average. The r2 value shows that for the RF method, 3.20% of the variance in the target variable is dependent on the features, while it is 3.13% for the decision tree model

In general, the random forest method is better, but both have very underwhelming performance

The underwhelming performance of the model could be explained by the following:

1) the features that i have hypothesised to be used and not used may have been the best features to be used. The model may have experienced over or underfitting.

2) The data cleaning that i performed may be incomplete, resulting in possible misisng values or outliers, affecting the training capabilities of the model.
"""

# #finetuning for RF

# # Define the parameter grid
# paramGrid = (ParamGridBuilder()
#              .addGrid(rf.numTrees, [20, 35, 50])
#              .addGrid(rf.maxDepth, [5, 10, 20])
#              .addGrid(rf.maxDepth, [33, 50, 100])
#              .build())

# # Set up cross-validation
# crossval = CrossValidator(estimator=rf,
#                           estimatorParamMaps=paramGrid,
#                           evaluator=RegressionEvaluator(labelCol='unit_sales', metricName='rmse'),
#                           numFolds=3)

# # Fit the model
# cv_model = crossval.fit(train_vector)

# # Make predictions
# predictions = cv_model.transform(test_vector)

# # Calculate RMSE
# rmse = evaluator_rmse.evaluate(predictions)
# print(" RootMean Squared Error:", rmse)

# # Calculate R2
# r2 = evaluator_r2.evaluate(predictions)
# print("R2:", r2)

# # Print best model parameters
# best_model = cv_model.bestModel
# print("Best Param (numTrees): ", best_model.stages[-1]._java_obj.getNumTrees())
# print("Best Param (maxDepth): ", best_model.stages[-1]._java_obj.getMaxDepth())
# print("Best Param (maxBins): ", best_model.stages[-1]._java_obj.getMaxDepth())

# #finetuning for DT

# # Define the parameter grid
# paramGrid = (ParamGridBuilder()
#              .addGrid(rf.numTrees, [20, 35, 50])
#              .addGrid(rf.maxDepth, [5, 10, 20])
#              .addGrid(rf.maxDepth, [33, 50, 100])
#              .build())

# # Set up cross-validation
# crossval = CrossValidator(estimator=dt,
#                           estimatorParamMaps=paramGrid,
#                           evaluator=RegressionEvaluator(labelCol='unit_sales', metricName='rmse'),
#                           numFolds=3)

# # Fit the model
# cv_model = crossval.fit(train_vector)

# # Make predictions
# predictions = cv_model.transform(test_vector)

# # Calculate RMSE
# rmse = evaluator_rmse.evaluate(predictions)
# print(" RootMean Squared Error:", rmse)

# # Calculate R2
# r2 = evaluator_r2.evaluate(predictions)
# print("R2:", r2)

# # Print best model parameters
# best_model = cv_model.bestModel
# print("Best Param (numTrees): ", best_model.stages[-1]._java_obj.getNumTrees())
# print("Best Param (maxDepth): ", best_model.stages[-1]._java_obj.getMaxDepth())
# print("Best Param (maxBins): ", best_model.stages[-1]._java_obj.getMaxDepth())
