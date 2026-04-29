class SeverityScorer:

    def __init__(self):
        pass

    def compute(self, depth, bbox_area):

        score = (depth * 0.6) + (bbox_area * 0.4)

        if score < 0.3:
            return "LOW"

        elif score < 0.6:
            return "MEDIUM"

        elif score < 1:
            return "HIGH"

        else:
            return "CRITICAL"