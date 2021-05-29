r"""
Calculate error rates in an OpenITI text (or folder of texts) \
using a spell check algorithm.
The spell check algorithm currently used is a pyEnchant implementation
of the Hunspell spell checker - but other spellcheck functions could
be plugged in using the `spellcheck_func` argument.

Main functions:

* collect_spellcheck_error_data_in_folder
* collect_spellcheck_error_data_in_file

!!!!!!!!!!!!!!!!!!!!!!!!!works only with python 3.6+!!!!!!!!!!!!!!!!!!!!!

If you install pyEnchant with pip in Python 3.6+, it will also install enchant.

NB: Arabic dictionary created by ayaspell project (http://ayaspell.sourceforge.net/)
and downloaded from
https://cgit.freedesktop.org/libreoffice/dictionaries/tree/ar
Put both dictionary files (.dic and .app) into this folder
inside the enchant folder in your Python folder's site packages:
Lib\site-packages\enchant\data\mingw32\share\enchant\hunspell
(e.g., on my computer:
C:\Users\peter\AppData\Local\Programs\Python\Python38-32\Lib\site-packages\enchant\data\mingw32\share\enchant\hunspell
)
"""

import re
import os
import enchant
import json
from openiti.helper.ara import ar_tok
from openiti.helper.funcs import get_all_text_files_in_folder

# load the enchant dictionary to be used:
d = enchant.Dict("ar")

def check_with_pyEnchant(tok):
    """Check whether a token is recognized by the spell checker.

    Args:
        tok (str): token to be checked

    Returns:
        bool
    """
    return d.check(tok)

def calculate_error_rate(t, spellcheck_func=check_with_pyEnchant,
                         token_regex=ar_tok, long=8, verbose=False):
    """Get the error rate for each book and each page of a book.

    The function goes through every token on each page of the book
    and checks whether or not the `spellcheck_func` recognizes
    the token. It counts the number of unrecognized tokens.
    In addition, it checks how many of these errors are in
    "over-long" tokens.
    Finally, an error rate (number of errors divided by number of tokens)
    is calculated for every page of the book, and every book as a whole.

    Args:
        t (str): the text of the book as a string
        spellcheck_func (func): function to be used to check spelling
        token_regex (str): regular expression pattern describing the
            tokens that need to be checked
        long (int): minimum number of characters in a token to be
            considered a long token
        verbose (bool): if False, no output will be printed

    Returns:
        dict (containing the overall error rates and page-level error rates)
    """
    errors = {"all": 0, "long": 0, "tok_count": 0, "page_errors": []}
    page_errors = {"all": 0, "long": 0, "tok_count": 0, "page_no": ""}
    for p in re.split("(PageV\d+P\d+)", t):
        #print(p)
        if p.startswith("Page"):  # end of page: save page_errors
            if verbose and p.endswith("0"):
                print(p)
            page_errors["page_no"] = p
            errors["page_errors"].append(page_errors)
            page_errors = {"all": 0, "long": 0, "tok_count": 0, "page_no": ""}
        else:  # analyze all tokens in the page:
            if p: 
                for m in re.finditer(token_regex, p):
                    errors["tok_count"] += 1
                    page_errors["tok_count"] += 1
                    tok = m.group()
                    if verbose:
                        print("      ", tok, d.check(tok))
                    #if d.check(tok) == False:
                    if spellcheck_func(tok) == False:
                        errors["all"] += 1
                        page_errors["all"] += 1
                        if len(tok) > long:
                            errors["long"] += 1
                            page_errors["long"] += 1
    error_rate = errors["all"]/errors["tok_count"]
    errors["error_rate"] = error_rate
    if verbose:
        print("  error_rate:", 100*error_rate, "%")
    long_rate = errors["long"]/errors["tok_count"]
    errors["long_tokens_error_rate"] = long_rate
    return errors

def collect_spellcheck_error_data_in_file(fp, spellcheck_func,
                                          outfolder="error_data",
                                          error_data={}, overwrite=False):
    """Collect "error" data for the text file at `fp` \
    using a spellchecker function.

    This function creates a json file containing error data for each page.
    It also adds the error data to the `error_data` dictionary.

    Args:
        fp (str): path to a file containing an OpenITI text
        spellcheck_func (func): function to be used to check spelling
        overwrite (bool): if True, book-level json files will be overwritten;
            if False, book-level error data will be read from the json
            files instead of re-analysing the text.
    """
    v_uri = os.path.basename(fp)
    outfp = os.path.join(outfolder, v_uri+"_error_data.json")
    if overwrite or not os.path.exists(outfp):
        # load text:
        with open(fp, mode="r", encoding="utf-8") as file:
            t = file.read()

        # split off metadata header:
        t = t.split("#META#Header#End")[-1]
        
        # get spellcheck data for this book:
        error_data[v_uri] = calculate_error_rate(t)
        
        # save page-level error data for this book: 
        with open(outfp, mode="w", encoding="utf-8") as file:
            json.dump(error_data[v_uri], file,
                      ensure_ascii=False, indent=2, sort_keys=True)
    else: # read existing error data from json file
        with open(outfp, mode="r", encoding="utf-8") as file:
            error_data[v_uri] = json.load(file)
            
    # remove page-level error data from the corpus-wide statistics:
    del error_data[v_uri]["page_errors"]

def collect_spellcheck_error_data_in_folder(folder, tsv_fp, json_fp,
                                            outfolder="error_data",
                                            lang_code="ara",
                                            spellcheck_func=check_with_pyEnchant,
                                            overwrite=False):
    """Collect "error" data for all text files in the folder
    (and its subfolders) using a spellchecker.

    This function creates multiple outputs:
    
    * For each book, a json file containing error data for each page.
    * a json file containing containing book-level error data for all
    files in the folder (and its sub-folders)
    * a tsv file containing containing book-level error data for all
    files in the folder (and its sub-folders)

    Args:
        folder (str): path to a folder containing OpenITI text files
        tsv_fp (str): path to the tsv output file
        json_fp (str): path to the json output file
        lang_code (str): language code used in the OpenITI URI;
            to make sure that only texts in the relevant language are spell-checked.
            Set to None if all files should be checked, regardless of their language.
        spellcheck_func (func): function to be used to check spelling
        overwrite (bool): if True, book-level json files will be overwritten;
            if False, book-level error data will be read from the json
            files instead of re-analysing the text.
    """
    # prepare json output dictionary:
    error_data = dict()

    # prepare tsv output file:

    # create empty tsv output file with header:
    # (NB: existing tsv output file will be overwritten)
    header = ["uri", "all", "long", "error_rate",
              "long_tokens_error_rate", "tok_count"]
    cols = header[1:]
    with open(tsv_fp, mode="w", encoding="utf-8") as tsv_file:
        print("writing corpus-wide data to", tsv_fp)
        tsv_file.write("\t".join(header) + "\n")

    # get error data for every book and write it to tsv:
    with open(tsv_fp, mode="a", encoding="utf-8") as tsv_file:
        for fp in get_all_text_files_in_folder(folder):
            check = True
            if lang_code:
                if not "-"+lang_code in fp:
                    check = False
            if check: 
                v_uri = os.path.basename(fp)
                print(v_uri)
                collect_spellcheck_error_data_in_file(fp, error_data=error_data,
                                                      spellcheck_func = spellcheck_func,
                                                      overwrite=overwrite)
                
                # write the book-level error data to the corpus-wide tsv file:
                tsv_data = [v_uri,] + [str(error_data[v_uri][col]) for col in cols]
                tsv_file.write("\t".join(tsv_data) + "\n")
            
    # save corpus-level error data as json file:
    with open(json_fp, mode="w", encoding="utf-8") as file:
        json.dump(error_data, file, ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == "__main__":
    folder = r"D:\London\OpenITI\25Y_repos"
    tsv_fp = os.path.basename(folder) + "_error_data.tsv"
    json_fp = os.path.basename(folder) + "_error_data.json"
    collect_spellcheck_error_data_in_folder(folder, tsv_fp, json_fp, spellcheck_func=check_with_pyEnchant)


