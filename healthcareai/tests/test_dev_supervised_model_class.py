import unittest

import numpy as np
import pandas as pd

from healthcareai import DevelopSupervisedModel
from healthcareai.tests.helpers import fixture, assertBetween
from healthcareai.common.helpers import count_unique_elements_in_column
from healthcareai.common.healthcareai_error import HealthcareAIError
import healthcareai.pipelines.data_preparation as pipelines

# Set some constants to save errors and typing
CLASSIFICATION = 'classification'
PREDICTED_COLUMN = 'ThirtyDayReadmitFLG'
GRAIN_COLUMN_NAME = 'PatientID'


class TestRandomForestClassification(unittest.TestCase):
    def setUp(self):
        df = pd.read_csv(fixture('DiabetesClincialSampleData.csv'), na_values=['None'])
        # Drop uninformative columns
        df.drop(['PatientID', 'InTestWindowFLG'], axis=1, inplace=True)

        np.random.seed(42)
        clean_df = pipelines.full_pipeline(CLASSIFICATION, PREDICTED_COLUMN, GRAIN_COLUMN_NAME,
                                           impute=True).fit_transform(df)
        self.trainer = DevelopSupervisedModel(clean_df, CLASSIFICATION, PREDICTED_COLUMN)
        self.trainer.train_test_split()

    def test_random_forest_no_tuning(self):
        rf = self.trainer.random_forest_2(trees=200, randomized_search=False)
        assertBetween(self, 0.8, 0.97, rf.metrics['roc_auc'])

    def test_random_forest_tuning(self):
        rf = self.trainer.random_forest_2(trees=200, randomized_search=True)
        assertBetween(self, 0.8, 0.97, rf.metrics['roc_auc'])

    def test_random_foarest_tuning_2_column_raises_error(self):
        cols = ['ThirtyDayReadmitFLG', 'SystolicBPNBR', 'LDLNBR']
        df = pd.read_csv(fixture('DiabetesClincialSampleData.csv'),
                         na_values=['None'],
                         usecols=cols)

        np.random.seed(42)
        clean_df = pipelines.full_pipeline(CLASSIFICATION, PREDICTED_COLUMN, GRAIN_COLUMN_NAME,
                                           impute=True).fit_transform(df)
        trainer = DevelopSupervisedModel(clean_df, CLASSIFICATION, PREDICTED_COLUMN)

        trainer.train_test_split()

        self.assertRaises(HealthcareAIError, trainer.random_forest_2, trees=200, randomized_search=True)

class TestLinearDevTuneFalse(unittest.TestCase):
    def test_linear_dev_tune_false(self):
        df = pd.read_csv(fixture('DiabetesClincialSampleData.csv'), na_values=['None'])

        # Drop uninformative columns
        df.drop(['PatientID', 'InTestWindowFLG'], axis=1, inplace=True)

        np.random.seed(42)
        clean_df = pipelines.full_pipeline(CLASSIFICATION, PREDICTED_COLUMN, GRAIN_COLUMN_NAME,
                                           impute=True).fit_transform(df)
        o = DevelopSupervisedModel(clean_df, CLASSIFICATION, PREDICTED_COLUMN)

        o.train_test_split()
        o.linear(cores=1)

        # self.assertAlmostEqual(np.round(o.au_roc, 2), 0.67000)
        assertBetween(self, 0.66, 0.69, o.au_roc)


class TestHelpers(unittest.TestCase):
    def test_class_counter_on_binary(self):
        df = pd.read_csv(fixture('DiabetesClincialSampleData.csv'), na_values=['None'])
        df.dropna(axis=0, how='any', inplace=True)
        result = count_unique_elements_in_column(df, 'ThirtyDayReadmitFLG')
        self.assertEqual(result, 2)

    def test_class_counter_on_many(self):
        df = pd.read_csv(fixture('DiabetesClincialSampleData.csv'), na_values=['None'])
        result = count_unique_elements_in_column(df, 'PatientEncounterID')
        self.assertEqual(result, 1000)


if __name__ == '__main__':
    unittest.main()
