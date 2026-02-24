/**
 * 참가자 정보 입력 페이지 JavaScript
 */

(function() {
    'use strict';

    const form = document.getElementById('traitForm');
    const consentCheckbox = document.getElementById('consent');
    const submitButton = document.querySelector('.btn-submit');

    /**
     * 폼 유효성 검사
     */
    function validateForm() {
        // 필수 필드 확인
        const product = document.querySelector('input[name="product"]:checked');
        const expectedPrice = document.getElementById('expectedPrice');
        const risk = document.querySelector('input[name="risk"]:checked');
        const loss = document.querySelector('input[name="loss"]:checked');
        const exp = document.querySelector('input[name="exp"]:checked');
        const consent = document.getElementById('consent');

        const validations = [
            { field: product, message: '구매 희망 상품을 선택해주세요' },
            { field: expectedPrice, message: '예상 가격을 입력해주세요', custom: () => {
                const value = parseInt(expectedPrice.value);
                if (!value || value < 5 || value > 100) {
                    return '예상 가격은 5~100만원 사이로 입력해주세요';
                }
                return null;
            }},
            { field: risk, message: '위험성향 질문에 답해주세요' },
            { field: loss, message: '손실회피 질문에 답해주세요' },
            { field: exp, message: '경매 경험 여부를 선택해주세요' },
            { field: consent, message: '실험 참여 동의가 필요합니다', custom: () => {
                if (!consent.checked) {
                    return '실험 참여에 동의해주세요';
                }
                return null;
            }}
        ];

        for (const validation of validations) {
            if (validation.custom) {
                const customError = validation.custom();
                if (customError) {
                    showAlert(customError, 'warning');
                    scrollToElement(validation.field);
                    return false;
                }
            } else if (!validation.field) {
                showAlert(validation.message, 'warning');
                return false;
            }
        }

        return true;
    }

    /**
     * 요소로 스크롤
     */
    function scrollToElement(element) {
        if (element) {
            const elementRect = element.getBoundingClientRect();
            const absoluteElementTop = elementRect.top + window.pageYOffset;
            const middle = absoluteElementTop - (window.innerHeight / 2);
            window.scrollTo({
                top: middle,
                behavior: 'smooth'
            });
        }
    }

    /**
     * 알림 메시지 표시
     */
    function showAlert(message, type = 'warning') {
        // 기존 알림 제거
        const existingAlert = document.querySelector('.custom-alert');
        if (existingAlert) {
            existingAlert.remove();
        }

        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show custom-alert`;
        alert.style.position = 'fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.style.minWidth = '300px';
        alert.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        
        const icon = type === 'warning' ? 'fa-exclamation-triangle' : 
                     type === 'success' ? 'fa-check-circle' : 'fa-info-circle';
        
        alert.innerHTML = `
            <i class="fas ${icon}"></i> ${message}
            <button type="button" class="close" onclick="this.parentElement.remove()">
                <span>&times;</span>
            </button>
        `;
        
        document.body.appendChild(alert);

        // 5초 후 자동 제거
        setTimeout(() => {
            if (alert.parentElement) {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.3s';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    }

    /**
     * 진행률 계산 및 표시
     */
    function updateProgress() {
        const totalQuestions = 6;
        let answeredQuestions = 0;

        // 각 질문 확인
        if (document.querySelector('input[name="product"]:checked')) answeredQuestions++;
        if (document.getElementById('expectedPrice').value) answeredQuestions++;
        if (document.querySelector('input[name="risk"]:checked')) answeredQuestions++;
        if (document.querySelector('input[name="loss"]:checked')) answeredQuestions++;
        if (document.querySelector('input[name="exp"]:checked')) answeredQuestions++;
        if (document.getElementById('consent').checked) answeredQuestions++;

        const progress = Math.round((answeredQuestions / totalQuestions) * 100);
        
        // 제출 버튼 텍스트 업데이트
        if (progress === 100) {
            submitButton.innerHTML = '<i class="fas fa-check"></i> 모두 완료! 실험 시작하기';
            submitButton.classList.add('btn-success');
            submitButton.classList.remove('btn-primary');
        } else {
            submitButton.innerHTML = `<i class="fas fa-arrow-right"></i> 실험 시작하기 (${progress}%)`;
            submitButton.classList.add('btn-primary');
            submitButton.classList.remove('btn-success');
        }
    }

    /**
     * 라디오 버튼 애니메이션
     */
    function initRadioAnimations() {
        const radioButtons = document.querySelectorAll('input[type="radio"]');
        
        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                // 같은 name의 다른 라디오 버튼들 스타일 초기화
                const name = this.name;
                document.querySelectorAll(`input[name="${name}"]`).forEach(r => {
                    const parent = r.closest('.custom-radio, .scale-button, label');
                    if (parent) {
                        parent.style.animation = 'none';
                    }
                });

                // 선택된 버튼 애니메이션
                const parent = this.closest('.custom-radio, .scale-button, label');
                if (parent) {
                    parent.style.animation = 'pulse 0.3s ease-out';
                    setTimeout(() => {
                        parent.style.animation = '';
                    }, 300);
                }

                updateProgress();
            });
        });
    }

    /**
     * 숫자 입력 검증
     */
    function initPriceInput() {
        const priceInput = document.getElementById('expectedPrice');
        
        if (!priceInput) return;

        priceInput.addEventListener('input', function() {
            // 숫자만 입력 허용
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // 범위 확인
            const value = parseInt(this.value);
            if (value > 100) {
                this.value = '100';
            } else if (value < 0) {
                this.value = '';
            }

            updateProgress();
        });

        // 포커스 시 자동 선택
        priceInput.addEventListener('focus', function() {
            this.select();
        });

        // 엔터키로 다음 질문으로 이동
        priceInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const riskSection = document.querySelector('input[name="risk"]');
                if (riskSection) {
                    scrollToElement(riskSection);
                }
            }
        });
    }

    /**
     * 동의 체크박스 이벤트
     */
    function initConsentCheckbox() {
        if (!consentCheckbox) return;

        consentCheckbox.addEventListener('change', function() {
            if (this.checked) {
                const consentBox = this.closest('.consent-box');
                if (consentBox) {
                    consentBox.style.animation = 'pulse 0.3s ease-out';
                    setTimeout(() => {
                        consentBox.style.animation = '';
                    }, 300);
                }
            }
            updateProgress();
        });
    }

    /**
     * 폼 제출 처리
     */
    function initFormSubmit() {
        if (!form) return;

        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // 유효성 검사
            if (!validateForm()) {
                return false;
            }

            // 제출 확인
            const confirmed = confirm(
                '입력하신 정보를 확인해주세요.\n\n' +
                '제출 후에는 수정할 수 없습니다.\n' +
                '실험을 시작하시겠습니까?'
            );

            if (!confirmed) {
                return false;
            }

            // 로딩 상태
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 처리 중...';

            // 폼 제출
            this.submit();
        });
    }

    /**
     * 키보드 단축키
     */
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + Enter로 제출
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                if (form) {
                    form.dispatchEvent(new Event('submit', { cancelable: true }));
                }
            }
        });
    }

    /**
     * 툴팁 초기화
     */
    function initTooltips() {
        // Bootstrap tooltip 사용 (있는 경우)
        if (typeof $().tooltip === 'function') {
            $('[data-toggle="tooltip"]').tooltip();
        }
    }

    /**
     * 페이지 이탈 경고
     */
    function initBeforeUnload() {
        let formTouched = false;

        // 폼 입력 감지
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                formTouched = true;
            });
        });

        // 페이지 이탈 시 경고
        window.addEventListener('beforeunload', function(e) {
            if (formTouched && !form.submitted) {
                e.preventDefault();
                e.returnValue = '입력한 정보가 저장되지 않을 수 있습니다. 페이지를 나가시겠습니까?';
                return e.returnValue;
            }
        });

        // 폼 제출 시 플래그 설정
        form.addEventListener('submit', function() {
            form.submitted = true;
        });
    }

    /**
     * 초기화
     */
    function init() {
        initRadioAnimations();
        initPriceInput();
        initConsentCheckbox();
        initFormSubmit();
        initKeyboardShortcuts();
        initTooltips();
        initBeforeUnload();
        updateProgress();

        console.log('참가자 정보 입력 페이지 초기화 완료');
    }

    // 페이지 로드 시 초기화
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();