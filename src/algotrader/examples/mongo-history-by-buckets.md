```json
[
  {
    '$match': {
      "attachments.indicators_matched_buckets.sma5.ident": {
        '$exists': true
      },
      "attachments.indicators_matched_buckets.sma20.ident": {
        '$exists': true
      },
      "attachments.returns.ctc1": {
        '$exists': true
      }
    }
  },
  {
    "$group": {
      "_id": {
        "sma5": "$attachments.indicators_matched_buckets.sma5.ident",
        "sma20": "$attachments.indicators_matched_buckets.sma20.ident"
      },
      "avg": {
        "$avg": "$attachments.returns.ctc1"
      },
      "count": {
        "$sum": 1
      }
    }
  },
  {
    '$match': {
      "count": {
        '$gte': 1000
      },
      "avg": {
        '$gte': 0
      }
    }
  }
]
```
