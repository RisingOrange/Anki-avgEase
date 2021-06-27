# Average Ease
# Anki 2.1 addon
# Original Author EJS
# https://eshapard.github.io/
#
# Sets the initial ease factor of a deck options group to the average
# ease factor of the mature cards within that deck options group.
import argparse

from anki.hooks import addHook

from . import config as cfg

COL = None


def update_ease_factors():
    for option_group in COL.decks.all_config():
        update_ease_factor(option_group)


# Average mature card ease factor in settings group
def update_ease_factor(option_group):
    avg_ease, _ = mature_ease_in_settings_group(option_group)
    option_group['new']['initialFactor'] = int(avg_ease)
    COL.decks.update_config(option_group)
    COL.decks.save(option_group)
    COL.decks.flush()


def mature_ease_in_settings_group(option_group):
    tot_mature_cards = 0
    weighted_ease = 0
    avg_mature_ease = 0

    dids = COL.decks.didsForConf(option_group)
    for did in dids:
        mature_cards = amount_mature_cards_in_deck(did)
        mature_ease = average_ease_of_mature_cards_in_deck(did)
        tot_mature_cards += mature_cards
        weighted_ease += mature_cards * mature_ease

    if tot_mature_cards >= cfg.get("option_group_min_mature_card_amount"):
        avg_mature_ease = int(weighted_ease / tot_mature_cards)
    else:
        # not enough data; don't change the init ease factor
        avg_mature_ease = option_group["new"]["initialFactor"]

    cur_ease = option_group['new']['initialFactor']
    return avg_mature_ease, cur_ease


def amount_mature_cards_in_deck(deck_id):
    result = COL.db.scalar(f"""select
        count()
        from cards where
        type = 2 and
        ivl > {cfg.get("mature_card_min_interval")} and
        did = ?""", deck_id)
    if not result:
        result = 0
    return result


def average_ease_of_mature_cards_in_deck(deck_id):
    result = COL.db.scalar(f"""select
        avg(factor)
        from cards where
        type = 2 and
        ivl > {cfg.get("mature_card_min_interval")} and
        did = ?""", deck_id)
    if not result:
        result = 0
    return result


def main():
    global COL
    COL = mw.col
    update_ease_factors()


try:
    from aqt import mw
    addHook("profileLoaded", main)

except:
    from anki import Collection as Col
    parser = argparse.ArgumentParser()
    parser.add_argument('collection_path')
    args = parser.parse_args()

    COL = Col(args.collection_path)
    update_ease_factors()
    COL.save()
    COL.flush()
