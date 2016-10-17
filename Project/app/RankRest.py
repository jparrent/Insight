#!/usr/bin/python3

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
# import math


def RankIt(df, model, model_hs1, model_hs1_neg0, allergens, nutrition_data, big8):

    all_allergens = []
    all_allergens.extend(big8)
    all_allergens.extend(allergens)
    print(all_allergens)
    num_of_allerg = len(all_allergens)

    g = {k: list(s) for k, s in df.groupby(
        ['restid', 'restname', 'address'])['sentence']}

    scores = []
    for key, llist in g.items():
        key_score = 100
        num_of_items = len(llist)
        strike = key_score / num_of_items / num_of_allerg
        if len(allergens) > 0:
            for allerg in allergens:
                for sen in llist:
                    sen_list = sen.split()
                    for word in sen_list:
                        # step 1: check for direct word match
                        if fuzz.ratio(word.lower(), allerg) > 80:
                            key_score -= strike
                            print(word, allerg, strike)
                            break
                        # if none, step 2: check for indirect word match
                        else:
                            try:
                                test1 = model.similar_by_word(
                                    word.lower(), topn=20)
                                test2 = model_hs1.similar_by_word(
                                    word.lower(), topn=20)
                                test3 = model_hs1_neg0.similar_by_word(
                                    word.lower(), topn=20)
                            except KeyError:
                                continue

                            check1 = [i[0].lower() for i in test1 if i[1] >
                                      0.40 and fuzz.ratio(i[0].lower(), allerg) > 80]
                            check2 = [i[0].lower() for i in test2 if i[1] >
                                      0.40 and fuzz.ratio(i[0].lower(), allerg) > 80]
                            check3 = [i[0].lower() for i in test3 if i[1] >
                                      0.30 and fuzz.ratio(i[0].lower(), allerg) > 80]

                            if allerg in check1 and allerg in check2 and allerg in check3:
                                print(word, allerg, strike)
                                key_score -= strike
                                break

        # step 3: check for match with big8 list
        if len(big8) > 0:
            for item in big8:
                for sen in llist:
                    sen_list = sen.split()
                    for word in sen_list:
                        if fuzz.ratio(word.lower(), item) > 80:
                            key_score -= strike
                            print(word, item, strike)
                            break
                        if word in nutrition_data.keys():
                            if item in nutrition_data[word.lower()]:
                                key_score -= strike
                                print(word, item, strike)
                                break

        key_score = int(round(key_score))
        scores.append([key_score, key])
        scores.sort(reverse=True)
    return scores, all_allergens
