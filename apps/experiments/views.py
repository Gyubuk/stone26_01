from django.shortcuts import render, redirect, get_object_or_404
from apps.participants.models import Participant
from .models import RoundDecision
import random

MAX_ROUND = 5

# 일단 조건은 "고정"으로 시작 (나중에 라운드별로 바꿔도 됨)
DEFAULT_Ps = 190000
DEFAULT_k = 110000
DEFAULT_c = 5000

STEP = 1000  # 입찰 단위(천원). 교수님 피드백에 맞춰 UI도 버튼으로 만들 예정

def _get_participant(request):
    pid = request.session.get("participant_id")
    if not pid:
        return None
    return Participant.objects.filter(id=pid).first()

def _clamp_to_step(value: int, step: int) -> int:
    return int(round(value / step) * step)

def round_view(request, round_no: int):
    p = _get_participant(request)
    if not p:
        return redirect("/p/trait/")

    if round_no < 1 or round_no > MAX_ROUND:
        return redirect("/exp/round/1/")

    Ps, k, c = DEFAULT_Ps, DEFAULT_k, DEFAULT_c

    if request.method == "POST":
        decision = request.POST.get("decision")  # "buy" or "bid"

        if decision == "buy":
            d = RoundDecision.objects.create(
                participant=p,
                round_no=round_no,
                Ps=Ps, k=k, c=c,
                decision_type="buy",
                bid_value=None,
                market_price=None,
                outcome="bought",
                paid_price=Ps,  # 추측: 즉시구매는 Ps만 지불(수수료 없음)
            )
            return redirect(f"/exp/result/{d.id}/")

        if decision == "bid":
            raw = request.POST.get("bid_value")
            if not raw:
                return render(request, "experiments/round.html", {
                    "error": "입찰가를 입력해 주세요.",
                    "round_no": round_no, "max_round": MAX_ROUND,
                    "Ps": Ps, "k": k, "c": c, "step": STEP,
                    "default_bid": k,
                })

            try:
                bid = int(raw)
            except ValueError:
                bid = k

            # step 맞추기 + 범위 제한
            bid = _clamp_to_step(bid, STEP)
            bid = max(k, min(Ps, bid))

            # ------- 낙찰 로직 (추측) -------
            # 숨은 시장가격 M을 [k, Ps]에서 랜덤으로 하나 뽑고, bid >= M 이면 낙찰
            market_price = random.randrange(k, Ps + STEP, STEP)
            win = bid >= market_price
            # --------------------------------

            if win:
                outcome = "win"
                paid = bid + c  # 추측: 입찰 낙찰 시 수수료 c 추가
            else:
                outcome = "lose"
                paid = 0

            d = RoundDecision.objects.create(
                participant=p,
                round_no=round_no,
                Ps=Ps, k=k, c=c,
                decision_type="bid",
                bid_value=bid,
                market_price=market_price,
                outcome=outcome,
                paid_price=paid,
            )
            return redirect(f"/exp/result/{d.id}/")

        # decision 값 이상할 때
        return redirect(f"/exp/round/{round_no}/")

    # GET 화면
    return render(request, "experiments/round.html", {
        "round_no": round_no,
        "max_round": MAX_ROUND,
        "Ps": Ps,
        "k": k,
        "c": c,
        "step": STEP,
        "default_bid": k,
    })

def result_view(request, decision_id: int):
    p = _get_participant(request)
    if not p:
        return redirect("/p/trait/")

    d = get_object_or_404(RoundDecision, id=decision_id, participant=p)

    # 다음 라운드
    next_round = d.round_no + 1

    # 5회 끝나면 done으로
    if d.round_no >= MAX_ROUND:
        return redirect("/exp/done/")

    return render(request, "experiments/result.html", {
        "d": d,
        "next_round": next_round,
        "max_round": MAX_ROUND,
    })

def done_view(request):
    p = _get_participant(request)
    if not p:
        return redirect("/p/trait/")

    # 간단 요약(선택)
    decisions = RoundDecision.objects.filter(participant=p).order_by("round_no")
    return render(request, "experiments/done.html", {
        "participant": p,
        "decisions": decisions,
    })
