import json
from typing import Optional, List, Union

from entities.bucket import Bucket, BucketList
from entities.bucketscontainer import BucketsContainer
from entities.candle import Candle
from entities.generic_candle_attachment import GenericCandleAttachment
from pipeline.processor import Processor
from pipeline.processors.technicals_normalizer import NormalizedIndicators, NORMALIZED_INDICATORS_ATTACHMENT_KEY
from pipeline.shared_context import SharedContext
from serialization.store import DeserializationService

INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY = 'indicators_matched_buckets'


class IndicatorsMatchedBuckets(GenericCandleAttachment[Union[List[Bucket], Bucket]]):
    pass


IndicatorsMatchedBuckets()


class TechnicalsBucketsMatcher(Processor):
    def __init__(self, bins_file_path: str, next_processor: Optional[Processor]) -> None:
        super().__init__(next_processor)

        with open(bins_file_path) as bins_file_content:
            content = bins_file_content.read()
            self.bins: BucketsContainer = DeserializationService.deserialize(json.loads(content))

    def process(self, context: SharedContext, candle: Candle):
        normalized_indicators: NormalizedIndicators = candle.attachments.get_attachment(
            NORMALIZED_INDICATORS_ATTACHMENT_KEY)

        matched_buckets = IndicatorsMatchedBuckets()

        for indicator, value in normalized_indicators.items():
            bins = self.bins.get(indicator)
            if bins:
                if isinstance(bins[0], list):
                    match = self._indicator_list_match(value, bins)
                else:
                    match = self._indicator_match(value, bins)

                matched_buckets.set(indicator, match)

        candle.attachments.add_attachement(INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY, matched_buckets)

        if self.next_processor:
            self.next_processor.process(context, candle)

    def _indicator_list_match(self, values: List[float], bins: List[BucketList]) -> List[Optional[Bucket]]:
        return [self._indicator_match(v, b) for v in values for b in bins]

    def _indicator_match(self, value: float, bins: BucketList) -> Optional[Bucket]:
        for bin in bins:
            if bin.start <= value < bin.end:
                return bin
