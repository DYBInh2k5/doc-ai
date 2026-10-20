const state = { token: localStorage.getItem('documind_token'), register: false, documentId: null };
const $ = (selector) => document.querySelector(selector);
const api = async (path, options = {}) => {
  const headers = options.headers || {};
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { ...options, headers });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Có lỗi xảy ra');
  return data;
};

function showWorkspace() { $('#auth-view').classList.add('hidden'); $('#workspace').classList.remove('hidden'); loadWorkspace(); }
async function loadWorkspace() { await loadDocuments(); await loadHistory(); }

$('#toggle-auth').onclick = () => { state.register = !state.register; $('#toggle-auth').textContent = state.register ? 'Đã có tài khoản? Đăng nhập' : 'Chưa có tài khoản? Đăng ký'; document.querySelector('#auth-form .primary').innerHTML = state.register ? 'Tạo tài khoản <span>↗</span>' : 'Đăng nhập <span>↗</span>'; };
$('#auth-form').onsubmit = async (event) => {
  event.preventDefault(); $('#auth-error').textContent = '';
  try { const data = await api(state.register ? '/api/auth/register' : '/api/auth/login', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({email: $('#email').value, password: $('#password').value}) }); state.token = data.token; localStorage.setItem('documind_token', state.token); showWorkspace(); } catch (error) { $('#auth-error').textContent = error.message; }
};
$('#logout').onclick = () => { localStorage.removeItem('documind_token'); location.reload(); };
$('#file-input').onchange = async (event) => { const file = event.target.files[0]; if (!file) return; const form = new FormData(); form.append('file', file); try { await api('/api/documents', {method:'POST', body:form}); await loadDocuments(); } catch (error) { alert(error.message); } event.target.value = ''; };
async function loadDocuments() { const documents = await api('/api/documents'); $('#document-list').innerHTML = documents.map(doc => `<div class="document ${doc.id === state.documentId ? 'selected' : ''}" data-id="${doc.id}">${escapeHtml(doc.filename)}<small>${new Date(doc.created_at).toLocaleDateString('vi-VN')}</small></div>`).join('') || '<p class="hint">Chưa có tài liệu.</p>'; document.querySelectorAll('.document').forEach(item => item.onclick = () => selectDocument(Number(item.dataset.id))); }
function selectDocument(id) { state.documentId = id; $('#question').disabled = false; $('#chat-form button').disabled = false; $('#empty-chat').classList.add('hidden'); $('#messages').classList.remove('hidden'); $('#question').placeholder = 'Đặt câu hỏi về tài liệu...'; loadDocuments(); }
$('#chat-form').onsubmit = async (event) => { event.preventDefault(); const question = $('#question').value.trim(); if (!question || !state.documentId) return; addMessage(question, 'user'); $('#question').value = ''; try { const result = await api('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({document_id:state.documentId, question})}); addMessage(result.answer, 'ai', result.citations); loadHistory(); } catch(error) { addMessage(error.message, 'ai'); } };
function addMessage(text, type, citations = []) { const citationHtml = citations.map(item => `<div class="citation">Đoạn ${item.section}: ${escapeHtml(item.text.slice(0, 280))}${item.text.length > 280 ? '...' : ''}</div>`).join(''); $('#messages').insertAdjacentHTML('beforeend', `<div class="message ${type}">${escapeHtml(text)}${citationHtml}</div>`); $('#messages').scrollTop = $('#messages').scrollHeight; }
async function loadHistory() { const history = await api('/api/history'); $('#history-list').innerHTML = history.map(item => `<div class="history-item">${escapeHtml(item.question.slice(0, 64))}${item.question.length > 64 ? '...' : ''}</div>`).join('') || '<p class="hint">Chưa có câu hỏi.</p>'; }
function escapeHtml(value) { const div = document.createElement('div'); div.textContent = value; return div.innerHTML; }
if (state.token) showWorkspace();
