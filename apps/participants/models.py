from django.db import models
import uuid

class Participant(models.Model):
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    consent = models.BooleanField(default=False)

    # 아주 단순한 값 저장(나중에 척도 바꿔도 됨)
    risk = models.CharField(max_length=20)   # safe / risky 등
    loss = models.CharField(max_length=20)   # low / high 등
    exp = models.CharField(max_length=20)    # yes / no 등

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code}"