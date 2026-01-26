/**
 * 결과 페이지 JavaScript
 */

(function() {
    'use strict';

    /**
     * 자동 이동 카운트다운 (선택사항)
     */
    function initAutoRedirect() {
        const nextButton = document.querySelector('.btn-next');
        if (!nextButton) return;

        // 자동 이동을 원하면 주석 해제
        // let countdown = 10;
        // const originalText = nextButton.innerHTML;
        
        // const timer = setInterval(() => {
        //     countdown--;
        //     nextButton.innerHTML = `${originalText} (${countdown}초)`;
            
        //     if (countdown <= 0) {
        //         clearInterval(timer);
        //         nextButton.click();
        //     }
        // }, 1000);

        // 사용자가 클릭하면 카운트다운 중지
        // nextButton.addEventListener('click', () => {
        //     clearInterval(timer);
        // });
    }

    /**
     * 결과 애니메이션 강조
     */
    function emphasizeResult() {
        const resultCard = document.querySelector('.result-card');
        if (!resultCard) return;

        // 1초 후 강조 효과
        setTimeout(() => {
            resultCard.style.transform = 'scale(1.02)';
            setTimeout(() => {
                resultCard.style.transform = 'scale(1)';
            }, 200);
        }, 500);
    }

    /**
     * 키보드 단축키
     */
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Enter 또는 Space 키로 다음 버튼 클릭
            if (e.key === 'Enter' || e.key === ' ') {
                const nextButton = document.querySelector('.btn-next');
                if (nextButton && document.activeElement !== nextButton) {
                    e.preventDefault();
                    nextButton.click();
                }
            }
        });
    }

    /**
     * 초기화
     */
    function init() {
        emphasizeResult();
        initKeyboardShortcuts();
        // initAutoRedirect(); // 자동 이동 원하면 주석 해제

        console.log('결과 페이지 초기화 완료');
    }

    // 페이지 로드 시 초기화
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();