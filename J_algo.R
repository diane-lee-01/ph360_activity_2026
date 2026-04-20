$ cat J_algo.R
install.packages("fastLink")
install.packages("dplyr")
install.packages("stringr")
library(dplyr)
library(stringr)
library(fastLink)
# Set and Load Data
setwd("C:/Users/exf3638/Desktop/ph360_activity_2026")
df1 <- read.csv("data/sampledata1.csv", stringsAsFactors = FALSE)
df2 <- read.csv("data/sampledata2.csv", stringsAsFactors = FALSE)
#Preprocessing
head(df1)
head(df2)
clean_df1 <- df1 %>%
  mutate(
    first_name  = str_to_lower(str_trim(first_name)),
    last_name   = str_to_lower(str_trim(last_name)),
    sex         = str_to_upper(str_trim(sex)),
    birth_date  = str_trim(birth_date),
    phone       = str_remove_all(phone, "[^0-9]"),
    zip_code    = str_trim(as.character(zip_code)),
    email       = str_to_lower(str_trim(email))
  )
head(clean_df1)
clean_df2 <- df2 %>%
  mutate(
    first_name  = str_to_lower(str_trim(FirstName)),
    last_name   = str_to_lower(str_trim(LastName)),
    sex         = str_to_upper(str_trim(Sex)),
    birth_date  = str_trim(DOB),
    phone       = str_remove_all(PhoneNumber, "[^0-9]"),
    zip_code    = str_trim(as.character(Zip)),
    email       = str_to_lower(str_trim(EmailAddress))
  )
clean_df1 <- clean_df1 %>%
  mutate(
    phone    = as.numeric(phone),
    zip_code = as.numeric(zip_code)
  )
clean_df2 <- clean_df2 %>%
  mutate(
    phone    = as.numeric(phone),
    zip_code = as.numeric(zip_code)
  )
#Run fastlink to match by names, emails, phone, zip, and DOB
ja_out <- fastLink(
  dfA              = clean_df1,
  dfB              = clean_df2,
  varnames         = c("first_name", "last_name", "birth_date", "phone", "zip_code", "email"),
  stringdist.match = c("first_name", "last_name", "email"),
  numeric.match    = c("phone", "zip_code"),
  partial.match    = c("first_name", "last_name"),
  threshold.match  = 0.85,
  verbose          = TRUE
)
#Pull out Matches
matches <- ja_out$matches
matched_df1 <- clean_df1[matches$inds.a, ] %>%
select(first_name, last_name, birth_date, UUID) %>%
rename(UUID_df1 = UUID)
matched_df2 <-clean_df2[matches$inds.b, ] %>%
rename(UUID_df2 = UUID)
results <- bind_cols(matched_df1, matched_df2) %>%
mutate(correct_match = UUID_df1 == UUID_df2)
#Evaluate
uuid_df1 <- df1$UUID
uuid_df2 <- df2$UUID
true_matches_total <- length(intersect(uuid_df1, uuid_df2))
TP <- sum(results$correct_match)
FP <- sum(!results$correct_match)
FN <- true_matches_total - TP
precision <- TP / (TP + FP)
recall    <- TP / (TP + FN)
accuracy  <- TP / true_matches_total
cat("\n===== Evaluation Metrics =====\n")
cat(sprintf("True Positives  (TP): %d\n", TP))
cat(sprintf("False Positives (FP): %d\n", FP))
cat(sprintf("False Negatives (FN): %d\n", FN))
cat(sprintf("True Matches in Both Datasets: %d\n\n", true_matches_total))
cat(sprintf("Precision : %.4f\n", precision))
cat(sprintf("Recall    : %.4f\n", recall))
cat(sprintf("Accuracy  : %.4f\n", accuracy))
save.image("C:\\Users\\exf3638\\Documents\\week2")
savehistory("C:/Users/exf3638/Desktop/ph360_activity_2026/J_algo.R")
