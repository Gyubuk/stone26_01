/**
 * 경매 라운드 페이지 JavaScript
 * 입찰가 스텝퍼 및 폼 검증 로직
 */

(function() {
    'use strict';

    // 설정값 가져오기
    const config = window.AUCTION_CONFIG || {};
    const min = config.min || 110000;
    const max = config.max || 190000;
    const step = config.step || 1000;
    const commission = config.commission || 20000;

    // DOM 요소
    const display = document.getElementById('bidDisplay');
    const input = document.getElementById('bidValue');
    const stepperButtons = document.querySelectorAll('.stepper-btn');
    const form = document.getElementById('auctionForm');

    /**
     * 값을 step 단위로 보정하고 범위 제한
     */
    function clampAndSnap(value) {
        // step 단위로 반올림
        value = Math.round(value / step) * step;
        // 범위 제한
        return Math.max(min, Math.min(max, value));
    }

    /**
     * 입찰가 설정 및 화면 업데이트
     */
    function setValue(value) {
        const oldValue = Number(input.value);
        const newValue = clampAndSnap(value);
        
        input.value = newValue;
        display.textContent = newValue.toLocaleString();

        // 값 변경 애니메이션
        if (oldValue !== newValue) {
            display.classList.add('value-changed');
            setTimeout(() => {
                display.classList.remove('value-changed');
            }, 300);
        }

        // 범위 초과 경고
        if (value < min) {
            showToast('최저입찰가는 ' + min.toLocaleString() + '원입니다.', 'warning');
        } else if (value > max) {
            showToast('최대입찰가는 ' + max.toLocaleString() + '원입니다.', 'warning');
        }
    }

    /**
     * 토스트 알림 표시
     */
    function showToast(message, type = 'warning') {
        const container = document.getElementById('toastContainer');
        
        // 아이콘 선택
        let icon = 'fa-exclamation-triangle';
        if (type === 'success') icon = 'fa-check-circle';
        if (type === 'error') icon = 'fa-times-circle';

        // 토스트 생성
        const toast = document.createElement('div');
        toast.className = `custom-toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${icon}"></i>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        container.appendChild(toast);

        // 3초 후 자동 제거
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * 스텝퍼 버튼 이벤트 리스너
     */
    stepperButtons.forEach(button => {
        button.addEventListener('click', function() {
            const delta = Number(this.getAttribute('data-delta'));
            const currentValue = Number(input.value);
            setValue(currentValue + delta);
        });
    });

    /**
     * 폼 제출 전 검증
     */
    form.addEventListener('submit', function(e) {
        const submitButton = document.activeElement;
        const decision = submitButton.value;

        if (decision === 'bid') {
            // 입찰 검증
            const bidValue = Number(input.value);

            // 범위 확인
            if (bidValue < min || bidValue > max) {
                e.preventDefault();
                showToast(
                    `입찰가는 ${min.toLocaleString()}원에서 ${max.toLocaleString()}원 사이여야 합니다.`,
                    'error'
                );
                return false;
            }

            // 확인 메시지
            const totalCost = bidValue + commission;
            const confirmMsg = 
                `${bidValue.toLocaleString()}원으로 입찰하시겠습니까?\n\n` +
                `낙찰 시 총 비용: ${totalCost.toLocaleString()}원\n` +
                `(입찰가 ${bidValue.toLocaleString()}원 + 수수료 ${commission.toLocaleString()}원)`;

            if (!confirm(confirmMsg)) {
                e.preventDefault();
                return false;
            }

        } else if (decision === 'buy') {
            // 즉시구매 확인
            const confirmMsg = 
                `${max.toLocaleString()}원으로 즉시구매 하시겠습니까?\n\n` +
                `확인을 누르면 바로 상품을 받게 됩니다.`;

            if (!confirm(confirmMsg)) {
                e.preventDefault();
                return false;
            }
        }

        // 폼 제출 중 표시
        form.classList.add('form-submitting');
    });

    /**
     * 키보드 단축키 (선택사항)
     */
    document.addEventListener('keydown', function(e) {
        // 입력 필드에 포커스가 있으면 무시
        if (document.activeElement.tagName === 'INPUT' || 
            document.activeElement.tagName === 'TEXTAREA') {
            return;
        }

        const currentValue = Number(input.value);

        switch(e.key) {
            case 'ArrowUp':
                e.preventDefault();
                setValue(currentValue + (e.shiftKey ? 10000 : 1000));
                break;
            case 'ArrowDown':
                e.preventDefault();
                setValue(currentValue - (e.shiftKey ? 10000 : 1000));
                break;
        }
    });

    /**
     * 초기화
     */
    function init() {
        // 초기값 설정
        setValue(Number(input.value));

        console.log('경매 라운드 초기화 완료', {
            min: min,
            max: max,
            step: step,
            commission: commission
        });
    }

    // 페이지 로드 시 초기화
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();