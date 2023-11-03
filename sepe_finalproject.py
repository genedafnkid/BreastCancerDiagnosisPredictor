# -*- coding: utf-8 -*-
"""Sepe_FinalProject

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WUR5XCIPXTZgjv6b_yj7BiOPQ16IPVzd

**GENERAL PROBLEM**

In the context of breast cancer diagnosis, the challenge is to develop an accurate and reliable predictive model that can assist medical professionals in classifying tumors as malignant or benign based on various diagnostic features. The objective is to enhance the diagnostic process, ensuring early detection of malignant tumors and reducing unnecessary interventions for benign cases.

---


# **DATA GATHERING**

This is the part where the dataset will be loaded into the notebook. The source of the dataset is from Kaggle. The dataset used in this project contains essential features related to tumor characteristics. These features are crucial in the diagnosis of breast cancer. Understanding these features and their significance is vital for medical professionals and researchers working in oncology.
"""

!pip install -U -q PyDrive

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

#Drive link for the data: https://drive.google.com/file/d/1dRni2rXX5cdgckwHQLKreS3QHKnX1A1-/view?usp=sharing
# Authenticate and create the PyDrive client
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

file_id = '1dRni2rXX5cdgckwHQLKreS3QHKnX1A1-'
downloaded = drive.CreateFile({'id': file_id})
downloaded.GetContentFile('data.csv')
df = pd.read_csv('data.csv')

#df = pd.read_csv("data.csv", sep=",")
df

"""# **CLEANING THE DATA**

In this step, we will verify that all columns have appropriate data types, ensuring consistency and accuracy in our analysis. By confirming the correct data types (such as integer, and floats for ratios and averages), we guarantee meaningful calculations and visualizations.
"""

#remove the null values in my data set
df.dropna()

df.reset_index()

#Remove duplicated datas in the set
df.drop_duplicates()

df.info()

# Format columns to have 2 decimal places and replace missing values with 'NA'
df.iloc[:,2:33].applymap(lambda x: f'{x:.4f}' if not pd.isnull(x) else 'NA')

# List of columns to be dropped
columns_to_drop = ['id','radius_se', 'texture_se', 'perimeter_se', 'area_se',
                   'smoothness_se', 'compactness_se', 'concavity_se',
                   'concave points_se', 'symmetry_se', 'fractal_dimension_se',
                   'radius_worst', 'texture_worst', 'perimeter_worst',
                   'area_worst', 'smoothness_worst', 'compactness_worst',
                   'concavity_worst', 'concave points_worst', 'symmetry_worst',
                   'fractal_dimension_worst']

# Drop the specified columns from the DataFrame
df.drop(columns=columns_to_drop, inplace=True)

"""Concentrating on mean-related features indicates a specific area of interest, possibly aiming to understand the average tumor characteristics. This focused approach enables a deep dive into understanding the central tendencies of the tumor features, providing valuable insights for further analysis and modeling.

---


# **EXPLORATORY DATA ANALYSIS**

**Data Science Questions:**

1. **Model Accuracy and Reliability**
- Can machine learning algorithms accurately classify breast tumors as malignant or benign? What is the most reliable model for this classification task?

2. **Feature Importance and Interpretability**
- Which diagnostic features contribute significantly to the accurate classification of breast tumors? Understanding the importance of these features can aid medical professionals in their decision-making process.

3. **Generalizability and Real-World Applicability**
- How well does the developed model generalize to unseen data, and what are the practical implications of its application in real-world clinical settings? Assessing the model's performance beyond the training dataset is crucial for its practical utility.
"""

df.describe()

plt.figure(figsize=(8, 6))
sns.countplot(data=df, x='diagnosis', palette='Set2')
plt.title('Count of Diagnosis (M: Malignant, B: Benign)', fontsize=14)
plt.xlabel('Diagnosis', fontsize=12)
plt.ylabel('Count', fontsize=12)
plt.show()

"""Here, the ratio is approximately 1:1.67 (M:B). While it's not perfectly balanced, it's not highly skewed either. A good rule of thumb is that a class imbalance becomes a significant concern when the ratio of samples in the minority class to the majority class is much less than 1:10. However, to avoid model bias, SMOTE will be utilized in the modeling phase for enhanced accuracy and fairness."""

from sklearn.preprocessing import LabelEncoder
df['diagnosis']=LabelEncoder().fit_transform(df['diagnosis'])

plt.figure(figsize=(12, 10))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0)
plt.title('Feature Correlation Heatmap')
plt.show()

"""##Positive Correlations:##
  1. Radius Mean, Perimeter Mean, Area Mean, and Concave Points Mean: These features show strong positive correlations, which is expected since they are related geometrically. Tumors with larger radius tend to have higher perimeter and area values.
  2. Compactness Mean, Concavity Mean, and Concave Points Mean: These features are positively correlated, suggesting that tumors with higher compactness tend to have more concave shapes.

##Negative Correlations:##
  1. Texture Mean and Smoothness Mean: These features exhibit a negative correlation, indicating that tumors with smoother textures tend to have lower texture mean values.

##Weak Correlations:
  1. Some features show weak correlations (close to 0) with each other, indicating a lack of linear relationship.
"""

selected_features = df.columns[1:11]

for feature in selected_features:
    plt.figure(figsize=(10, 5))

    # Histogram
    plt.subplot(1, 2, 1)
    sns.histplot(data=df, x=feature, hue='diagnosis', element="step", common_norm=False, kde=True, palette='Set2')
    plt.title(f'Histogram of {feature}')

    # Boxplot
    plt.subplot(1, 2, 2)
    sns.boxplot(data=df, x='diagnosis', y=feature, palette='Set2')
    plt.title(f'Boxplot of {feature}')

    plt.tight_layout()
    plt.show()

"""##Radius Mean:

- Benign (B) Tumors: The histogram shows a right-skewed distribution, indicating that benign tumors tend to have lower mean radius values. This suggests that smaller tumors are more likely to be benign.
- Malignant (m) Tumors: The histogram displays a relatively normal distribution with a peak around a lower radius mean, indicating that malignant tumors are generally larger in size.

##Concave Points Mean:

- Benign (M) Tumors: The histogram demonstrates a right-skewed distribution, implying that benign tumors often have less varied texture mean values. This suggests increased complexity in the texture of malignant tumors.
- Malignant (B) Tumors: The histogram shows a more concentrated distribution around higher mean values, indicating that benign tumors have a more consistent concave points.

##Perimeter Mean:

- Benign (B) Tumors: The histogram is right-skewed, indicating that benign tumors tend to have lower mean perimeter values. This aligns with the observation from the Radius Mean, suggesting irregular and larger-shaped malignant tumors.
- Malignant (M) Tumors: The histogram is relatively normal but broader, indicating that malignant tumors have a higher and more consistent perimeter compared to malignant tumors.

##Area Mean:

- Benign (B) Tumors: The histogram is right-skewed, indicating that benign tumors tend to have lower mean area values. This reiterates the trend observed in Radius Mean and Perimeter Mean, emphasizing the smaller size of benign tumors.
- Malignant (M) Tumors: The histogram shows a relatively normal distribution, centered around higher area mean values than benign, suggesting that malignant tumors are generally larger in size and have more variability in their areas.

---


# **DATA MODELING**

In this section, the features selected for the classification task of predicting tumor malignancy are crucial in capturing the nuances of the underlying data. The following features were chosen based on their known relevance in the domain of oncology and extensive research in the field:

- Concave Points Mean
- Radius Mean
- Perimeter Mean
- Area Mean

**Classifier Selection and Training**

- Decision Tree Classifier: A decision tree model was chosen due to its interpretability and ability to capture non-linear relationships in the data.

- MLP Classifier: A Multi-Layer Perceptron was chosen for its capacity to learn complex patterns in the data.

- Random Forest Classifier: A Random Forest model, an ensemble of decision trees, was selected for its robustness and ability to handle noisy data.

Data Splitting: The dataset was divided into a training set and a testing set. The training set (usually 80% of the data) was used to train the models, and the testing set (remaining 20% of the data) was kept separate to evaluate the models' performance.
"""

# Import necessary libraries
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_val_score, StratifiedKFold
from imblearn.over_sampling import SMOTE


# Select features and target variable
features = ['radius_mean', 'concave points_mean', 'perimeter_mean', 'area_mean']
X = df[features]
y = df['diagnosis']

# Split the data into training and testing sets with stratification
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Apply SMOTE to balance the classes in the training set
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# Initialize models
decision_tree = DecisionTreeClassifier(random_state=42)
mlp_classifier = MLPClassifier(random_state=42)
random_forest = RandomForestClassifier(random_state=42)

# Train models
decision_tree.fit(X_resampled, y_resampled)
mlp_classifier.fit(X_resampled, y_resampled)
random_forest.fit(X_resampled, y_resampled)

# Predictions
y_pred_decision_tree = decision_tree.predict(X_test)
y_pred_mlp = mlp_classifier.predict(X_test)
y_pred_random_forest = random_forest.predict(X_test)

"""Handling Class Imbalance: Due to the imbalanced nature of the dataset with more benign cases than malignant cases, Synthetic Minority Over-sampling Technique (SMOTE) was applied on the training set. SMOTE helps balance the class distribution by creating synthetic samples of the minority class.

**Evaluation Metrics**

**Precision**: Precision is the ratio of correctly predicted positive observations to the total predicted positives. A higher precision indicates fewer false positives.

**Recall**: Recall, or sensitivity, calculates the ratio of correctly predicted positive observations to all the actual positives. Higher recall indicates fewer false negatives.

**F1-Score**: The F1-score is the harmonic mean of precision and recall. It provides a balance between precision and recall. A higher F1-score indicates a better balance between precision and recall.
"""

# Calculate classification metrics
accuracy_decision_tree = accuracy_score(y_test, y_pred_decision_tree)
precision_decision_tree = precision_score(y_test, y_pred_decision_tree, pos_label=0)
recall_decision_tree = recall_score(y_test, y_pred_decision_tree, pos_label=0)
f1_score_decision_tree = f1_score(y_test, y_pred_decision_tree, pos_label=0)

accuracy_mlp = accuracy_score(y_test, y_pred_mlp)
precision_mlp = precision_score(y_test, y_pred_mlp, pos_label=0)
recall_mlp = recall_score(y_test, y_pred_mlp, pos_label=0)
f1_score_mlp = f1_score(y_test, y_pred_mlp, pos_label=0)

accuracy_random_forest = accuracy_score(y_test, y_pred_random_forest)
precision_random_forest = precision_score(y_test, y_pred_random_forest, pos_label=0)
recall_random_forest = recall_score(y_test, y_pred_random_forest, pos_label=0)
f1_score_random_forest = f1_score(y_test, y_pred_random_forest, pos_label=0)

print("Decision Tree Metrics:")
print(f"Accuracy: {accuracy_decision_tree:.2f}")
print(f"Precision: {precision_decision_tree:.2f}")
print(f"Recall: {recall_decision_tree:.2f}")
print(f"F1 Score: {f1_score_decision_tree:.2f}")

print("\nMLP Metrics:")
print(f"Accuracy: {accuracy_mlp:.2f}")
print(f"Precision: {precision_mlp:.2f}")
print(f"Recall: {recall_mlp:.2f}")
print(f"F1 Score: {f1_score_mlp:.2f}")

print("\nRandom Forest Metrics:")
print(f"Accuracy: {accuracy_random_forest:.2f}")
print(f"Precision: {precision_random_forest:.2f}")
print(f"Recall: {recall_random_forest:.2f}")
print(f"F1 Score: {f1_score_random_forest:.2f}")

"""**Cross Validation**

Stratified k-fold, was utilized to assess model performance comprehensively. Mean accuracy, derived from this method, provided a consolidated view of how well the models generalized across various dataset subsets. Higher mean accuracy scores indicated better overall predictive capability, aiding in reliable model selection.
"""

# Create a decision tree classifier
classifier = DecisionTreeClassifier(random_state=42)

# Define the cross-validation strategy (Stratified K-Folds for classification tasks)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Perform cross-validation and get accuracy scores
accuracy_scores = cross_val_score(classifier, X_resampled, y_resampled, cv=cv, scoring='accuracy')

# Print the accuracy scores for each fold
print("Accuracy Scores for Each Fold:", accuracy_scores)

# Calculate and print the mean accuracy score
mean_accuracy = accuracy_scores.mean()
print("Decision Tree Mean Accuracy:", mean_accuracy)

# Create an MPL classifier
classifier = MLPClassifier(random_state=42)

# Define the cross-validation strategy (Stratified K-Folds for classification tasks)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Perform cross-validation and get accuracy scores
accuracy_scores = cross_val_score(classifier, X_resampled, y_resampled, cv=cv, scoring='accuracy')

# Print the accuracy scores for each fold
print("Accuracy Scores for Each Fold:", accuracy_scores)

# Calculate and print the mean accuracy score
mean_accuracy = accuracy_scores.mean()
print("MLP Mean Accuracy:", mean_accuracy)

# Create a random forest classifier (or any other classifier you want to use)
classifier = RandomForestClassifier(random_state=42)

# Define the cross-validation strategy (Stratified K-Folds for classification tasks)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Perform cross-validation and get accuracy scores (or other metrics you're interested in)
accuracy_scores = cross_val_score(classifier, X_resampled, y_resampled, cv=cv, scoring='accuracy')

# Print the accuracy scores for each fold
print("Accuracy Scores for Each Fold:", accuracy_scores)

# Calculate and print the mean accuracy score
mean_accuracy = accuracy_scores.mean()
print("Random Forest Mean Accuracy:", mean_accuracy)

"""#EVALUATION"""

# Create comparison graphs
models = ['Decision Tree', 'MLP', 'Random Forest']
accuracy_scores = [accuracy_decision_tree, accuracy_mlp, accuracy_random_forest]
precision_scores = [precision_decision_tree, precision_mlp, precision_random_forest]
recall_scores = [recall_decision_tree, recall_mlp, recall_random_forest]
f1_scores = [f1_score_decision_tree, f1_score_mlp, f1_score_random_forest]

plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.bar(models, accuracy_scores, color='skyblue')
plt.ylabel('Accuracy')
plt.title('Accuracy Comparison')

plt.subplot(2, 2, 2)
plt.bar(models, precision_scores, color='lightgreen')
plt.ylabel('Precision')
plt.title('Precision Comparison')

plt.subplot(2, 2, 3)
plt.bar(models, recall_scores, color='lightcoral')
plt.ylabel('Recall')
plt.title('Recall Comparison')

plt.subplot(2, 2, 4)
plt.bar(models, f1_scores, color='lightsalmon')
plt.ylabel('F1 Score')
plt.title('F1 Score Comparison')

plt.tight_layout()
plt.show()

"""- **Decision Tree** performed consistently well across all metrics, with a high F1 score and mean accuracy.
- **MLP demonstrated** a balanced performance but with a slightly lower accuracy and F1 score compared to the Decision Tree.
- **Random Forest** outperformed the other models in terms of recall, indicating its ability to identify malignant cases effectively.

"""

# Calculate the confusion matrix for each model
confusion_matrix_decision_tree = confusion_matrix(y_test, y_pred_decision_tree)
confusion_matrix_mlp = confusion_matrix(y_test, y_pred_mlp)
confusion_matrix_random_forest = confusion_matrix(y_test, y_pred_random_forest)

# Define class labels
class_labels = ['Benign', 'Malignant']

# Plot confusion matrix for Decision Tree
plt.figure(figsize=(12, 4))
plt.subplot(1, 3, 1)
sns.heatmap(confusion_matrix_decision_tree, annot=True, fmt='g', cmap='Blues',
            xticklabels=class_labels, yticklabels=class_labels)
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix - Decision Tree')

# Plot confusion matrix for MLP
plt.subplot(1, 3, 2)
sns.heatmap(confusion_matrix_mlp, annot=True, fmt='g', cmap='Blues',
            xticklabels=class_labels, yticklabels=class_labels)
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix - MLP')

# Plot confusion matrix for Random Forest
plt.subplot(1, 3, 3)
sns.heatmap(confusion_matrix_random_forest, annot=True, fmt='g', cmap='Blues',
            xticklabels=class_labels, yticklabels=class_labels)
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix - Random Forest')

plt.tight_layout()
plt.show()

"""**Decision Tree Confusion Matrix:**

- True Positives (TP): 38 - The model correctly predicted 38 malignant cases.
- True Negatives (TN): 64 - The model correctly predicted 64 benign cases.
- False Positives (FP): 8 - The model incorrectly predicted 8 benign cases as malignant.
- False Negatives (FN): 4 - The model incorrectly predicted 4 malignant cases as benign.


**MLP Confusion Matrix:**

- True Positives (TP): 28 - The model correctly predicted 28 malignant cases.
- True Negatives (TN): 68 - The model correctly predicted 68 benign cases.
- False Positives (FP): 4 - The model incorrectly predicted 4 benign cases as malignant.
- False Negatives (FN): 14 - The model incorrectly predicted 14 malignant cases as benign.


**Random Forest Confusion Matrix:**

- True Positives (TP): 38 - The model correctly predicted 38 malignant cases.
- True Negatives (TN): 65 - The model correctly predicted 65 benign cases.
- False Positives (FP): 7 - The model incorrectly predicted 7 benign cases as malignant.
- False Negatives (FN): 4 - The model incorrectly predicted 4 malignant cases as benign.

**CONCLUSION**

**Question 1: Model Accuracy and Reliability**

Machine learning algorithms, specifically Decision Tree, MLP, and Random Forest, were applied to classify breast tumors as malignant or benign. The models demonstrated varying levels of accuracy, precision, recall, and F1 score

Considering the metrics, the Random Forest model stands out as the most reliable for classifying breast tumors due to its balanced accuracy, precision, recall, and F1 score.

**Question 2: Feature Importance and Interpretability**

Analyzing the models, key diagnostic features contributing significantly to accurate classification include radius_mean, concave points_mean, perimeter_mean, and area_mean. These features are crucial in distinguishing between malignant and benign tumors. Understanding the importance of these features is vital for medical professionals, as it provides insights into the specific tumor characteristics influencing the diagnosis.

**Question 3: Generalizability and Real-World Applicability**

The models' ability to identify True Positives and True Negatives showcases their potential in real-world clinical applications. For instance, they can assist medical professionals in confirming malignancy or benignity, thereby guiding treatment decisions. However, it's crucial to note the occurrence of False Positives and False Negatives, which might lead to misdiagnosis. Continuous monitoring and refinement of the models are necessary to enhance their real-world applicability.

Based on the provided metrics and analyses, the Random Forest model appears to be the most suitable for classifying breast tumors as malignant or benign. It consistently demonstrated high accuracy, precision, recall, and F1-score. Additionally, its mean accuracy across cross-validation folds was notably superior, indicating robust performance across different subsets of the data. Random Forest's ability to balance precision, recall, and overall accuracy makes it a strong candidate for  classification task.

**Recommendation:**

**Data Augmentation and Feature Engineering:**

Considering the dropped columns contain various measurements at different scales, explore the possibility of creating new composite features or normalizing the existing ones before dropping them. Feature engineering techniques like combining related features or deriving ratios can sometimes reveal hidden patterns and enhance the model's predictive power. Additionally, consider data augmentation techniques, such as rotation, scaling, or flipping for image data, to artificially increase the dataset's size. Augmented data can enrich the learning process, leading to more robust models.

**References**

**Data Sources:**

[Kaggle Dataset: Breast Cancer Wisconsin (Diagnostic) Data Set](https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data?fbclid=IwAR00bhEtLy0wA1r4H-kpeuHxp98AemR1owSkPtuQKRWQ9g7AaTvGYLj8THs)


**Code Sources:**

[Scikit-Learn Documentation](https://scikit-learn.org/stable/documentation.html)

[Pandas Documentation](https://pandas.pydata.org/pandas-docs/stable/index.html)

[Matplotlib Documentation](https://matplotlib.org/stable/contents.html)

**Literature:**

Breiman, L. (2001). Random forests. Machine learning, 45(1), 5-32.

Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. Journal of artificial intelligence research, 16, 321-357.

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., ... & Vanderplas, J. (2011). Scikit-learn: Machine learning in Python. Journal of machine learning research, 12(Oct), 2825-2830.
"""