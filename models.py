import re
from bson import DBRef
from mongoengine import Document, EmailField, BinaryField, DynamicField
from mongoengine import DateTimeField, EmbeddedDocument, StringField, URLField
from mongoengine import ReferenceField, EmbeddedDocumentListField, ListField
from mongoengine import IntField, FloatField, BooleanField, DateField, DictField


class Entity(Document):
    entity_type = StringField(required=True, choices=["equity", "crypto", "us_equity"])
    entity_name = StringField(required=True)
    entity_ticker = StringField(required=True)
    entity_ticker_alt = StringField()
    entity_icon_url = URLField()
    entity_index = ListField(StringField())
    entity_sector = StringField()
    fundamental_analysis = DynamicField()
    technical_analysis = DynamicField()
    important_links = DynamicField()
    data_feed = URLField()
    entity_fb_id = StringField()
    is_entity_complete = BooleanField()
    entity_ecosystem = StringField(
        choices=["Ethereum", "BSC", "Polygon", " Avalanche", "Fantom"]
    )
    entity_ecosystem_rank = IntField()
    entity_exchange = StringField()
    tag = StringField(choices=["top gainer", "top loser", "spotlight"])
    tag_validity = DateTimeField()
    technical_pattern = StringField()
    technical_sentiment = StringField()

class Insights(Document):
    insight_title = StringField(unique=True, required=True)
    insight_description = StringField()
    insight_published_date = DateTimeField()
    insight_publish_price = FloatField()
    insight_read_time = IntField()
    insight_source = StringField()
    insight_img_url = URLField()
    insight_source_page_url = URLField()
    insight_event_group = StringField()
    insight_signal_sentiment = FloatField()
    insight_entity_sentiment = FloatField()
    insight_signal_relevance = FloatField()
    insight_event_sentiment = FloatField()
    insight_order = FloatField()
    insight_entity_id = StringField()
    insight_entity_name = StringField()
    insight_entity_index = StringField()
    insight_entity_sector = StringField()
    insight_entity_ticker = StringField()
    insight_entity_logo = StringField()
    insight_entity_type = StringField(choices=["crypto", "equity", "us_equity"])
    insight_likes = IntField(default=0)
    technical_pattern = StringField()
    technical_sentiment = StringField()
    meta = {
        "indexes": [
            {
                "fields": ["$insight_title", "$insight_description"],
                "default_language": "english",
            }
        ]
    }

    def fetch_insights_as_dict(
        self, user_insights_bookmarked=None, is_search_res=False
    ):
        first_split_pos = re.search("//", self.insight_source)
        market_impact_opt = ["Low", "Medium", "High"]
        if first_split_pos is not None:
            self.insight_source = self.insight_source[first_split_pos.end() :]
        secnd_split_pos = re.search("[^A-Za-z0-9.]", self.insight_source)
        if secnd_split_pos is not None:
            self.insight_source = self.insight_source[: secnd_split_pos.start()]

        user_insights_bookmarked = user_insights_bookmarked

        bookmarked = True
        if user_insights_bookmarked is not None:
            bookmarked = False
            for i in range(len(user_insights_bookmarked)):
                if str(self.id) == str(user_insights_bookmarked[i]["insight_id"].id):
                    bookmarked = True
                    break

        resp = {
            "insights_id": str(self.id),
            "insights_name": self.insight_title,
            "tag": self.insight_event_group,
            "insights_icon":self.insight_img_url,
            "entity": {
                "id": self.insight_entity_id,
                "ticker": self.insight_entity_ticker,
                "logo": self.insight_entity_logo,
            },
            "read_time": self.insight_read_time,
            "days": self.insight_published_date.isoformat(),
            "bookmarked": bookmarked,
            "event_group": self.insight_event_group,
            "entity_sentiment": self.insight_entity_sentiment,
            "projected_market_impact": market_impact_opt[
                int(self.insight_order//3334)
            ],
            "article_sentiment": self.insight_event_sentiment,
            "insight_likes": 0 if self.insight_likes is not None else self.insight_likes
        }
        if is_search_res:
            resp["result_type"] = "insight"
        return resp

    def fetch_insights_as_dict_full(self,user_insights_bookmarked=None, is_search_res=False):
        market_impact_opt = ["Low", "Medium", "High"]
        entity = Entity.objects(id=self.insight_entity_id).only("entity_fb_id").first()

        user_insights_bookmarked = user_insights_bookmarked

        bookmarked = False
        if user_insights_bookmarked is not None:
            bookmarked = False
            for i in range(len(user_insights_bookmarked)):
                if str(self.id) == str(user_insights_bookmarked[i]["insight_id"].id):
                    bookmarked = True
                    break
        resp= {
            "insight_id": str(self.id),
            "insight_name": self.insight_title,
            "insight_icon": self.insight_img_url,
            "tags": {
                "event_type": self.insight_event_group,
                "entity_name": self.insight_entity_name,
                "entity_index": [self.insight_entity_index if self.insight_entity_index is not None else "crypto"][0],
            },
            "entity": {
                "id": self.insight_entity_id,
                "ticker": self.insight_entity_ticker,
                "logo": self.insight_entity_logo,
                "firebase_price_identifier": entity.entity_fb_id,
                "entity_type": self.insight_entity_type
            },
            "read_time": self.insight_read_time,
            "publish_date": self.insight_published_date,
            "bookmarked": bookmarked,
            "description": self.insight_description,
            "read_more": self.insight_source_page_url,
            "projected_market_impact": market_impact_opt[
                int(self.insight_order//3334)
            ],
            "article_sentiment": self.insight_event_sentiment,
            "portfolio_exposure": "-",
            "days": self.insight_published_date.isoformat(),
            "entity_sentiment": self.insight_entity_sentiment,
            "price_publication": self.insight_publish_price,
            "insight_likes": 0 if self.insight_likes is not None else self.insight_likes
        }
        if is_search_res:
            resp["result_type"] = "insight"
        return resp


class Transactions(EmbeddedDocument):
    pass


class ProductCatalog(Document):
    pass


class Holdings(EmbeddedDocument):
    purchased_instrument = ReferenceField(Entity, required=True)
    purchase_platform = StringField(required=True)
    purchase_time = DateField(required=True)
    purchase_price = FloatField(required=True)
    purchase_qty = FloatField(required=True)
    portfolio_exposure = FloatField()
    purchase_platform_logo = StringField()

    def process_holding_as_dict(self, instrument_type):    
        if isinstance(self.purchased_instrument, DBRef):
            self.purchased_instrument = Entity.objects(
                id=self.purchased_instrument
            ).first()
        data = {
            "purchase_platform": self.purchase_platform,
            "avg_purchase_price": self.purchase_price,
            "purchase_qty": self.purchase_qty,
            "firebase_path": self.purchased_instrument.entity_fb_id,
            "entity_name": self.purchased_instrument.entity_name,
            "entity_logo": self.purchased_instrument.entity_icon_url,
            "entity_id": str(self.purchased_instrument.id),
            "entity_type": self.purchased_instrument.entity_type,
            "entity_ticker": self.purchased_instrument.entity_ticker,
        }
        if instrument_type is not None and instrument_type != self.purchased_instrument.entity_type:
            return None
        return data


class User(Document):
    user_binance_api_key = StringField()
    user_binance_api_secret = StringField()
    user_portfolio_holdings = EmbeddedDocumentListField(Holdings, default=list)
    user_transactions = EmbeddedDocumentListField(Transactions, default=list)
    user_crypto_portfolio_value = FloatField()
    user_crypto_portfolio_percentage_change = FloatField()