"""Human-assessed commercial acceptance, separate from heuristic triage."""
WEIGHTS = {'photography':25, 'copy':20, 'technical_accuracy':20,
           'trust_and_desire':15, 'mobile_conversion':15, 'non_redundancy':5}
MINIMUM_DIMENSION_SCORE = 4
HARD_GATES = ('exact_model_and_verified_gallery', 'essential_facts_verified',
              'distinct_image_purposes', 'correct_spec_labels', 'no_truncated_or_empty_rows',
              'no_repeated_order_notice', 'clear_cta_and_availability',
              'customer_and_seller_questions_answered', 'trust_claims_verified',
              'mobile_render_reviewed', 'desktop_render_reviewed')


def assess(review, plan_hash):
    """Validate reviewer-supplied observations, never infer or certify screenshots."""
    if not isinstance(review, dict) or review.get('plan_hash') != plan_hash:
        raise ValueError('revisión comercial no vinculada al plan')
    scores, gates, notes = (review.get(k) for k in ('scores','gates','notes'))
    if (not isinstance(scores,dict) or set(scores) != set(WEIGHTS)
            or any(type(v) is not int or not 0 <= v <= 5 for v in scores.values())
            or not isinstance(gates,dict) or set(gates) != set(HARD_GATES)
            or any(type(v) is not bool for v in gates.values())
            or not isinstance(notes,dict) or set(notes) != set(WEIGHTS)
            or any(not isinstance(v,str) or not v.strip() for v in notes.values())):
        raise ValueError('evaluación comercial incompleta')
    score = sum(WEIGHTS[k]*scores[k] for k in WEIGHTS)/5
    blockers = [k for k in HARD_GATES if gates[k] is not True]
    blockers.extend(f'{k}_below_{MINIMUM_DIMENSION_SCORE}' for k in WEIGHTS
                    if scores[k] < MINIMUM_DIMENSION_SCORE)
    if score < 90:
        blockers.append('score_below_90')
    return {'score':score,'blockers':blockers,'eligible':not blockers,'publish_allowed':False}
