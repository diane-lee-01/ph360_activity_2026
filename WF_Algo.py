#Importing necessary libraries for the work and analysis:
import pandas as pd #calling pandas pd, as usual
import numpy as np #numpy is np 

#importing fuzz and product from their respective packages
from rapidfuzz import fuzz
from itertools import product

#loading in the datasets:
data_1 = pd.read_csv("data/sampledata1.csv", dtype=str).fillna("") #dataset 1
data_2 = pd.read_csv("data/sampledata2.csv", dtype=str).fillna("") #dataset 2

#Creating normalization functions for each column to ensure that the values match up properly: 

#General normalize function
def normalise(s: str) -> str: #normalization 
    return str(s).strip().lower()  #return line
 
#normalization function for ssn column: 
def normalise_ssn(s: str) -> str:
    """Keep digits only.""" #keeping only digits in SSN
    return "".join(c for c in str(s) if c.isdigit()) #return line to give us the SSN
 
 #normalization function for phone number column:
def normalise_phone(s: str) -> str:
    """Keep digits only, drop leading country code 1.""" #keeping digits only, dropping country code 
    digits = "".join(c for c in str(s) if c.isdigit())
    return digits[-10:] if len(digits) >= 10 else digits #returning the phone number
 
#normalization function zipcode column
def normalise_zip(s: str) -> str:
    """Keep first 5 digits.""" #keeping first 5 digits of the zipcode
    digits = "".join(c for c in str(s) if c.isdigit())
    return digits[:5] #returning the 5 digit zipcode
 
#normalization function for date of birth column
def normalise_dob(s: str) -> str:
    """Try to parse to YYYY-MM-DD, return empty string on failure.""" 
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y%m%d"):
        try:
            return pd.to_datetime(s, format=fmt).strftime("%Y-%m-%d")
        except Exception:
            pass
    return normalise(s) #returning the date of birth normalized


#Applying normalization functions to the data: 

#data set 1 application (utilizing the normalization functions): 
data_1["n_first"]  = data_1["first_name"].apply(normalise) #applying the general normalize function 
data_1["n_last"]   = data_1["last_name"].apply(normalise) #applying the general normalize function 
data_1["n_sex"]    = data_1["sex"].apply(normalise) #applying the general normalize function 
data_1["n_zip"]    = data_1["zip_code"].apply(normalise_zip) #zipcode normalization function application
data_1["n_dob"]    = data_1["birth_date"].apply(normalise_dob) #date of birth normalization function application
data_1["n_ssn"]    = data_1["ssn"].apply(normalise_ssn) #ssn normalizaton function application
data_1["n_phone"]  = data_1["phone"].apply(normalise_phone) #phone number normalization applied
data_1["n_email"]  = data_1["email"].apply(normalise) #generalized normalization applied
data_1["n_street"] = (data_1["street_1"] + " " + data_1["street_2"]).apply(normalise) #generalzied normalization applied

#data set 2 application: 
data_2["n_first"]  = data_2["FirstName"].apply(normalise) #applying the general normalize function 
data_2["n_last"]   =data_2["LastName"].apply(normalise)#applying the general normalize function 
data_2["n_sex"]    = data_2["Sex"].apply(normalise) #applying the general normalize function 
data_2["n_zip"]    = data_2["Zip"].apply(normalise_zip)#applying zipcode normalize function 
data_2["n_dob"]    = data_2["DOB"].apply(normalise_dob) #date of birth normalization function
data_2["n_ssn"]    = data_2["SSN"].apply(normalise_ssn) #ssn normalization function
data_2["n_phone"]  = data_2["PhoneNumber"].apply(normalise_phone) #phone number normalization function
data_2["n_email"]  = data_2["EmailAddress"].apply(normalise) #general normalization function
data_2["n_street"] = data_2["Address"].apply(normalise) #general normalization function
 

#now applying blocking, where the code will grouping records by last name, birthyear and zipcode instead of just each patient to each patient to make it easier to match 

#utilizing dataset 1: creating a block key which is a single string to combine records together in groups
data_1["block_key"] = ( 
data_1["n_last"].str[:3] + "|" +
    data_1["n_zip"]          + "|" +
    data_1["n_dob"].str[:4]
)

#now utilizing dataset 2:creating a block key which is a single string to combine records together in groups
data_2["block_key"] = (
    data_2["n_last"].str[:3] + "|" +
    data_2["n_zip"]          + "|" +
    data_2["n_dob"].str[:4]
)
 

#finding the common blocks between the dataset: (utilizing the keys created above) -- overlap between the keys essentially
common_blocks = set(data_1["block_key"]) & set(data_2["block_key"])
print(f"Unique blocks (df1): {data_1['block_key'].nunique()}")
print(f"Unique blocks (df2): {data_2['block_key'].nunique()}")
print(f"Shared blocks:       {len(common_blocks)}")
 
#Builing candidate pairs via blocking:
#code joins the dataset together on the block key value to create candidates for comparison
pairs = (
    data_1[data_1["block_key"].isin(common_blocks)][
        ["UUID","n_first","n_last","n_sex","n_zip","n_dob","n_ssn","n_phone","n_email","n_street"]
    ].assign(key=data_1["block_key"])
    .merge(
        data_2[data_2["block_key"].isin(common_blocks)][
            ["UUID","n_first","n_last","n_sex","n_zip","n_dob","n_ssn","n_phone","n_email","n_street"]
        ].assign(key=data_2["block_key"]),
        on="key",
        suffixes=("_1","_2")
    )
    .drop(columns="key")
)
print(f"Candidate pairs after blocking: {len(pairs):,}")


#Now creating the scores and weighting each score properly as well so that the accuracy can be higher: 

#Weights creation: 
WEIGHTS = {
    "ssn":    0.30,   #ssn weight
    "dob":    0.20, #date of birth weight
    "last":   0.15, #last name weight
    "first":  0.10, #first name weight
    "email":  0.10, #email weight
    "phone":  0.07, #phone number weight
    "zip":    0.04, #zipcode weight
    "sex":    0.02, #sex weight
    "street": 0.02, #street weight
}
#weights sum to 1.0 which is good!
 

#first off - simple yes or no function to make sure that if dob/ssn are same that its a match and you can return the match
def score_exact(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return 1.0 if a == b else 0.0
 
#function for fuzzy matching scoring + provides a value to utilize as well:
def score_fuzzy(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return fuzz.token_sort_ratio(a, b) / 100.0
 
#now a function that computes the scores utilizing the weights provided:
def compute_score(row) -> float:
    s = 0.0
    s += WEIGHTS["ssn"]    * score_exact( row["n_ssn_1"],    row["n_ssn_2"]) #SSN
    s += WEIGHTS["dob"]    * score_exact( row["n_dob_1"],    row["n_dob_2"]) #DOB 
    s += WEIGHTS["last"]   * score_fuzzy( row["n_last_1"],   row["n_last_2"]) #Last name
    s += WEIGHTS["first"]  * score_fuzzy( row["n_first_1"],  row["n_first_2"]) #first name
    s += WEIGHTS["email"]  * score_exact( row["n_email_1"],  row["n_email_2"]) #email 
    s += WEIGHTS["phone"]  * score_exact( row["n_phone_1"],  row["n_phone_2"])#phone number
    s += WEIGHTS["zip"]    * score_exact( row["n_zip_1"],    row["n_zip_2"]) #zipcode
    s += WEIGHTS["sex"]    * score_exact( row["n_sex_1"],    row["n_sex_2"]) #sex
    s += WEIGHTS["street"] * score_fuzzy( row["n_street_1"], row["n_street_2"]) #street name
    return s
 
print("Scoring candidate pairs (this may take a moment)...")
pairs["score"] = pairs.apply(compute_score, axis=1) #scores

#now deciding threshold for tolerance for picks/accuracy: 

THRESHOLD = 0.65 #0.65 threshold chosen
 
#Keeping only pairs that are above the threshold
above = pairs[pairs["score"] >= THRESHOLD].copy()
 
#For each dataset 1 UUID keeping only the highest-scoring dataset 2 match
best_matches = (
    above
    .sort_values("score", ascending=False)
    .drop_duplicates(subset="UUID_1", keep="first")
    [["UUID_1", "UUID_2", "score"]]
    .rename(columns={"UUID_1": "uuid_df1", "UUID_2": "uuid_pred_df2"})
)
 
print(f"\nMatched pairs (score ≥ {THRESHOLD}): {len(best_matches):,}")
 

 #Now last step: calculating accuracy, precision, and recall + true positive/false positive rate: 

#best matches:
best_matches["correct"] = best_matches["uuid_df1"] == best_matches["uuid_pred_df2"]
 

#true and false positive values:
TP = int(best_matches["correct"].sum())
FP = int((~best_matches["correct"]).sum())
 
#False negative rate:
all_df1_uuids = set(data_1["UUID"])
all_df2_uuids = set(data_2["UUID"])
true_positives_possible = all_df1_uuids & all_df2_uuids   # records that SHOULD be matched
matched_df1_uuids = set(best_matches["uuid_df1"])
FN = len(true_positives_possible - matched_df1_uuids)
 

#precison, accuracy, recall
precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0 #precision
recall    = TP / (TP + FN) if (TP + FN) > 0 else 0.0 #recall
accuracy  = TP / len(true_positives_possible) if len(true_positives_possible) > 0 else 0.0 #accuracy
 

#printing all our results:
print("\n─────────────────────────────────────────")
print("  EVALUATION RESULTS")
print("─────────────────────────────────────────")
print(f"  True Positives  (TP): {TP}")
print(f"  False Positives (FP): {FP}")
print(f"  False Negatives (FN): {FN}")
print(f"  Accuracy  : {accuracy:.4f}  ({accuracy*100:.2f}%)")
print(f"  Precision : {precision:.4f}  ({precision*100:.2f}%)")
print(f"  Recall    : {recall:.4f}  ({recall*100:.2f}%)")
print("─────────────────────────────────────────")