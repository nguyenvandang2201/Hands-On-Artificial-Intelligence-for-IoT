"""Chạy code Chương 11 (SF_crime_category_detection.ipynb) dưới dạng script, in kết quả từng ô.

Code xử lý giữ nguyên như notebook của sách; script chỉ thêm phần in kiểm tra
(số phân vùng, kích thước từ vựng, thời gian) và tính thêm accuracy ở cuối.

Cách dùng:
    python run_ch11.py                       # Cách 2: Spark hiện hành, dùng mọi luồng CPU
    python run_ch11.py --master "local[8]"   # Cách 1: Spark 2.4.0 + 8 luồng -> trùng kết quả sách
"""
import argparse
import os
import sys
import time

here = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--csv", default=os.path.join(here, "..", "sf_crime_dataset.csv"))
ap.add_argument("--master", default=None, help='vd "local[8]"; bỏ trống = local[*] như notebook')
ap.add_argument("--driver-mem", default="50g")
ap.add_argument("--executor-mem", default="70g")
args = ap.parse_args()

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
t0 = time.time()

# --- [0]
from pyspark.ml.classification import LogisticRegression as LR
from pyspark.ml.feature import RegexTokenizer, StopWordsRemover, CountVectorizer
from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline
from pyspark.sql.functions import col

from pyspark.sql import SparkSession

builder = SparkSession.builder \
      .appName("Crime Category Prediction") \
      .config("spark.executor.memory", args.executor_mem) \
      .config("spark.driver.memory", args.driver_mem) \
      .config("spark.memory.offHeap.enabled", True) \
      .config("spark.memory.offHeap.size", "16g")
if args.master:
    builder = builder.master(args.master)
spark = builder.getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
print("SPARK VERSION:", spark.version, "| master:", spark.sparkContext.master,
      "| Python:", sys.version.split()[0])

# --- [1]
data = spark.read.format("csv"). \
            options(header="true", inferschema="true"). \
            load(os.path.abspath(args.csv))

# --- [2]
print("[2] columns:", data.columns)
print("    input partitions:", data.rdd.getNumPartitions())

# --- [3]
drop_list = ['Dates', 'DayOfWeek', 'PdDistrict', 'Resolution', 'Address', 'X', 'Y']
data = data.select([column for column in data.columns if column not in drop_list])

# --- [4], [5]
data.show(5)
data.printSchema()
print("    total rows:", data.count(), "| distinct categories:", data.select("Category").distinct().count())

# --- [6], [7]
data.groupBy("Category").count().orderBy(col("count").desc()).show()
data.groupBy("Descript").count().orderBy(col("count").desc()).show()

# --- [8], [9]
regexTokenizer = RegexTokenizer(inputCol="Descript", outputCol="words", pattern="\\W")
add_stopwords = ["http", "https", "amp", "rt", "t", "c", "the"]
stopwordsRemover = StopWordsRemover(inputCol="words", outputCol="filtered").setStopWords(add_stopwords)
countVectors = CountVectorizer(inputCol="filtered", outputCol="features", vocabSize=10000, minDF=5)
label_stringIdx = StringIndexer(inputCol="Category", outputCol="label")

# --- [10], [11]
pipeline = Pipeline(stages=[regexTokenizer, stopwordsRemover, countVectors, label_stringIdx])
pipelineFit = pipeline.fit(data)
dataset = pipelineFit.transform(data)
dataset.show(5)
print("    vocabulary size:", len(pipelineFit.stages[2].vocabulary))

# --- [12]
(trainingData, testData) = dataset.randomSplit([0.7, 0.3], seed=100)
print("Training Dataset Count: " + str(trainingData.count()))
print("Test Dataset Count: " + str(testData.count()))

# --- [13]
logistic_regrssor = LR(maxIter=20, regParam=0.3, elasticNetParam=0)
t1 = time.time()
model = logistic_regrssor.fit(trainingData)
print("    fit seconds: %.1f" % (time.time() - t1))

# --- [14]
predictions = model.transform(testData)
predictions.filter(predictions['prediction'] == 0) \
    .select("Descript", "Category", "probability", "label", "prediction") \
    .orderBy("probability", ascending=False) \
    .show(n=10, truncate=30)

# --- [15]
evaluator = MulticlassClassificationEvaluator(predictionCol="prediction")
print("[15] evaluator.evaluate(predictions) =", evaluator.evaluate(predictions), "(F1 có trọng số)")
print("     accuracy =", evaluator.evaluate(predictions, {evaluator.metricName: "accuracy"}))

print("TOTAL seconds: %.1f" % (time.time() - t0))
spark.stop()
