from django.db import models
import uuid

class Participant(models.Model):
    # 기본 정보
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    consent = models.BooleanField(default=False)
    
    # 개인정보 (임시로 null 허용)
    gender = models.CharField(max_length=10, verbose_name="성별", null=True, blank=True)
    age = models.PositiveIntegerField(verbose_name="나이", null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name="전화번호", null=True, blank=True)

    # 구매 희망 상품
    product = models.CharField(max_length=200, null=True, blank=True, verbose_name="구매 희망 상품")

    # 성향 측정
    risk = models.IntegerField(null=True, blank=True)
    lottery = models.IntegerField(null=True, blank=True)
    exp = models.CharField(max_length=20, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'participants'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})" if self.name else f"참가자 {self.code}"

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