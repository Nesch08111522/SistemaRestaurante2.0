(() => {
 const root = document.querySelector('.bp-page'); if (!root) return;
 root.querySelectorAll('[data-billing]').forEach(button => button.addEventListener('click', () => {
   const annual = button.dataset.billing === 'annual';
   root.querySelectorAll('[data-billing]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
   root.querySelectorAll('[data-price]').forEach(el => el.textContent = 'S/ ' + Number(el.dataset[annual ? 'annual' : 'monthly']).toLocaleString('en-US'));
   root.querySelectorAll('[data-period]').forEach(el => el.textContent = annual ? '/ año' : '/ mes');
 }));
})();
