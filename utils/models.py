def bm25_check(recipe):
    bm25 = recipe.get("BM25")
    if not bm25:
        return 'Expect to recive the "BM25" object!', 400
    b = bm25.get("b")
    if b == None:
        return 'Expect to recive the "b" parameter for BM25 model!', 400
    if type(b) != float:
        return 'The "b" must be a float!', 400
    if b < 0 or b > 1:
        return 'The "b" value  must be between 0 and 1!', 400

    k1 = bm25.get("k1")
    if k1 == None:
        return 'Expect to recive the "k1" parameter for BM25 model!', 400
    if type(k1) != float:
        return 'The "k1" must be a float!', 400
    if k1 < 0:
        return 'The "k1" value must be greater than zero!', 400
    return "ok", 200


def ann_feed_forward_check(recipe):
    pass


MODELS_CHECKS = {"ann_feed_forward": ann_feed_forward_check, "BM25": bm25_check}


def check_recipe(model_kind, recipe):
    check_function = MODELS_CHECKS.get(model_kind, None)
    if not check_function:
        return "There is no model %s" % model_kind, 404
    return check_function(recipe)
