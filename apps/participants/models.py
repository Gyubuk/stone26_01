from django.db import models
import uuid

class Participant(models.Model):
    # 기본 정보
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    consent = models.BooleanField(default=False)

    # 구매 희망 상품
    PRODUCT_CHOICES = [
        ('sneakers', '한정판 스니커즈'),
        ('concert', '콘서트/공연 티켓'),
        ('game', '한정판 게임/피규어'),
    ]
    product = models.CharField(max_length=20, choices=PRODUCT_CHOICES, null=True, blank=True)
    
    # 예상 가격 (만원 단위)
    expected_price = models.IntegerField(null=True, blank=True, help_text="만원 단위")

    # 위험성향 (1~7점)
    risk = models.IntegerField(null=True, blank=True, help_text="1=복권A(안전), 2=복권B(중립), 3=복권C(위험)")
    
    # 손실회피 (1~7점)
    loss = models.IntegerField(null=True, blank=True, help_text="1=손실회피 강함(상황A), 2=손실회피 약함(상황B)")
    
    # 경매/리셀 경험
    exp = models.CharField(max_length=20, null=True, blank=True)  # yes / no

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'participants'
        ordering = ['-created_at']

    def __str__(self):
        return f"참가자 {self.code}"

    @property
    def risk_type(self):
        """위험성향 유형 반환"""
        if not self.risk:
            return "미측정"
        if self.risk == 1:
            return "위험회피형 (복권A)"
        elif self.risk == 2:
            return "중립형 (복권B)"
        else:
            return "위험선호형 (복권C)"

    @property
    def loss_type(self):
        """손실회피 유형 반환"""
        if not self.loss:
            return "미측정"
        if self.loss == 1:
            return "손실회피 강함 (상황A)"
        else:
            return "손실회피 약함 (상황B)"