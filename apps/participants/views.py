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
        step1_raw = request.POST.get("risk_step1_raw", "").strip()
        step2_raw = request.POST.get("risk_step2_raw", "").strip()
        step3_raw = request.POST.get("risk_step3_raw", "").strip()

        if not product:
            return render(request, "participants/trait.html", {
                "error": "구매 희망 상품을 입력해주세요.",
                "participant": participant
            })

        if not step1_raw or not step2_raw or not step3_raw:
            return render(request, "participants/trait.html", {
                "error": "위험 성향 측정 금액을 모두 입력해주세요.",
                "participant": participant
            })

        try:
            step1_value = int(step1_raw)
            step2_value = int(step2_raw)
            step3_value = int(step3_raw)
            if any(v < 0 for v in [step1_value, step2_value, step3_value]):
                raise ValueError
        except (ValueError, TypeError):
            return render(request, "participants/trait.html", {
                "error": "올바른 금액을 입력해주세요.",
                "participant": participant
            })

        try:
            participant.product = product
            participant.lottery_step1 = step1_value
            participant.lottery_step2 = step2_value
            participant.lottery_step3 = step3_value
            participant.save()

            return redirect('experiments:practice_round_start')

        except Exception as e:
            return render(request, "participants/trait.html", {
                "error": f"저장 중 오류가 발생했습니다: {str(e)}",
                "participant": participant
            })

    return render(request, "participants/trait.html", {
        "participant": participant
    })