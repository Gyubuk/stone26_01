from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Participant

def trait(request):
    if request.method == "POST":
        # 폼 데이터 받기
        consent = (request.POST.get("consent") == "on")
        product = request.POST.get("product")
        expected_price = request.POST.get("expected_price")
        risk = request.POST.get("risk")
        loss = request.POST.get("loss")
        exp = request.POST.get("exp")

        # 유효성 검사
        if not consent:
            return render(request, "participants/trait.html", {
                "error": "실험 참여 동의는 필수입니다."
            })

        if not product:
            return render(request, "participants/trait.html", {
                "error": "구매 희망 상품을 선택해주세요."
            })

        if not expected_price:
            return render(request, "participants/trait.html", {
                "error": "예상 가격을 입력해주세요."
            })

        # 예상 가격 검증
        try:
            expected_price = int(expected_price)
            if expected_price < 5 or expected_price > 100:
                return render(request, "participants/trait.html", {
                    "error": "예상 가격은 5~100만원 사이로 입력해주세요."
                })
        except (ValueError, TypeError):
            return render(request, "participants/trait.html", {
                "error": "올바른 가격을 입력해주세요."
            })

        if not risk:
            return render(request, "participants/trait.html", {
                "error": "위험성향 질문에 답해주세요."
            })

        if not loss:
            return render(request, "participants/trait.html", {
                "error": "손실회피 질문에 답해주세요."
            })

        if not exp:
            return render(request, "participants/trait.html", {
                "error": "경매 경험 여부를 선택해주세요."
            })

        # 참가자 생성
        try:
            p = Participant.objects.create(
                consent=True,
                product=product,
                expected_price=expected_price,
                risk=int(risk),
                loss=int(loss),
                exp=exp,
            )

            # 세션에 참가자 정보 저장
            request.session["participant_id"] = p.id
            request.session["current_round"] = 1

            # 성공 메시지
            messages.success(request, f'참가자 코드: {p.code} - 실험을 시작합니다!')

            # 실험 시작
            return redirect('experiments:round', round_number=1)

        except Exception as e:
            return render(request, "participants/trait.html", {
                "error": f"참가자 생성 중 오류가 발생했습니다: {str(e)}"
            })

    # GET 요청
    return render(request, "participants/trait.html")