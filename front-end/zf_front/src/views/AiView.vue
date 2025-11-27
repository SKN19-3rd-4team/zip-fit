<script setup lang="ts">
    import { ref, nextTick, onMounted } from 'vue';
    import { v4 as uuidv4 } from 'uuid';
    import { marked } from 'marked';

    function generateGuidLib(): string {
        return uuidv4();
    }

    let guid2 = "";

    // 메시지 타입 정의
    interface Message {
        type: 'bot' | 'user';
        content: string;
        time: string;
    }

    // API 응답 타입 정의
    interface ChatResponse {
        query: string;
        answer: string;
        sources: Array<{
            announcement_id: string;                
            announcement_title: string;
            announcement_date: string;
            announcement_url: string;
            announcement_status: string;
            region: string;
            notice_type: string;
            category: string;
        }>;
        metadata?: Record<string, unknown>;
    }

    // 상태 관리
    const messages = ref<Message[]>([
        {
            type: 'bot',
            content: `
저는 LH, SH, GH 공공주택 전문 AI 어시스턴트입니다.<br />
<br />
** 저의 강점 :**<br />
• 실제 공고 PDF 문서를 분석하여 정확한 정보 제공<br />
• 복잡한 공고 내용을 쉽게 설명<br />
• 맞춤형 자격 요건 확인<br />
• 대출 및 지원 제도 안내<br />
<br />
공고에 대해 궁금하신 점을 편하게 물어보세요!`,
            time: getCurrentTime(),
        },
    ]);

    const userInput = ref('');
    const isLoading = ref(false);
    const messageContainer = ref<HTMLElement | null>(null);
    const showHeader = ref(true);
    const isFirstMessage = ref(true);

    // 현재 시간 가져오기
    function getCurrentTime(): string {
        const now = new Date();
        const hours = now.getHours();
        const minutes = now.getMinutes();
        const period = hours >= 12 ? '오후' : '오전';
        const displayHours = hours > 12 ? hours - 12 : hours === 0 ? 12 : hours;
        return `${period} ${String(displayHours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
    }

    // 스크롤을 하단으로 이동
    function scrollToBottom() {
        nextTick(() => {
            if (messageContainer.value) {
                // 여러 방법 시도
                messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
                
                // 또는 마지막 메시지로 스크롤
                const messageElements = messageContainer.value.querySelectorAll('.line');
                if (messageElements.length > 0) {
                    const lastMessage = messageElements[messageElements.length - 1] as HTMLElement;
                    if (lastMessage) {
                        lastMessage.scrollIntoView({ behavior: 'smooth', block: 'end' });
                    }
                }
            }
        });
    }

    // 메시지 전송
    async function sendMessage() {
        if (!userInput.value.trim() || isLoading.value) return;

        // 첫 메시지 전송 시 헤더 숨김
        if (isFirstMessage.value) {
            showHeader.value = false;
            isFirstMessage.value = false;
        }

        const query = userInput.value.trim();
        userInput.value = '';

        // 사용자 메시지 추가
        messages.value.push({
            type: 'user',
            content: query,
            time: getCurrentTime(),
        });

        // 스크롤을 하단으로 이동
        await nextTick();
        scrollToBottom();

        // 로딩 상태 시작
        isLoading.value = true;
        
        // 로딩 인디케이터가 나타난 후 스크롤
        await nextTick();
        scrollToBottom();

        try {
            // console.log(guid2);
            // API 호출
            const response = await fetch('http://127.0.0.1:8000/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: guid2,
                    query: query
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data: ChatResponse = await response.json();

            let sources_content = ""; // sources_content 변수 선언

            if (data.sources && data.sources.length > 0) {
                // 💡 HTML 문자열을 시작합니다. (답변과 소스 구분을 위한 태그 추가)
                sources_content += '<div class="sources-in-bubble">';
                sources_content += '<h4><i class="fa-solid fa-book-open"></i> 참고 공고</h4>';
                sources_content += '<ul>';

                for (const source of data.sources) {
                    // 공고 상태에 따른 뱃지 클래스 결정 (CSS에서 정의)
                    let statusClass = '';
                    if (source.announcement_status === '접수중') {
                        statusClass = 'status-badge-active';
                    } else if (source.announcement_status === '접수마감') {
                        statusClass = 'status-badge-closed';
                    } else {
                        statusClass = 'status-badge-default';
                    }

                    // 각 소스를 리스트 아이템으로 추가합니다. (새로운 데이터 필드 반영)
                    sources_content += `
                        <li class="source-item">
                            <div class="source-title-wrap">
                                <span class="source-title">${source.announcement_title}</span>
                                <span class="${statusClass}">${source.announcement_status}</span>
                            </div>
                            <div class="source-details">
                                <span>지역: ${source.region}</span>
                                <span>공고일: ${source.announcement_date}</span>
                                <a href="${source.announcement_url}" target="_blank" class="source-link">
                                    <i class="fa-solid fa-link"></i> 공고 바로가기
                                </a>
                            </div>
                        </li>
                    `;
                }
                
                sources_content += '</ul></div>';
            }

            const htmlAnswer = marked(data.answer);

            // 봇 응답 추가
            messages.value.push({
                type: 'bot',
                content: htmlAnswer + sources_content,
                time: getCurrentTime(),
            });

        } catch (error) {
            console.error('API 호출 오류:', error);
            
            // 에러 메시지 추가
            messages.value.push({
                type: 'bot',
                content: '죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
                time: getCurrentTime(),
            });
        } finally {
            isLoading.value = false;
            await nextTick();
            scrollToBottom();
        }
    }

    // 엔터키 핸들러
    function handleKeyPress(event: KeyboardEvent) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }

    // 💡 컴포넌트가 마운트된 후 데이터 로드 함수 호출
    onMounted(() => {
        guid2 = generateGuidLib()
    });
</script>
    
<template>
    <header class="com-header-wrap" :class="{ 'fade-out': !showHeader }">
        <div class="ui-breadcrumb">
            <ul class="location">
                <li>
                    <strong class="sb">AI 상담</strong>
                </li>
            </ul>
            <div class="info">
                <small>AI 기반 맞춤형 상담 서비스</small>
            </div>
        </div>
    </header>

    <main class="layout-contents">
        <div class="layout-ai-wrap">
            <div class="layer-msg">
                <div class="inner-wrap" ref="messageContainer">
                    <div class="inner">
                        <div 
                            v-for="(message, index) in messages" 
                            :key="index" 
                            class="line"
                        >
                            <!-- 봇 메시지 -->
                            <template v-if="message.type === 'bot'">
                                <div class="avatar bot">
                                    <i class="fa-solid fa-robot"></i>
                                </div>
                                <div class="bubble left" v-html="message.content"></div>
                                <div class="info">{{ message.time }}</div>
                            </template>

                            <!-- 사용자 메시지 -->
                            <template v-else>
                                <div class="bubble right">{{ message.content }}</div>
                                <div class="avatar">
                                    <i class="fa-regular fa-user"></i>
                                </div>
                                <div class="info">{{ message.time }}</div>
                            </template>
                        </div>

                        <!-- 로딩 인디케이터 -->
                        <div v-if="isLoading" class="line">
                            <div class="avatar bot">
                                <i class="fa-solid fa-robot"></i>
                            </div>
                            <div class="bubble left">
                                <i class="fa-solid fa-spinner fa-spin"></i> 답변 생성 중...
                            </div>
                            <div class="info">{{ getCurrentTime() }}</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="layer-input">
                <div class="input">
                    <input 
                        v-model="userInput"
                        type="text" 
                        class="ui-input" 
                        placeholder="공고에 대해 궁금한 점을 물어보세요"
                        @keypress="handleKeyPress"
                        :disabled="isLoading"
                    />
                    <button 
                        class="ui-btn center fill secondary"
                        @click="sendMessage"
                        :disabled="isLoading || !userInput.trim()"
                    >
                        <i class="fa-regular fa-paper-plane"></i>
                    </button>
                </div>
                <!-- <div class="info">
                    <i class="fa-solid fa-bolt txt-orange300 size-fz300"></i>
                    <strong class="sb txt-blue600">AI</strong> 가 실제 공고 문서를
                    분석하여 답변합니다. 정확한 정보는 공식 사이트를 확인해주세요.
                </div> -->
            </div>
        </div>
    </main>
</template>

<style scoped>
    /* AiView.vue에 특화된 스타일 */
    .layer-input .input .ui-btn {
        padding: 0.5rem;  /* 8px로 줄임 (원래 16px) */
        min-width: 3rem;
    }

    /* 헤더 슬라이드업 효과 */
    .com-header-wrap {
        transition: all 0.3s ease-out;
        transform: translateY(0);
        opacity: 1;
        max-height: 200px;
        overflow: hidden;
    }

    .com-header-wrap.fade-out {
        transform: translateY(-100%);
        opacity: 0;
        max-height: 0;
        margin-bottom: 0;
        padding-top: 0;
        padding-bottom: 0;
    }
</style>