(function() {
    'use strict';

    const config = window.AUCTION_CONFIG || {};
    const min = config.min || 110000;
    const max = config.max || 190000;
    const step = config.step || 1000;
    const commission = config.commission || 9000;
    const exp_no = config.exp_no || 1;
    const round_no = config.round_no || 1;

    // DOM
    const display = document.getElementById('bidDisplay');
    const stepperButtons = document.querySelectorAll('.stepper-btn');
    const bidSubmitBtn = document.getElementById('bidSubmitBtn');

    window.currentBid = min;

    // 값 보정
    function clampAndSnap(value) {
        value = Math.round(value / step) * step;
        return Math.max(min, Math.min(max, value));
    }

    // 디스플레이 업데이트
    window.updateDisplay = function() {
        display.textContent = window.currentBid.toLocaleString();
        display.classList.add('value-changed');
        setTimeout(() => display.classList.remove('value-changed'), 300);
    };

    // 스텝퍼 버튼
    stepperButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const delta = Number(this.getAttribute('data-delta'));
            const newVal = clampAndSnap(window.currentBid + delta);
            if (newVal !== window.currentBid) {
                window.currentBid = newVal;
                window.updateDisplay();
            } else {
                showToast(
                    window.currentBid + delta < min
                        ? `최저입찰가는 ${min.toLocaleString()}원입니다.`
                        : `최대입찰가는 ${max.toLocaleString()}원입니다.`,
                    'warning'
                );
            }
        });
    });

    // 입찰 제출
    bidSubmitBtn.addEventListener('click', function() {
        const confirmMsg =
            `${window.currentBid.toLocaleString()}원으로 입찰하시겠습니까?\n\n` +
            `낙찰 시 총 비용: ${(window.currentBid + commission).toLocaleString()}원`;

        if (!confirm(confirmMsg)) return;

        // 폼 생성 및 제출
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/exp/make_choice/';

        const csrfMatch = document.cookie.match(/csrftoken=([^;]+)/);
        const fields = {
            'exp_no': exp_no,
            'round_no': round_no,
            'decision': 'bid',
            'bid_value': window.currentBid,
            'csrfmiddlewaretoken': csrfMatch ? csrfMatch[1] : ''
        };

        Object.entries(fields).forEach(([name, value]) => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = name;
            input.value = value;
            form.appendChild(input);
        });

        document.body.appendChild(form);
        form.submit();
    });

    // 토스트
    function showToast(message, type = 'warning') {
        // Tailwind 버전 override가 있으면 사용
        if (window.showToastOverride) {
            window.showToastOverride(message, type);
            return;
        }
        // fallback
        alert(message);
    }

    // 초기화
    window.updateDisplay();

})();