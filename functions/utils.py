import numpy as np


def get_accounting_year(x):
    """Get accounting year, based on end date"""
    if x <= 20090701:
        print("error, data anterior to 2009")
        return np.nan
    elif x > 20090701 and x <= 20100701:
        return 2009
    elif x > 20100701 and x <= 20110701:
        return 2010
    elif x > 20110701 and x <= 20120701:
        return 2011
    elif x > 20120701 and x <= 20130701:
        return 2012
    elif x > 20130701 and x <= 20140701:
        return 2013
    elif x > 20140701 and x <= 20150701:
        return 2014
    elif x > 20150701 and x <= 20160701:
        return 2015
    elif x > 20160701 and x <= 20170701:
        return 2016
    elif x > 20170701 and x <= 20180701:
        return 2017
    elif x > 20180701 and x <= 20190701:
        return 2018
    elif x > 20190701 and x <= 20200701:
        return 2019
    elif x > 2020701 and x <= 20210701:
        return 2020
    elif x > 20210701 and x <= 20220701:
        return 2021
    elif x > 20220701 and x <= 20230701:
        return 2022
    elif x > 20230701 and x <= 20240701:
        return 2023
    else:
        print("error, data posterior to 2024")
        return np.nan


def keep_main_boundary(x):
    """Filter non standard GHG reporting boundary"""
    if x in ["Operational control", "Financial control", "Equity share"]:
        return x
    else:
        return np.nan


def dict_to_relevance(dict_relevance):
    """
    Derives the relevance of the disclosed scope 3. To do so, we use the division :
    [number of scope 3 categories for which the company reports] / [number of scope 3 categories potentially relevant].
    This has no linked to existing metrics and is based on Thibaud BARREAU intuition.
    """
    if sum(dict_relevance.values()) == 0:
        return 0  # No explanations so considered not relevant
    else:
        relevance_numerator = 0
        relevance_denominator = 0
        try:
            relevance_denominator += dict_relevance["Not evaluated"]
            # considered as potentially relevant
        except KeyError:
            pass
        try:
            relevance_denominator += dict_relevance["Question not applicable"]
            # Considered as potentially relevant
        except KeyError:
            pass
        try:
            relevance_numerator += dict_relevance["Relevant, calculated"]
            relevance_denominator += dict_relevance["Relevant, calculated"]
        except KeyError:
            pass
        try:
            relevance_denominator += dict_relevance["Relevant, not yet calculated"]
        except KeyError:
            pass
        try:
            relevance_numerator += dict_relevance["Not relevant, calculated"]
            relevance_denominator += dict_relevance["Not relevant, calculated"]
        except KeyError:
            pass
        if relevance_denominator == 0:
            return 0  # Only nan or uncalculated sub scopes
        else:
            return relevance_numerator / relevance_denominator
