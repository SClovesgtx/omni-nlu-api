# standard library imports
import sys

sys.path.append("./src/")

# third party imports
from flask import Blueprint, request, Response

intents_app = Blueprint("intents_app", __name__)

# local imports
from elasticsearch_db.elasticsearch import elastic_conection
from elasticsearch_db.elasticsearch import get_nlp_model

es = elastic_conection()


@intents_app.route("/nlp_models/intents", methods=["GET", "POST", "PUT", "DELETE"])
def intent_crud():
    try:
        if request.method == "POST":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            intent = request.get_json()
            if intent:
                res, status = index.add_intent(es, intent)
                if status != 200:
                    return Response(res, status=status)
                return res
            return Response("Expect to recive a intent object!", status=400)

        elif request.method == "GET":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            intent_id = request.args.get("intent_id")
            if intent_id:
                try:
                    res = es.get(index=index.index_name, id=intent_id)
                    return {"result": res}
                except NotFoundError:
                    return Response(
                        "Intent with id %s was not found!" % intent_id, status=404
                    )
            intent_name = request.args.get("intent_name")
            if intent_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"intent": intent_name}}},
                )
                if res["hits"]["hits"]:
                    return res["hits"]["hits"][-1]
                else:
                    return Response(
                        "Intent with name %s was not found!" % intent_name, status=404
                    )
            return Response(
                "Expect to recive workspace_id and intent_name or intent_id!",
                status=400,
            )

        elif request.method == "PUT":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            intent = request.get_json()
            if not intent:
                return Response("Expect to recive a intent object!", status=400)
            update_query = {"doc": intent}
            intent_id = request.args.get("intent_id")
            if intent_id:
                try:
                    res = es.update(
                        index=index.index_name, id=intent_id, body=update_query
                    )
                    return res
                except NotFoundError:
                    return Response(
                        "Intent with id %s was not found!" % intent_id, status=404
                    )

            intent_name = request.args.get("intent_name")
            if intent_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"intent": intent_name}}},
                )
                if res["hits"]["hits"]:
                    intent_id = res["hits"]["hits"][0]["_id"]
                    res = es.update(
                        index=index.index_name, id=intent_id, body=update_query
                    )
                    return res
                else:
                    return Response(
                        "Intent with name %s was not found!" % intent_name, status=404
                    )
            return Response(
                "Expect to recive workspace_id and intent_name or intent_id!",
                status=400,
            )

        elif request.method == "DELETE":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            intent_id = request.args.get("intent_id")
            if intent_id:
                try:
                    res = es.delete(index=index.index_name, id=intent_id)
                    return res
                except NotFoundError:
                    return Response(
                        "Intent with id %s was not found!" % intent_id, status=404
                    )
            intent_name = request.args.get("intent_name")
            if intent_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"intent": intent_name}}},
                )
                if res["hits"]["hits"]:
                    intent_id = res["hits"]["hits"][0]["_id"]
                    res = es.delete(index=index.index_name, id=intent_id)
                    return res
                else:
                    return Response(
                        "Intent with name %s was not found!" % intent_name, status=404
                    )

            return Response(
                "Expect to recive workspace_id and intent_name or intent_id!",
                status=400,
            )

    except:
        trace_back_error = "".join([str(item) for item in sys.exc_info()])
        print(sys.exc_info())
        return Response(
            '{"response":"%s"}' % trace_back_error,
            status=500,
            mimetype="application/json",
        )
