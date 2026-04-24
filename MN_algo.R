library(dplyr)
library(stringr)

#Load datasets
dataset1 <- read.csv("sampledata1.csv")
dataset2 <- read.csv("sampledata2.csv")
View(dataset1)
View(dataset2)

# Pre-processing steps ----

# - Count missing values in each column to determine weed out variables for matching algo
missing_counts_1 <- colSums(is.na(dataset1))
missing_counts_2 <- colSums(is.na(dataset2))
missing_counts_1
missing_counts_2


# - Remove spaces before and after names
names_clean <- function(df, first, last) {
  df[[first]] <- trimws(as.character(df[[first]]))
  df[[last]] <- trimws(as.character(df[[last]]))
}

# - Ensure zip codes are 5 digit numbers and remove spaces
zip_clean <- function(df, zipcol) {
  df[[zipcol]] <- trimws(as.character(df[[zipcol]]))
  df[[zipcol]] <- gsub("[^0-9]", "", df[[zipcol]])      
  df[[zipcol]] <- substr(paste0(df[[zipcol]], "00000"), 1, 5)  
}

# - Ensure all dates are in a standard format and remove spaces
date_clean <- function(df, birthcol) {
  df[[birthcol]] <- trimws(as.character(df[[birthcol]]))
  df[[birthcol]] <- format(as.Date(df[[birthcol]], format = "%Y-%m-%d"), "%Y-%m-%d")
}

# - Check the fill rate of columns of interest (I chose these variables instead of SSN because I noticed this variable was not filled out for everyone in dataset2, so may be inconsistent between files)
fill_rate <- function(df, col) {
  x <- df[[col]]
  mean(!is.na(x) & x != "") * 100
}

names_clean(dataset1, "first_name", "last_name")
names_clean(dataset2, "FirstName", "LastName")

zip_clean(dataset1, "zip_code")
zip_clean(dataset2, "Zip")

date_clean(dataset1, "birth_date")
date_clean(dataset2, "DOB")

fill_rate(dataset2, "Zip")

# Deterministic matching based on first initial, last initial, DOB and zip code ----

# - Create variables for first and last initials
dataset1 <- dataset1 %>%
  mutate(
    first_initial = str_sub(first_name, 1, 1),
    last_initial  = str_sub(last_name, 1, 1)
  )

dataset2 <- dataset2 %>%
  mutate(
    first_initial = str_sub(FirstName, 1, 1),
    last_initial  = str_sub(LastName, 1, 1)
  )

# - Create joined table
dataset1_linked <- dataset1 %>%
  left_join(
    dataset2 %>%
      select(first_initial, last_initial, DOB, Zip, UUID),
    by = c(
      "first_initial" = "first_initial",
      "last_initial" = "last_initial",
      "birth_date" = "DOB",
      "zip_code" = "Zip"
    ), 
    suffix = c("_dataset1", "_dataset2")
  )
View(dataset1_linked)

# Compute accuracy, precision, and recall of match ----

# - Define true positive, true negative, false positive, false negative
TP <- sum(dataset1_linked$UUID_dataset2 == dataset1_linked$UUID_dataset1, na.rm = TRUE)
FP <- sum(dataset1_linked$UUID_dataset2 != dataset1_linked$UUID_dataset1, na.rm = TRUE)
FN <- sum(is.na(dataset1_linked$UUID_dataset2) & !is.na(dataset1_linked$UUID_dataset1), na.rm = TRUE)
TN <- sum(is.na(dataset1_linked$UUID_dataset2) & is.na(dataset1_linked$UUID_dataset1), na.rm = TRUE)

# - Calculate match metrics
precision <- TP / (TP + FP)
recall <- TP / (TP + FN)
accuracy <- (TP + TN) / (TP + FP + FN + TN)

# - Display metrics
data.frame(
  "Correct matches" = TP,
  "Incorrect matches" = FP,
  "Unmatched records" = FN,
  "Precision" = precision,
  "Recall" = recall,
  "Accuracy" = accuracy
)


