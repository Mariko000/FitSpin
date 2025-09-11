// バウンスアニメーション
document.addEventListener('DOMContentLoaded', () => {
    // フォローボタン用
    document.querySelectorAll('.follow-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        btn.classList.remove('bounce');
        void btn.offsetWidth; // 再アニメーションのためリフロー
        btn.classList.add('bounce');
      });
    });
  
    // いいねボタン用（Font Awesomeの<i>アイコンを対象）
    document.querySelectorAll('.post-like-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const icon = btn.querySelector('i');
        if (icon) {
          icon.classList.remove('bounce');
          void icon.offsetWidth;
          icon.classList.add('bounce');
        }
      });
    });
  });
  
  function applyTypingEffect(element) {
    const text = element.textContent;
    element.textContent = ''; // 元のテキストをクリア
    let i = 0;
    
    // カーソル要素を作成
    const cursor = document.createElement('span');
    cursor.className = 'typing-cursor';
    cursor.textContent = '|';
    element.appendChild(cursor);
  
    // 一文字ずつ追加するアニメーション
    function type() {
      if (i < text.length) {
        const char = text.charAt(i);
        const span = document.createElement('span');
        span.textContent = char;
        element.insertBefore(span, cursor);
        i++;
        setTimeout(type, 100); // 100msごとに文字を追加
      } else {
        cursor.remove(); // アニメーション完了後にカーソルを削除
      }
    }
    type();
  }
  //タイピングアニメーション
  // apps/static/js/common.js

function applyTypingEffect(element) {
  const text = element.textContent;
  element.textContent = ''; // 元のテキストをクリア
  let i = 0;
  
  const cursor = document.createElement('span');
  cursor.className = 'typing-cursor';
  cursor.textContent = '|';
  element.appendChild(cursor);

  function type() {
    if (i < text.length) {
      const char = text.charAt(i);
      const span = document.createElement('span');
      span.textContent = char;
      element.insertBefore(span, cursor);
      i++;
      setTimeout(type, 250);
    } else {
      cursor.remove();
    }
  }
  type();
}

document.addEventListener('DOMContentLoaded', () => {
  // .typing-text クラスを持つすべての要素を取得
  const typingElements = document.querySelectorAll('.typing-text');
  typingElements.forEach(element => {
    applyTypingEffect(element);
  });
});