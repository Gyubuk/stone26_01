# apps/experiments/models.py

from django.db import models
from apps.participants.models import Participant

class RoundDecision(models.Model):
    DECISION_CHOICES = [
        ("buy", "즉시구매"),
        ("bid", "입찰"),
    ]
    OUTCOME_CHOICES = [
        ("bought", "즉시구매 완료"),
        ("win", "낙찰"),
        ("lose", "유찰"),
    ]

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    exp_no = models.PositiveIntegerField(default=1)   # 실험 번호 (1~6)
    round_no = models.PositiveIntegerField()          # 라운드 번호 (1~5)

    Ps = models.IntegerField()       # 즉시구매가
    k = models.IntegerField()        # 최저입찰가
    c = models.IntegerField()        # 수수료

    decision_type = models.CharField(max_length=10, choices=DECISION_CHOICES)
    bid_value = models.IntegerField(null=True, blank=True)
    market_price = models.IntegerField(null=True, blank=True)

    outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES)
    paid_price = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['exp_no', 'round_no']
        unique_together = ['participant', 'exp_no', 'round_no']

    def __str__(self):
        return f"P:{self.participant_id} E{self.exp_no}-R{self.round_no} {self.decision_type} {self.outcome}"