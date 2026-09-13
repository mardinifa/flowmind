# Eligibility Testing

## Test 1 — Everything Passes

Input:

- Age: 30
- Registration: 24 months
- Loan: ₦2,000,000
- Monthly turnover: ₦500,000
- Purpose: inventory

Results:

- Registration: PASS
- Age: PASS
- Loan-to-turnover: PASS
- Purpose: PASS

Overall: Eligible


## Test 2 — Registration = 5 Months

Input:

- Age: 30
- Registration: 5 months
- Loan: ₦2,000,000
- Monthly turnover: ₦500,000
- Purpose: inventory

Results:

- Registration: FAIL
- Age: PASS
- Loan-to-turnover: PASS
- Purpose: PASS

Overall: Not Eligible


## Test 3 — Age = 19

Input:

- Age: 19
- Registration: 24 months
- Loan: ₦2,000,000
- Monthly turnover: ₦500,000
- Purpose: inventory

Results:

- Registration: PASS
- Age: FAIL
- Loan-to-turnover: PASS
- Purpose: PASS

Overall: Not Eligible


## Test 4 — Age = 70

Input:

- Age: 70
- Registration: 24 months
- Loan: ₦2,000,000
- Monthly turnover: ₦500,000
- Purpose: inventory

Results:

- Registration: PASS
- Age: FAIL
- Loan-to-turnover: PASS
- Purpose: PASS

Overall: Not Eligible


## Test 5 — Loan Too Large

Input:

- Age: 30
- Registration: 24 months
- Loan: ₦6,000,000
- Monthly turnover: ₦500,000
- Purpose: inventory

Results:

- Registration: PASS
- Age: PASS
- Loan-to-turnover: FAIL
- Purpose: PASS

Overall: Not Eligible


## Test 6 — Invalid Purpose

Input:

- Age: 30
- Registration: 24 months
- Loan: ₦2,000,000
- Monthly turnover: ₦500,000
- Purpose: cryptocurrency

Results:

- Registration: PASS
- Age: PASS
- Loan-to-turnover: PASS
- Purpose: FAIL

Overall: Not Eligible


## Test 7 — Registration + Age Fail

Input:

- Age: 19
- Registration: 5 months
- Loan: ₦2,000,000
- Monthly turnover: ₦500,000
- Purpose: inventory

Results:

- Registration: FAIL
- Age: FAIL
- Loan-to-turnover: PASS
- Purpose: PASS

Overall: Not Eligible


## Test 8 — Loan + Purpose Fail

Input:

- Age: 30
- Registration: 24 months
- Loan: ₦6,000,000
- Monthly turnover: ₦500,000
- Purpose: cryptocurrency

Results:

- Registration: PASS
- Age: PASS
- Loan-to-turnover: FAIL
- Purpose: FAIL

Overall: Not Eligible


## Test 9 — Missing Age

Input:

- Age: Missing
- Registration: 24 months
- Loan: ₦2,000,000
- Monthly turnover: ₦500,000
- Purpose: inventory

Results:

- Registration: PASS
- Age: FAIL
- Loan-to-turnover: PASS
- Purpose: PASS

Overall: Not Eligible

Note: Age was missing, so the age check returned low confidence.


## Test 10 — Missing Turnover

Input:

- Age: 30
- Registration: 24 months
- Loan: ₦2,000,000
- Monthly turnover: Missing
- Purpose: inventory

Results:

- Registration: PASS
- Age: PASS
- Loan-to-turnover: FAIL
- Purpose: PASS

Overall: Not Eligible

Note: Turnover was missing, so the loan-to-turnover check returned low confidence.


## Test 11 — Turnover = 0

Input:

- Age: 30
- Registration: 24 months
- Loan: ₦2,000,000
- Monthly turnover: ₦0
- Purpose: inventory

Results:

- Registration: PASS
- Age: PASS
- Loan-to-turnover: FAIL
- Purpose: PASS

Overall: Not Eligible


## Test 12 — Age Exactly 21

Input:

- Age: 21
- Registration: 24 months
- Loan: ₦2,000,000
- Monthly turnover: ₦500,000
- Purpose: inventory

Results:

- Registration: PASS
- Age: PASS
- Loan-to-turnover: PASS
- Purpose: PASS

Overall: Eligible


## Test 13 — Age Exactly 65

Input:

- Age: 65
- Registration: 24 months
- Loan: ₦2,000,000
- Monthly turnover: ₦500,000
- Purpose: inventory

Results:

- Registration: PASS
- Age: PASS
- Loan-to-turnover: PASS
- Purpose: PASS

Overall: Eligible


## Test 14 — Loan Exactly 10 × Turnover

Input:

- Age: 30
- Registration: 24 months
- Loan: ₦5,000,000
- Monthly turnover: ₦500,000
- Purpose: inventory

Results:

- Registration: PASS
- Age: PASS
- Loan-to-turnover: PASS
- Purpose: PASS

Overall: Eligible


## Test 15 — Several Fields Missing

Input:

- Age: Missing
- Registration: Missing
- Loan: Missing
- Monthly turnover: Missing
- Purpose: inventory

Results:

- Registration: FAIL
- Age: FAIL
- Loan-to-turnover: FAIL
- Purpose: PASS

Overall: Not Eligible

Note: Several required fields were missing. These checks should be reviewed by the team if a different handling rule is desired.