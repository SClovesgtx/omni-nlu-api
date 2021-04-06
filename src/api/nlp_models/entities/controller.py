# standard library imports
import sys

sys.path.append("./src/")

# third party imports
from flask import Blueprint, request, Response

entities_app = Blueprint("entities_app", __name__)

# local imports
from utils.entities import SynonymMatcher, nlp, check_regex_pattern, entity_check
from elasticsearch_db.elasticsearch import elastic_conection
from elasticsearch_db.elasticsearch import get_nlp_model

es = elastic_conection()


@entities_app.route("/nlp_models/entities", methods=["GET", "POST", "PUT", "DELETE"])
def entities_crud():
    try:
        if request.method == "POST":
            entity = request.get_json()
            if entity == None:
                return Response("Expect to recive a entity object!", status=400)
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            if entity:
                res, status = entity_check(entity)
                if status != 200:
                    return Response(res, status=status)
                res, status = index.add_entity(es, entity)
                if status != 200:
                    return Response(res, status=status)
                return res
            return Response("Expect to recive a entity object!", status=400)
        if request.method == "GET":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            entity_id = request.args.get("entity_id")
            if entity_id:
                try:
                    res = es.get(index=index.index_name, id=entity_id)
                    return res
                except NotFoundError:
                    return Response(
                        "Entity with id %s was not found!" % entity_id, status=404
                    )
            entity_name = request.args.get("entity_name")
            if entity_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"entity": entity_name}}},
                )
                if res["hits"]["hits"]:
                    return res["hits"]["hits"][-1]
                else:
                    return Response(
                        "Entity with name %s was not found!" % entity_name, status=404
                    )
            return Response(
                "Expect to recive workspace_id and entity_name or entity_id!",
                status=400,
            )

        elif request.method == "PUT":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            entity = request.get_json()
            if not entity:
                return Response("Expect to recive a intent object!", status=400)
            update_query = {"doc": entity}
            entity_id = request.args.get("entity_id")
            if entity_id:
                try:
                    res = es.update(
                        index=index.index_name, id=entity_id, body=update_query
                    )
                    return res
                except NotFoundError:
                    return Response(
                        "Entity with id %s was not found!" % entity_id, status=404
                    )

            entity_name = request.args.get("entity_name")
            if entity_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"entity": entity_name}}},
                )
                if res["hits"]["hits"]:
                    entity_id = res["hits"]["hits"][0]["_id"]
                    res = es.update(
                        index=index.index_name, id=entity_id, body=update_query
                    )
                    return res
                else:
                    return Response(
                        "Entity_id with name %s was not found!" % entity_name,
                        status=404,
                    )
            return Response(
                "Expect to recive workspace_id and entity_name or entity_id!",
                status=400,
            )

        elif request.method == "DELETE":
            workspace_id = request.args.get("workspace_id")
            index, exist = get_nlp_model(es, workspace_id=workspace_id)
            if not exist:
                return index
            entity_id = request.args.get("entity_id")
            if entity_id:
                try:
                    res = es.delete(index=index.index_name, id=entity_id)
                    return res
                except NotFoundError:
                    return Response(
                        "Entity with id %s was not found!" % entity_id, status=404
                    )
            entity_name = request.args.get("entity_name")
            if entity_name:
                res = es.search(
                    index=index.index_name,
                    body={"query": {"term": {"entity": entity_name}}},
                )
                if res["hits"]["hits"]:
                    entity_id = res["hits"]["hits"][0]["_id"]
                    res = es.delete(index=index.index_name, id=entity_id)
                    return res
                else:
                    return Response(
                        "Entity with name %s was not found!" % entity_name, status=404
                    )

            return Response(
                "Expect to recive workspace_id and entity_name or entity_id!",
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
