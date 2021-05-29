# Spellcheck for post-correction of Kraken output


One way to assess the Kraken output is to check 
for every token whether it is recognized as an
existing token by a spell checker. 

## Creating ground proof data: 

PV ran a Hunspell spell checker on all Arabic texts in
the entire OpenITI corpus (`calculate_error_rates_using_spellcheck.py`).

Data for each page of each book can be found in the 
book json files in the `error data` folder.

Full book-level error rate data can be found in the 
`25Y_repos_error_data` json and tsv files. 

This data can be used to get statistics for the entire
corpus or sub-corpora. 

The error rate for the entire corpus as detected by
this script is 3% - that is, about one in 33 Arabic
tokens in the corpus is not recognized as a valid
token by the spell checker. 

About 5% of errors detected by the script are in 
tokens that are longer than 8 characters.

A graph of the average error rates by source
collection of the books (view in [Google Sheets]( 
https://docs.google.com/spreadsheets/d/1js71lwICBdVbq_Oz6v465txCFKmIXykvI5mN5ZMyq9I/edit?usp=sharing))

![./error rate per source collection.png]

It could also be interesting to check whether specific genres
typically have higher error rates than other genres. 

## Using a spell checker to assess OCR output quality

The `collect_spellcheck_error_data_in_folder` function
in the `calculate_error_rates_using_spellcheck.py`
module can be used to gather error data for all 
OCR output files in a folder. 

For one text file, use the `collect_spellcheck_error_data_in_file`
function from the same module. 



## Limitations:

This is of course not watertight: 

* an OCR error can still be an existing word, 
just not the one that was on the page
* a correctly OCR'ed word may not be recognized
by the spell checker because it is not part of its
dictionary. 
