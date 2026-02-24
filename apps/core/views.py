# apps/core/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from apps.participants.models import Participant


def home(request):
    """홈 화면"""
    if request.method == "POST":
        consent = (request.POST.get("consent") == "on")
        if not consent:
            return render(request, "core/home.html", {
                "error": "실험 참여 동의는 필수입니다."
            })

        gender = request.POST.get("gender", "").strip()
        age = request.POST.get("age", "").strip()
        phone = request.POST.get("phone", "").strip()

        if not gender:
            return render(request, "core/home.html", {
                "error": "성별을 선택해주세요."
            })

        if not age:
            return render(request, "core/home.html", {
                "error": "나이를 입력해주세요."
            })

        try:
            age = int(age)
            if age < 1 or age > 120:
                return render(request, "core/home.html", {
                    "error": "올바른 나이를 입력해주세요."
                })
        except (ValueError, TypeError):
            return render(request, "core/home.html", {
                "error": "나이는 숫자로 입력해주세요."
            })

        try:
            p = Participant.objects.create(
                consent=True,
                gender=gender,
                age=age,
                phone=phone if phone else None,
            )
            request.session["participant_id"] = p.id
            return redirect('participants:trait')

        except Exception as e:
            return render(request, "core/home.html", {
                "error": f"참가자 등록 중 오류가 발생했습니다: {str(e)}"
            })

    return render(request, "core/home.html")