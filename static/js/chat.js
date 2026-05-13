async function loadFileList() {
    try {
        const res = await fetch("/files");
        const data = await res.json();
        const fileListElement = document.getElementById('fileList');
        fileListElement.innerHTML = data.files.map(f => `
            <div class="file-item" onclick="openViewer('${f}', 1)">
                <div class="file-info">📄 ${f}</div>
                <button class="delete-btn" onclick="deleteFile(event, '${f}')">×</button>
            </div>
        `).join('');
        document.getElementById('usageDisplay').innerText = `${data.current_size}MB / ${data.max_size}MB`;
    } catch (e) { console.error(e); }
}

async function deleteFile(event, filename) {
    event.stopPropagation();
    if (!confirm(`'${filename}' 파일을 삭제하시겠습니까?`)) return;

    const statusMsg = document.getElementById('uploadStatus');
    const statusTitle = document.getElementById('statusTitle');
    const statusDesc = document.getElementById('statusDesc');

    if (statusMsg) {
        statusTitle.innerText = "파일 삭제 및 분석 중...";
        statusDesc.innerText = "지식 베이스를 동기화하고 있습니다.";
        statusMsg.style.display = 'block';
    }

    try {
        const res = await fetch(`/delete/${filename}`, { method: 'DELETE' });
        if (res.ok) await loadFileList();
    } catch (e) { alert("오류 발생"); }
    finally { if (statusMsg) statusMsg.style.display = 'none'; }
}

function openViewer(n, p) {
    const viewerPanel = document.getElementById('viewerPanel');
    const iframe = document.getElementById('pdfViewer');
    viewerPanel.classList.add('open');
    iframe.src = "about:blank"; 
    setTimeout(() => {
        iframe.src = `/pdf_files/${n}?t=${Date.now()}#page=${p}&zoom=100`;
    }, 50);
}

function closeViewer() { document.getElementById('viewerPanel').classList.remove('open'); }

async function uploadFile() {
    const fileInput = document.getElementById('hiddenFile');
    const statusMsg = document.getElementById('uploadStatus');
    const statusTitle = document.getElementById('statusTitle');
    const statusDesc = document.getElementById('statusDesc');
    
    if (fileInput.files.length === 0) return;
    const formData = new FormData();
    for (let file of fileInput.files) { formData.append('files', file); }

    if (statusMsg) {
        statusTitle.innerText = "업로딩 및 분석 중...";
        statusDesc.innerText = "문서를 분석하여 엔진을 구성 중입니다.";
        statusMsg.style.display = 'block';
    }

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        if (response.ok) await loadFileList(); 
    } catch (e) { alert("오류 발생"); }
    finally {
        if (statusMsg) statusMsg.style.display = 'none';
        fileInput.value = ''; 
    }
}

async function askQuestion() {
    const input = document.getElementById('questionInput');
    const sendBtn = document.getElementById('sendBtn');
    const q = input.value.trim();
    
    if(!q || document.getElementById('loading').style.display === "block") return;
    
    input.value = "";
    if(document.getElementById('welcomeMsg')) document.getElementById('welcomeMsg').remove();

    const chat = document.getElementById('chatArea');
    chat.innerHTML += `<div style="align-self:flex-end; background:var(--accent); color:white; padding:12px 20px; border-radius:20px 20px 0 20px; max-width:80%; margin-bottom:10px;">${q}</div>`;
    
    // 답변 박스 생성 (다운로드 버튼 포함)
    const answerBox = document.createElement('div');
    answerBox.className = 'answer-box';
    answerBox.innerHTML = `
        <button class="download-btn-hidden">💾 메모장 저장</button>
        <div style="font-weight:bold; color:var(--accent); margin-bottom:8px;">AI 분석 결과:</div>
        <div class="content"></div>
        <div class="source-container"></div>
    `;
    chat.appendChild(answerBox);
    
    const dlBtn = answerBox.querySelector('button'); // 현재 생성된 버튼 참조
    
    document.getElementById('loading').style.display = "block";
    if(sendBtn) {
        sendBtn.disabled = true;
        sendBtn.style.opacity = "0.5";
        sendBtn.style.cursor = "not-allowed";
    }
    chat.scrollTop = chat.scrollHeight;

    try {
        const fd = new FormData();
        fd.append("question", q);
        fd.append("session_id", "user_123");

        const response = await fetch("/ask", { method: "POST", body: fd });
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullMarkdown = "";
        let sourcesRaw = [];

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            for (let line of lines) {
                if (line.startsWith('data: ')) {
                    const raw = line.substring(6).trim();
                    if (raw === '[DONE]') break;
                    try {
                        const p = JSON.parse(raw);
                        if (p.type === 'content') {
                            fullMarkdown += p.delta;
                            answerBox.querySelector('.content').innerHTML = marked.parse(fullMarkdown);
                        } else if (p.type === 'sources') {
                            sourcesRaw = p.data;
                            answerBox.querySelector('.source-container').innerHTML = `
                                <div style="font-size:0.8rem; font-weight:bold; color:#666; margin-bottom:10px;">참조된 문서 출처:</div>
                                ${p.data.map(s => `
                                    <div class="source-item" onclick="openViewer('${s.file}', ${s.page})">
                                        <span class="source-tag">📍 ${s.file} (p.${s.page})</span>
                                        <span class="source-snippet">"...${s.snippet}..."</span>
                                    </div>
                                `).join('')}
                            `;
                        }
                        chat.scrollTop = chat.scrollHeight;
                    } catch(e) {}
                }
            }
        }

        // 답변이 완료되면 다운로드 버튼 표시 및 기능 연결
        if (fullMarkdown.length > 0) {
            dlBtn.className = 'download-btn-visible'; 
            dlBtn.onclick = () => {
                const pureAnswer = answerBox.querySelector('.content').innerText;
                const sourcesText = sourcesRaw.map(s => `[출처] ${s.file} (p.${s.page})\n- 내용 요약: ${s.snippet}`).join('\n\n');
                const fileContent = `▶ 질문: ${q}\n\n▶ AI 분석 답변:\n${pureAnswer}\n\n▶ 근거 문서 정보:\n${sourcesText}`;
                
                const blob = new Blob([fileContent], { type: 'text/plain;charset=utf-8' });
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `AI_분석결과_${new Date().getTime()}.txt`;
                link.click();
                window.URL.revokeObjectURL(url);
            };
        }

    } catch (error) { 
        console.error(error); 
        answerBox.querySelector('.content').innerHTML = "<span style='color:red;'>답변을 가져오는 중 오류가 발생했습니다.</span>";
    } finally {
        document.getElementById('loading').style.display = "none";
        if(sendBtn) {
            sendBtn.disabled = false;
            sendBtn.style.opacity = "1";
            sendBtn.style.cursor = "pointer";
        }
        chat.scrollTop = chat.scrollHeight;
        input.focus();
    }
}

window.onload = loadFileList;