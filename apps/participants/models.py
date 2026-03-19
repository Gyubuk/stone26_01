from django.db import models
import uuid

class Participant(models.Model):
    # 기본 정보
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    consent = models.BooleanField(default=False)
    
    # 개인정보
    gender = models.CharField(max_length=10, verbose_name="성별", null=True, blank=True)
    age = models.PositiveIntegerField(verbose_name="나이", null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name="전화번호", null=True, blank=True)

    # 구매 희망 상품
    product = models.CharField(max_length=200, null=True, blank=True, verbose_name="구매 희망 상품")

    # 성향 측정
    risk = models.IntegerField(null=True, blank=True)
    exp = models.CharField(max_length=20, null=True, blank=True)

    # 위험 성향 측정 (동전 던지기 3단계) - 단위: 만원
    lottery_step1 = models.IntegerField(null=True, blank=True, verbose_name="위험성향_중간지점")
    lottery_step2 = models.IntegerField(null=True, blank=True, verbose_name="위험성향_상위구간")
    lottery_step3 = models.IntegerField(null=True, blank=True, verbose_name="위험성향_하위구간")

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'participants'
        ordering = ['-created_at']

    def __str__(self):
        return f"참가자 {self.code}"

    @property
    def risk_type(self):
        if not self.risk:
            return "미측정"
        if self.risk == 1:
            return "위험회피형 (복권A)"
        elif self.risk == 2:
            return "중립형 (복권B)"
        else:
            return "위험선호형 (복권C)"