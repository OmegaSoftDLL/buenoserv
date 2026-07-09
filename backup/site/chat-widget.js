(function () {
  const CONFIG = {
    primary: '#0a1628',
    gold: '#C9A84C',
    goldLight: '#E8D48B',
    userBubble: '#1A237E',
    botBubble: '#1e2d4d',
    bg: '#0d1a30',
    text: '#e8e8e8',
    muted: '#7a87a0',
    border: '#1e2d4d',
  };

  const STATUS = { agents: 12, pipeline: 'SE 138kV · Anel DWDM · Consultoria' };

  const email = 'ricardo.bueno@buenoservengenharia.com';
  const phone = '(19) 99999-9999';

  // ---------- state ----------
  let open = false;
  let escHandler = null;

  // ---------- create DOM ----------
  const container = document.createElement('div');
  container.id = 'bs-chat-container';
  container.innerHTML = `
    <button id="bs-chat-toggle" aria-label="Abrir chat">💬</button>
    <div id="bs-chat-panel">
      <div id="bs-chat-header">
        <div>
          <div id="bs-chat-title">BUENOSERV Chat</div>
          <div id="bs-chat-status"><span class="dot"></span> Online</div>
        </div>
        <button id="bs-chat-close" aria-label="Fechar">✕</button>
      </div>
      <div id="bs-chat-messages">
        <div class="msg bot">Olá! Como a BUENOSERV pode ajudar?</div>
      </div>
      <div id="bs-chat-shortcuts">
        <button data-cmd="proposta">📋 Quero uma proposta</button>
        <button data-cmd="status">📊 Status de projeto</button>
        <button data-cmd="contato">📞 Falar com engenheiro</button>
      </div>
      <div id="bs-chat-input-row">
        <input id="bs-chat-input" type="text" placeholder="Digite sua mensagem..." autocomplete="off">
        <button id="bs-chat-send" aria-label="Enviar">→</button>
      </div>
    </div>
  `;

  document.body.appendChild(container);

  // ---------- refs ----------
  const toggle = container.querySelector('#bs-chat-toggle');
  const panel = container.querySelector('#bs-chat-panel');
  const closeBtn = container.querySelector('#bs-chat-close');
  const messages = container.querySelector('#bs-chat-messages');
  const input = container.querySelector('#bs-chat-input');
  const sendBtn = container.querySelector('#bs-chat-send');
  const shortcuts = container.querySelectorAll('[data-cmd]');

  // ---------- helpers ----------
  function addMessage(text, role) {
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  // ---------- bot response ----------
  function botResponse(msg) {
    const lower = msg.toLowerCase();

    if (lower.includes('proposta') || lower.includes('orçamento') || lower.includes('orcamento')) {
      addMessage('Ótimo! Um engenheiro entrará em contato em até 24h.', 'bot');
    } else if (lower.includes('status') || lower.includes('projeto')) {
      if (lower.includes('status')) {
        addMessage(
          `📊 **Resumo do Sistema**\nAgentes alocados: ${STATUS.agents}\nPipeline ativo: ${STATUS.pipeline}`,
          'bot'
        );
      } else {
        addMessage('Qual projeto? (ex: SE 138kV, Anel DWDM, Consultoria)', 'bot');
      }
    } else if (lower.includes('contato') || lower.includes('engenheiro') || lower.includes('falar')) {
      addMessage(`📧 ${email}\n📱 ${phone}`, 'bot');
    } else {
      addMessage('Comando não reconhecido. Opções: proposta, status, contato, projeto', 'bot');
    }
  }

  // ---------- send ----------
  function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    addMessage(text, 'user');
    input.value = '';

    // Simula latência do bot
    setTimeout(() => {
      botResponse(text);
    }, 400);

    // TODO: substituir por POST para API real
    // const resp = await fetch('http://localhost:8095/webhook', {
    //   method: 'POST',
    //   body: JSON.stringify({ from: 'web', text })
    // });
  }

  // ---------- open / close ----------
  function openPanel() {
    open = true;
    panel.classList.add('open');
    toggle.classList.add('hidden');
    input.focus();
    escHandler = function (e) {
      if (e.key === 'Escape') closePanel();
    };
    document.addEventListener('keydown', escHandler);
  }

  function closePanel() {
    open = false;
    panel.classList.remove('open');
    toggle.classList.remove('hidden');
    if (escHandler) document.removeEventListener('keydown', escHandler);
  }

  function togglePanel() {
    open ? closePanel() : openPanel();
  }

  // ---------- events ----------
  toggle.addEventListener('click', openPanel);
  closeBtn.addEventListener('click', closePanel);
  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') sendMessage();
  });

  shortcuts.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const cmd = this.getAttribute('data-cmd');
      addMessage(this.textContent.trim(), 'user');
      setTimeout(function () {
        botResponse(cmd);
      }, 400);
    });
  });

  // ---------- styles (injected) ----------
  const style = document.createElement('style');
  style.textContent = `
    #bs-chat-container * { box-sizing: border-box; }
    #bs-chat-container { font-family: 'Inter', -apple-system, sans-serif; }

    /* toggle button */
    #bs-chat-toggle {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 99999;
      width: 56px;
      height: 56px;
      border-radius: 50%;
      border: none;
      background: ${CONFIG.gold};
      color: ${CONFIG.primary};
      font-size: 1.5rem;
      cursor: pointer;
      box-shadow: 0 6px 24px rgba(201,168,76,0.35);
      transition: all 0.25s ease;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    #bs-chat-toggle:hover { background: ${CONFIG.goldLight}; transform: scale(1.08); }
    #bs-chat-toggle.hidden { opacity: 0; transform: scale(0.6); pointer-events: none; }

    /* panel container */
    #bs-chat-panel {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 99999;
      width: 380px;
      height: 560px;
      max-height: calc(100vh - 48px);
      background: ${CONFIG.bg};
      border: 1px solid ${CONFIG.border};
      border-radius: 16px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 12px 48px rgba(0,0,0,0.6);
      transform: translateY(24px) scale(0.95);
      opacity: 0;
      pointer-events: none;
      transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
      overflow: hidden;
    }
    #bs-chat-panel.open {
      transform: translateY(0) scale(1);
      opacity: 1;
      pointer-events: auto;
    }

    /* header */
    #bs-chat-header {
      background: ${CONFIG.primary};
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid ${CONFIG.border};
      flex-shrink: 0;
    }
    #bs-chat-title { font-weight: 700; font-size: 1rem; color: #fff; }
    #bs-chat-status { font-size: 0.78rem; color: ${CONFIG.muted}; display: flex; align-items: center; gap: 5px; margin-top: 2px; }
    #bs-chat-status .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #34d399; }
    #bs-chat-close {
      background: none; border: none; color: ${CONFIG.muted}; font-size: 1.2rem;
      cursor: pointer; padding: 4px 8px; border-radius: 6px; transition: all 0.2s;
    }
    #bs-chat-close:hover { background: rgba(255,255,255,0.08); color: #fff; }

    /* messages */
    #bs-chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px 16px 8px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      scroll-behavior: smooth;
    }
    #bs-chat-messages::-webkit-scrollbar { width: 4px; }
    #bs-chat-messages::-webkit-scrollbar-thumb { background: ${CONFIG.border}; border-radius: 4px; }
    .msg {
      max-width: 85%;
      padding: 10px 14px;
      border-radius: 14px;
      font-size: 0.9rem;
      line-height: 1.5;
      word-wrap: break-word;
      white-space: pre-wrap;
      animation: bsFadeIn 0.2s ease-out;
    }
    .msg.user {
      align-self: flex-end;
      background: ${CONFIG.userBubble};
      color: #fff;
      border-bottom-right-radius: 4px;
    }
    .msg.bot {
      align-self: flex-start;
      background: ${CONFIG.botBubble};
      color: ${CONFIG.text};
      border-bottom-left-radius: 4px;
    }

    /* shortcuts */
    #bs-chat-shortcuts {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding: 8px 16px 4px;
      flex-shrink: 0;
    }
    #bs-chat-shortcuts button {
      background: transparent;
      border: 1px solid ${CONFIG.border};
      color: ${CONFIG.gold};
      font-size: 0.78rem;
      padding: 6px 12px;
      border-radius: 20px;
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;
      font-weight: 500;
    }
    #bs-chat-shortcuts button:hover {
      background: ${CONFIG.gold};
      color: ${CONFIG.primary};
      border-color: ${CONFIG.gold};
    }

    /* input row */
    #bs-chat-input-row {
      display: flex;
      gap: 8px;
      padding: 10px 16px 16px;
      flex-shrink: 0;
    }
    #bs-chat-input {
      flex: 1;
      padding: 10px 14px;
      background: ${CONFIG.primary};
      border: 1px solid ${CONFIG.border};
      border-radius: 10px;
      color: #fff;
      font-size: 0.9rem;
      outline: none;
      font-family: inherit;
      transition: border-color 0.2s;
    }
    #bs-chat-input:focus { border-color: ${CONFIG.gold}; }
    #bs-chat-input::placeholder { color: ${CONFIG.muted}; }
    #bs-chat-send {
      width: 42px;
      height: 42px;
      border-radius: 10px;
      border: none;
      background: ${CONFIG.gold};
      color: ${CONFIG.primary};
      font-size: 1.1rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
      flex-shrink: 0;
    }
    #bs-chat-send:hover { background: ${CONFIG.goldLight}; }

    @keyframes bsFadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    /* mobile */
    @media (max-width: 480px) {
      #bs-chat-panel {
        right: 0;
        bottom: 0;
        width: 100%;
        height: 100%;
        max-height: 100vh;
        border-radius: 0;
        border: none;
        transform: translateY(24px) scale(0.95);
      }
      #bs-chat-panel.open {
        transform: translateY(0) scale(1);
      }
      #bs-chat-toggle {
        bottom: 16px;
        right: 16px;
      }
    }
  `;
  document.head.appendChild(style);
})();
