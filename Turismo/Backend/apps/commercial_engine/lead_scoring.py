class LeadScoringEngine:
    """
    Motor de calificación de prospectos.
    """

    @staticmethod
    def score_lead(lead):
        score = 0

        # Heurísticas simples
        if lead.contact_email.endswith(('.gov', '.org', '.edu')):
            score += 50

        # Otras reglas pueden ser agregadas aquí
        lead.score = score
        lead.save()
        return score

    @staticmethod
    def should_qualify(lead):
        return lead.score >= 40
