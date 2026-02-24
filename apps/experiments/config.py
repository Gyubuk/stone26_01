# apps/experiments/config.py

import numpy as np

# 전체 설정
MAX_TYPE = 6
REPEAT_PER_TYPE = 7
MAX_EXP = MAX_TYPE * REPEAT_PER_TYPE  # 총 42회
MAX_ROUND = 5
PS = 190000
K_INITIAL = 110000
STEP = 1000

# 타입별 설정 (내부용 - 절대 템플릿에 노출 금지)
TYPE_CONFIGS = {
    1: {'seller': '안짠돌이', 'c': 3000, 'beta': (2, 5)},
    2: {'seller': '안짠돌이', 'c': 6000, 'beta': (2, 5)},
    3: {'seller': '안짠돌이', 'c': 9000, 'beta': (2, 5)},
    4: {'seller': '짠돌이',   'c': 3000, 'beta': (5, 2)},
    5: {'seller': '짠돌이',   'c': 6000, 'beta': (5, 2)},
    6: {'seller': '짠돌이',   'c': 9000, 'beta': (5, 2)},
}

# 실험 순서: 1→4→2→5→3→6 (각 7번씩 블록)
# exp_no 1~7   → 타입 1 (안짠돌이 c=3000)
# exp_no 8~14  → 타입 4 (짠돌이   c=3000)
# exp_no 15~21 → 타입 2 (안짠돌이 c=6000)
# exp_no 22~28 → 타입 5 (짠돌이   c=6000)
# exp_no 29~35 → 타입 3 (안짠돌이 c=9000)
# exp_no 36~42 → 타입 6 (짠돌이   c=9000)
EXP_ORDER = [1, 4, 2, 5, 3, 6]  # 타입 순서


def get_type_no(exp_no):
    """
    실험 번호 → 타입 번호
    블록 단위: exp 1~7 → EXP_ORDER[0], exp 8~14 → EXP_ORDER[1], ...
    """
    block_index = (exp_no - 1) // REPEAT_PER_TYPE  # 0~5
    return EXP_ORDER[block_index]


def get_repeat_no(exp_no):
    """블록 내 몇 번째 반복인지 (1~7)"""
    return ((exp_no - 1) % REPEAT_PER_TYPE) + 1


def get_exp_config(exp_no):
    """실험 번호에 해당하는 설정 반환 (seller 키 포함되나 템플릿에 넘기지 말 것)"""
    type_no = get_type_no(exp_no)
    return TYPE_CONFIGS[type_no]


def generate_market_price(exp_no, round_no):
    """
    Beta 분포로 시장가 생성 (시드 고정 → 재현 가능)
    짠돌이: beta(5,2) → 높은 시장가 (낙찰 어려움)
    안짠돌이: beta(2,5) → 낮은 시장가 (낙찰 쉬움)
    """
    seed = exp_no * 100 + round_no
    rng = np.random.default_rng(seed)

    config = get_exp_config(exp_no)
    a, b = config['beta']

    beta_value = rng.beta(a, b)
    market_price = int(beta_value * (PS - K_INITIAL) + K_INITIAL)

    return round(market_price / STEP) * STEP