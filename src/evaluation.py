def calculate_kg_metrics(predicted_triples, gold_triples):
    """
    Calculate Precision, Recall, and F1 for extracted triples.
    Triples should be a list of tuples or dictionaries (head, type, tail).
    """
    # Convert to sets of tuples for easy comparison
    pred_set = set()
    for t in predicted_triples:
        if isinstance(t, dict):
            pred_set.add((t['head'], t['type'], t['tail']))
        else:
            pred_set.add(t)

    gold_set = set()
    for t in gold_triples:
        if isinstance(t, dict):
            gold_set.add((t['head'], t['type'], t['tail']))
        else:
            gold_set.add(t)

    true_positives = len(pred_set.intersection(gold_set))
    false_positives = len(pred_set - gold_set)
    false_negatives = len(gold_set - pred_set)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }
