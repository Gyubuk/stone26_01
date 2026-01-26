from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import RoundDecision  # Round, Result 대신


# 라운드별 고정 시장가격 스케줄 (단위: 원)
MARKET_PRICE_SCHEDULE = [170000, 160000, 150000, 140000, 130000]  # 라운드 1~5

# 경매 조건
MAX_ROUND = 5
PS = 190000  # 즉시구매가
K = 110000   # 최저입찰가
C = 20000    # 수수료
STEP = 1000  # 입찰가 조정 단위

def get_market_price(round_number):
    """
    라운드별 고정 시장가격 반환
    나중에 실험 설계 확정되면 이 함수만 수정하면 됨
    """
    if 1 <= round_number <= len(MARKET_PRICE_SCHEDULE):
        return MARKET_PRICE_SCHEDULE[round_number - 1]
    return MARKET_PRICE_SCHEDULE[-1]  # 범위 초과시 마지막 값


def determine_auction_result(bid_amount, round_number):
    """
    입찰 결과 결정 (고정 로직)
    
    Args:
        bid_amount: 입찰가 (원)
        round_number: 현재 라운드 번호
    
    Returns:
        tuple: (win: bool, market_price: float)
    """
    market_price = get_market_price(round_number)
    win = bid_amount >= market_price
    return win, market_price


# ============================================
# 뷰 함수
# ============================================

@require_http_methods(["GET"])
def round_view(request, round_number):  # URL에서 오는 이름 그대로 유지
    """라운드 화면 표시"""
    participant_id = request.session.get('participant_id')
    if not participant_id:
        messages.error(request, '먼저 참가자 정보를 입력해주세요.')
        return redirect('participants:trait')
    
    # 라운드 범위 확인
    if round_number < 1 or round_number > MAX_ROUND:
        messages.error(request, '유효하지 않은 라운드입니다.')
        return redirect('experiments:done')
    
    # 이미 구매/낙찰된 적 있는지 확인
    has_acquired = RoundDecision.objects.filter(
        participant_id=participant_id,
        outcome__in=['bought', 'win']
    ).exists()
    
    if has_acquired:
        messages.info(request, '이미 상품을 획득하셨습니다.')
        return redirect('experiments:done')
    
    # 현재 라운드 세션에 저장
    request.session['current_round'] = round_number
    
    context = {
        'round_no': round_number,      # 👈 여기서 변환
        'max_round': MAX_ROUND,
        'Ps': PS,
        'k': K,
        'c': C,
        'default_bid': K,
        'step': STEP,
    }
    
    return render(request, 'experiments/round.html', context)

@require_http_methods(["POST"])
def make_choice(request):
    """즉시구매 또는 입찰 선택 처리"""
    participant_id = request.session.get('participant_id')
    if not participant_id:
        messages.error(request, '세션이 만료되었습니다.')
        return redirect('participants:trait')
    
    # 현재 라운드 확인
    current_round = request.session.get('current_round', 1)
    
    # 선택 확인
    decision = request.POST.get('decision')
    if decision not in ['buy', 'bid']:
        messages.error(request, '올바른 선택을 해주세요.')
        return redirect('experiments:round', round_number=current_round)
    
    if decision == 'buy':
        # 즉시구매
        round_decision = RoundDecision.objects.create(
            participant_id=participant_id,
            round_no=current_round,
            Ps=PS,
            k=K,
            c=C,
            decision_type='buy',
            outcome='bought',
            paid_price=PS
        )
        request.session['acquisition_round'] = current_round
        return redirect('experiments:result', decision_id=round_decision.id)
    
    else:  # decision == 'bid'
        # 입찰
        try:
            bid_amount = int(request.POST.get('bid_value', K))
        except (ValueError, TypeError):
            messages.error(request, '올바른 입찰가를 입력해주세요.')
            return redirect('experiments:round', round_number=current_round)
        
        # 입찰가 검증
        if bid_amount < K or bid_amount > PS:
            messages.error(request, f'입찰가는 {K:,}원에서 {PS:,}원 사이여야 합니다.')
            return redirect('experiments:round', round_number=current_round)
        
        # 입찰가 step 검증
        if (bid_amount - K) % STEP != 0:
            messages.error(request, f'입찰가는 {STEP:,}원 단위로 입력해주세요.')
            return redirect('experiments:round', round_number=current_round)
        
        # 낙찰/유찰 결정
        win, market_price = determine_auction_result(bid_amount, current_round)
        
        if win:
            # 낙찰
            paid_price = bid_amount + C
            outcome = 'win'
            request.session['acquisition_round'] = current_round
        else:
            # 유찰
            paid_price = 0
            outcome = 'lose'
        
        round_decision = RoundDecision.objects.create(
            participant_id=participant_id,
            round_no=current_round,
            Ps=PS,
            k=K,
            c=C,
            decision_type='bid',
            bid_value=bid_amount,
            market_price=market_price,
            outcome=outcome,
            paid_price=paid_price
        )
        
        return redirect('experiments:result', decision_id=round_decision.id)

@require_http_methods(["GET"])
def result_view(request, decision_id):
    """결과 화면"""
    try:
        decision = RoundDecision.objects.get(id=decision_id)
    except RoundDecision.DoesNotExist:
        messages.error(request, '결과를 찾을 수 없습니다.')
        return redirect('experiments:round', round_number=1)
    
    current_round = decision.round_no
    next_round = current_round + 1
    
    # 상품 획득 여부 확인
    acquired = decision.outcome in ['bought', 'win']
    
    # 다음 단계 결정
    if acquired:
        # 구매/낙찰 성공
        next_url = 'experiments:done'
        show_next_button = True
        next_button_text = '실험 종료'
        next_round_number = None
    elif current_round >= MAX_ROUND:
        # 5회 모두 유찰
        next_url = 'experiments:done'
        show_next_button = True
        next_button_text = '결과 확인'
        next_round_number = None
    else:
        # 다음 라운드로
        next_url = 'experiments:round'
        next_round_number = next_round
        show_next_button = True
        next_button_text = f'라운드 {next_round}로'
    
    context = {
        'decision': decision,  # 👈 'd' → 'decision'
        'round_number': current_round,
        'next_url': next_url,
        'next_round_number': next_round_number,
        'show_next_button': show_next_button,
        'next_button_text': next_button_text,
        'max_round': MAX_ROUND,
    }
    
    return render(request, 'experiments/result.html', context)
    
from apps.participants.models import Participant

@require_http_methods(["GET"])
def done_view(request):
    """실험 종료 화면 (5회 강제구매 처리 포함)"""
    participant_id = request.session.get('participant_id')
    if not participant_id:
        messages.error(request, '세션이 만료되었습니다.')
        return redirect('participants:trait')
    
    # 👇 participant 객체 가져오기 (함수 안에서!)
    try:
        participant = Participant.objects.get(id=participant_id)  # 👈 participant_id 사용
    except Participant.DoesNotExist:
        participant = None
    
    # 구매/낙찰 여부 확인
    acquired_decision = RoundDecision.objects.filter(
        participant_id=participant_id,
        outcome__in=['bought', 'win']
    ).first()
    
    # 5회 강제구매 처리
    if not acquired_decision:
        decision_count = RoundDecision.objects.filter(
            participant_id=participant_id
        ).count()
        
        if decision_count >= MAX_ROUND:
            # 초기 Ps로 강제구매 레코드 생성
            acquired_decision = RoundDecision.objects.create(
                participant_id=participant_id,
                round_no=MAX_ROUND,
                Ps=PS,
                k=K,
                c=C,
                decision_type='buy',
                outcome='bought',
                paid_price=PS
            )
            
            messages.warning(request, 
                f'{MAX_ROUND}회 라운드가 모두 종료되어 초기 즉시구매가 {PS:,}원으로 자동 구매 처리되었습니다.')
    
    # 전체 결과 조회
    all_decisions = RoundDecision.objects.filter(
        participant_id=participant_id
    ).order_by('round_no')
    
    # 최종 지불액 계산
    if acquired_decision:
        final_payment = acquired_decision.paid_price
        if acquired_decision.outcome == 'bought':
            if acquired_decision.round_no == MAX_ROUND and \
               RoundDecision.objects.filter(participant_id=participant_id).count() == MAX_ROUND:
                acquisition_method = '강제구매 (5회 유찰)'
            else:
                acquisition_method = '즉시구매'
        else:  # win
            acquisition_method = '입찰(낙찰)'
    else:
        final_payment = 0
        acquisition_method = '미구매'
    
    context = {
        'participant': participant, 
        'all_decisions': all_decisions,
        'acquired_decision': acquired_decision,
        'final_payment': final_payment,
        'acquisition_method': acquisition_method,
        'max_round': MAX_ROUND,
    }
    
    return render(request, 'experiments/done.html', context)