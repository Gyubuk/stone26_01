# apps/experiments/views.py

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from apps.participants.models import Participant
from .models import RoundDecision
from .config import (
    MAX_EXP, MAX_ROUND, MAX_TYPE, PS, K_INITIAL, STEP,
    TYPE_CONFIGS, get_exp_config, get_type_no, get_repeat_no,
    generate_market_price
)


def _get_participant(request):
    """세션에서 참가자 가져오기"""
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return None
    try:
        return Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        return None


def _get_min_bid(participant_id, exp_no, round_no):
    """
    현재 라운드의 최저입찰가 계산
    - 라운드 1: 초기값 K_INITIAL
    - 라운드 2~5: 전 라운드에서 유찰했다면 그때 입찰한 가격으로 업데이트
    """
    if round_no == 1:
        return K_INITIAL

    prev = RoundDecision.objects.filter(
        participant_id=participant_id,
        exp_no=exp_no,
        round_no=round_no - 1
    ).first()

    if prev and prev.outcome == 'lose' and prev.bid_value:
        return prev.bid_value

    return K_INITIAL


@require_http_methods(["GET"])
def round_view(request, exp_no, round_no):
    """라운드 화면"""
    participant = _get_participant(request)
    if not participant:
        messages.error(request, '먼저 참가자 정보를 입력해주세요.')
        return redirect('core:home')

    # 범위 검증
    if exp_no < 1 or exp_no > MAX_EXP:
        return redirect(reverse('experiments:done'))
    if round_no < 1 or round_no > MAX_ROUND:
        return redirect(reverse('experiments:done'))

    # 현재 실험에서 이미 구매/낙찰한지 확인
    has_acquired = RoundDecision.objects.filter(
        participant=participant,
        exp_no=exp_no,
        outcome__in=['bought', 'win']
    ).exists()

    if has_acquired:
        if exp_no < MAX_EXP:
            return redirect(reverse('experiments:round', kwargs={'exp_no': exp_no + 1, 'round_no': 1}))
        else:
            return redirect(reverse('experiments:done'))

    # 이미 이 라운드를 했는지 확인
    existing = RoundDecision.objects.filter(
        participant=participant,
        exp_no=exp_no,
        round_no=round_no
    ).first()
    if existing:
        return redirect(reverse('experiments:result', kwargs={'decision_id': existing.id}))

    config = get_exp_config(exp_no)
    min_bid = _get_min_bid(participant.id, exp_no, round_no)

    request.session['current_exp'] = exp_no
    request.session['current_round'] = round_no

    context = {
        'exp_no': exp_no,
        'round_no': round_no,
        'max_exp': MAX_EXP,
        'max_round': MAX_ROUND,
        'Ps': PS,
        'k': min_bid,
        'c': config['c'],
        'step': STEP,
        'participant': participant,
    }
    return render(request, 'experiments/round.html', context)


@require_http_methods(["POST"])
def make_choice(request):
    """즉시구매 또는 입찰 처리"""
    participant = _get_participant(request)
    if not participant:
        messages.error(request, '세션이 만료되었습니다.')
        return redirect('core:home')

    exp_no = int(request.POST.get('exp_no', 1))
    round_no = int(request.POST.get('round_no', 1))
    decision = request.POST.get('decision')

    # 중복 제출 방지
    existing = RoundDecision.objects.filter(
        participant=participant,
        exp_no=exp_no,
        round_no=round_no
    ).first()
    if existing:
        return redirect(reverse('experiments:result', kwargs={'decision_id': existing.id}))

    config = get_exp_config(exp_no)
    c = config['c']
    min_bid = _get_min_bid(participant.id, exp_no, round_no)

    if decision == 'buy':
        # 즉시구매: PS 그대로 지불
        rd = RoundDecision.objects.create(
            participant=participant,
            exp_no=exp_no,
            round_no=round_no,
            Ps=PS,
            k=min_bid,
            c=c,
            decision_type='buy',
            outcome='bought',
            paid_price=PS,
        )
        return redirect(reverse('experiments:result', kwargs={'decision_id': rd.id}))

    elif decision == 'bid':
        try:
            bid_amount = int(request.POST.get('bid_value', min_bid))
        except (ValueError, TypeError):
            messages.error(request, '올바른 입찰가를 입력해주세요.')
            return redirect(reverse('experiments:round', kwargs={'exp_no': exp_no, 'round_no': round_no}))

        if bid_amount < min_bid or bid_amount > PS:
            messages.error(request, f'입찰가는 {min_bid:,}원 ~ {PS:,}원 사이여야 합니다.')
            return redirect(reverse('experiments:round', kwargs={'exp_no': exp_no, 'round_no': round_no}))

        market_price = generate_market_price(exp_no, round_no)

        if bid_amount >= market_price:
            outcome = 'win'
            paid_price = bid_amount + c  # 낙찰: 입찰가 + 수수료
        else:
            outcome = 'lose'
            paid_price = 0

        rd = RoundDecision.objects.create(
            participant=participant,
            exp_no=exp_no,
            round_no=round_no,
            Ps=PS,
            k=min_bid,
            c=c,
            decision_type='bid',
            bid_value=bid_amount,
            market_price=market_price,
            outcome=outcome,
            paid_price=paid_price,
        )
        return redirect(reverse('experiments:result', kwargs={'decision_id': rd.id}))

    messages.error(request, '올바른 선택을 해주세요.')
    return redirect(reverse('experiments:round', kwargs={'exp_no': exp_no, 'round_no': round_no}))


@require_http_methods(["GET"])
def result_view(request, decision_id):
    """결과 화면"""
    participant = _get_participant(request)
    if not participant:
        return redirect('core:home')

    try:
        decision = RoundDecision.objects.get(id=decision_id, participant=participant)
    except RoundDecision.DoesNotExist:
        return redirect('core:home')

    exp_no = decision.exp_no
    round_no = decision.round_no
    acquired = decision.outcome in ['bought', 'win']

    # 다음 단계 결정
    if acquired or round_no >= MAX_ROUND:
        # 구매/낙찰 완료 OR 5라운드 모두 유찰 → 다음 실험
        if exp_no < MAX_EXP:
            next_url = reverse('experiments:round', kwargs={'exp_no': exp_no + 1, 'round_no': 1})
            next_label = f"실험 {exp_no + 1} 시작"
        else:
            next_url = reverse('experiments:done')
            next_label = "실험 종료"
    else:
        # 유찰 → 다음 라운드
        next_url = reverse('experiments:round', kwargs={'exp_no': exp_no, 'round_no': round_no + 1})
        next_label = f"라운드 {round_no + 1}"

    context = {
        'decision': decision,
        'exp_no': exp_no,
        'round_no': round_no,
        'max_exp': MAX_EXP,
        'max_round': MAX_ROUND,
        'next_url': next_url,
        'next_label': next_label,
        'acquired': acquired,
    }
    return render(request, 'experiments/result.html', context)


@require_http_methods(["GET"])
def done_view(request):
    """실험 종료 화면"""
    participant = _get_participant(request)
    if not participant:
        return redirect('core:home')

    exp_summaries = []
    # type_no 기준으로 집계 (수수료별)
    c_totals = {}  # {c값: {'count': 0, 'total_paid': 0}}
    total_paid = 0

    for exp_no in range(1, MAX_EXP + 1):
        config = get_exp_config(exp_no)
        type_no = get_type_no(exp_no)
        repeat_no = get_repeat_no(exp_no)
        c = config['c']

        decisions = RoundDecision.objects.filter(
            participant=participant,
            exp_no=exp_no
        ).order_by('round_no')

        # 구매/낙찰 여부 확인
        final = decisions.filter(outcome__in=['bought', 'win']).first()

        if final:
            paid = final.paid_price
        else:
            # 5라운드 모두 유찰 → PS(190,000원)로 강제 구매
            paid = PS + c

        total_paid += paid

        # 수수료별 집계
        if c not in c_totals:
            c_totals[c] = {'count': 0, 'total_paid': 0}
        c_totals[c]['count'] += 1
        c_totals[c]['total_paid'] += paid

        exp_summaries.append({
            'exp_no': exp_no,
            'type_no': type_no,
            'repeat_no': repeat_no,
            # ✅ seller 키 제거 - 실험자에게 노출 금지
            'c': c,
            'decisions': decisions,
            'final': final,
            'paid': paid,
        })

    # 수수료별 요약 (seller 정보 없이)
    type_summaries = []
    for c_val in sorted(c_totals.keys()):
        count = c_totals[c_val]['count']
        total = c_totals[c_val]['total_paid']
        type_summaries.append({
            'c': c_val,
            'count': count,
            'avg_paid': total / count if count > 0 else 0,
        })

    context = {
        'participant': participant,
        'exp_summaries': exp_summaries,
        'type_summaries': type_summaries,
        'total_paid': total_paid,
        'max_exp': MAX_EXP,
    }
    return render(request, 'experiments/done.html', context)