```json
[
    {
        '$set': {
            'timespan': {
                '$switch': {
                    'branches': [
                        {
                            'case': {
                                '$eq': [
                                    '$timespan', 'Minute'
                                ]
                            }, 
                            'then': 60
                        }, {
                            'case': {
                                '$eq': [
                                    '$timespan', 'Day'
                                ]
                            }, 
                            'then': 86400
                        }
                    ], 
                    'default': '$timespan'
                }
            }, 
            '__class__': 'entities.candle:Candle', 
            'attachments.__class__': 'entities.candle_attachments:CandleAttachments', 
            'attachments.indicators': {
                '$cond': {
                    'if': {
                        '$and': [
                            {
                                '$eq': [
                                    '$attachments.indicators.__class__', 'Indicators'
                                ]
                            }, {
                                '$eq': [
                                    {
                                        '$type': '$attachments.indicators'
                                    }, 'object'
                                ]
                            }
                        ]
                    }, 
                    'then': {
                        '$mergeObjects': [
                            '$attachments.indicators', {
                                '__class__': 'pipeline.processors.technicals:Indicators'
                            }
                        ]
                    }, 
                    'else': '$$REMOVE'
                }
            }
        }
    }, {
        '$group': {
            '_id': {
                'timestamp': '$timestamp', 
                'symbol': '$symbol', 
                'timespan': '$timespan'
            }, 
            'doc': {
                '$first': '$$ROOT'
            }
        }
    }, {
        '$replaceRoot': {
            'newRoot': '$doc'
        }
    }, {
        '$out': 'candles'
    }
]
```