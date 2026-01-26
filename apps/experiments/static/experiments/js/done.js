/**
 * 실험 종료 페이지 JavaScript
 */

(function() {
    'use strict';

    /**
     * 테이블 행 클릭 시 강조 효과
     */
    function initTableRowHighlight() {
        const rows = document.querySelectorAll('.table tbody tr');
        
        rows.forEach(row => {
            row.addEventListener('click', function() {
                // 기존 강조 제거
                rows.forEach(r => r.style.outline = 'none');
                
                // 클릭한 행 강조
                this.style.outline = '2px solid #007bff';
                this.style.outlineOffset = '-2px';
                
                // 2초 후 강조 제거
                setTimeout(() => {
                    this.style.outline = 'none';
                }, 2000);
            });
        });
    }

    /**
     * 참가자 코드 복사 기능
     */
    function initCodeCopy() {
        const codeElement = document.querySelector('.alert-info h3');
        if (!codeElement) return;

        const code = codeElement.textContent.trim();
        
        // 클릭 시 복사
        codeElement.style.cursor = 'pointer';
        codeElement.title = '클릭하여 복사';
        
        codeElement.addEventListener('click', function() {
            // 클립보드에 복사
            if (navigator.clipboard) {
                navigator.clipboard.writeText(code).then(() => {
                    showCopyMessage('복사되었습니다!');
                }).catch(err => {
                    console.error('복사 실패:', err);
                });
            } else {
                // 구형 브라우저 대응
                const textarea = document.createElement('textarea');
                textarea.value = code;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                try {
                    document.execCommand('copy');
                    showCopyMessage('복사되었습니다!');
                } catch (err) {
                    console.error('복사 실패:', err);
                }
                document.body.removeChild(textarea);
            }
        });
    }

    /**
     * 복사 완료 메시지 표시
     */
    function showCopyMessage(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success';
        alert.style.position = 'fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.style.minWidth = '200px';
        alert.innerHTML = `<i class="fas fa-check"></i> ${message}`;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s';
            setTimeout(() => alert.remove(), 300);
        }, 2000);
    }

    /**
     * 통계 계산 및 표시 (선택사항)
     */
    function displayStatistics() {
        const rows = document.querySelectorAll('.table tbody tr');
        if (rows.length === 0) return;

        let totalRounds = 0;
        let buyCount = 0;
        let bidCount = 0;
        let winCount = 0;
        let loseCount = 0;

        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 3) return;

            totalRounds++;
            const decisionBadge = cells[1].querySelector('.badge');
            const outcomeBadge = cells[3].querySelector('.badge');

            if (decisionBadge && decisionBadge.classList.contains('badge-success')) {
                buyCount++;
            } else if (decisionBadge) {
                bidCount++;
            }

            if (outcomeBadge) {
                if (outcomeBadge.textContent.includes('낙찰')) {
                    winCount++;
                } else if (outcomeBadge.textContent.includes('유찰')) {
                    loseCount++;
                }
            }
        });

        console.log('실험 통계:', {
            총_라운드: totalRounds,
            즉시구매: buyCount,
            입찰: bidCount,
            낙찰: winCount,
            유찰: loseCount
        });
    }

    /**
     * 초기화
     */
    function init() {
        initTableRowHighlight();
        initCodeCopy();
        displayStatistics();

        console.log('실험 종료 페이지 초기화 완료');
    }

    // 페이지 로드 시 초기화
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();