from aqt import mw


def get(key):
    config = mw.addonManager.getConfig(__name__)
    return config.get(key, None)


def set(key, value):
    config = mw.addonManager.getConfig(__name__)
    config[key] = value
    mw.addonManager.writeConfig(__name__, config)
