from flask import Flask, jsonify, make_response
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class PortfolioOrders(Resource):

    def get(self):
        # Return holdings data 
        pass

    def post(self):
        # Set API secret/API Key
        pass


class KnowledgeBase(Resource):
    def get(self):
        # This is the get call for financial knowledge base


class ChatResponse(Resource):
    def get(self):
        # Bot Response


class ProductCatalog(Resource):
    def get(self):
        # Fetch from product catalog
    def post(self):
        # Set a product catalog


api.add_resource(PortfolioOrders, "/portfolio")
api.add_resource(KnowledgeBase, "/knowledgebase")
api.add_resource(ChatResponse, "/bot")
api.add_resource(ProductCatalog, "/products")