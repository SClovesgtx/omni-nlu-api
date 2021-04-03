# standard library imports
import sys

sys.path.append("./src/")

# third party imports
from flask import Blueprint, request, Response, jsonify

models_settings_app = Blueprint("models_settings_app", __name__)

# local imports
from elasticsearch_db.elasticsearch import elastic_conection, NLPmodelIndex
from elasticsearch_db.elasticsearch import get_nlp_model, pipeline_to_update_index

es = elastic_conection()


@models_settings_app.route("/nlp_modelsv2", methods=["GET", "POST", "PUT", "DELETE"])
def nlp_models_crud():
    try:
        if request.method == "GET":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            doc = es.get(index=index.index_name, id=index.workspace_id)
            return doc

        elif request.method == "POST":
            workspace_id = request.args.get("workspace_id")
            nlp_model = request.get_json()
            if not nlp_model:
                return Response("Expect to recive the nlp_model object!", status=400)
            recipe = nlp_model.get("recipe")
            # Do tests after
            # if recipe:
            #     msg, status = check_recipe(recipe.get("model_kind"), recipe)
            #     if status != 200:
            #         return Response(msg, status=status)
            index = NLPmodelIndex(
                es=es,
                workspace_id=workspace_id,
                customer_id=nlp_model["customer_id"],
                recipe=recipe,
            )

            if index.index_exist(es):
                return Response("NLP Model already exist!", status=409)
            index.create_index(es)
            _, res = index.create_recipe(es)
            return res

        elif request.method == "PUT":
            workspace_id = request.args.get("workspace_id")
            nlp_model = request.get_json()
            if not nlp_model:
                return Response("Expect to recive the nlp_model object!", status=400)
            recipe = nlp_model.get("recipe")
            # if recipe:
            #     msg, status = check_recipe(recipe.get("model_kind"), recipe)
            #     if status != 200:
            #         return Response(msg, status=status)
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            update_query = {"doc": nlp_model}
            res = es.update(
                index=index.index_name, id=index.workspace_id, body=update_query
            )
            index = pipeline_to_update_index(es, index)
            res["_index"] = index.index_name
            return res

        elif request.method == "DELETE":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            res = es.indices.delete(index=index.index_name)
            return res

    except:
        trace_back_error = "".join([str(item) for item in sys.exc_info()])
        print(sys.exc_info())
        return Response(
            '{"response":"%s"}' % trace_back_error,
            status=500,
            mimetype="application/json",
        )
