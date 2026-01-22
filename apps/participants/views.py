from django.shortcuts import render, redirect
from .models import Participant

def trait(request):
    if request.method == "POST":
        consent = (request.POST.get("consent") == "on")
        risk = request.POST.get("risk")
        loss = request.POST.get("loss")
        exp = request.POST.get("exp")

        if not consent:
            return render(request, "participants/trait.html", {"error": "동의는 필수입니다."})

        # 참가자 생성
        p = Participant.objects.create(
            consent=True,
            risk=risk,
            loss=loss,
            exp=exp,
        )

        # 세션에 참가자 id 저장
        request.session["participant_id"] = p.id
        request.session["round_no"] = 1

        return redirect("/exp/round/1/")

    return render(request, "participants/trait.html")
