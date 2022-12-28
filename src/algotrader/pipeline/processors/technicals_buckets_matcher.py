import json
from typing import Optional, List, Union, Dict

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
    """
    Match technical indicators to buckets and saves them on the candle attachments objects.
    This processor is a companion for the TechnicalsBinner terminator which in charge of creating the bins and
    saving them to file.
    Use the TechnicalsBinner on historical data to create the bins, then run realtime date with
    this processor and get the matching bins.
    """

    def __init__(self, bins_file_path: str, next_processor: Optional[Processor]) -> None:
        """
        @param bins_file_path: path to the bins file created by TechnicalsBinner
        """
        super().__init__(next_processor)

        self.bins_file_path = bins_file_path

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

        super().process(context, candle)

    def _indicator_list_match(self, values: List[float], bins: List[BucketList]) -> List[Optional[Bucket]]:
        return [self._indicator_match(values[i], bins[i]) for i in range(len(values))]

    def _indicator_match(self, value: float, bins: BucketList) -> Optional[Bucket]:
        for bin in bins:
            if bin.start <= value < bin.end:
                return bin

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'bins_file_path': self.bins_file_path
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict) -> Optional[Processor]:
        return cls(data.get('bins_file_path'), cls._deserialize_next_processor(data))
