class AvsContext:
    audio_player = '''
    {
        "header": {
            "namespace": "AudioPlayer",
            "name": "PlaybackState"
        },
        "payload": {
            "token": "1",
            "offsetInMilliseconds": 0,
            "playerActivity": "IDLE"
        }
    }
    '''.strip()

    alerts = '''
    {
        "header": {
            "namespace": "Alerts",
            "name": "AlertsState"
        },
        "payload": {
            "allAlerts": [
                {
                    "token": "1",
                    "type": "",
                    "scheduledTime": "0"
                }
            ]
        }
    }
    '''.strip()

    speaker = '''
    {
        "header": {
            "namespace": "Speaker",
            "name": "VolumeState"
        },
        "payload": {
            "volume": 1,
            "muted": false
        }
    }
    '''.strip()


    speech_synthersizer = '''
    {
        "header": {
            "namespace": "SpeechSynthesizer",
            "name": "SpeechState"
        },
        "payload": {
            "token": "1",
            "offsetInMilliseconds": 10,
            "playerActivity": "PLAYING"
        }
    }
    '''.strip()
