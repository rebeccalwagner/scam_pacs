# scam_pacs
## app_sandbox
This directory has the files related to the app hosted [here](https://sjmpythonanywhere.pythonanywhere.com/)

## Code
*01_download_filings.ipynb*
    1. Uses the filings/ endpoint of the FEC API to pull all filing ids for PACs from the 2024 election cycle. These filing IDs will be used to pull lineitem details. Also pulls aggregate metrics for each filing
        - outputs:  fec_filings_2024.csv
    2. Uses the filing_url_ids from fec_filings_2024 to pull lineitem details from each filing using FastFEC from the Washington Post. We are only interested in spending data for this project so we only keep SE and SB lineitems as well as the summary data for the filing.
        - outputs: one directory for each filing id included in fec_filings_2024.csv including SB, SE, F3X files where available.
    3. Delete all empty directories resulting from step two. These fill be filing IDs that didn't have any spending lineitem data. 

*02_join_filiing_data.ipynb*
Combines all of the SE and SB lineitems data from each filing into two datasets
    - outputs: SB_dataset.csv, SE_dataset.csv

*03_download_pac_financials.ipynb*
Uses the committee/ endpoint from the FEC API to pull PAC financial summary data for the 2024 election cycle 
    - outputs: pac_financials.csv

*04_preprocessing_clusters.ipynb*
Cleans & wrangles SB and SE datasets for use in network app 

*05_vizz_app.ipynb*
Original work on app 


## Data

### Raw

### Processed 