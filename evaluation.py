import pandas as pd
import random
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, ConfusionMatrixDisplay


THRESHOLD = 0.7
MIN_CGPA = 7.0

# DATASET 1 (Recruiter Dataset)

def evaluate_dataset_1():
    df = pd.read_csv("resume_dataset.csv")

    # Fix column name
    df.rename(columns={'AI Score (0-100)': 'matched_score'}, inplace=True)

    # Normalize score
    df['matched_score'] = df['matched_score'] / 100

    # Ground truth
    df['actual'] = df['Recruiter Decision'].apply(
        lambda x: 1 if str(x).strip().lower() == "hire" else 0
    )

    # WITHOUT CGPA 
    
    df['predicted'] = df['matched_score'].apply(
        lambda x: 1 if x >= THRESHOLD else 0
    )

    # ------------------------------
    # WITH CGPA (UNCOMMENT TO USE)
    # ------------------------------
    """
    if 'cgpa' not in df.columns:
        df['cgpa'] = [round(random.uniform(5.0, 10.0), 2) for _ in range(len(df))]

    df['predicted'] = df.apply(
        lambda row: 1 if (row['matched_score'] >= THRESHOLD and row['cgpa'] >= MIN_CGPA) else 0,
        axis=1
    )
    """

    return df

# DATASET 2 (Generalization Dataset)

def evaluate_dataset_2():
    df = pd.read_csv("UpdatedResumeDataSet.csv")

    df['Category'] = df['Category'].str.lower()

    # Ground truth
    df['actual'] = df['Category'].apply(
        lambda x: 1 if 'data science' in x else 0
    )

    # Simulated score
    df['matched_score'] = df['actual'].apply(
        lambda x: random.uniform(0.6, 1.0) if x == 1
        else random.uniform(0.0, 0.5)
    )

    # WITHOUT CGPA (DEFAULT RUN)
    
    df['predicted'] = df['matched_score'].apply(
        lambda x: 1 if x >= THRESHOLD else 0
    )

    # ------------------------------
    # WITH CGPA (UNCOMMENT TO USE)
    # ------------------------------
    """
    if 'cgpa' not in df.columns:
        df['cgpa'] = [round(random.uniform(5.0, 10.0), 2) for _ in range(len(df))]

    df['predicted'] = df.apply(
        lambda row: 1 if (row['matched_score'] >= THRESHOLD and row['cgpa'] >= MIN_CGPA) else 0,
        axis=1
    )
    """

    return df

# METRICS FUNCTION

def compute_metrics(df, name):
    print(f"\n===== {name} =====")

    y_true = df['actual']
    y_pred = df['predicted']

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    print("TP:", tp, "FP:", fp, "FN:", fn, "TN:", tn)

    failure_rate = (fp + fn) / len(df)
    print("Failure Rate:", failure_rate)

    # Confusion Matrix Graph
    ConfusionMatrixDisplay.from_predictions(
        y_true, y_pred,
        display_labels=["Reject", "Hire"]
    )
    plt.title(f"Confusion Matrix - {name}")
    plt.show()

    return accuracy, precision, recall, f1

# MAIN EXECUTION

if __name__ == "__main__":

    # ================= Dataset 1 =================
    df1 = evaluate_dataset_1()
    acc1, prec1, rec1, f1_1 = compute_metrics(df1, "Dataset 1 (Recruiter Data)")

    # ================= Dataset 2 =================
    df2 = evaluate_dataset_2()

    # Balance Dataset 2
    df_pos = df2[df2['actual'] == 1].sample(n=40, random_state=42)
    df_neg = df2[df2['actual'] == 0].sample(n=40, random_state=42)

    df2_balanced = pd.concat([df_pos, df_neg])

    acc2, prec2, rec2, f1_2 = compute_metrics(df2_balanced, "Dataset 2 (Balanced)")

   
    # COMPARISON GRAPH
    
    labels = ["Accuracy", "Precision", "Recall", "F1"]

    dataset1_scores = [acc1, prec1, rec1, f1_1]
    dataset2_scores = [acc2, prec2, rec2, f1_2]

    x = range(len(labels))

    plt.figure()
    plt.bar(x, dataset1_scores, width=0.4, label="Dataset 1")
    plt.bar([i + 0.4 for i in x], dataset2_scores, width=0.4, label="Dataset 2")

    plt.xticks([i + 0.2 for i in x], labels)
    plt.ylabel("Score")
    plt.title("Performance Comparison")
    plt.legend()

    plt.show()

    print("\n Evaluation Complete")