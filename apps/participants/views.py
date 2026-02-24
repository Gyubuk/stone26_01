# apps/participants/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Participant


def trait(request):
    """상품 선택 및 실험 설명 화면"""
    participant_id = request.session.get('participant_id')
    if not participant_id:
        messages.error(request, '먼저 개인정보를 입력해주세요.')
        return redirect('core:home')

    try:
        participant = Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        messages.error(request, '참가자 정보를 찾을 수 없습니다.')
        return redirect('core:home')

    if request.method == "POST":
        product = request.POST.get("product", "").strip()
        lottery_raw = request.POST.get("expected_price_raw", "").strip()

        if not product:
            return render(request, "participants/trait.html", {
                "error": "구매 희망 상품을 입력해주세요.",
                "participant": participant
            })

        if not lottery_raw:
            return render(request, "participants/trait.html", {
                "error": "위험 성향 측정 금액을 입력해주세요.",
                "participant": participant
            })

        try:
            lottery_value = int(lottery_raw)
            if lottery_value < 0:
                raise ValueError
        except (ValueError, TypeError):
            return render(request, "participants/trait.html", {
                "error": "올바른 금액을 입력해주세요.",
                "participant": participant
            })

        try:
            participant.product = product
            participant.lottery = lottery_value
            participant.save()

            return redirect('experiments:round', exp_no=1, round_no=1)

        except Exception as e:
            return render(request, "participants/trait.html", {
                "error": f"저장 중 오류가 발생했습니다: {str(e)}",
                "participant": participant
            })

    return render(request, "participants/trait.html", {
        "participant": participant
    })